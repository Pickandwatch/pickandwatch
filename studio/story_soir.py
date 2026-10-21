"""Story Instagram du soir : les visuels du carrousel de la nuit D, publiés aussi en story.

Usage : python studio/story_soir.py AAAA-MM-JJ
Lit posts/<D>/post.json (le carrousel) et ses images 1080x1350. Chaque image est posée au centre
d'un fond 1080x1920 de sa propre couleur de fond : le visuel est identique, sans recadrage, et
tient dans la zone que l'interface d'Instagram ne couvre pas (250 à 1640 px).
Écrit posts/<D>-story/0N.jpg et post.json (type « story », même heure et même statut que le
carrousel, champ « suit » = <D>). À relancer après toute correction d'image du carrousel.
Le robot ne publie pas la story si le carrousel est annulé (pipeline.instagram).
"""
from __future__ import annotations

import json
import pathlib
import sys

from PIL import Image

ROOT = pathlib.Path(__file__).resolve().parent.parent
W, H = 1080, 1920
SAFE_TOP, SAFE_BOTTOM = 250, 1640


def main(night: str) -> int:
    src = ROOT / "posts" / night
    post = json.loads((src / "post.json").read_text(encoding="utf-8"))
    out = ROOT / "posts" / f"{night}-story"
    out.mkdir(exist_ok=True)
    for old in out.glob("*.jpg"):
        old.unlink()
    names = []
    for i, name in enumerate(post["images"], 1):
        img = Image.open(src / name).convert("RGB")
        if img.width != W:
            img = img.resize((W, round(img.height * W / img.width)), Image.LANCZOS)
        top = (H - img.height) // 2
        if top < SAFE_TOP or top + img.height > SAFE_BOTTOM:
            print(f"ATTENTION {name} : {img.height} px de haut, sort de la zone sûre de la story")
        canvas = Image.new("RGB", (W, H), img.getpixel((4, 4)))  # couleur du bord de la slide
        canvas.paste(img, (0, top))
        n = f"{i:02d}.jpg"
        canvas.save(out / n, quality=92, optimize=True)
        names.append(n)
    f = out / "post.json"
    story = json.loads(f.read_text(encoding="utf-8")) if f.exists() else {}
    if story.get("statut") == "publie":
        print("Story déjà publiée : images refaites, post.json laissé tel quel.")
        return 0
    story = {"type": "story", "suit": night, "publier_a": post["publier_a"],
             "statut": post["statut"] if post.get("statut") in ("valide", "annule") else "propose", "images": names, "legende": ""}
    f.write_text(json.dumps(story, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"{len(names)} stories dans {out} ({story['statut']}, {story['publier_a']})")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1]))
