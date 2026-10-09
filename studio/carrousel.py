"""Fabrique le carrousel Instagram du soir (charte « papier »).

Usage : python studio/carrousel.py posts/AAAA-MM-JJ/spec.json
Produit posts/AAAA-MM-JJ/01.jpg … (couverture, une slide par match, slide site), 1080x1350.
Le fichier spec.json décrit la couverture et les matchs (voir posts/2026-10-08/spec.json).
"""
import json, re, sys, tempfile, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from gen import fit, line, rule, mono
import gen_match

ST = pathlib.Path(__file__).resolve().parent
FONTS = '<link href="https://fonts.googleapis.com/css2?family=Barlow+Condensed:wght@600;800&family=IBM+Plex+Mono:wght@400;500&family=Source+Serif+4:ital,wght@0,400;0,600;1,400&display=swap" rel="stylesheet">'
HEAD = '''<!doctype html><html lang="fr"><head><meta charset="utf-8"></head><body><x-dc><helmet></helmet>'''
def cover(c, out):
    bg, ink, head, sub, frame = '#F2EEE6', '#111214', '#F06A2F', '#5C5850', 'rgba(17,18,20,0.18)'
    b = [rule(head, 6), line('CETTE NUIT EN NBA', color=ink), rule(ink), mono(c['date'], sub), rule(ink),
         mono(c.get('top_label', "★★★ L'IMMANQUABLE"), head, 26, 6)]
    b += [line(c['top'][0] + ' – ' + c['top'][1], color=head, lh=0.84),
          mono(c['top_info'], sub, 22, 1)]
    rows = []
    for t, info, st in sorted(c['others'], key=lambda x: x[1]):
        rows.append(f'<div style="display: grid; grid-template-columns: 110px minmax(0, 1fr) auto; align-items: baseline; gap: 18px; padding: 12px 0; border-top: 1px solid {ink}">'
                    f'<span style="font-family: \'IBM Plex Mono\', monospace; font-weight: 500; font-size: 30px; color: {head}">{info}</span>'
                    f'<span style="font-family: \'Barlow Condensed\', sans-serif; font-weight: 800; font-size: 54px; line-height: 0.95; white-space: nowrap">{t}</span>'
                    f'<span style="font-size: 34px; letter-spacing: 3px; color: {head}">{st}</span></div>')
    b += [f'<div style="display: flex; flex-direction: column; border-bottom: 2px solid {ink}">' + ''.join(rows) + '</div>',
          f'<div style="font-family: \'IBM Plex Mono\', monospace; font-size: 20px; letter-spacing: 1px; color: {sub}; text-align: center">{c["note"]}</div>']
    b += [f'<div style="display: flex; justify-content: space-between; align-items: center; font-family: \'IBM Plex Mono\', monospace; font-size: 22px; letter-spacing: 2px; color: {sub}"><span>PICKANDWATCH.FR · ZÉRO SPOILER</span><span style="font-family: \'Barlow Condensed\', sans-serif; font-weight: 800; font-size: 34px; letter-spacing: 2px; color: {head}">LES MATCHS EN DÉTAIL →</span></div>']
    svg = f'<svg width="1080" height="1350" viewBox="0 0 1080 1350" fill="none" style="position: absolute; left: 0; top: 0; z-index: -1"><rect x="30" y="30" width="1020" height="1290" stroke="{frame}" stroke-width="4"></rect></svg>'
    inner = '\n'.join(b)
    (out / 'cover.dc.html').write_text(HEAD + f'<div style="position: relative; isolation: isolate; overflow: hidden; width: 1080px; height: 1350px; box-sizing: border-box; padding: 72px; background: {bg}; color: {ink}; display: flex; flex-direction: column; justify-content: space-between; font-family: \'Source Serif 4\', Georgia, serif">{svg}{inner}</div></x-dc></body></html>')



def render(src, out, names):
    """Rend chaque slide en JPEG et signale tout débordement du cadre."""
    from playwright.sync_api import sync_playwright
    from PIL import Image
    problems = []
    with sync_playwright() as p:
        b = p.chromium.launch(); pg = b.new_page(viewport={'width': 1080, 'height': 1350})
        for i, n in enumerate(names, 1):
            body = (src / f'{n}.dc.html').read_text().split('</helmet>')[1].split('</x-dc>')[0]
            h = src / f'_{n}.html'
            h.write_text(f'<html><head><meta charset="utf-8">{FONTS}<style>body{{margin:0}}</style></head><body>{body}</body></html>')
            pg.goto(f'file://{h.resolve()}'); pg.wait_for_load_state('networkidle'); pg.evaluate('document.fonts.ready'); pg.wait_for_timeout(600)
            fams = set(pg.evaluate("[...document.fonts].filter(f=>f.status==='loaded').map(f=>f.family)"))
            if not {'Barlow Condensed', 'IBM Plex Mono'} <= fams:
                problems.append(f'{n} : polices non chargées ({sorted(fams)})')
            over = pg.evaluate("""() => { const r=[]; const root=document.querySelector('body > div');
              root.querySelectorAll('*').forEach(el=>{ if(el.closest('svg')) return;
                if(el.scrollWidth>el.clientWidth+1 && getComputedStyle(el).whiteSpace==='nowrap') r.push((el.textContent||'').slice(0,40));
                if(el.getBoundingClientRect().bottom>1310) r.push('bas : '+(el.textContent||'').slice(0,40)); });
              return r; }""")
            problems += [f'{n} : déborde ({o})' for o in over]
            png = src / f'{i:02d}.png'
            pg.locator('body > div').first.screenshot(path=str(png))
            Image.open(png).convert('RGB').save(out / f'{i:02d}.jpg', quality=92, optimize=True)
        b.close()
    return problems


def main(spec_path):
    spec_path = pathlib.Path(spec_path); out = spec_path.parent
    spec = json.loads(spec_path.read_text())
    tmp = pathlib.Path(tempfile.mkdtemp())
    gen_match.OUT = tmp
    cover(spec['cover'], tmp)
    names = ['cover']
    for i, m in enumerate(spec['matches'], 2):
        gen_match.match(f'm{i}.dc.html', m); names.append(f'm{i}')
    (tmp / 'cta.dc.html').write_text((ST / 'gabarits' / 'cta.dc.html').read_text()); names.append('cta')
    problems = render(tmp, out, names)
    print(f'{len(names)} slides dans {out}')
    for p in problems: print('ATTENTION', p)
    return 1 if problems else 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1]))
