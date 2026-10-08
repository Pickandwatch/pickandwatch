"""Point d'entrée du robot quotidien.

Usage :
    python -m pipeline.run                 # nuit du jour (heure de Paris)
    python -m pipeline.run --night 2026-10-07
"""
from __future__ import annotations

import argparse
import json
import os
from datetime import date, datetime, timedelta
from pathlib import Path

from .night import PARIS, build_night
from .render import build_site

ROOT = Path(__file__).resolve().parent.parent


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--night", help="AAAA-MM-JJ (par défaut : aujourd'hui, heure de Paris)")
    ap.add_argument("--cache", help="dossier où garder les fichiers sources téléchargés")
    args = ap.parse_args()

    d = date.fromisoformat(args.night) if args.night else datetime.now(PARIS).date()
    night = build_night(d, ROOT, Path(args.cache) if args.cache else None)

    out = ROOT / "data" / "nuits" / f"{d.isoformat()}.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(night, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    # Verdicts de la nuit précédente (validés), affichés en tête de page.
    p = (d - timedelta(days=1)).isoformat()
    prev_path, verd_path = ROOT / "data" / "nuits" / f"{p}.json", ROOT / "data" / "verdicts" / f"{p}.json"
    prev = json.loads(prev_path.read_text(encoding="utf-8")) if prev_path.exists() else None
    verdicts = json.loads(verd_path.read_text(encoding="utf-8")) if verd_path.exists() else None
    build_site(ROOT, night, prev, verdicts)

    lines = [f"## Programme · nuit du {d.isoformat()}", ""]
    for g in night["games"]:
        live = g["tv"]["live"]["channel"] if g["tv"]["live"] else "League Pass (à confirmer)"
        lines.append(f"- {g['tip_paris'][11:16]} · {g['home']['name']} – {g['away']['name']} · "
                     f"{g['city']}{' (terrain neutre)' if g['neutral'] else ''} · {live}")
    lines += ["", "### Points à vérifier", ""] + ([f"- {c}" for c in night["checks"]] or ["- Aucun"])
    report = "\n".join(lines) + "\n"
    print(report)
    if os.environ.get("GITHUB_STEP_SUMMARY"):
        with open(os.environ["GITHUB_STEP_SUMMARY"], "a", encoding="utf-8") as fh:
            fh.write(report)


if __name__ == "__main__":
    main()
