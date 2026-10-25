"""Reel tiré d'un carrousel : chaque slide (1080x1350) posée au centre d'un fond 1080x1920 de sa
couleur, 3,2 s par slide, fondu de 0,4 s, léger zoom. Piste audio muette (l'API ne permet pas
d'ajouter une musique de la bibliothèque Instagram).

Usage : python studio/reel_carrousel.py DOSSIER_DU_CARROUSEL DOSSIER_DU_REEL
Écrit DOSSIER_DU_REEL/reel.mp4 et cover.jpg (la première slide, en 1080x1920).
"""
import pathlib, subprocess, sys
from PIL import Image

W, H, D, T = 1080, 1920, 3.2, 0.4


def main(src, out):
    src, out = pathlib.Path(src), pathlib.Path(out); out.mkdir(parents=True, exist_ok=True)
    frames = []
    for i, f in enumerate(sorted(src.glob('0*.jpg')), 1):
        img = Image.open(f).convert('RGB')
        if img.width != W:
            img = img.resize((W, round(img.height * W / img.width)), Image.LANCZOS)
        canvas = Image.new('RGB', (W, H), img.getpixel((4, 4)))
        canvas.paste(img, (0, (H - img.height) // 2))
        p = out / f'_f{i}.png'; canvas.save(p); frames.append(p)
    if len(frames) < 2:
        raise SystemExit('Il faut au moins 2 slides.')
    durees = [D] * len(frames); durees[-1] = D + 0.8
    inputs, filt = [], []
    for k, (p, d) in enumerate(zip(frames, durees)):
        inputs += ['-loop', '1', '-t', str(d + T), '-i', str(p)]
        filt.append(f"[{k}:v]scale={W*2}:-1,zoompan=z='min(zoom+0.0005,1.03)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)'"
                    f":d={int((d+T)*30)}:s={W}x{H}:fps=30,setsar=1[v{k}]")
    prev, off = 'v0', 0.0
    for k in range(1, len(frames)):
        off += durees[k - 1]
        filt.append(f'[{prev}][v{k}]xfade=transition=fade:duration={T}:offset={off:.2f}[x{k}]'); prev = f'x{k}'
    total = sum(durees) + T
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', *inputs, '-f', 'lavfi', '-t', f'{total:.2f}', '-i', 'anullsrc=r=44100:cl=stereo',
                    '-filter_complex', ';'.join(filt), '-map', f'[{prev}]', '-map', f'{len(frames)}:a', '-c:v', 'libx264',
                    '-pix_fmt', 'yuv420p', '-profile:v', 'high', '-r', '30', '-b:v', '6M', '-c:a', 'aac', '-b:a', '128k',
                    '-shortest', '-movflags', '+faststart', str(out / 'reel.mp4')], check=True)
    Image.open(frames[0]).convert('RGB').save(out / 'cover.jpg', quality=92)
    for p in frames:
        p.unlink()
    print(f'reel.mp4 ({total:.1f} s) et cover.jpg dans {out}')


if __name__ == '__main__':
    main(*sys.argv[1:3])
