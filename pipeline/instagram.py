"""Publication Instagram (API Graph de Meta, via la Page Facebook reliée).

La clé d'accès n'est jamais dans le code : elle vient du secret GitHub IG_ACCESS_TOKEN.

Usage :
    python -m pipeline.instagram check          # vérifie la clé, ne publie rien
    python -m pipeline.instagram publish-due    # publie les posts arrivés à échéance
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

# Garde-fou anti-spoiler : un score du type « 112-108 » ou « 112 à 108 » bloque la publication.
SCORE_RE = re.compile(r"\b1?\d{2}\s?(?:-|–|à|a)\s?1?\d{2}\b")


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


def publish_carousel(image_urls: list[str], caption: str) -> str:
    if SCORE_RE.search(caption):
        raise SystemExit("Garde-fou : la légende semble contenir un score. Publication bloquée.")
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


def publish_due() -> list[Path]:
    """Publie les posts dont l'heure est passée et qui ne sont ni annulés ni déjà publiés.

    Règle validée par Alexandre : sans réponse, la version proposée part à l'heure prévue,
    sauf si statut « annule ». Les garde-fous (score, images) peuvent toujours bloquer.
    """
    now = datetime.now(PARIS)
    done = []
    for f in sorted((ROOT / "posts").glob("*/post.json")):
        post = json.loads(f.read_text(encoding="utf-8"))
        if post.get("statut") in ("annule", "publie"):
            continue
        if datetime.fromisoformat(post["publier_a"]) > now:
            continue
        urls = [f"{SITE}/posts/{f.parent.name}/{name}" for name in post["images"]]
        for u in urls:  # les images doivent déjà être en ligne
            with urllib.request.urlopen(urllib.request.Request(u, method="HEAD"), timeout=30) as r:
                if r.status != 200:
                    raise SystemExit(f"Image non disponible : {u}")
        media_id = publish_carousel(urls, post["legende"])
        post.update(statut="publie", publie_le=now.isoformat(timespec="minutes"), media_id=media_id)
        f.write_text(json.dumps(post, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(f"Publié : {f.parent.name} (média {media_id})")
        done.append(f)
    if not done:
        print("Rien à publier.")
    return done


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "check"
    {"check": check, "publish-due": publish_due}[cmd]()
