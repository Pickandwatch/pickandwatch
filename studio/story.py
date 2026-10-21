"""Fabrique la story Instagram des verdicts du matin (charte « papier », 1080x1920).

Usage :
    python studio/story.py AAAA-MM-JJ              # nuit D-1 : écrit posts/AAAA-MM-JJ-verdicts/
    python studio/story.py AAAA-MM-JJ --out DOSSIER  # aperçu : images seulement, aucun post.json

Lit data/nuits/<nuit>.json et data/verdicts/<nuit>.json, produit :
  01.jpg : le récapitulatif de la nuit (tous les matchs, leur verdict) ;
  02.jpg … : une carte par match (replay, puis résumé, puis zapper), avec où le voir.
Écrit posts/<nuit>-verdicts/post.json (type « story », publication le lendemain de la nuit à 8h,
ou tout de suite si 8h est passé). Aucune légende : une story n'en a pas.
Le garde-fou anti-score (pipeline.instagram.SCORE_RE) bloque tout texte suspect.
"""
from __future__ import annotations

import html
import json
import pathlib
import sys
import tempfile
from datetime import date, datetime, time, timedelta
from zoneinfo import ZoneInfo

from PIL import ImageFont

ST = pathlib.Path(__file__).resolve().parent
ROOT = ST.parent
sys.path.insert(0, str(ROOT))
from pipeline.instagram import SCORE_RE  # noqa: E402

PARIS = ZoneInfo("Europe/Paris")
W, H = 1080, 1920
SAFE_TOP, SAFE_BOTTOM = 250, 1640      # l'interface d'Instagram couvre le haut et le bas
BG, INK, HEAD, SUB, FRAME = "#F2EEE6", "#111214", "#F06A2F", "#5C5850", "rgba(17,18,20,0.18)"
BAR = str(ST / "fonts/BarlowCondensed-ExtraBold.ttf")
FONTS = ('<link href="https://fonts.googleapis.com/css2?family=Barlow+Condensed:wght@600;800'
         '&family=IBM+Plex+Mono:wght@400;500&family=Source+Serif+4:ital,wght@0,400;0,600;1,400&display=swap" rel="stylesheet">')
LABELS = {"replay": "REPLAY", "resume": "RÉSUMÉ", "zapper": "ZAPPER"}
LONG = {"replay": "À VOIR EN REPLAY", "resume": "LE RÉSUMÉ SUFFIT", "zapper": "TU PEUX ZAPPER"}
ORDER = {"replay": 0, "resume": 1, "zapper": 2}
JOURS = ["LUNDI", "MARDI", "MERCREDI", "JEUDI", "VENDREDI", "SAMEDI", "DIMANCHE"]
MOIS = ["JANVIER", "FÉVRIER", "MARS", "AVRIL", "MAI", "JUIN", "JUILLET", "AOÛT",
        "SEPTEMBRE", "OCTOBRE", "NOVEMBRE", "DÉCEMBRE"]

BAR_CSS = "font-family: 'Barlow Condensed', sans-serif; font-weight: 800"
MONO_CSS = "font-family: 'IBM Plex Mono', monospace; font-weight: 500"


def e(s: str) -> str:
    return html.escape(s, quote=False)


def size_for(text: str, width: float, cap: int) -> int:
    """Plus grande taille (≤ cap) pour que le texte tienne dans la largeur."""
    w = ImageFont.truetype(BAR, 100).getlength(text)
    return max(20, min(cap, int(100 * width / w)))


def matchup(g: dict) -> str:
    return f"{g['home']['name']} – {g['away']['name']}".upper()


def nuit_titre(d: date) -> str:
    n = d + timedelta(days=1)
    if d.month == n.month:
        return f"NUIT DU {d.day} AU {n.day} {MOIS[n.month - 1]}"
    return f"NUIT DU {d.day} {MOIS[d.month - 1]} AU {n.day} {MOIS[n.month - 1]}"


def page(inner: str, accent: str = HEAD) -> str:
    svg = (f'<svg width="{W}" height="{H}" viewBox="0 0 {W} {H}" fill="none" style="position: absolute; left: 0; top: 0; z-index: -1">'
           f'<rect x="30" y="30" width="{W - 60}" height="{H - 60}" stroke="{FRAME}" stroke-width="4"></rect></svg>')
    return (f'<html><head><meta charset="utf-8">{FONTS}<style>body{{margin:0}}</style></head><body>'
            f'<div style="position: relative; isolation: isolate; overflow: hidden; width: {W}px; height: {H}px; box-sizing: border-box; '
            f'padding: {SAFE_TOP}px 72px {H - SAFE_BOTTOM}px; background: {BG}; color: {INK}; display: flex; flex-direction: column; '
            f'justify-content: space-between; gap: 28px; font-family: \'Source Serif 4\', Georgia, serif">{svg}'
            f'<div style="position: absolute; left: 0; right: 0; top: 0; height: 18px; background: {accent}"></div>'
            f'{inner}</div></body></html>')


def brand() -> str:
    return (f'<div style="position: relative; display: flex; align-items: center">'
            f'<div style="position: absolute; left: 0; right: 0; top: 50%; height: 6px; margin-top: -3px; background: {HEAD}"></div>'
            f'<span style="position: relative; background: {BG}; padding-right: 22px; {BAR_CSS}; font-size: 44px; line-height: 1; letter-spacing: 7px">PICK &amp; WATCH</span></div>')


def foot(cta: str) -> str:
    return (f'<div style="display: flex; justify-content: space-between; align-items: center; gap: 24px; border: 3px solid {HEAD}; padding: 22px 30px">'
            f'<div style="display: flex; flex-direction: column; gap: 4px"><span style="{BAR_CSS}; font-size: 54px; line-height: 1">pickandwatch.fr</span>'
            f'<span style="{MONO_CSS}; font-size: 24px; color: {SUB}">{e(cta)}</span></div>'
            f'<span style="{BAR_CSS}; font-size: 40px; letter-spacing: 2px">LIEN EN BIO ↑</span></div>')


def pill(v: str, size: int) -> str:
    styles = {"replay": f"background: {HEAD}; color: {BG}; border: 3px solid {HEAD}",
              "resume": f"background: transparent; color: {INK}; border: 3px solid {INK}",
              "zapper": f"background: transparent; color: {SUB}; border: 3px dashed {SUB}"}
    return (f'<span style="{styles[v]}; {MONO_CSS}; font-size: {size}px; letter-spacing: 2px; padding: 6px 0; '
            f'width: {int(size * 7.2)}px; text-align: center; flex-shrink: 0">{LABELS[v]}</span>')


def recap(d: date, games: list, vs: dict) -> str:
    n = len(games)
    big = 72 if n <= 5 else 60 if n <= 8 else 48 if n <= 11 else 40
    pad = 26 if n <= 5 else 18 if n <= 8 else 10 if n <= 11 else 6
    hsize = 230 if n <= 5 else 180 if n <= 8 else 130
    psize = 30 if n <= 8 else 24
    width = W - 144 - int(psize * 7.2) - 28
    rows = "".join(
        f'<div style="display: flex; align-items: center; gap: 28px; padding: {pad}px 0; border-top: 1px solid {INK}">'
        f'{pill(vs[g["id"]]["verdict"], psize)}'
        f'<span style="{BAR_CSS}; font-size: {size_for(matchup(g), width, big)}px; line-height: 0.95; white-space: nowrap">{e(matchup(g))}</span></div>'
        for g in games)
    count = {k: sum(vs[g["id"]]["verdict"] == k for g in games) for k in ORDER}
    resume = " · ".join(f"{count[k]} {LABELS[k]}" for k in ORDER if count[k])
    inner = (brand() +
             f'<div style="display: flex; flex-direction: column; gap: 18px">'
             f'<div style="{BAR_CSS}; font-size: {hsize}px; line-height: 0.82; text-align: center; color: {INK}">VERDICTS</div>'
             f'<div style="{BAR_CSS}; font-size: {hsize // 3}px; line-height: 0.9; text-align: center; color: {HEAD}">ÇA VALAIT LE COUP ?</div>'
             f'<div style="{MONO_CSS}; font-size: 26px; letter-spacing: 3px; text-align: center; color: {SUB}">{nuit_titre(d)} · ZÉRO SPOILER</div></div>'
             f'<div style="display: flex; flex-direction: column; border-bottom: 2px solid {INK}">{rows}</div>'
             f'<div style="{MONO_CSS}; font-size: 24px; letter-spacing: 2px; text-align: center; color: {SUB}">{resume} · JAMAIS LE SCORE</div>'
             + foot("Le pourquoi de chaque verdict"))
    return page(inner)


def quand(iso: str, now: datetime) -> str:
    t = datetime.fromisoformat(iso).astimezone(PARIS)
    jour = "aujourd'hui" if t.date() == now.date() else JOURS[t.weekday()].lower()
    return f"{jour} à {t.hour}h{t.minute:02d}"


def ou_revoir(g: dict, now: datetime, slots: list[dict] | None = None) -> list[str]:
    out = []
    for r in g.get("tv", {}).get("replays", []):
        if datetime.fromisoformat(r["start"]) > now:
            out.append(f"Rediffusion {quand(r['start'], now)} sur {r['channel']}")
    fut = [x for x in slots or [] if datetime.fromisoformat(x["start"]) > now]
    if fut:  # le guide TV ne dit pas quel match : on ne devine pas
        out.append("Rediffusions de matchs de la nuit " + ", ".join(f"{quand(x['start'], now)} sur {x['channel']}" for x in fut)
                   + " (affiche non précisée)")
    out.append("Match complet sur NBA League Pass (abonnement payant)")
    return out


def ink_of(team: dict) -> str:
    """Couleur de l'équipe pour son nom, sauf si elle est trop sombre ou trop claire sur le papier."""
    for c in (team.get("color", ""), team.get("color2", "")):
        c = c.lstrip("#")
        if len(c) != 6:
            continue
        r, g, b = (int(c[k:k + 2], 16) for k in (0, 2, 4))
        lum = 0.2126 * r + 0.7152 * g + 0.0722 * b
        if 40 < lum < 150:
            return "#" + c
    return INK


def carte(d: date, g: dict, v: dict, i: int, total: int, now: datetime, slots: list[dict] | None = None) -> str:
    accent = g["home"].get("color", HEAD)
    home, away = g["home"]["name"].upper(), g["away"]["name"].upper()
    long = len(v["text"]) > 170
    s = min(size_for(home, W - 144, 170 if long else 220), size_for(away, W - 144, 170 if long else 220))
    fs = 38 if long else 44
    if v["verdict"] == "replay":
        titre, lignes = "OÙ LE REVOIR", ou_revoir(g, now, slots)
    elif v["verdict"] == "resume":  # même mention que le site (pipeline/render.py)
        titre, lignes = "OÙ VOIR LE RÉSUMÉ", ["Résumé sur la chaîne YouTube de la NBA",
                                              "Attention : le résumé affiche le score"]
    else:
        titre, lignes = "", []
    where = "".join(f'<div style="padding: 14px 0; border-top: 1px solid {INK}; font-size: 34px; line-height: 1.25">{e(w)}</div>' for w in lignes)
    badge = {"replay": f"background: {HEAD}; color: {BG}; border: 4px solid {HEAD}",
             "resume": f"background: {INK}; color: {BG}; border: 4px solid {INK}",
             "zapper": f"background: transparent; color: {SUB}; border: 4px dashed {SUB}"}[v["verdict"]]
    bloc = (f'<div style="display: flex; flex-direction: column; border-bottom: 2px solid {INK}">'
            f'<div style="{MONO_CSS}; font-size: 24px; letter-spacing: 3px; color: {SUB}; padding-bottom: 10px">{titre}</div>{where}</div>'
            if lignes else "")
    inner = (brand() +
             f'<div style="display: flex; flex-direction: column; gap: 14px">'
             f'<div style="{MONO_CSS}; font-size: 26px; letter-spacing: 3px; text-align: center; color: {SUB}">{nuit_titre(d)} · {i}/{total}</div>'
             f'<div style="align-self: center; {badge}; {BAR_CSS}; font-size: 64px; line-height: 1; padding: 10px 28px; letter-spacing: 2px">{LONG[v["verdict"]]}</div>'
             f'<div style="{BAR_CSS}; font-size: {s}px; line-height: 0.84; text-align: center; color: {ink_of(g["home"])}; margin-top: 18px">{e(home)}</div>'
             f'<div style="{MONO_CSS}; font-size: 30px; text-align: center; color: {SUB}">REÇOIVENT LES</div>'
             f'<div style="{BAR_CSS}; font-size: {s}px; line-height: 0.84; text-align: center; color: {ink_of(g["away"])}">{e(away)}</div></div>'
             f'<div style="font-size: {fs}px; line-height: 1.3; border-left: 8px solid {HEAD}; padding-left: 28px">{e(v["text"])}</div>'
             + bloc + foot("Zéro spoiler. Jamais."))
    return page(inner, accent)


def render(pages: list[str], out: pathlib.Path) -> list[str]:
    from playwright.sync_api import sync_playwright
    from PIL import Image
    tmp = pathlib.Path(tempfile.mkdtemp())
    problems, names = [], []
    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page(viewport={"width": W, "height": H})
        for i, src in enumerate(pages, 1):
            h = tmp / f"s{i}.html"
            h.write_text(src, encoding="utf-8")
            pg.goto(f"file://{h}")
            pg.wait_for_load_state("networkidle")
            pg.evaluate("document.fonts.ready")
            pg.wait_for_timeout(600)
            fams = set(pg.evaluate("[...document.fonts].filter(f=>f.status==='loaded').map(f=>f.family)"))
            if not {"Barlow Condensed", "IBM Plex Mono"} <= fams:
                problems.append(f"{i:02d} : polices non chargées ({sorted(fams)})")
            over = pg.evaluate("""([top, bottom]) => { const r=[]; const root=document.querySelector('body > div');
              root.querySelectorAll('*').forEach(el=>{ if(el.closest('svg') || el.style.position==='absolute') return;
                const b=el.getBoundingClientRect();
                if(el.scrollWidth>el.clientWidth+1 && getComputedStyle(el).whiteSpace==='nowrap') r.push('largeur : '+(el.textContent||'').slice(0,40));
                if(b.right>1080-60 || b.left<60) r.push('côté : '+(el.textContent||'').slice(0,40));
                if(b.top<top-40 || b.bottom>bottom+10) r.push('zone masquée : '+(el.textContent||'').slice(0,40)); });
              return r; }""", [SAFE_TOP, SAFE_BOTTOM])
            problems += [f"{i:02d} : déborde ({o})" for o in dict.fromkeys(over)]
            png = tmp / f"{i:02d}.png"
            pg.locator("body > div").first.screenshot(path=str(png))
            Image.open(png).convert("RGB").save(out / f"{i:02d}.jpg", quality=92, optimize=True)
            names.append(f"{i:02d}.jpg")
        b.close()
    return problems, names


def main(argv: list[str]) -> int:
    nuit = argv[0]
    preview = "--out" in argv
    d = date.fromisoformat(nuit)
    night = json.loads((ROOT / "data/nuits" / f"{nuit}.json").read_text(encoding="utf-8"))
    vs = json.loads((ROOT / "data/verdicts" / f"{nuit}.json").read_text(encoding="utf-8"))["matchs"]
    games = sorted([g for g in night["games"] if g["id"] in vs],
                   key=lambda g: (ORDER[vs[g["id"]]["verdict"]], g["tip_paris"]))
    if not games:
        print("Aucun verdict pour cette nuit : pas de story.")
        return 0
    for g in games:  # garde-fou anti-score sur tout ce qui sera écrit sur les images
        if SCORE_RE.search(vs[g["id"]]["text"]):
            sys.exit(f"Garde-fou : le verdict de {matchup(g)} semble contenir un score. Rien n'est produit.")
    due = datetime.combine(d + timedelta(days=1), time(8, 0), PARIS)
    # rediffusions annoncées : celles qui commencent au moins 30 min après la publication
    now = max(datetime.now(PARIS), due) + timedelta(minutes=30)
    # une carte par match, tous verdicts confondus (consigne d'Alexandre du 21/10)
    pages = [recap(d, games, vs)] + [carte(d, g, vs[g["id"]], i, len(games), now, night.get("rediffusions_nuit")) for i, g in enumerate(games, 1)]
    out = pathlib.Path(argv[argv.index("--out") + 1]) if preview else ROOT / "posts" / f"{nuit}-verdicts"
    out.mkdir(parents=True, exist_ok=True)
    problems, names = render(pages, out)
    for p in problems:
        print("ATTENTION", p)
    if problems:
        return 1
    if not preview:
        f = out / "post.json"
        if f.exists() and json.loads(f.read_text(encoding="utf-8")).get("statut") in ("publie", "annule"):
            print(f"{f} déjà {json.loads(f.read_text())['statut']} : non réécrit.")
            return 0
        post = {"type": "story", "nuit": nuit,
                # en retard sur 8h : 15 min de marge pour que le site mette les images en ligne
                "publier_a": max(due, datetime.now(PARIS).replace(second=0, microsecond=0)
                                 + timedelta(minutes=15)).isoformat(),
                "statut": "propose", "images": names, "legende": ""}
        f.write_text(json.dumps(post, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"{len(names)} image(s) dans {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
