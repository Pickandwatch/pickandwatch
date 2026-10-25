"""Génère le site statique (charte « papier » Pick & Watch). Jamais de score."""
from __future__ import annotations

import html
import json
import shutil
from datetime import date, datetime
from pathlib import Path

JOURS = ["lundi", "mardi", "mercredi", "jeudi", "vendredi", "samedi", "dimanche"]
JOURS_COURTS = ["lun.", "mar.", "mer.", "jeu.", "ven.", "sam.", "dim."]
MOIS = ["janvier", "février", "mars", "avril", "mai", "juin", "juillet", "août",
        "septembre", "octobre", "novembre", "décembre"]

FONTS = ('<link rel="preconnect" href="https://fonts.googleapis.com">'
         '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
         '<link href="https://fonts.googleapis.com/css2?family=Barlow+Condensed:wght@600;800'
         '&family=IBM+Plex+Mono:wght@400;500&family=Source+Serif+4:ital,wght@0,400;0,600;1,400'
         '&display=swap" rel="stylesheet">')

e = html.escape

FIT_JS = """<script>
/* Titres pleine largeur (charte) : on ajuste la taille au conteneur, sans descendre sous data-min. */
(function () {
  function fit() {
    document.querySelectorAll('.fit').forEach(function (el) {
      el.style.fontSize = ''; el.style.whiteSpace = 'nowrap';
      var base = parseFloat(getComputedStyle(el).fontSize);
      var size = base * el.clientWidth / el.scrollWidth;
      if (size >= (+el.dataset.min || 0)) { el.style.fontSize = size.toFixed(2) + 'px'; }
      else { el.style.whiteSpace = ''; }
    });
  }
  (document.fonts ? document.fonts.ready : Promise.resolve()).then(fit);
  window.addEventListener('resize', fit);
})();
</script>"""


def night_title(d: date) -> str:
    d2 = date.fromordinal(d.toordinal() + 1)
    if d.month == d2.month:
        return f"Nuit du {JOURS[d.weekday()]} {d.day} au {JOURS[d2.weekday()]} {d2.day} {MOIS[d2.month - 1]}"
    return (f"Nuit du {JOURS[d.weekday()]} {d.day} {MOIS[d.month - 1]} "
            f"au {JOURS[d2.weekday()]} {d2.day} {MOIS[d2.month - 1]}")


def hhmm(iso: str) -> str:
    return datetime.fromisoformat(iso).strftime("%H:%M")


MOIS_COURTS = ["janv.", "févr.", "mars", "avr.", "mai", "juin", "juil.", "août",
               "sept.", "oct.", "nov.", "déc."]


def day_short(iso: str) -> str:
    dt = datetime.fromisoformat(iso)
    return f"{JOURS_COURTS[dt.weekday()]} {dt.day} {MOIS_COURTS[dt.month - 1]}"


def ch(name: str) -> str:
    """Nom de chaîne insécable (« beIN SPORTS 1 » ne se coupe pas)."""
    return e(name).replace(" ", "&nbsp;")


def flag(team: dict) -> str:
    return (f'<span class="flag" aria-hidden="true"><i style="background:{e(team["color"])}"></i>'
            f'<i style="background:{e(team["color2"])}"></i></span>')


def stars(n: int | None) -> str:
    if not n:
        return ""
    labels = {3: "Immanquable", 2: "À surveiller", 1: "Pour les curieux"}
    return (f'<div class="stars"><span class="st">{"★" * n}<span class="off">{"★" * (3 - n)}</span></span>'
            f' <span class="lab">{labels.get(n, "")}</span></div>')


def game_card(g: dict, night_day: date, UP: str = "") -> str:
    h, a = g["home"], g["away"]
    place = " · ".join(x for x in (g.get("city"), g.get("venue")) if x)
    if g.get("neutral"):
        place += " (terrain neutre)"
    tv = g["tv"]
    tv_lines = []
    if tv.get("live"):
        tv_lines.append(f'<li><span class="pill live">Direct</span><span>{ch(tv["live"]["channel"])}</span></li>')
    else:
        tv_lines.append('<li><span class="pill">Direct</span><span>NBA League Pass '
                        '<span class="muted">· pas de diffusion TV française repérée</span></span></li>')
    for other in tv.get("also", []):
        tv_lines.append(f'<li><span class="pill live">Direct</span><span>{ch(other)}</span></li>')
    for r in tv.get("replays", [])[:2]:
        tv_lines.append(f'<li><span class="pill">Différé</span><span>{e(day_short(r["start"]))} à '
                        f'{hhmm(r["start"])} · {ch(r["channel"])}</span></li>')
    if g.get("commentators"):
        tv_lines.append(f'<li><span class="pill">Au micro</span><span>{e(g["commentators"])}</span></li>')
    if tv["status"] == "confirmé":
        check = '<p class="check ok">Diffusion vérifiée dans le guide TV</p>'
    elif tv["status"] == "annoncé":
        check = f'<p class="check ok">Diffusion annoncée · {e(tv.get("source") or "")}</p>'
    else:
        check = '<p class="check">Diffusion à confirmer</p>'
    brief = f'<p class="brief">{e(g["brief"])}</p>' if g.get("brief") else ""
    return f"""
<article class="match{' top' if g.get('stars') == 3 else ''}">
  <div class="time"><span>{hhmm(g["tip_paris"])}</span></div>
  <div class="body">
    {stars(g.get("stars"))}
    <h3 class="teams">{flag(h)}<a href="{UP}equipes/{h["abbr"].lower()}.html">{e(h["name"])}</a> <span class="dash">–</span> {flag(a)}<a href="{UP}equipes/{a["abbr"].lower()}.html">{e(a["name"])}</a></h3>
    <p class="place">{'<span class="cup">NBA Cup</span> ' if g.get("cup") else ''}{e(place)}</p>
    {brief}
    {f'<p class="fr"><span class="frflag" aria-hidden="true"><i></i><i></i><i></i></span>Les Français : {e(", ".join(g["francais"]))}</p>' if g.get("francais") else ''}
    <ul class="tv">{''.join(tv_lines)}</ul>
    {check}
    <p class="addline">Programme ton match : <a class="add" href="{UP}agenda/m/{g["id"]}.ics">+ Agenda (direct)</a>{f' <a class="add" href="{UP}agenda/m/{g["id"]}-differe.ics">+ Agenda (différé)</a>' if tv.get("replays") else ''}</p>
  </div>
</article>"""


VERDICTS = {
    "replay": ("À voir en replay", "v-replay"),
    "resume": ("Le résumé suffit", "v-resume"),
    "zapper": ("Tu peux zapper", "v-zapper"),
}


def rediff_nuit(slots: list[dict], now: datetime) -> str | None:
    """Rediffusions beIN dont le guide TV ne précise pas l'affiche (voir night.rediffusions_sans_affiche)."""
    fut = [s for s in slots if datetime.fromisoformat(s["start"]) > now]
    if not fut:
        return None
    lst = ", ".join(f'{e(day_short(s["start"]))} à {hhmm(s["start"])} · {ch(s["channel"])}' for s in fut)
    return f'Rediffusions de matchs de cette nuit : {lst} <span class="muted">(le guide TV ne précise pas lesquels)</span>'


def verdict_card(g: dict, v: dict, now: datetime, slots: list[dict] | None = None) -> str:
    label, cls = VERDICTS[v["verdict"]]
    h, a = g["home"], g["away"]
    where = []
    if v["verdict"] == "replay":
        future = [r for r in g["tv"].get("replays", []) if datetime.fromisoformat(r["start"]) > now]
        for r in future[:1]:
            where.append(f'Rediffusion {e(day_short(r["start"]))} à {hhmm(r["start"])} · {ch(r["channel"])}')
        autres = rediff_nuit(slots or [], now)
        if autres:
            where.append(autres)
        where.append("Match complet en replay sur NBA League Pass")
    elif v["verdict"] == "resume":
        where.append('Résumé sur la <a href="https://www.youtube.com/@NBA">chaîne YouTube de la NBA</a> '
                     '<span class="muted">(attention : le résumé affiche le score)</span>')
    where_html = "".join(f"<li>{w}</li>" for w in where)
    return f"""
<article class="verdict">
  <p class="vlabel {cls}">{label}</p>
  <h3 class="teams small">{flag(h)}<span>{e(h["name"])}</span> <span class="dash">–</span> {flag(a)}<span>{e(a["name"])}</span></h3>
  <p class="brief">{e(v["text"])}</p>
  {f'<ul class="where">{where_html}</ul>' if where_html else ''}
</article>"""


def verdict_cards(night: dict, verdicts: dict, now: datetime) -> str:
    vs = verdicts.get("matchs", {})
    order = {"replay": 0, "resume": 1, "zapper": 2}
    games = sorted((g for g in night["games"] if g["id"] in vs),
                   key=lambda g: (order[vs[g["id"]]["verdict"]], g["tip_paris"]))
    return "".join(verdict_card(g, vs[g["id"]], now, night.get("rediffusions_nuit")) for g in games)


def verdict_section(prev_date: date, prev: dict | None, verdicts: dict | None, now: datetime,
                    latest: str | None = None) -> str:
    """Rubrique permanente « Verdicts des matchs d'hier » : toujours affichée, même vide."""
    cards = verdict_cards(prev, verdicts, now) if prev and verdicts else ""
    if cards:
        body = f'<div class="vlist">{cards}\n    </div>'
    elif prev is not None and not prev.get("games"):
        body = '<p class="vwait">Pas de match NBA cette nuit-là : rien à rattraper.</p>'
    else:
        body = '<p class="vwait">Les verdicts de cette nuit arrivent dans la matinée.</p>'
        if latest:
            body += (f'<p class="vwait"><a href="verdicts/{latest}.html">Voir les derniers verdicts publiés '
                     f'({e(night_title(date.fromisoformat(latest)).replace("Nuit du ", "nuit du "))})</a></p>')
    return f"""
  <section class="lastnight" id="verdicts" aria-label="Verdicts des matchs d'hier">
    <p class="kicker small fit" data-min="26">Verdicts des matchs d'hier</p>
    <h2 class="vtitle">{e(night_title(prev_date))}</h2>
    <p class="summary">Ça valait le coup ? Notre verdict sur chaque match. Jamais le score.</p>
    {body}
  </section>"""


def tabs(up: str) -> str:
    return (f'<nav class="tabs" aria-label="Rubriques">'
            f'<a href="{up}index.html#aujourdhui">À voir aujourd\'hui</a>'
            f'<a href="{up}index.html#verdicts">Verdicts d\'hier</a>'
            f'<a class="alt" href="{up}equipes/index.html">Mon équipe</a>'
            f'<a class="alt" href="{up}nba-cup.html">NBA Cup</a></nav>')


def head(title: str, canonical: str, up: str, description: str) -> str:
    return f"""<!doctype html>
<html lang="fr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(title)} · Pick &amp; Watch</title>
<meta name="description" content="{e(description)}">
<link rel="canonical" href="{e(canonical)}">
<link rel="icon" type="image/png" href="{up}assets/favicon.png">
<meta property="og:title" content="{e(title)}">
<meta property="og:description" content="Quoi regarder, où, quand. Sans spoiler.">
<meta property="og:image" content="https://pickandwatch.fr/assets/logo.png">
{FONTS}
<link rel="stylesheet" href="{up}assets/style.css">
</head>
<body>
<div class="ball" aria-hidden="true"></div>
<header class="bar">
  <a class="brand" href="{up}index.html">Pick &amp; Watch</a>
  <span class="date">{{date}}</span>
</header>
{tabs(up)}
"""


def foot(gen: datetime) -> str:
    return f"""<footer>
  <p class="sign">Ton programme NBA. Zéro spoiler. Jamais.</p>
  <p>Suis-nous sur Instagram : <a href="https://www.instagram.com/pickandwatch.fr/">@pickandwatch.fr</a></p>
  <p class="src">Sources : calendrier NBA via ESPN, diffusions via le guide TV XMLTV France, recoupés automatiquement.
  Mis à jour le {gen.day} {MOIS[gen.month - 1]} à {gen:%H:%M}.</p>
</footer>
{FIT_JS}
</body>
</html>
"""


def verdict_page(night: dict, verdicts: dict, now: datetime) -> str:
    """Archive permanente des verdicts d'une nuit : site/verdicts/AAAA-MM-JJ.html."""
    d = date.fromisoformat(night["night"])
    title = night_title(d)
    top = head(f"Verdicts · {title}", f"https://pickandwatch.fr/verdicts/{d}.html", "../",
               "Nos verdicts NBA sans spoiler : replay, résumé ou zapper. Jamais le score.")
    return (top.replace("{date}", e(title.replace("Nuit du ", "").upper())) + f"""<main>
  <section class="lastnight" aria-label="Verdicts">
    <p class="kicker small fit" data-min="26">Nos verdicts</p>
    <h2 class="vtitle">{e(title)}</h2>
    <p class="summary">Ça valait le coup ? Notre verdict sur chaque match. Jamais le score.</p>
    <div class="vlist">{verdict_cards(night, verdicts, now)}
    </div>
  </section>
</main>
""" + foot(now))


def page(night: dict, *, canonical: str, depth: int = 0, prev: dict | None = None,
         verdicts: dict | None = None, latest: str | None = None, home: bool = False) -> str:
    d = date.fromisoformat(night["night"])
    up = "../" * depth
    games = night["games"]
    n_tv = sum(1 for g in games if g["tv"].get("live"))
    preseason = any(g.get("phase") == "preseason" for g in games)
    if games:
        summary = (f'{len(games)} match{"s" if len(games) > 1 else ""} · '
                   f'{n_tv} en direct à la télé française')
        cards = "".join(game_card(g, d, up) for g in games)
    else:
        summary = "Pas de match NBA cette nuit."
        cards = '<p class="empty">Repos pour tout le monde. On se retrouve demain.</p>'
    notes = ["Toutes les heures sont à l'heure de Paris."]
    if preseason:
        notes.append("Présaison : les stars peuvent être ménagées.")
    title = night_title(d)
    gen = datetime.fromisoformat(night["generated_at"])
    last = ""
    if home:
        prev_date = date.fromordinal(d.toordinal() - 1)
        last = verdict_section(prev_date, prev, verdicts, gen, latest)
    top = head(f"Cette nuit en NBA · {title}", canonical, up,
               "Le programme NBA de la nuit à l'heure de Paris : chaîne, lieu, direct ou différé. Zéro spoiler.")
    return (top.replace("{date}", e(title.replace("Nuit du ", "").upper())) + f"""<main>
  <section class="hero" id="aujourdhui">
    <p class="kicker fit" data-min="40">{"À voir aujourd'hui" if home else "Cette nuit en NBA"}</p>
    <h1 class="fit" data-min="34">{e(title)}</h1>
    <p class="summary">{e(summary)}</p>
  </section>
  <section class="list" aria-label="Matchs de la nuit">{cards}
  </section>
  <p class="notes">{' '.join(e(n) for n in notes)}</p>{last}
  <section class="soon">
    <p class="kicker small fit" data-min="26">Bientôt sur pickandwatch.fr</p>
    <ul>
      <li><strong>La newsletter</strong> du matin.</li>
    </ul>
  </section>
</main>
""" + foot(gen))


def build_site(root: Path, night: dict, prev: dict | None = None, verdicts: dict | None = None,
               archive: list[tuple[dict, dict]] | None = None, progs: list[dict] | None = None) -> Path:
    """archive : toutes les nuits dont les verdicts sont validés, (nuit, verdicts), par date."""
    site = root / "site"
    (site / "nuits").mkdir(parents=True, exist_ok=True)
    (site / "assets").mkdir(parents=True, exist_ok=True)
    for f in (root / "assets").iterdir():
        shutil.copy2(f, site / "assets" / f.name)
    # Images des posts Instagram : Meta les récupère sur pickandwatch.fr/posts/…
    for img in [*(root / "posts").glob("*/*.jpg"), *(root / "posts").glob("*/*.mp4")]:  # images et vidéos (Reels)
        dest = site / "posts" / img.parent.name
        dest.mkdir(parents=True, exist_ok=True)
        shutil.copy2(img, dest / img.name)
    gen = datetime.fromisoformat(night["generated_at"])
    latest = None
    for n, v in archive or []:
        (site / "verdicts").mkdir(parents=True, exist_ok=True)
        (site / "verdicts" / f"{n['night']}.html").write_text(verdict_page(n, v, gen), encoding="utf-8")
        if n["night"] < night["night"]:
            latest = max(latest or n["night"], n["night"])
    if progs is not None:  # Mon équipe, NBA Cup, agendas (.ics)
        from . import equipes
        equipes.build(root, site, progs, gen, head, foot)
    hp = hors_parquet_page(root, gen)
    if hp:
        (site / "hors-parquet.html").write_text(hp, encoding="utf-8")
    d = night["night"]
    (site / "nuits" / f"{d}.html").write_text(
        page(night, canonical=f"https://pickandwatch.fr/nuits/{d}.html", depth=1), encoding="utf-8")
    (site / "index.html").write_text(
        page(night, canonical="https://pickandwatch.fr/", prev=prev, verdicts=verdicts,
             latest=latest, home=True), encoding="utf-8")
    return site


def hors_parquet_page(root: Path, now: datetime) -> str | None:
    """Archive des numéros publiés de Hors parquet (posts/*-hors-parquet), avec les liens des sources."""
    nums = []
    for f in sorted((root / "posts").glob("*-hors-parquet/post.json"), reverse=True):
        post = json.loads(f.read_text(encoding="utf-8"))
        if post.get("statut") != "publie":
            continue
        spec = json.loads((f.parent / "spec.json").read_text(encoding="utf-8"))
        items = "".join(
            f'<li><strong>{e(s.get("rubrique", "").capitalize())}</strong> · {e(" ".join(s["titre"]))}'
            + (f' · <a href="{e(s["lien"])}">{e(s.get("lien_titre") or "la source")}</a>' if s.get("lien") else "")
            + "</li>" for s in spec.get("sujets", []))
        d = datetime.fromisoformat(post["publier_a"])
        nums.append(f'<article class="verdict"><h3 class="mois">Semaine du {e(spec["couverture"]["semaine"].lower())}</h3>'
                    f'<ul class="where">{items}</ul>'
                    f'<p class="muted small">Publié le {d.day} {MOIS[d.month - 1]} {d.year} sur Instagram.</p></article>')
    if not nums:
        return None
    top = head("Hors parquet : l'actu basket de la semaine, hors des matchs", "https://pickandwatch.fr/hors-parquet.html", "",
               "Chaque vendredi, le meilleur de l'actu basket hors des parquets : livres, documentaires, événements en France, interviews.")
    return (top.replace("{date}", "HORS PARQUET") + f"""<main>
  <section class="hero">
    <p class="kicker fit" data-min="40">Hors parquet</p>
    <h1 class="fit" data-min="30">Chaque vendredi, ce qu'il ne fallait pas rater</h1>
    <p class="summary">Livres, documentaires, événements en France, interviews : le basket en dehors des matchs, avec les liens.</p>
  </section>
  <section class="vlist">{''.join(nums)}</section>
</main>
""" + foot(now))
