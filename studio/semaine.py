"""Classe les matchs d'une semaine (lundi → dimanche, nuits à l'heure de Paris) pour le Reel du lundi.

Usage : python studio/semaine.py AAAA-MM-JJ   (le lundi de la semaine)
Note de base = somme des notes d'équipe (data/grille-equipes.json), sans le bonus « événement »,
à ajouter à la main. Affiche aussi la diffusion française (beIN, Prime Video) et les différés.
"""
import json, sys
from datetime import date, timedelta
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from pipeline.night import build_night
from pipeline import sources

ROOT = Path(__file__).resolve().parent.parent
ALIAS = {'SA': 'SAS', 'GS': 'GSW'}  # codes ESPN → codes de la grille


def main(lundi: str):
    grid = json.loads((ROOT / 'data' / 'grille-equipes.json').read_text())['equipes']
    progs = sources.fetch_bein_basket(None)
    rows = []
    for k in range(7):
        d = date.fromisoformat(lundi) + timedelta(days=k)
        for g in build_night(d, ROOT, progs=progs)['games']:
            note = sum(grid.get(ALIAS.get(t['abbr'], t['abbr']), {}).get('note', 0) for t in (g['home'], g['away']))
            tv = (g['tv']['live'] or {}).get('channel') or 'NBA League Pass'
            rep = ', '.join(f"{r['start'][5:16]} {r['channel']}" for r in g['tv']['replays'][:1])
            rows.append((note, d.isoformat(), g['tip_paris'][5:16], f"{g['home']['name']} – {g['away']['name']}", tv, rep, g['id']))
    for r in sorted(rows, key=lambda r: -r[0])[:15]:
        print(f'{r[0]:>2}  nuit {r[1]}  {r[2]}  {r[3]:<30} {r[4]:<18} {r[5]}  ({r[6]})')


if __name__ == '__main__':
    main(sys.argv[1])
