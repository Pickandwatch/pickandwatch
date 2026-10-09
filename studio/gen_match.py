import sys, math, pathlib, html as H
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from gen import fit, line, rule, mono, D
OUT = D
from contrast import cr
IV, WHITE = '#F2EEE6', '#FFFFFF'

def court(color, op=0.14, w=4):
    s = 21.6; base = 1350; cx = 540
    by = base - 5.25 * s; ky = base - 19 * s; kx0, kx1 = cx - 8 * s, cx + 8 * s
    r3 = 23.75 * s; c3 = 22 * s; y3 = by - math.sqrt(r3**2 - c3**2); ft = 6 * s
    g = f'<g stroke="{color}" stroke-opacity="{op}" stroke-width="{w}">'
    g += f'<path d="M{kx0:.1f} {base} V{ky:.1f} H{kx1:.1f} V{base}"></path>'
    g += f'<path d="M{cx-ft:.1f} {ky:.1f} A{ft:.1f} {ft:.1f} 0 0 1 {cx+ft:.1f} {ky:.1f}"></path>'
    g += f'<path d="M{cx-c3:.1f} {base} V{y3:.1f} A{r3:.1f} {r3:.1f} 0 0 1 {cx+c3:.1f} {y3:.1f} V{base}"></path>'
    g += f'<circle cx="{cx}" cy="{by:.1f}" r="{0.75*s:.1f}"></circle></g>'
    return g

def pick_text(bg, candidates, need):
    for c in candidates:
        if cr(bg, c) >= need: return c
    return max([IV, WHITE, '#111214'], key=lambda c: cr(bg, c))

def match(fname, m):
    bg = m['home_bg']
    big = pick_text(bg, [m['home_sec'], IV, WHITE], 3.0)      # very large type: WCAG large-text threshold
    small = pick_text(bg, [IV, WHITE, '#111214'], 3.0)         # all small text is >= 24px
    accent = m['home_sec']                                    # rules, bars: decorative
    size = min(fit(m['home'].upper())[0], fit(m['away'].upper())[0], 172)
    b = []
    b.append(rule(accent, 6))
    b.append(f'<div style="display: flex; justify-content: space-between; align-items: baseline; font-family: \'IBM Plex Mono\', monospace; font-size: 24px; letter-spacing: 2px; color: {small}">'
             f'<span style="font-family: \'Barlow Condensed\', sans-serif; font-weight: 800; font-size: 34px; letter-spacing: 6px">PICK &amp; WATCH</span><span>{m["counter"]}</span></div>')
    b.append(rule(small, 2))
    b.append(mono(m['label'], big, 28, 5))
    b.append(mono(m['home_city'], small, 24, 4))
    b.append(line(m['home'].upper(), size=size, color=big, lh=0.84))
    b.append(f'<div style="display: flex; align-items: center; gap: 24px"><div style="flex: 1; height: 2px; background: {small}; opacity: 0.5"></div>'
             f'<span style="font-family: \'Barlow Condensed\', sans-serif; font-weight: 800; font-size: 40px; letter-spacing: 6px; color: {small}">CONTRE</span>'
             f'<div style="flex: 1; height: 2px; background: {small}; opacity: 0.5"></div></div>')
    b.append(line(m['away'].upper(), size=size, color=big, lh=0.84))
    b.append(f'<div style="display: flex; justify-content: center; align-items: center; gap: 18px; font-family: \'IBM Plex Mono\', monospace; font-size: 24px; letter-spacing: 4px; color: {small}">'
             f'<span style="display: flex; gap: 4px"><span style="width: 44px; height: 12px; background: {m["away_c1"]}; outline: 2px solid {small}"></span><span style="width: 44px; height: 12px; background: {m["away_c2"]}; outline: 2px solid {small}"></span></span>'
             f'<span>{m["away_city"]}</span></div>')
    b.append(rule(small, 2))
    b.append(f'<div style="display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); color: {small}">'
             f'<div style="display: flex; flex-direction: column; gap: 6px; border-right: 2px solid {small}; padding-right: 24px">'
             f'<div style="font-family: \'IBM Plex Mono\', monospace; font-size: 24px; letter-spacing: 2px">COUP D\'ENVOI</div>'
             f'<div style="font-family: \'Barlow Condensed\', sans-serif; font-weight: 800; font-size: 84px; line-height: 1; color: {big}">{m["time"]}</div>'
             f'<div style="font-family: \'IBM Plex Mono\', monospace; font-size: 24px">{m["venue"]}</div></div>'
             f'<div style="display: flex; flex-direction: column; gap: 6px; padding-left: 32px">'
             f'<div style="font-family: \'IBM Plex Mono\', monospace; font-size: 24px; letter-spacing: 2px">OÙ REGARDER</div>'
             f'<div style="font-family: \'Barlow Condensed\', sans-serif; font-weight: 800; font-size: 64px; line-height: 1.05; color: {big}">{m["channel"]}</div>'
             f'<div style="font-family: \'IBM Plex Mono\', monospace; font-size: 24px; letter-spacing: 1px">{m["mode"]}</div></div></div>')
    b.append(rule(small, 2))
    b.append(f'<div style="font-size: 29px; line-height: 1.42; color: {small}">{H.escape(m["brief"])}</div>')
    chips = ''.join(f'<span style="border: 2px solid {small}; padding: 6px 14px">{H.escape(c)}</span>' for c in m['chips'])
    b.append(f'<div style="display: flex; flex-wrap: wrap; gap: 12px; align-items: center; font-family: \'IBM Plex Mono\', monospace; font-size: 24px; color: {small}">'
             f'<span style="letter-spacing: 2px; margin-right: 6px">À SUIVRE</span>{chips}</div>')
    b.append(f'<div style="margin-top: auto; display: flex; justify-content: space-between; align-items: flex-end; gap: 24px; color: {small}">'
             f'<span style="font-family: \'Barlow Condensed\', sans-serif; font-weight: 800; font-size: 34px; letter-spacing: 1px">LE PROGRAMME COMPLET · PICKANDWATCH.FR</span>'
             f'<span style="font-family: \'IBM Plex Mono\', monospace; font-size: 24px; text-align: right">{m["foot"]}</span></div>')
    svg = (f'<svg width="1080" height="1350" viewBox="0 0 1080 1350" fill="none" aria-hidden="true" style="position: absolute; left: 0; top: 0; z-index: -1; pointer-events: none">'
           + court(big) + '</svg>')
    inner = '\n  '.join(b)
    out = f'''<!doctype html>
<html lang="fr">
<head>
<meta charset="utf-8">
<title>Pick &amp; Watch · {m["home"]} – {m["away"]}</title>
<script src="./support.js"></script>
</head>
<body>
<x-dc>
<helmet>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Barlow+Condensed:wght@600;800&amp;family=IBM+Plex+Mono:wght@400;500&amp;family=Source+Serif+4:ital,wght@0,400;0,600;1,400&amp;display=swap" rel="stylesheet">
<style>
body{{margin:0}}
</style>
</helmet>
<div style="position: relative; isolation: isolate; overflow: hidden; width: 1080px; height: 1350px; box-sizing: border-box; padding: 64px 72px 60px; background: {bg}; color: {small}; display: flex; flex-direction: column; gap: 20px; font-family: 'Source Serif 4', Georgia, serif">
  {svg}
  {inner}
</div>
</x-dc>
<script type="text/x-dc" data-dc-script data-props='{{"$preview":{{"width":1080,"height":1350}}}}'>
class Component extends DCLogic {{
  renderVals() {{
    return {{}};
  }}
}}
</script>
</body>
</html>
'''
    (OUT / fname).write_text(out)
    print(fname, 'big', big, round(cr(bg, big), 2), 'small', small, round(cr(bg, small), 2), 'size', size)

