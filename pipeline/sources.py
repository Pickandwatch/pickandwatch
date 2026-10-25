"""Sources de données du programme Pick & Watch.

- Calendrier : API publique (non officielle) du scoreboard ESPN. Horaires en UTC,
  salle, ville, terrain neutre, couleurs des équipes.
  On ne lit JAMAIS les scores : Pick & Watch est garanti sans spoiler.
- Diffusion en France : guide TV XMLTV France (xmltvfr.fr), chaînes beIN SPORTS.
"""
from __future__ import annotations

import io
import json
import re
import unicodedata
import urllib.request
import xml.etree.ElementTree as ET
import zipfile
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

# Akamai (ESPN) refuse les user-agents « exotiques » : on reste générique.
UA = {"User-Agent": "Mozilla/5.0"}
ESPN_URL = "https://site.api.espn.com/apis/site/v2/sports/basketball/nba/scoreboard?dates={d}"
XMLTV_URL = "https://xmltvfr.fr/xmltv/xmltv.zip"


def _get(url: str, timeout: int = 120) -> bytes:
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read()


# --------------------------------------------------------------------------- ESPN

def fetch_espn_day(d: date, cache: Path | None = None) -> list[dict]:
    """Matchs d'une journée US (format ESPN), sans aucune donnée de score."""
    raw = _get(ESPN_URL.format(d=d.strftime("%Y%m%d")))
    if cache:
        cache.mkdir(parents=True, exist_ok=True)
        (cache / f"espn_{d:%Y%m%d}.json").write_bytes(raw)
    data = json.loads(raw)
    games = []
    for ev in data.get("events", []):
        comp = ev["competitions"][0]
        teams = {}
        for c in comp["competitors"]:
            t = c["team"]
            teams[c["homeAway"]] = {
                "abbr": t.get("abbreviation"),
                "name": t.get("name") or t.get("shortDisplayName"),
                "location": t.get("location"),
                "full": t.get("displayName"),
                "color": "#" + (t.get("color") or "111214"),
                "color2": "#" + (t.get("alternateColor") or "F2EEE6"),
            }
        venue = comp.get("venue") or {}
        addr = venue.get("address") or {}
        season = ev.get("season") or {}
        games.append({
            "id": ev["id"],
            "tip_utc": ev["date"],
            "home": teams.get("home"),
            "away": teams.get("away"),
            "venue": venue.get("fullName"),
            "city": addr.get("city"),
            "country": addr.get("country"),
            "neutral": bool(comp.get("neutralSite")),
            "phase": season.get("slug"),  # preseason / regular-season / post-season
            "status": (ev.get("status") or {}).get("type", {}).get("name"),
            "us_tv": [n for b in comp.get("broadcasts", []) for n in b.get("names", [])],
            "cup": "NBA Cup" if any("NBA Cup" in (n.get("headline") or "") for n in comp.get("notes", [])) else None,
        })
    return games


# --------------------------------------------------------------------------- XMLTV

BEIN_PREFIX = "beINSPORTS"


def _norm(s: str) -> str:
    s = unicodedata.normalize("NFKD", s or "").encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9 ]+", " ", s.lower()).strip()


def _xmltv_time(s: str) -> datetime:
    # "20261008011000 +0200"
    return datetime.strptime(s, "%Y%m%d%H%M%S %z")


def fetch_bein_basket(cache: Path | None = None) -> list[dict]:
    """Programmes basket des chaînes beIN SPORTS dans le guide TV XMLTV France."""
    raw = _get(XMLTV_URL, timeout=300)
    if cache:
        cache.mkdir(parents=True, exist_ok=True)
        (cache / "xmltv.zip").write_bytes(raw)
    zf = zipfile.ZipFile(io.BytesIO(raw))
    name = next(n for n in zf.namelist() if n.endswith(".xml"))
    channels: dict[str, str] = {}
    progs: list[dict] = []
    with zf.open(name) as fh:
        for _, el in ET.iterparse(fh, events=("end",)):
            if el.tag == "channel":
                cid = el.get("id", "")
                if cid.startswith(BEIN_PREFIX):
                    channels[cid] = el.findtext("display-name") or cid
                el.clear()
            elif el.tag == "programme":
                cid = el.get("channel", "")
                if cid.startswith(BEIN_PREFIX):
                    title = el.findtext("title") or ""
                    sub = el.findtext("sub-title") or ""
                    desc = el.findtext("desc") or ""
                    blob = f"{title} {sub} {desc}"
                    if "NBA" in blob and "WNBA" not in title:
                        progs.append({
                            "channel_id": cid,
                            "start": _xmltv_time(el.get("start")).isoformat(),
                            "stop": _xmltv_time(el.get("stop")).isoformat(),
                            "title": title,
                            "sub": sub,
                        })
                el.clear()
    for p in progs:
        p["channel"] = channels.get(p["channel_id"], p["channel_id"])
    return progs


def mentions_team(text: str, team: dict) -> bool:
    t = _norm(text)
    keys = {_norm(team["name"]), _norm(team["full"])}
    return any(k and re.search(rf"\b{re.escape(k)}\b", t) for k in keys)


TEAMS_URL = "https://site.api.espn.com/apis/site/v2/sports/basketball/nba/teams"
SCHEDULE_URL = "https://site.api.espn.com/apis/site/v2/sports/basketball/nba/teams/{slug}/schedule"


def fetch_teams() -> dict[str, dict]:
    """Les 30 équipes : abréviation ESPN → nom, ville, couleurs, identifiant d'URL."""
    data = json.loads(_get(TEAMS_URL))
    out = {}
    for item in data["sports"][0]["leagues"][0]["teams"]:
        t = item["team"]
        out[t["abbreviation"]] = {
            "abbr": t["abbreviation"],
            "slug": t["abbreviation"].lower(),
            "name": t.get("name") or t.get("shortDisplayName"),
            "location": t.get("location"),
            "full": t.get("displayName"),
            "color": "#" + (t.get("color") or "111214"),
            "color2": "#" + (t.get("alternateColor") or "F2EEE6"),
        }
    return out


def fetch_team_schedule(slug: str, teams: dict[str, dict]) -> list[dict]:
    """Calendrier de la saison régulière d'une équipe, au même format que fetch_espn_day.
    Aucune donnée de score n'est lue (on ne garde que le statut)."""
    data = json.loads(_get(SCHEDULE_URL.format(slug=slug)))
    games = []
    for ev in data.get("events", []):
        comp = ev["competitions"][0]
        side = {}
        for c in comp["competitors"]:
            abbr = c["team"].get("abbreviation")
            side[c["homeAway"]] = teams.get(abbr) or {"abbr": abbr, "name": c["team"].get("shortDisplayName"),
                                                     "location": c["team"].get("location"),
                                                     "full": c["team"].get("displayName"),
                                                     "color": "#111214", "color2": "#F2EEE6"}
        venue = comp.get("venue") or {}
        notes = " ".join(n.get("headline", "") for n in comp.get("notes", []))
        games.append({
            "id": ev["id"],
            "tip_utc": ev["date"],
            "home": side.get("home"),
            "away": side.get("away"),
            "venue": venue.get("fullName"),
            "city": (venue.get("address") or {}).get("city"),
            "neutral": bool(comp.get("neutralSite")),
            "phase": "regular-season" if (ev.get("seasonType") or {}).get("type") == 2 else "post-season",
            "status": ((comp.get("status") or {}).get("type") or {}).get("name"),
            "us_tv": [b.get("media", {}).get("shortName") for b in comp.get("broadcasts", []) if b.get("media")],
            "cup": "NBA Cup" if "NBA Cup" in notes else None,
            "cup_stage": notes or None,
            # Vainqueur seulement (jamais le score) : sert au classement NBA Cup, caché derrière un bouton.
            "winner": next((c["team"].get("abbreviation") for c in comp["competitors"] if c.get("winner")), None),
        })
    return games
