"""Publication Instagram (API Graph de Meta, via la Page Facebook reliée).

La clé d'accès n'est jamais dans le code : elle vient du secret GitHub IG_ACCESS_TOKEN.

Usage :
    python -m pipeline.instagram check          # vérifie la clé, ne publie rien
    python -m pipeline.instagram publish-due    # publie les posts arrivés à échéance
    python -m pipeline.instagram verify         # contrôle hors ligne des posts en attente (sans clé)
"""
from __future__ import annotations

import json
import os
import re
import sys
import time
import urllib.parse
import urllib.request
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parent.parent
CFG = json.loads((ROOT / "config" / "instagram.json").read_text(encoding="utf-8"))
API = f"https://graph.facebook.com/{CFG['graph_version']}"
PARIS = ZoneInfo("Europe/Paris")
SITE = "https://pickandwatch.fr"
EARLY_WAIT = 40 * 60  # les crons GitHub passent parfois toutes les 35 min : un passage peut démarrer jusqu'à 40 min avant l'heure et attendre

# Garde-fou anti-spoiler : un score du type « 112-108 » ou « 112 à 108 » bloque la publication.
SCORE_RE = re.compile(r"\b1?\d{2}\s?(?:-|–|à|a)\s?1?\d{2}\b")
CAPTION_MAX = 2200  # limite Instagram (caractères)


def token() -> str:
    t = os.environ.get("IG_ACCESS_TOKEN", "").strip()
    if not t:
        sys.exit("Secret IG_ACCESS_TOKEN absent.")
    return t


def call(method: str, path: str, **params) -> dict:
    params["access_token"] = token()
    data = urllib.parse.urlencode(params).encode()
    url = f"{API}/{path}"
    if method == "GET":
        req = urllib.request.Request(f"{url}?{data.decode()}")
    else:
        req = urllib.request.Request(url, data=data, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return json.loads(r.read())
    except urllib.error.HTTPError as e:
        body = e.read().decode(errors="replace")
        # On n'affiche jamais la clé : seule la réponse de Meta est montrée.
        raise SystemExit(f"Erreur Meta {e.code} sur {path} : {body}")
    except urllib.error.URLError as e:
        raise SystemExit(f"Erreur réseau sur {path} : {e.reason}")


def check() -> None:
    me = call("GET", CFG["ig_user_id"], fields="username,media_count")
    print(f"Connexion OK : @{me.get('username')} ({me.get('media_count')} publications).")
    lim = call("GET", f"{CFG['ig_user_id']}/content_publishing_limit", fields="quota_usage,config")
    print(f"Quota de publication : {json.dumps(lim.get('data', lim), ensure_ascii=False)}")


def wait_ready(container_id: str, tries: int = 30) -> None:
    for _ in range(tries):
        st = call("GET", container_id, fields="status_code").get("status_code")
        if st == "FINISHED":
            return
        if st in ("ERROR", "EXPIRED"):
            raise SystemExit(f"Conteneur {container_id} en erreur : {st}")
        time.sleep(5)
    raise SystemExit(f"Conteneur {container_id} pas prêt à temps.")


def caption_problems(caption: str) -> list[str]:
    """Garde-fous de la légende, communs à la vérification et à la publication."""
    pb = []
    if SCORE_RE.search(caption):
        pb.append("la légende semble contenir un score")
    if len(caption) > CAPTION_MAX:
        pb.append(f"légende de {len(caption)} caractères (maximum Instagram : {CAPTION_MAX})")
    return pb


def verify() -> None:
    """Contrôle, sans clé ni réseau, chaque post encore en attente : à lancer avant de pousser
    un post.json. Sort en erreur si un post serait refusé à 19h."""
    bad = 0
    for f in sorted((ROOT / "posts").glob("*/post.json")):
        post = json.loads(f.read_text(encoding="utf-8"))
        if post.get("statut") in ("annule", "publie", "echec", "brouillon"):  # brouillon : jamais publié sans validation
            continue
        pb = caption_problems(post.get("legende", ""))
        n = len(post.get("images", []))
        if post.get("type") == "story":  # une story par image : pas de plafond à 10
            if n < 1:
                pb.append("aucune image")
        elif post.get("type") == "reel":  # une vidéo + son image de couverture
            if n != 1:
                pb.append("un Reel attend exactement 1 image (la couverture)")
            if not post.get("video") or not (f.parent / post["video"]).exists():
                pb.append("vidéo du Reel absente")
        elif not 1 <= n <= 10:
            pb.append(f"{n} image(s) (Instagram : 1 à 10)")
        pb += [f"image absente : {n}" for n in post.get("images", []) if not (f.parent / n).exists()]
        try:  # heure d'été / d'hiver : le décalage de publier_a doit être celui de Paris à cette date
            due = datetime.fromisoformat(post["publier_a"])
            if due.utcoffset() != due.astimezone(PARIS).utcoffset():
                pb.append(f"publier_a {post['publier_a']} : décalage attendu {due.astimezone(PARIS):%z} à Paris")
        except (KeyError, TypeError, ValueError):
            pb.append("publier_a absent ou illisible")
        print(f"{f.parent.name} : " + ("OK" if not pb else "PROBLÈME — " + " ; ".join(pb))
              + f" ({len(post.get('legende', ''))} caractères)")
        bad += bool(pb)
    if bad:
        raise SystemExit(f"{bad} post(s) seraient refusés à la publication.")


def publish_carousel(image_urls: list[str], caption: str) -> str:
    pb = caption_problems(caption)
    if pb:
        raise SystemExit("Garde-fou : " + " ; ".join(pb) + ". Publication bloquée.")
    ig = CFG["ig_user_id"]
    children = []
    for u in image_urls:
        c = call("POST", f"{ig}/media", image_url=u, is_carousel_item="true")
        wait_ready(c["id"])
        children.append(c["id"])
    if len(children) == 1:
        raise SystemExit("Un carrousel demande au moins 2 images.")
    parent = call("POST", f"{ig}/media", media_type="CAROUSEL", children=",".join(children), caption=caption)
    wait_ready(parent["id"])
    res = call("POST", f"{ig}/media_publish", creation_id=parent["id"])
    return res["id"]


def publish_reel(video_url: str, cover_url: str, caption: str) -> str:
    """Publie un Reel (vidéo MP4 H.264, 9:16), partagé aussi dans le fil, avec sa couverture."""
    pb = caption_problems(caption)
    if pb:
        raise SystemExit("Garde-fou : " + " ; ".join(pb) + ". Publication bloquée.")
    ig = CFG["ig_user_id"]
    c = call("POST", f"{ig}/media", media_type="REELS", video_url=video_url, cover_url=cover_url,
             caption=caption, share_to_feed="true")
    wait_ready(c["id"], tries=72)  # le traitement d'une vidéo prend plus de temps (jusqu'à 6 min)
    return call("POST", f"{ig}/media_publish", creation_id=c["id"])["id"]


def publish_stories(image_urls: list[str], f: Path, post: dict) -> str:
    """Publie chaque image en story, dans l'ordre. Les stories déjà parties sont notées dans
    post.json (« stories_publiees ») : un nouvel essai reprend là où le précédent s'est arrêté."""
    ig = CFG["ig_user_id"]
    done = post.setdefault("stories_publiees", [])
    for u in image_urls[len(done):]:
        c = call("POST", f"{ig}/media", image_url=u, media_type="STORIES")
        wait_ready(c["id"])
        res = call("POST", f"{ig}/media_publish", creation_id=c["id"])
        done.append(res["id"])
        save(f, post)
    return ",".join(done)


MAX_TENTATIVES = 3           # au-delà, le post passe en « echec »
TROP_TARD = 3 * 3600          # un post jamais parti 3 h après l'heure prévue n'est plus publié
ECHECS = Path(os.environ.get("RUNNER_TEMP", "/tmp")) / "pw-echecs.txt"


def suit_annule(post: dict) -> bool:
    """Une story du soir (« suit » = nuit du carrousel) suit l'annulation de son carrousel."""
    parent = ROOT / "posts" / str(post.get("suit", "")) / "post.json"
    if not post.get("suit") or not parent.exists():
        return False
    return json.loads(parent.read_text(encoding="utf-8")).get("statut") == "annule"


def save(f: Path, post: dict) -> None:
    f.write_text(json.dumps(post, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def fail(f: Path, post: dict, msg: str, definitif: bool) -> str:
    """Note l'échec dans post.json. Passe en « echec » si l'erreur est définitive ou répétée."""
    post["tentatives"] = post.get("tentatives", 0) + 1
    post["erreur"] = msg[:500]
    post["erreur_le"] = datetime.now(PARIS).isoformat(timespec="minutes")
    if definitif or post["tentatives"] >= MAX_TENTATIVES:
        post["statut"] = "echec"
    save(f, post)
    return f"{f.parent.name} ({post['statut']}, tentative {post['tentatives']}) : {msg[:300]}"


def deja_publie(f: Path) -> bool:
    """Relit le statut du post sur GitHub (branche main) juste avant de publier."""
    import subprocess
    rel = f.relative_to(ROOT).as_posix()
    try:
        subprocess.run(["git", "-C", str(ROOT), "fetch", "-q", "origin", "main"], check=True, timeout=60)
        txt = subprocess.run(["git", "-C", str(ROOT), "show", f"origin/main:{rel}"], check=True,
                             capture_output=True, text=True, timeout=30).stdout
        return json.loads(txt).get("statut") in ("publie", "annule")
    except Exception as e:  # dépôt injoignable : on ne prend pas le risque d'un doublon
        print(f"{f.parent.name} : statut distant illisible ({e}), publication reportée au passage suivant.")
        return True


def publish_due() -> list[Path]:
    """Publie les posts dont l'heure est passée et qui ne sont ni annulés, ni publiés, ni en échec.

    Règle validée par Alexandre : sans réponse, la version proposée part à l'heure prévue,
    sauf si statut « annule ». Les garde-fous (score, longueur, images) peuvent toujours bloquer.
    Un post en échec ne bloque jamais les suivants. Erreur passagère : nouvel essai au passage suivant
    (3 au plus). Abandon (« echec ») : listé dans ECHECS, le workflow ouvre une issue GitHub.
    """
    done, echecs = [], []
    for f in sorted((ROOT / "posts").glob("*/post.json")):
        post = json.loads(f.read_text(encoding="utf-8"))
        if post.get("statut") in ("annule", "publie", "echec", "brouillon"):  # brouillon : jamais publié sans validation
            continue
        if suit_annule(post):  # story du soir : annulée avec son carrousel
            post["statut"] = "annule"
            save(f, post)
            print(f"{f.parent.name} : carrousel {post['suit']} annulé, story annulée aussi")
            continue
        due = datetime.fromisoformat(post["publier_a"])
        wait = (due - datetime.now(PARIS)).total_seconds()
        if wait > EARLY_WAIT:
            continue
        if -wait > TROP_TARD:
            echecs.append(fail(f, post, f"jamais parti : plus de {TROP_TARD // 3600} h après l'heure prévue, "
                                        "publication abandonnée (les matchs ont commencé)", True))
            continue
        if wait > 0:  # les crons GitHub partent souvent en retard : on attend l'heure exacte
            print(f"{f.parent.name} : attente de {int(wait)} s jusqu'à {due:%H:%M}")
            time.sleep(wait)
        if deja_publie(f):  # un autre passage du robot l'a publié entre-temps : jamais de doublon
            print(f"{f.parent.name} : déjà publié par un autre passage, on n'y touche pas.")
            continue
        try:
            urls = [f"{SITE}/posts/{f.parent.name}/{name}" for name in post["images"]]
            video_url = f"{SITE}/posts/{f.parent.name}/{post['video']}" if post.get("type") == "reel" else None
            for u in urls + ([video_url] if video_url else []):  # images et vidéo doivent déjà être en ligne
                try:
                    with urllib.request.urlopen(urllib.request.Request(u, method="HEAD"), timeout=30) as r:
                        ok = r.status == 200
                except urllib.error.URLError:
                    ok = False
                if not ok:
                    raise SystemExit(f"Image non disponible : {u}")
            if post.get("type") == "story":
                media_id = publish_stories(urls, f, post)
            elif post.get("type") == "reel":
                media_id = publish_reel(video_url, urls[0], post["legende"])
            else:
                media_id = publish_carousel(urls, post["legende"])
        except SystemExit as e:
            msg = str(e)
            definitif = msg.startswith("Garde-fou") or '"is_transient":false' in msg
            line = fail(f, post, msg, definitif)
            print(f"ÉCHEC {line}")
            if post["statut"] == "echec":  # alerte seulement quand on abandonne ; sinon nouvel essai au passage suivant
                echecs.append(line)
            continue
        post.update(statut="publie", publie_le=datetime.now(PARIS).isoformat(timespec="minutes"), media_id=media_id)
        for k in ("erreur", "erreur_le"):
            post.pop(k, None)
        save(f, post)
        print(f"Publié : {f.parent.name} (média {media_id})")
        done.append(f)
    if echecs:
        ECHECS.write_text("\n".join(echecs) + "\n", encoding="utf-8")
        raise SystemExit("Échec de publication :\n" + "\n".join(echecs))
    if not done:
        print("Rien à publier.")
    return done


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "check"
    {"check": check, "publish-due": publish_due, "verify": verify}[cmd]()
