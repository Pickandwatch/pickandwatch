"""Carrousel « mode d'emploi » d'une fonction du site, avec captures d'écran (charte « papier »).

Sert à présenter un service de pickandwatch.fr pas à pas, pour qu'on comprenne que ça se passe
sur le site : couverture, une slide par étape (texte à gauche, capture dans un téléphone à droite),
slide de fin.

Usage : python studio/site_tuto.py chemin/spec.json  → 01.jpg … dans le dossier du spec.
Spec : {"couverture": {"etiquette", "titre": [orange, noir], "lignes": [[k, t], …], "accroche"},
        "etapes": [{"rubrique", "titre": [orange, noir], "texte", "capture": "fichier.png",
                    "cadrage": "top" | "bottom"}],
        "fin": {"etiquette", "titre": [orange, noir], "texte"}}
Les captures (PNG, téléphone 390 px de large) sont dans le dossier du spec.
"""
import json, sys, tempfile, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from hors_parquet import frame, header, title, BAR, MONO, INK, OR, SUB
from guide import cover, fin
from carrousel import render


def _texte(t):
    t = t.replace('« ', '«&nbsp;').replace(' »', '&nbsp;»').replace(' :', '&nbsp;:').replace(' ?', '&nbsp;?')
    return f'<div style="font-size: 36px; line-height: 1.38">{t}</div>'


def etape(e, i, n, base):
    img = (base / e['capture']).resolve()
    pos = 'bottom' if e.get('cadrage') == 'bottom' else 'top'
    phone = (f'<div style="flex: none; width: 430px; height: 800px; box-sizing: border-box; border: 12px solid {INK}; '
             f'border-radius: 56px; overflow: hidden; background: #F2EEE6; box-shadow: 0 18px 40px rgba(17,18,20,0.18)">'
             f'<img src="file://{img}" style="width: 100%; height: 100%; object-fit: cover; object-position: center {pos}; display: block"></div>')
    gauche = (f'<div style="display: flex; flex-direction: column; justify-content: space-between; gap: 30px; min-width: 0; flex: 1">'
              f'{_texte(e["texte"])}'
              f'<div style="border: 3px solid {OR}; padding: 18px 22px; display: flex; flex-direction: column; gap: 6px">'
              f'<span style="{MONO}; font-size: 20px; letter-spacing: 3px; color: {SUB}">SUR LE SITE</span>'
              f'<span style="{BAR}; font-size: 46px; line-height: 1">pickandwatch.fr</span>'
              f'<span style="{MONO}; font-size: 22px; color: {OR}">lien en bio</span></div></div>')
    inner = [header(f'{e.get("etiquette", "MODE D\'EMPLOI")} · {i}/{n}'),
             f'<div style="display: flex; flex-direction: column; gap: 20px"><div style="{MONO}; font-size: 24px; letter-spacing: 4px; color: {OR}">{e["rubrique"]}</div>{title(*e["titre"])}</div>',
             f'<div style="display: flex; gap: 40px; align-items: stretch">{gauche}{phone}</div>']
    return frame('\n'.join(inner))


def couverture(c, n, base):
    """Couverture avec téléphone : on voit tout de suite que ça se passe sur le site."""
    img = (base / c['capture']).resolve()
    pos = 'bottom' if c.get('cadrage') == 'bottom' else 'top'
    rows = ''.join(
        f'<div style="padding: 16px 0; border-top: 1px solid {INK}; display: flex; flex-direction: column; gap: 6px">'
        f'<span style="{BAR}; font-size: 50px; line-height: 1">{k}</span>'
        f'<span style="{MONO}; font-size: 21px; letter-spacing: 1px; color: {SUB}">{t}</span></div>' for k, t in c['lignes'])
    phone = (f'<div style="flex: none; width: 430px; height: 780px; box-sizing: border-box; border: 12px solid {INK}; '
             f'border-radius: 56px; overflow: hidden; background: #F2EEE6; box-shadow: 0 18px 40px rgba(17,18,20,0.18)">'
             f'<img src="file://{img}" style="width: 100%; height: 100%; object-fit: cover; object-position: center {pos}; display: block"></div>')
    gauche = (f'<div style="display: flex; flex-direction: column; justify-content: space-between; min-width: 0; flex: 1">'
              f'<div style="display: flex; flex-direction: column; border-bottom: 2px solid {INK}">{rows}</div>'
              f'<div style="display: flex; flex-direction: column; gap: 6px; background: {OR}; color: #F2EEE6; padding: 20px 22px">'
              f'<span style="{MONO}; font-size: 20px; letter-spacing: 3px">GRATUIT, SUR LE SITE</span>'
              f'<span style="{BAR}; font-size: 50px; line-height: 1">pickandwatch.fr</span></div></div>')
    inner = [header(f'{c.get("etiquette", "SUR LE SITE")} · 1/{n}'), title(*c['titre']),
             f'<div style="display: flex; gap: 40px; align-items: stretch">{gauche}{phone}</div>',
             f'<div style="display: flex; justify-content: space-between; align-items: baseline"><span style="font-size: 30px; font-style: italic; color: {SUB}">{c["accroche"]}</span>'
             f'<span style="{BAR}; font-size: 40px; letter-spacing: 2px; color: {OR}">SWIPE →</span></div>']
    return frame('\n'.join(inner))


def main(spec_path):
    spec_path = pathlib.Path(spec_path); spec = json.loads(spec_path.read_text())
    base = spec_path.parent
    tmp = pathlib.Path(tempfile.mkdtemp()); n = len(spec['etapes']) + 2
    pages = ([couverture(spec['couverture'], n, base) if spec['couverture'].get('capture') else cover(spec['couverture'], n)] + [etape(e, i, n, base) for i, e in enumerate(spec['etapes'], 2)]
             + [fin(spec['fin'], n)])
    names = []
    for k, p in enumerate(pages, 1):
        (tmp / f't{k}.dc.html').write_text(p); names.append(f't{k}')
    problems = render(tmp, base, names, spec.get('theme'))
    print(f'{len(names)} slides dans {base}')
    for p in problems: print('ATTENTION', p)
    return 1 if problems else 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1]))
