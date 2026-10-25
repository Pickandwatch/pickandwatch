"""Construit et vérifie le programme d'une nuit NBA, en heure de Paris.

Nuit du jour J : tous les matchs dont l'entre-deux tombe entre J 12:00 et J+1 12:00
(heure de Paris). On couvre ainsi la nuit américaine et les matchs joués en Europe
ou au Moyen-Orient l'après-midi ou en soirée.
"""
from __future__ import annotations

import json
import re
from datetime import date, datetime, time, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

from . import sources

PARIS = ZoneInfo("Europe/Paris")
LIVE_TOLERANCE = timedelta(minutes=45)
REPLAY_HORIZON = timedelta(hours=96)


def night_window(d: date) -> tuple[datetime, datetime]:
    start = datetime.combine(d, time(12, 0), PARIS)
    return start, start + timedelta(days=1)


def _paris(iso: str) -> datetime:
    return datetime.fromisoformat(iso.replace("Z", "+00:00")).astimezone(PARIS)


def load_json(path: Path, default):
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else default


def match_tv(game: dict, progs: list[dict]) -> tuple[dict | None, list[dict]]:
    """Retourne (direct, différés) beIN SPORTS pour un match."""
    tip = _paris(game["tip_utc"])
    live, replays = None, []
    for p in progs:
        text = f"{p['title']} {p['sub']}"
        if not (sources.mentions_team(text, game["home"]) and sources.mentions_team(text, game["away"])):
            continue
        # Les rediffusions de matchs d'archives (finales, playoffs) ne sont pas ce match-ci.
        if game["phase"] != "post-season" and re.search(r"playoff|finale", p["sub"], re.I):
            continue
        start = datetime.fromisoformat(p["start"]).astimezone(PARIS)
        slot = {"channel": p["channel"], "start": start.isoformat()}
        if abs(start - tip) <= LIVE_TOLERANCE:
            if live is None or abs(start - tip) < abs(datetime.fromisoformat(live["start"]) - tip):
                live = slot
        elif tip + LIVE_TOLERANCE < start <= tip + REPLAY_HORIZON:
            replays.append(slot)
    replays.sort(key=lambda s: s["start"])
    # Une même rediffusion peut apparaître sur deux chaînes au même horaire : on dédoublonne.
    seen, uniq = set(), []
    for r in replays:
        k = (r["channel"], r["start"])
        if k not in seen:
            seen.add(k)
            uniq.append(r)
    return live, uniq


SANS_AFFICHE = re.compile(r"^\s*basket-ball\s*:\s*nba\s*$", re.I)


def rediffusions_sans_affiche(night: dict, progs: list[dict]) -> list[dict]:
    """Créneaux beIN « Basket-ball : NBA » sans affiche, placés après les directs de la nuit et
    avant 18h le lendemain : ce sont des rediffusions de matchs de la nuit, sans que le guide dise
    lequel. On les annonce comme tels, sans jamais deviner le match."""
    lives = [datetime.fromisoformat(g["tv"]["live"]["start"]) for g in night["games"] if g["tv"].get("live")]
    if not lives:
        return []
    d = date.fromisoformat(night["night"])
    debut, fin = max(lives) + LIVE_TOLERANCE, datetime.combine(d + timedelta(days=1), time(18, 0), PARIS)
    deja = {(r["channel"], r["start"]) for g in night["games"] for r in g["tv"].get("replays", [])}
    out = []
    for p in progs:
        if not SANS_AFFICHE.match(p["title"]) or p.get("sub"):
            continue
        start = datetime.fromisoformat(p["start"]).astimezone(PARIS)
        slot = {"channel": p["channel"], "start": start.isoformat()}
        if debut < start < fin and (slot["channel"], slot["start"]) not in deja and slot not in out:
            out.append(slot)
    return sorted(out, key=lambda s: s["start"])


def refresh_tv(night: dict, progs: list[dict]) -> dict:
    """Met à jour les rediffusions d'une nuit déjà passée avec le guide TV du moment
    (le guide de la veille au soir ne connaît pas toujours les rediffusions du matin)."""
    for g in night["games"]:
        _, replays = match_tv({**g, "tip_utc": g["tip_paris"]}, progs)
        known = {(r["channel"], r["start"]) for r in g["tv"].get("replays", [])}
        g["tv"]["replays"] = sorted(g["tv"].get("replays", []) + [r for r in replays if (r["channel"], r["start"]) not in known],
                                    key=lambda s: s["start"])
    night["rediffusions_nuit"] = rediffusions_sans_affiche(night, progs)
    return night


def build_night(d: date, root: Path, cache: Path | None = None,
                espn_days: dict | None = None, progs: list | None = None) -> dict:
    start, end = night_window(d)
    games = []
    seen = set()
    for us_day in (d - timedelta(days=1), d, d + timedelta(days=1)):
        day_games = (espn_days or {}).get(us_day)
        if day_games is None:
            day_games = sources.fetch_espn_day(us_day, cache)
        for g in day_games:
            tip = _paris(g["tip_utc"])
            if start <= tip < end and g["id"] not in seen:
                seen.add(g["id"])
                games.append(g)
    games.sort(key=lambda g: g["tip_utc"])

    if progs is None:
        progs = sources.fetch_bein_basket(cache)

    diffuseurs = load_json(root / "data" / "diffuseurs.json", {"matchs": {}})
    manual = diffuseurs.get("matchs", {})
    # Prime Video : le calendrier ESPN signale les matchs « Prime Video » nationaux aux États-Unis.
    # Ils ne valent pour la France qu'une fois la règle confirmée (clé prime_usa_en_france).
    prime_fr = bool(diffuseurs.get("prime_usa_en_france"))
    editorial = load_json(root / "data" / "editorial" / f"{d.isoformat()}.json", {}).get("matchs", {})

    fr = load_json(root / "data" / "francais.json", {})
    francais = fr.get("equipes", {}) if fr.get("valide") else {}
    checks = []
    out_games = []
    for g in games:
        tip = _paris(g["tip_utc"])
        live, replays = match_tv(g, progs)
        man = manual.get(g["id"], {})
        tv = {"live": None, "replays": replays, "source": None, "status": None}
        prime_us = "Prime Video" in (g.get("us_tv") or [])
        if live:
            tv["live"] = live
            tv["source"] = "guide TV beIN SPORTS (XMLTV France)"
            tv["status"] = "confirmé"
            if prime_us and prime_fr:
                tv["also"] = ["Prime Video"]
        elif man.get("live"):
            tv["live"] = {"channel": man["live"], "start": tip.isoformat()}
            tv["source"] = man.get("source", "annonce du diffuseur")
            tv["status"] = "annoncé"
        elif prime_us and prime_fr:
            tv["live"] = {"channel": "Prime Video", "start": tip.isoformat()}
            tv["source"] = "calendrier NBA on Prime (repris par Prime Video France)"
            tv["status"] = "annoncé"
        else:
            tv["status"] = "league-pass"
            checks.append(f"{g['home']['name']} – {g['away']['name']} : aucune diffusion TV française "
                          f"trouvée → NBA League Pass (à confirmer).")
        if prime_us and not prime_fr:
            checks.append(f"{g['home']['name']} – {g['away']['name']} : sur Prime Video aux États-Unis. "
                          f"Vérifier qu'il est aussi sur Prime Video France.")
        if live and man.get("live") and man["live"] != live["channel"]:
            checks.append(f"{g['home']['name']} – {g['away']['name']} : le guide TV indique "
                          f"{live['channel']}, la saisie manuelle {man['live']}. À arbitrer.")

        # Recoupement de l'horaire : un direct TV qui démarre près de l'entre-deux confirme l'heure.
        if live:
            time_status = "recoupé"
        else:
            time_status = "calendrier officiel"
        if g["status"] not in ("STATUS_SCHEDULED", None):
            checks.append(f"{g['home']['name']} – {g['away']['name']} : statut {g['status']} "
                          f"(report ou annulation ?).")

        ed = editorial.get(g["id"], {})
        out_games.append({
            "id": g["id"],
            "tip_paris": tip.isoformat(),
            "home": g["home"],
            "away": g["away"],
            "venue": g["venue"],
            "city": g["city"],
            "neutral": g["neutral"],
            "phase": g["phase"],
            "cup": g.get("cup"),
            "francais": francais.get(g["home"]["abbr"], []) + francais.get(g["away"]["abbr"], []),
            "time_status": time_status,
            "tv": tv,
            "stars": ed.get("stars"),
            "brief": ed.get("brief"),
            "commentators": ed.get("commentators") or man.get("commentators"),
        })

    night = {
        "night": d.isoformat(),
        "generated_at": datetime.now(PARIS).isoformat(timespec="minutes"),
        "games": out_games,
        "checks": checks,
        "sources": {
            "calendrier": "ESPN (scoreboard NBA), horaires convertis en heure de Paris",
            "diffusion": "Guide TV XMLTV France (xmltvfr.fr), chaînes beIN SPORTS",
        },
    }
    night["rediffusions_nuit"] = rediffusions_sans_affiche(night, progs)
    return night
