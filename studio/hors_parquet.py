"""Carrousel « Hors parquet » du vendredi, charte « papier ».

Usage : python studio/hors_parquet.py chemin/spec.json
Produit 01.jpg … dans le dossier du spec : couverture, une slide par sujet, slide de fin.
"""
import json, sys, tempfile, pathlib, html as H
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from gen import line, rule, mono
from carrousel import render

BG, INK, OR, SUB = '#F2EEE6', '#111214', '#F06A2F', '#5C5850'
BAR = "font-family: 'Barlow Condensed', sans-serif; font-weight: 800"
MONO = "font-family: 'IBM Plex Mono', monospace"
HEAD = '<!doctype html><html lang="fr"><head><meta charset="utf-8"></head><body><x-dc><helmet></helmet>'
# Univers basket : la ligne de touche, avec le repère du milieu de terrain.
SVG = ('<svg width="1080" height="1350" viewBox="0 0 1080 1350" fill="none" style="position: absolute; left: 0; top: 0; z-index: -1">'
       '<rect x="30" y="30" width="1020" height="1290" stroke="rgba(17,18,20,0.18)" stroke-width="4"></rect>'
       '<g stroke="#F06A2F" stroke-opacity="0.22" stroke-width="6"><path d="M1050 30 V1320"></path><path d="M985 675 H1050"></path>'
       '<path d="M1050 520 A155 155 0 0 0 1050 830"></path></g></svg>')


def frame(inner):
    return (HEAD + f'<div style="position: relative; isolation: isolate; overflow: hidden; width: 1080px; height: 1350px; '
            f'box-sizing: border-box; padding: 72px; background: {BG}; color: {INK}; display: flex; flex-direction: column; '
            f"justify-content: space-between; font-family: 'Source Serif 4', Georgia, serif\">{SVG}{inner}</div></x-dc></body></html>")


def header(counter):
    return (f'<div style="position: relative; display: flex; justify-content: space-between; align-items: center">'
            f'<div style="position: absolute; left: 0; right: 0; top: 50%; height: 6px; margin-top: -3px; background: {OR}"></div>'
            f'<span style="position: relative; background: {BG}; padding-right: 22px; {BAR}; font-size: 44px; line-height: 1; letter-spacing: 7px">PICK &amp; WATCH</span>'
            f'<span style="position: relative; background: {BG}; padding-left: 18px; {MONO}; font-size: 22px; letter-spacing: 3px; color: {SUB}">{counter}</span></div>')


def title(top, bottom):
    return f'<div style="display: flex; flex-direction: column; gap: 14px">{line(top, color=OR)}{line(bottom, color=INK)}</div>'


def stats(items):
    cells = ''.join(
        f'<div style="padding: 18px 20px 16px {0 if i == 0 else 20}px; {"border-left: 1px solid " + INK if i else ""}">'
        f'<div style="{MONO}; font-size: 20px; letter-spacing: 2px; color: {SUB}">{k}</div>'
        f'<div style="{BAR}; font-size: 66px; line-height: 1; margin-top: 8px; white-space: nowrap">{v}</div></div>'
        for i, (k, v) in enumerate(items))
    return (f'<div style="display: grid; grid-template-columns: repeat({len(items)}, minmax(0, 1fr)); '
            f'border-top: 2px solid {INK}; border-bottom: 2px solid {INK}">{cells}</div>')


def body(text):
    text = text.replace('« ', '«&nbsp;').replace(' »', '&nbsp;»').replace(' :', '&nbsp;:').replace(' ;', '&nbsp;;').replace(' ?', '&nbsp;?')
    return f'<div style="font-size: 37px; line-height: 1.38">{text}</div>'


def source_box(label, name, right=''):
    return (f'<div style="display: flex; justify-content: space-between; align-items: center; gap: 24px; border: 3px solid {OR}; padding: 20px 30px">'
            f'<div style="display: flex; flex-direction: column; gap: 6px"><span style="{MONO}; font-size: 22px; letter-spacing: 3px; color: {SUB}">{label}</span>'
            f'<span style="{BAR}; font-size: 54px; line-height: 1">{name}</span></div>'
            f'<span style="{MONO}; font-size: 26px; color: {OR}">{right}</span></div>')


def cover(c, n):
    rows = ''.join(
        f'<div style="padding: 18px 0; border-top: 1px solid {INK}">'
        f'<div style="{MONO}; font-size: 22px; letter-spacing: 3px; color: {OR}">{k}</div>'
        f'<div style="{BAR}; font-size: 56px; line-height: 1.02; margin-top: 6px">{t}</div></div>' for k, t in c['sommaire'])
    inner = [header(f'1/{n}'), title('CHAQUE VENDREDI', 'HORS PARQUET.'),
             f'<div style="{MONO}; font-size: 26px; letter-spacing: 4px; text-align: center; color: {SUB}; padding: 14px 0; border-top: 2px solid {INK}; border-bottom: 2px solid {INK}">{c["semaine"]}</div>',
             f'<div style="display: flex; flex-direction: column; border-bottom: 2px solid {INK}">{rows}</div>',
             f'<div style="display: flex; justify-content: space-between; align-items: baseline"><span style="font-size: 30px; font-style: italic; color: {SUB}">{c["accroche"]}</span>'
             f'<span style="{BAR}; font-size: 40px; letter-spacing: 2px; color: {OR}">SWIPE →</span></div>']
    return frame('\n'.join(inner))


def sujet(s, i, n):
    inner = [header(f'HORS PARQUET · {i}/{n}'),
             f'<div style="display: flex; flex-direction: column; gap: 22px"><div style="{MONO}; font-size: 24px; letter-spacing: 4px; color: {OR}">{s["rubrique"]}</div>{title(*s["titre"])}</div>',
             stats(s['chiffres']), body(s['texte']), source_box(*s['source'])]
    return frame('\n'.join(inner))


def fin(f, n):
    inner = [header(f'HORS PARQUET · {n}/{n}'), title('LE VENDREDI,', "C'EST HORS PARQUET."),
             body(f['texte']),
             f'<div style="display: flex; justify-content: space-between; align-items: center; gap: 24px; border: 3px solid {OR}; padding: 20px 30px">'
             f'<div style="display: flex; flex-direction: column; gap: 4px"><span style="{BAR}; font-size: 54px; line-height: 1">pickandwatch.fr</span>'
             f'<span style="{MONO}; font-size: 24px; color: {SUB}">Zéro spoiler. Jamais.</span></div>'
             f'<span style="{BAR}; font-size: 42px; letter-spacing: 2px">LIEN EN BIO ↑</span></div>']
    return frame('\n'.join(inner))


def main(spec_path):
    spec_path = pathlib.Path(spec_path); spec = json.loads(spec_path.read_text())
    tmp = pathlib.Path(tempfile.mkdtemp()); n = len(spec['sujets']) + 2
    pages = [cover(spec['couverture'], n)] + [sujet(s, i, n) for i, s in enumerate(spec['sujets'], 2)] + [fin(spec['fin'], n)]
    names = []
    for k, p in enumerate(pages, 1):
        (tmp / f'hp{k}.dc.html').write_text(p); names.append(f'hp{k}')
    problems = render(tmp, spec_path.parent, names)
    print(f'{len(names)} slides dans {spec_path.parent}')
    for p in problems: print('ATTENTION', p)
    return 1 if problems else 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1]))
