"""Reel « Les matchs à ne pas rater cette semaine » (charte « papier »), 1080x1920, ~17 s.

Usage : python studio/reel_semaine.py chemin/spec.json
Produit reel.mp4 (H.264 + piste audio muette, 30 i/s) et cover.jpg dans le dossier du spec.
Spec : {"semaine": "DU 26 OCT. AU 1ER NOV.", "matchs": [{"quand": "MARDI · 1H00", "equipes": "KNICKS – PISTONS",
        "chaine": "beIN SPORTS 1", "plus": "Différé mercredi 9h15", "enjeu": "…", "etoiles": 3}], "fin": "…"}
"""
import json, subprocess, sys, tempfile, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from gen import line
from hors_parquet import BAR, MONO, INK, OR, SUB, BG
from carrousel import FONTS

W, H = 1080, 1920
SVG = (f'<svg width="{W}" height="{H}" viewBox="0 0 {W} {H}" fill="none" style="position: absolute; left: 0; top: 0; z-index: -1">'
       f'<rect x="30" y="30" width="{W-60}" height="{H-60}" stroke="rgba(17,18,20,0.18)" stroke-width="4"></rect>'
       '<g transform="rotate(-24 1010 150)" stroke="#F06A2F" stroke-opacity="0.16" stroke-width="6"><circle cx="1010" cy="150" r="470"></circle>'
       '<path d="M1010 -320 V620"></path><path d="M540 150 H1480"></path></g></svg>')


def page(inner):
    # Zone utile 1080x1420 centrée : Instagram recouvre le haut et le bas d'un Reel (interface).
    return (f'<html><head><meta charset="utf-8">{FONTS}<style>body{{margin:0}}</style></head><body>'
            f'<div style="position: relative; isolation: isolate; overflow: hidden; width: {W}px; height: {H}px; box-sizing: border-box; '
            f'padding: 250px 72px 270px; background: {BG}; color: {INK}; display: flex; flex-direction: column; justify-content: center; gap: 46px; '
            f"font-family: 'Source Serif 4', Georgia, serif\">{SVG}{inner}</div></body></html>")


def head(txt):
    return (f'<div style="position: relative; display: flex; align-items: center"><div style="position: absolute; left: 0; right: 0; top: 50%; height: 6px; margin-top: -3px; background: {OR}"></div>'
            f'<span style="position: relative; background: {BG}; padding-right: 22px; {BAR}; font-size: 44px; letter-spacing: 7px">PICK &amp; WATCH</span>'
            f'<span style="position: relative; background: {BG}; padding-left: 18px; margin-left: auto; {MONO}; font-size: 24px; letter-spacing: 3px; color: {SUB}">{txt}</span></div>')


def ouverture(s, n):
    return page(head('CETTE SEMAINE') + f'<div style="display: flex; flex-direction: column; gap: 18px">{line(f"{n} MATCHS", color=OR)}{line("À NE PAS RATER", color=INK)}</div>'
                + f'<div style="{MONO}; font-size: 30px; letter-spacing: 4px; text-align: center; color: {SUB}; padding: 18px 0; border-top: 2px solid {INK}; border-bottom: 2px solid {INK}">{s["semaine"]} · HEURE DE PARIS</div>'
                + f'<div style="font-size: 40px; font-style: italic; text-align: center; color: {SUB}">Notre sélection, sans spoiler.</div>')


def match(m, i, n):
    stars = f'<span style="color: {OR}">{"★" * m["etoiles"]}</span><span style="color: rgba(17,18,20,0.18)">{"★" * (3 - m["etoiles"])}</span>'
    plus = f'<div style="{MONO}; font-size: 28px; color: {SUB}; margin-top: 10px">{m["plus"]}</div>' if m.get('plus') else ''
    return page(head(f'{i}/{n}')
                + f'<div style="font-size: 120px; letter-spacing: 8px; line-height: 0.8; text-align: center">{stars}</div>'
                + f'<div style="display: flex; flex-direction: column; gap: 16px">{line(m["quand"], color=OR)}{line(m["equipes"], color=INK)}</div>'
                + f'<div style="border: 3px solid {OR}; padding: 22px 30px"><div style="{MONO}; font-size: 24px; letter-spacing: 3px; color: {SUB}">OÙ REGARDER</div>'
                  f'<div style="{BAR}; font-size: 64px; line-height: 1.05; margin-top: 6px">{m["chaine"]}</div>{plus}</div>'
                + f'<div style="font-size: 50px; line-height: 1.32">{m["enjeu"]}</div>')


def fin(s):
    return page(head('CHAQUE JOUR') + f'<div style="display: flex; flex-direction: column; gap: 18px">{line("LE PROGRAMME", color=OR)}{line("CHAQUE SOIR À 19H.", color=INK)}</div>'
                + f'<div style="font-size: 46px; line-height: 1.4">{s["fin"]}</div>'
                + f'<div style="border: 3px solid {OR}; padding: 24px 30px; display: flex; justify-content: space-between; align-items: center">'
                  f'<span style="{BAR}; font-size: 60px">@pickandwatch.fr</span><span style="{BAR}; font-size: 44px; color: {OR}">SUIS-NOUS</span></div>')


def main(spec_path):
    from playwright.sync_api import sync_playwright
    spec_path = pathlib.Path(spec_path); out = spec_path.parent; spec = json.loads(spec_path.read_text())
    ms = spec['matchs']; tmp = pathlib.Path(tempfile.mkdtemp())
    pages = [ouverture(spec, len(ms))] + [match(m, i, len(ms)) for i, m in enumerate(ms, 1)] + [fin(spec)]
    durees = [3.0] + [4.0] * len(ms) + [3.5]
    pngs, problems = [], []
    with sync_playwright() as p:
        b = p.chromium.launch(); pg = b.new_page(viewport={'width': W, 'height': H})
        for k, html in enumerate(pages):
            h = tmp / f'f{k}.html'; h.write_text(html)
            pg.goto(f'file://{h}'); pg.wait_for_load_state('networkidle'); pg.evaluate('document.fonts.ready'); pg.wait_for_timeout(600)
            over = pg.evaluate("""() => { const r=[]; document.querySelectorAll('body > div *').forEach(el=>{ if(el.closest('svg')) return;
                if(el.scrollWidth>el.clientWidth+1 && getComputedStyle(el).whiteSpace==='nowrap') r.push((el.textContent||'').slice(0,40));
                const bb=el.getBoundingClientRect(); if(bb.height && (bb.top<220 || bb.bottom>1680)) r.push('hors zone utile : '+(el.textContent||'').slice(0,40)); }); return r; }""")
            problems += [f'image {k} : {o}' for o in over]
            png = tmp / f'f{k}.png'; pg.screenshot(path=str(png)); pngs.append(png)
        b.close()
    # Fondu de 0,4 s entre images, léger zoom avant sur chacune.
    T = 0.4; inputs, filt = [], []
    for k, (png, d) in enumerate(zip(pngs, durees)):
        inputs += ['-loop', '1', '-t', str(d + T), '-i', str(png)]
        filt.append(f'[{k}:v]scale={W*2}:-1,zoompan=z=\'min(zoom+0.0006,1.04)\':x=\'iw/2-(iw/zoom/2)\':y=\'ih/2-(ih/zoom/2)\':d={int((d+T)*30)}:s={W}x{H}:fps=30,setsar=1[v{k}]')
    prev, off = 'v0', 0.0
    for k in range(1, len(pngs)):
        off += durees[k - 1]
        filt.append(f'[{prev}][v{k}]xfade=transition=fade:duration={T}:offset={off:.2f}[x{k}]'); prev = f'x{k}'
    total = sum(durees) + T
    cmd = ['ffmpeg', '-y', '-loglevel', 'error', *inputs, '-f', 'lavfi', '-t', f'{total:.2f}', '-i', 'anullsrc=r=44100:cl=stereo',
           '-filter_complex', ';'.join(filt), '-map', f'[{prev}]', '-map', f'{len(pngs)}:a', '-c:v', 'libx264', '-pix_fmt', 'yuv420p',
           '-profile:v', 'high', '-r', '30', '-b:v', '6M', '-c:a', 'aac', '-b:a', '128k', '-shortest', '-movflags', '+faststart', str(out / 'reel.mp4')]
    subprocess.run(cmd, check=True)
    from PIL import Image
    Image.open(pngs[0]).convert('RGB').save(out / 'cover.jpg', quality=92)
    print(f'reel.mp4 ({total:.1f} s) et cover.jpg dans {out}')
    for pr in problems: print('ATTENTION', pr)
    return 1 if problems else 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1]))
