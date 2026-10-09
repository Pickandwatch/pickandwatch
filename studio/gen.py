import pathlib
from PIL import ImageFont
D = pathlib.Path(__file__).resolve().parent
BAR = str(D / 'fonts/BarlowCondensed-ExtraBold.ttf')
MONO = str(D / 'fonts/IBMPlexMono-Medium.ttf')
W = 936 - 8   # slack for browser/PIL metric differences

def fit(text, size=None, font=BAR, target=W):
    """Return (size, letter_spacing) so that text spans target width."""
    import html as _h
    text = _h.unescape(text)
    if size is None:  # scale font to fill
        w = ImageFont.truetype(font, 100).getlength(text)
        size = int(100 * target / w)
        return size, 0.0
    w = ImageFont.truetype(font, size).getlength(text)
    n = len(text)
    return size, max(0.0, (target - w) / (n - 1))

def line(text, size=None, color='', lh=0.86, font=BAR, family="'Barlow Condensed', sans-serif", weight=800, extra=''):
    s, ls = fit(text, size, font)
    return (f'<div style="font-family: {family}; font-weight: {weight}; font-size: {s}px; line-height: {lh}; '
            f'letter-spacing: {ls:.2f}px; margin-right: -{ls:.2f}px; white-space: nowrap; text-align: center; color: {color}{extra}">{text}</div>')

def rule(color, h=2):
    return f'<div style="height: {h}px; background: {color}; flex-shrink: 0"></div>'

def mono(text, color, size=24, ls=3):
    return (f'<div style="font-family: \'IBM Plex Mono\', monospace; font-weight: 500; font-size: {size}px; letter-spacing: {ls}px; '
            f'text-align: center; white-space: nowrap; color: {color}">{text}</div>')

def poster(name, title, bg, ink, head, sub, frame):
    body = []
    body.append(rule(head, 6))
    body.append(line('CETTE NUIT EN NBA', color=ink, weight=800))
    body.append(rule(ink))
    body.append(mono('MERCREDI 7 OCTOBRE · HEURE DE PARIS', sub))
    body.append(rule(ink))
    body.append(mono('★★★ L\'IMMANQUABLE', head, 26, 6))
    ws, _ = fit('WARRIORS')
    body.append(line('WARRIORS', color=head, lh=0.84))
    body.append(line('LAKERS', size=ws, color=head, lh=0.84))
    body.append(mono('04:00 · SAN FRANCISCO · DIRECT beIN MAX 6 · DIFFÉRÉ MER. 11:00', sub, 22, 1))
    body.append(rule(ink))
    for t, info in [('THUNDER – PELICANS', '02:00 · TULSA (TERRAIN NEUTRE) · LEAGUE PASS* · ★★'),
                    ('JAZZ – NUGGETS', '03:00 · SALT LAKE CITY · LEAGUE PASS* · ★★'),
                    ('HORNETS – NETS', '01:00 · CHARLOTTE · LEAGUE PASS* · ★')]:
        body.append(line(t, size=78, color=ink))
        body.append(mono(info, sub, 22, 2))
    body.append(rule(ink))
    body.append(f'<div style="display: flex; justify-content: space-between; align-items: center; font-family: \'IBM Plex Mono\', monospace; font-size: 22px; letter-spacing: 2px; color: {sub}">'
                f'<span>PICKANDWATCH.FR · ZÉRO SPOILER</span><span style="font-family: \'Barlow Condensed\', sans-serif; font-weight: 800; font-size: 34px; letter-spacing: 2px; color: {head}">LES MATCHS EN DÉTAIL →</span></div>')
    inner = '\n  '.join(body)
    svg = (f'<svg width="1080" height="1350" viewBox="0 0 1080 1350" fill="none" aria-hidden="true" style="position: absolute; left: 0; top: 0; z-index: -1; pointer-events: none">'
           f'<rect x="30" y="30" width="1020" height="1290" stroke="{frame}" stroke-width="4"></rect></svg>')
    html = f'''<!doctype html>
<html lang="fr">
<head>
<meta charset="utf-8">
<title>{title}</title>
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
<div style="position: relative; isolation: isolate; overflow: hidden; width: 1080px; height: 1350px; box-sizing: border-box; padding: 72px; background: {bg}; color: {ink}; display: flex; flex-direction: column; justify-content: space-between; font-family: 'Source Serif 4', Georgia, serif">
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
    (D / 'tipoff/project' / f'{name}.dc.html').write_text(html)

if __name__ == '__main__':
    poster('PosterA', 'Affiche · charte', '#111214', '#F2EEE6', '#F06A2F', '#A39E94', 'rgba(242,238,230,0.14)')
    poster('PosterB', 'Affiche · papier', '#F2EEE6', '#111214', '#F06A2F', '#5C5850', 'rgba(17,18,20,0.18)')
    poster('PosterC', 'Affiche · couleurs du jour', '#1D428A', '#FFC72C', '#FFC72C', '#F2EEE6', 'rgba(255,199,44,0.35)')
    print('ok')
