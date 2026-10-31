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


def _img(path, size, radius=0):
    return (f'<img src="file://{path}" style="flex: none; width: {size}px; height: {size}px; object-fit: cover; '
            f'border-radius: {radius}px; box-shadow: 0 0 0 2px {INK}; display: block">')


def cover(c, n, base=None):
    def row(k, t, *logo):
        vignette = _img((base / logo[0]).resolve(), 64, 8) if logo and base else ''
        return (f'<div style="padding: 14px 0; border-top: 1px solid {INK}; display: flex; justify-content: space-between; align-items: center; gap: 20px">'
                f'<span style="display: flex; align-items: center; gap: 20px">{vignette}<span style="{BAR}; font-size: 54px; line-height: 1">{k}</span></span>'
                f'<span style="{MONO}; font-size: 22px; letter-spacing: 1px; color: {SUB}; text-align: right">{t}</span></div>')
    rows = ''.join(row(*l) for l in c['lignes'])
    inner = [header(f'{c.get("etiquette", "LE GUIDE")} · 1/{n}'), title(*c['titre']),
             f'<div style="display: flex; flex-direction: column; border-bottom: 2px solid {INK}">{rows}</div>',
             f'<div style="display: flex; justify-content: space-between; align-items: baseline"><span style="font-size: 30px; font-style: italic; color: {SUB}">{c["accroche"]}</span>'
             f'<span style="{BAR}; font-size: 40px; letter-spacing: 2px; color: {OR}">SWIPE →</span></div>']
    return frame('\n'.join(inner))


def slide(s, i, n, base=None):
    bas = source_box(*s['encadre'])
    if s.get('logo') and base:  # logo officiel du podcast / de la chaîne, à côté de l'encadré
        bas = (f'<div style="display: flex; gap: 28px; align-items: center">{_img((base / s["logo"]).resolve(), 150, 14)}'
               f'<div style="flex: 1; min-width: 0">{bas}</div></div>')
    inner = [header(f'{s.get("etiquette", "LE GUIDE")} · {i}/{n}'),
             f'<div style="display: flex; flex-direction: column; gap: 22px"><div style="{MONO}; font-size: 24px; letter-spacing: 4px; color: {OR}">{s["rubrique"]}</div>{title(*s["titre"])}</div>',
             stats(s['chiffres']),
             (body(s['texte']) if not s.get('taille') else body(s['texte']).replace('font-size: 37px', f"font-size: {s['taille']}px")),
             bas]
    return frame('\n'.join(inner))


def fin(f, i, n=None):
    n = n or i
    if f.get('sans_site'):  # la slide de présentation qui suit porte déjà le site et l'appel à nous suivre
        return frame('\n'.join([header(f'{f.get("etiquette", "LE GUIDE")} · {i}/{n}'), title(*f['titre']), body(f['texte']), '<div></div>']))
    inner = [header(f'{f.get("etiquette", "LE GUIDE")} · {i}/{n}'), title(*f['titre']), body(f['texte']),
             f'<div style="display: flex; justify-content: space-between; align-items: center; gap: 24px; border: 3px solid {OR}; padding: 20px 30px">'
             f'<div style="display: flex; flex-direction: column; gap: 4px"><span style="{BAR}; font-size: 54px; line-height: 1">pickandwatch.fr</span>'
             f'<span style="{MONO}; font-size: 24px; color: {SUB}">Zéro spoiler. Jamais.</span></div>'
             f'<span style="{BAR}; font-size: 42px; letter-spacing: 2px">LIEN EN BIO ↑</span></div>']
    return frame('\n'.join(inner))


def presentation(p, n):
    """Dernière slide : qui est Pick & Watch (concept, ligne éditoriale) + appel à nous suivre."""
    rows = ''.join(
        f'<div style="padding: 14px 0; border-top: 1px solid {INK}; display: grid; grid-template-columns: 210px 1fr; align-items: baseline; gap: 20px">'
        f'<span style="{BAR}; font-size: 48px; line-height: 1; color: {OR}">{k}</span>'
        f'<span style="font-size: 30px; line-height: 1.3">{t}</span></div>' for k, t in p['lignes'])
    cta = (f'<div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px">'
           f'<div style="background: {OR}; color: #F2EEE6; padding: 20px 24px; display: flex; flex-direction: column; gap: 6px">'
           f'<span style="{MONO}; font-size: 20px; letter-spacing: 3px">SUIS-NOUS</span>'
           f'<span style="{BAR}; font-size: 46px; line-height: 1">@pickandwatch.fr</span></div>'
           f'<div style="border: 3px solid {OR}; padding: 17px 21px; display: flex; flex-direction: column; gap: 6px">'
           f'<span style="{MONO}; font-size: 20px; letter-spacing: 3px; color: {SUB}">VISITE NOTRE SITE</span>'
           f'<span style="{BAR}; font-size: 46px; line-height: 1">pickandwatch.fr</span></div></div>')
    inner = [header(f'{p.get("etiquette", "PICK & WATCH")} · {n}/{n}'), title(*p['titre']),
             f'<div style="font-size: 32px; line-height: 1.35; font-style: italic; color: {SUB}">{p["texte"]}</div>',
             f'<div style="display: flex; flex-direction: column; border-bottom: 2px solid {INK}">{rows}</div>', cta]
    return frame('\n'.join(inner))


def main(spec_path):
    spec_path = pathlib.Path(spec_path); spec = json.loads(spec_path.read_text())
    tmp = pathlib.Path(tempfile.mkdtemp()); n = len(spec['slides']) + 2 + (1 if spec.get('presentation') else 0)
    base = spec_path.parent
    pages = [cover(spec['couverture'], n, base)] + [slide(s, i, n, base) for i, s in enumerate(spec['slides'], 2)] + [fin(spec['fin'], n - (1 if spec.get('presentation') else 0), n)] + ([presentation(spec['presentation'], n)] if spec.get('presentation') else [])
    names = []
    for k, p in enumerate(pages, 1):
        (tmp / f'g{k}.dc.html').write_text(p); names.append(f'g{k}')
    problems = render(tmp, spec_path.parent, names, spec.get('theme'))
    print(f'{len(names)} slides dans {spec_path.parent}')
    for p in problems: print('ATTENTION', p)
    return 1 if problems else 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1]))
