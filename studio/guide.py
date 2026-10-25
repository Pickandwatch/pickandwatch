"""Carrousel « guide » (contenu permanent, à épingler), charte « papier ».

Usage : python studio/guide.py chemin/spec.json  → 01.jpg … dans le dossier du spec.
Spec : {"couverture": {"titre": [orange, noir], "lignes": [[étiquette, texte], …], "accroche": str},
        "slides": [{"rubrique", "titre": [orange, noir], "chiffres": [[k, v], …], "texte", "encadre": [label, nom, droite]}],
        "fin": {"titre": [orange, noir], "texte": str}}
"""
import json, sys, tempfile, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from hors_parquet import frame, header, title, stats, body, source_box, BAR, MONO, INK, OR, SUB
from carrousel import render


def cover(c, n):
    rows = ''.join(
        f'<div style="padding: 18px 0; border-top: 1px solid {INK}; display: flex; justify-content: space-between; align-items: baseline; gap: 20px">'
        f'<span style="{BAR}; font-size: 58px; line-height: 1">{k}</span>'
        f'<span style="{MONO}; font-size: 24px; letter-spacing: 1px; color: {SUB}; text-align: right">{t}</span></div>' for k, t in c['lignes'])
    inner = [header(f'LE GUIDE · 1/{n}'), title(*c['titre']),
             f'<div style="display: flex; flex-direction: column; border-bottom: 2px solid {INK}">{rows}</div>',
             f'<div style="display: flex; justify-content: space-between; align-items: baseline"><span style="font-size: 30px; font-style: italic; color: {SUB}">{c["accroche"]}</span>'
             f'<span style="{BAR}; font-size: 40px; letter-spacing: 2px; color: {OR}">SWIPE →</span></div>']
    return frame('\n'.join(inner))


def slide(s, i, n):
    inner = [header(f'LE GUIDE · {i}/{n}'),
             f'<div style="display: flex; flex-direction: column; gap: 22px"><div style="{MONO}; font-size: 24px; letter-spacing: 4px; color: {OR}">{s["rubrique"]}</div>{title(*s["titre"])}</div>',
             stats(s['chiffres']), body(s['texte']), source_box(*s['encadre'])]
    return frame('\n'.join(inner))


def fin(f, n):
    inner = [header(f'LE GUIDE · {n}/{n}'), title(*f['titre']), body(f['texte']),
             f'<div style="display: flex; justify-content: space-between; align-items: center; gap: 24px; border: 3px solid {OR}; padding: 20px 30px">'
             f'<div style="display: flex; flex-direction: column; gap: 4px"><span style="{BAR}; font-size: 54px; line-height: 1">pickandwatch.fr</span>'
             f'<span style="{MONO}; font-size: 24px; color: {SUB}">Zéro spoiler. Jamais.</span></div>'
             f'<span style="{BAR}; font-size: 42px; letter-spacing: 2px">LIEN EN BIO ↑</span></div>']
    return frame('\n'.join(inner))


def main(spec_path):
    spec_path = pathlib.Path(spec_path); spec = json.loads(spec_path.read_text())
    tmp = pathlib.Path(tempfile.mkdtemp()); n = len(spec['slides']) + 2
    pages = [cover(spec['couverture'], n)] + [slide(s, i, n) for i, s in enumerate(spec['slides'], 2)] + [fin(spec['fin'], n)]
    names = []
    for k, p in enumerate(pages, 1):
        (tmp / f'g{k}.dc.html').write_text(p); names.append(f'g{k}')
    problems = render(tmp, spec_path.parent, names)
    print(f'{len(names)} slides dans {spec_path.parent}')
    for p in problems: print('ATTENTION', p)
    return 1 if problems else 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1]))
