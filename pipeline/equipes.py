"""Pages « Mon équipe », NBA Cup et agendas (.ics) de pickandwatch.fr. Jamais de score.

- site/equipes/index.html        : les 30 équipes
- site/equipes/<slug>.html       : calendrier de la saison à l'heure de Paris, avec les chaînes
- site/agenda/<slug>.ics         : agenda de l'équipe, à s'abonner (mis à jour à chaque passage)
- site/agenda/m/<id>.ics         : un match (direct) ; <id>-differe.ics : sa rediffusion
- site/nba-cup.html              : groupes, matchs, chaînes ; classement masqué derrière un bouton
"""
from __future__ import annotations

import html
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

from . import sources
from .night import PARIS, match_tv

e = html.escape
SITE_URL = "https://pickandwatch.fr"
JOURS = ["lun.", "mar.", "mer.", "jeu.", "ven.", "sam.", "dim."]
MOIS = ["janvier", "février", "mars", "avril", "mai", "juin", "juillet", "août", "septembre", "octobre",
        "novembre", "décembre"]
DUREE = timedelta(hours=2, minutes=30)


def _paris(iso: str) -> datetime:
    return datetime.fromisoformat(iso.replace("Z", "+00:00")).astimezone(PARIS)


# --------------------------------------------------------------------------- diffusion

def tv_for(g: dict, progs: list[dict], diffuseurs: dict) -> dict:
    """Diffusion française d'un match à venir : beIN (guide TV, ~8 jours), saisie manuelle, Prime Video."""
    live, replays = match_tv(g, progs)
    man = diffuseurs.get("matchs", {}).get(g["id"], {})
    prime = diffuseurs.get("prime_usa_en_france") and "Prime Video" in (g.get("us_tv") or [])
    chans = []
    if live:
        chans.append(live["channel"])
    if man.get("live") and man["live"] not in chans:
        chans.append(man["live"])
    if prime and "Prime Video" not in chans:
        chans.append("Prime Video")
    horizon = max((datetime.fromisoformat(p["start"]) for p in progs), default=datetime.now(PARIS))
    connu = bool(chans) or _paris(g["tip_utc"]) <= horizon
    return {"live": chans, "replays": replays, "connu": connu}


def tv_text(tv: dict) -> str:
    if tv["live"]:
        return " + ".join(tv["live"])
    return "NBA League Pass" if tv["connu"] else "Chaîne annoncée la semaine du match"


# --------------------------------------------------------------------------- agenda (.ics)

def _fold(line: str) -> str:
    out, cur = [], ""
    for ch in line:
        if len((cur + ch).encode()) > 73:
            out.append(cur)
            cur = " " + ch
        else:
            cur += ch
    out.append(cur)
    return "\r\n".join(out)


def _esc(s: str) -> str:
    return s.replace("\\", "\\\\").replace(";", "\\;").replace(",", "\\,").replace("\n", "\\n")


def vevent(uid: str, start: datetime, titre: str, desc: str, url: str) -> list[str]:
    st = start.astimezone(timezone.utc)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    return ["BEGIN:VEVENT", f"UID:{uid}@pickandwatch.fr", f"DTSTAMP:{stamp}",
            f"DTSTART:{st:%Y%m%dT%H%M%SZ}", f"DTEND:{st + DUREE:%Y%m%dT%H%M%SZ}",
            f"SUMMARY:{_esc(titre)}", f"DESCRIPTION:{_esc(desc)}", f"URL:{url}",
            "BEGIN:VALARM", "ACTION:DISPLAY", f"DESCRIPTION:{_esc(titre)}", "TRIGGER:-PT15M", "END:VALARM",
            "END:VEVENT"]


def calendar(name: str, events: list[list[str]]) -> str:
    lines = ["BEGIN:VCALENDAR", "VERSION:2.0", "PRODID:-//Pick & Watch//pickandwatch.fr//FR", "CALSCALE:GREGORIAN",
             "METHOD:PUBLISH", f"X-WR-CALNAME:{_esc(name)}", "X-WR-TIMEZONE:Europe/Paris",
             "REFRESH-INTERVAL;VALUE=DURATION:PT12H", "X-PUBLISHED-TTL:PT12H"]
    for ev in events:
        lines += ev
    lines.append("END:VCALENDAR")
    return "\r\n".join(_fold(l) for l in lines) + "\r\n"


def match_title(g: dict) -> str:
    return f"NBA · {g['home']['name']} – {g['away']['name']}"


def match_events(g: dict, tv: dict) -> tuple[list[str], list[str] | None]:
    tip = _paris(g["tip_utc"])
    titre = match_title(g)
    desc = (f"Où regarder : {tv_text(tv)}. "
            + ("Match de NBA Cup. " if g.get("cup") else "")
            + f"Le verdict sans spoiler demain à 8h sur Instagram : @pickandwatch.fr. Programme : {SITE_URL}")
    direct = vevent(g["id"], tip, titre, desc, SITE_URL)
    rep = tv["replays"][0] if tv["replays"] else None
    differe = None
    if rep:
        differe = vevent(f"{g['id']}-differe", datetime.fromisoformat(rep["start"]),
                         f"{titre} (différé, {rep['channel']})",
                         f"Rediffusion sur {rep['channel']}. Zéro spoiler : {SITE_URL}", SITE_URL)
    return direct, differe


# --------------------------------------------------------------------------- liens d'agenda (Google, Outlook, Apple)

from urllib.parse import quote, urlencode


def subscribe_menu(slug: str, name: str) -> str:
    """S'abonner à l'agenda d'une équipe depuis Google Agenda, Outlook ou Apple."""
    https = f"{SITE_URL}/agenda/{slug}.ics"
    webcal = https.replace("https://", "webcal://")
    google = "https://calendar.google.com/calendar/r?" + urlencode({"cid": webcal})
    q = urlencode({"url": https, "name": f"{name} · Pick & Watch"})
    return (f'<div class="subs"><a class="btn" href="{e(google)}">Google Agenda</a>'
            f'<a class="btn" href="https://outlook.live.com/calendar/0/addfromweb?{e(q)}">Outlook</a>'
            f'<a class="btn" href="https://outlook.office.com/calendar/0/addfromweb?{e(q)}">Outlook pro (Microsoft 365)</a>'
            f'<a class="btn" href="{e(webcal)}">Apple Calendrier</a></div>'
            f'<p class="muted small">Autre application : abonne-toi avec ce lien → <code>{e(https)}</code></p>')


def add_menu(label: str, titre: str, start: datetime, desc: str, ics_href: str) -> str:
    """Ajouter un match (ou son différé) : Google, Outlook, Outlook pro, Apple / fichier .ics."""
    st = start.astimezone(timezone.utc)
    en = st + DUREE
    g = "https://calendar.google.com/calendar/render?" + urlencode({
        "action": "TEMPLATE", "text": titre, "dates": f"{st:%Y%m%dT%H%M%SZ}/{en:%Y%m%dT%H%M%SZ}", "details": desc})
    o = urlencode({"path": "/calendar/action/compose", "rru": "addevent", "subject": titre,
                   "startdt": st.strftime("%Y-%m-%dT%H:%M:%SZ"), "enddt": en.strftime("%Y-%m-%dT%H:%M:%SZ"), "body": desc})
    return (f'<details class="addmenu"><summary>{e(label)}</summary><span class="addopts">'
            f'<a href="{e(g)}">Google</a><a href="https://outlook.live.com/calendar/0/deeplink/compose?{e(o)}">Outlook</a>'
            f'<a href="https://outlook.office.com/calendar/0/deeplink/compose?{e(o)}">Outlook pro</a>'
            f'<a href="{e(ics_href)}">Apple / autre</a></span></details>')


def game_add_menus(g: dict, tv: dict, up: str) -> str:
    """Menus « + Agenda » (direct, et différé s'il est prévu) pour une carte de match."""
    tip = _paris(g["tip_utc"])
    titre = match_title(g)
    desc = f"Où regarder : {tv_text(tv)}. Le verdict sans spoiler demain à 8h sur Instagram : @pickandwatch.fr. Programme : {SITE_URL}"
    out = add_menu("+ Agenda (direct)", titre, tip, desc, f"{up}agenda/m/{g['id']}.ics")
    if tv["replays"]:
        r = tv["replays"][0]
        out += add_menu("+ Agenda (différé)", f"{titre} (différé, {r['channel']})", datetime.fromisoformat(r["start"]),
                        f"Rediffusion sur {r['channel']}. Zéro spoiler : {SITE_URL}", f"{up}agenda/m/{g['id']}-differe.ics")
    return out


# --------------------------------------------------------------------------- pages

def _flag(t: dict) -> str:
    return (f'<span class="flag" aria-hidden="true"><i style="background:{e(t["color"])}"></i>'
            f'<i style="background:{e(t["color2"])}"></i></span>')


MOIS_COURTS = ["janv.", "févr.", "mars", "avr.", "mai", "juin", "juil.", "août", "sept.", "oct.", "nov.", "déc."]


def _day(dt: datetime) -> str:
    return f"{JOURS[dt.weekday()]} {dt.day} {MOIS_COURTS[dt.month - 1]}"


def fin_du_mois(mois: str) -> datetime:
    """« 2026-11 » → 1er décembre 2026 à 12h, heure de Paris (la nuit du 30 novembre est incluse)."""
    y, m = map(int, mois.split("-"))
    y, m = (y + 1, 1) if m == 12 else (y, m + 1)
    return datetime(y, m, 1, 12, tzinfo=PARIS)


def team_page(team: dict, games: list[dict], tvs: dict, now: datetime, head, foot, mois: str) -> str:
    slug = team["slug"]
    limite = fin_du_mois(mois)
    a_venir = [g for g in games if now - timedelta(hours=3) < _paris(g["tip_utc"]) < limite]
    y, m = map(int, mois.split("-"))
    nom_mois = f"{MOIS[m - 1]} {y}"
    rows, mois = [], None
    for g in a_venir:
        tip = _paris(g["tip_utc"])
        if tip.month != mois:
            mois = tip.month
            rows.append(f'<h3 class="mois">{MOIS[mois - 1].capitalize()} {tip.year}</h3>')
        dom = g["home"]["abbr"] == team["abbr"]
        adv = g["away"] if dom else g["home"]
        tv = tvs[g["id"]]
        tvh = (f'<span class="pill live">Direct</span> {e(tv_text(tv))}' if tv["live"]
               else f'<span class="pill">Direct</span> <span class="muted">{e(tv_text(tv))}</span>')
        rep = (f'<br><span class="pill">Différé</span> {e(_day(datetime.fromisoformat(tv["replays"][0]["start"])))} '
               f'à {datetime.fromisoformat(tv["replays"][0]["start"]):%H:%M} · {e(tv["replays"][0]["channel"])}'
               if tv["replays"] else "")
        cup = '<span class="cup">NBA Cup</span>' if g.get("cup") else ""
        agenda = game_add_menus(g, tv, "../")
        rows.append(f"""<div class="row">
  <div class="when"><b>{e(_day(tip))}</b><span>{tip:%H:%M}</span></div>
  <div class="what"><p class="vs">{'' if dom else '<span class="muted">à</span> '}{_flag(adv)}<a href="{adv['slug']}.html">{e(adv['name'])}</a> {cup}</p>
    <p class="tvline">{tvh}{rep}</p></div>
  <div class="cal">{agenda}</div>
</div>""")
    top = head(f"{team['full']} · calendrier et chaînes", f"{SITE_URL}/equipes/{slug}.html", "../",
               f"Tous les matchs des {team['name']} à l'heure de Paris, avec la chaîne : beIN SPORTS, Prime Video ou NBA League Pass. Zéro spoiler.")
    body = "\n".join(rows) or '<p class="empty">Plus de match prévu pour l\'instant.</p>'
    return (top.replace("{date}", "MON ÉQUIPE") + f"""<main>
  <section class="hero">
    <p class="kicker fit" data-min="40">{e(team['name'])}</p>
    <h1 class="fit" data-min="30">Le calendrier, à l'heure de Paris</h1>
    <p class="summary">Le programme jusqu'à fin {nom_mois} · {len(a_venir)} matchs · chaînes françaises dès qu'elles sont annoncées</p>
  </section>
  <section class="subscribe">
    <p class="muted small">Un match te tente ? « + Agenda » l'ajoute à Google Agenda, Outlook ou ton iPhone, avec l'heure de Paris et la chaîne.
    Et le lendemain à 8h, notre verdict sans spoiler sur Instagram : <a href="https://www.instagram.com/pickandwatch.fr/">@pickandwatch.fr</a>.</p>
  </section>
  <section class="schedule">{body}</section>
  <p class="notes">Heures de Paris. Le programme du mois suivant est mis en ligne à la fin de chaque mois. La chaîne française est connue environ une semaine avant le match (guide TV beIN SPORTS) ; les matchs Prime Video sont annoncés plus tôt.</p>
  <p><a href="index.html">← Toutes les équipes</a></p>
</main>
""" + foot(now))


def index_page(teams: dict, now: datetime, head, foot) -> str:
    cards = "".join(f'<a class="team" href="{t["slug"]}.html">{_flag(t)}<span>{e(t["name"])}</span>'
                    f'<small>{e(t["location"])}</small></a>'
                    for t in sorted(teams.values(), key=lambda t: t["name"]))
    top = head("Mon équipe : le calendrier NBA de ton équipe", f"{SITE_URL}/equipes/", "../",
               "Le calendrier de chaque équipe NBA à l'heure de Paris, avec les chaînes françaises, à ajouter à ton agenda.")
    return (top.replace("{date}", "MON ÉQUIPE") + f"""<main>
  <section class="hero">
    <p class="kicker fit" data-min="40">Mon équipe</p>
    <h1 class="fit" data-min="30">Choisis ton équipe</h1>
    <p class="summary">Tous ses matchs du mois à l'heure de Paris, la chaîne française de chaque match, et ceux qui te tentent dans ton agenda, en un clic.</p>
  </section>
  <section class="teams">{cards}</section>
</main>
""" + foot(now))


def cup_page(cfg: dict, teams: dict, cup_games: list[dict], tvs: dict, standings: dict, now: datetime, head, foot) -> str:
    groupes = "".join(
        f'<div class="groupe"><h3>{e(nom)}</h3><ul>' + "".join(
            f'<li>{_flag(teams[a])}<a href="equipes/{teams[a]["slug"]}.html">{e(teams[a]["name"])}</a></li>' for a in membres)
        + "</ul></div>" for nom, membres in cfg["groupes"].items())
    rows, jour = [], None
    for g in sorted(cup_games, key=lambda g: g["tip_utc"]):
        tip = _paris(g["tip_utc"])
        nuit = (tip - timedelta(hours=12)).date()
        if nuit != jour:
            jour = nuit
            rows.append(f'<h3 class="mois">Nuit du {JOURS[nuit.weekday()]} {nuit.day} {MOIS[nuit.month - 1]}</h3>')
        tv = tvs[g["id"]]
        tvh = (f'<span class="pill live">Direct</span> {e(tv_text(tv))}' if tv["live"]
               else f'<span class="pill">Direct</span> <span class="muted">{e(tv_text(tv))}</span>')
        rows.append(f"""<div class="row">
  <div class="when"><b>{e((g.get('cup_stage') or '').replace('NBA Cup - ', '').replace('Group Play', 'Groupes'))}</b><span>{tip:%H:%M}</span></div>
  <div class="what"><p class="vs">{_flag(g['home'])}{e(g['home']['name'])} <span class="dash">–</span> {_flag(g['away'])}{e(g['away']['name'])}</p>
    <p class="tvline">{tvh}</p></div>
  <div class="cal">{game_add_menus(g, tv, "")}</div>
</div>""")
    if any(v["j"] for v in standings.values()):
        tables = "".join(
            f'<div class="groupe"><h3>{e(nom)}</h3><ol>' + "".join(
                f'<li>{e(teams[a]["name"])} <span class="muted">{standings[a]["v"]} v. – {standings[a]["d"]} d.</span></li>'
                for a in sorted(membres, key=lambda a: (-standings[a]["v"], standings[a]["d"])))
            + "</ol></div>" for nom, membres in cfg["groupes"].items())
        classement = (f'<div class="groupes">{tables}</div><p class="muted small">Victoires et défaites en NBA Cup uniquement. '
                      "Départage officiel (confrontations directes, écart de points) non pris en compte.</p>")
    else:
        classement = '<p class="muted">Les premiers matchs se jouent dans la nuit du vendredi 30 octobre : le classement apparaîtra ici.</p>'
    top = head("NBA Cup 2026 : groupes, calendrier et chaînes", f"{SITE_URL}/nba-cup.html", "",
               "La NBA Cup 2026 à l'heure de Paris : les groupes, tous les matchs, les chaînes françaises (Prime Video). Classement caché, zéro spoiler.")
    return (top.replace("{date}", "NBA CUP 2026") + f"""<main>
  <section class="hero">
    <p class="kicker fit" data-min="40">NBA Cup 2026</p>
    <h1 class="fit" data-min="30">Du 30 octobre au 11 décembre</h1>
    <p class="summary">6 groupes de 5 · 8 qualifiés · quarts les 4 et 5 décembre, demies les 8 et 9, finale le 11 à Indianapolis</p>
  </section>
  <section class="cupinfo">
    <p>Chaque équipe affronte une fois les quatre autres de son groupe. Les six premiers de groupe et le meilleur deuxième de chaque
    conférence vont en quarts, joués chez le mieux classé. Les matchs de groupe comptent aussi pour le classement de la saison.
    Fini Las Vegas : la finale se joue au Hinkle Fieldhouse d'Indianapolis.</p>
    <p><strong>En France :</strong> les doubles affiches du vendredi et la phase finale sur Prime Video (inclus dans Amazon Prime), les autres matchs sur le NBA League Pass.</p>
  </section>
  <h2 class="kicker small fit" data-min="26">Les groupes</h2>
  <section class="groupes">{groupes}</section>
  <h2 class="kicker small fit" data-min="26">Tous les matchs</h2>
  <section class="schedule">{''.join(rows)}</section>
  <details class="spoiler">
    <summary>Afficher le classement (spoiler)</summary>
    {classement}
  </details>
  <p class="notes">Heures de Paris. Sources : NBA.com (format et calendrier), ESPN (calendrier), guide TV beIN SPORTS, Prime Video.</p>
</main>
""" + foot(now))


# --------------------------------------------------------------------------- construction

def build(root: Path, site: Path, progs: list[dict], now: datetime, head, foot) -> dict:
    """Construit toutes les pages et agendas. Retourne {id: tv} pour le reste du site."""
    teams = sources.fetch_teams()
    diffuseurs = json.loads((root / "data" / "diffuseurs.json").read_text(encoding="utf-8"))
    schedules, all_games = {}, {}
    for abbr, t in teams.items():
        try:
            schedules[abbr] = sources.fetch_team_schedule(t["slug"], teams)
        except Exception as err:  # une équipe en panne ne bloque pas le site
            print(f"Calendrier {abbr} indisponible : {err}")
            schedules[abbr] = []
        for g in schedules[abbr]:
            all_games.setdefault(g["id"], g)
    tvs = {gid: tv_for(g, progs, diffuseurs) for gid, g in all_games.items()}
    # Programme publié mois par mois (décision d'Alexandre du 25/10/2026) : data/mois-publie.json.
    mp = root / "data" / "mois-publie.json"
    mois = json.loads(mp.read_text(encoding="utf-8"))["mois"] if mp.exists() else f"{now:%Y-%m}"

    (site / "equipes").mkdir(parents=True, exist_ok=True)
    (site / "agenda" / "m").mkdir(parents=True, exist_ok=True)
    for gid, g in all_games.items():
        if _paris(g["tip_utc"]) < now - timedelta(hours=3):
            continue
        direct, differe = match_events(g, tvs[gid])
        (site / "agenda" / "m" / f"{gid}.ics").write_text(calendar(match_title(g), [direct]), encoding="utf-8", newline="")
        if differe:
            (site / "agenda" / "m" / f"{gid}-differe.ics").write_text(calendar(match_title(g), [differe]), encoding="utf-8", newline="")
    for abbr, t in teams.items():
        games = sorted(schedules[abbr], key=lambda g: g["tip_utc"])
        (site / "equipes" / f"{t['slug']}.html").write_text(team_page(t, games, tvs, now, head, foot, mois), encoding="utf-8")
    (site / "equipes" / "index.html").write_text(index_page(teams, now, head, foot), encoding="utf-8")

    cfg_path = root / "data" / "nba-cup-2026.json"
    if cfg_path.exists():
        cfg = json.loads(cfg_path.read_text(encoding="utf-8"))
        cup_games = [g for g in all_games.values() if g.get("cup")]
        standings = {a: {"v": 0, "d": 0, "j": 0} for m in cfg["groupes"].values() for a in m}
        # Classement masqué : seul le vainqueur (indicateur ESPN « winner ») est lu, jamais le score.
        for g in cup_games:
            if g.get("winner") and "Group" in (g.get("cup_stage") or ""):
                for a in (g["home"]["abbr"], g["away"]["abbr"]):
                    if a in standings:
                        standings[a]["j"] += 1
                        standings[a]["v" if a == g["winner"] else "d"] += 1
        (site / "nba-cup.html").write_text(cup_page(cfg, teams, cup_games, tvs, standings, now, head, foot), encoding="utf-8")
    return {gid: tvs[gid] for gid in all_games}
