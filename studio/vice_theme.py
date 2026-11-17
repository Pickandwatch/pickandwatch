"""Charte « Vice City » (GTA VI × NBA, novembre 2026) : la mise en page papier en version nuit,
violet profond, texte ivoire, rose néon à la place de l'orange et une touche de turquoise.
Couleurs seulement : aucun logo ni visuel du jeu."""

INK, PAPER, OR_ = '#111214', '#F2EEE6', '#F06A2F'
NUIT, ROSE, TURQ, SUB = '#1A1030', '#FF4FA3', '#3FE0D0', '#B9A9CF'

# Soleil couchant au trait, en bas à droite.
SOLEIL = ('<g fill="none" stroke-width="5">'
          '<path d="M800 1240 A180 180 0 0 1 1080 1240" stroke="#FF4FA3" stroke-opacity="0.35"></path>'
          '<path d="M840 1240 A140 140 0 0 1 1040 1240" stroke="#3FE0D0" stroke-opacity="0.25"></path>'
          '<path d="M790 1270 H1080 M820 1295 H1080" stroke="#FF4FA3" stroke-opacity="0.2"></path></g>')


def vicify(html: str) -> str:
    h = html.replace(INK, '@@INK@@').replace(PAPER, NUIT).replace('@@INK@@', PAPER)
    h = h.replace('#5C5850', SUB).replace('rgba(17,18,20,0.18)', 'rgba(255,79,163,0.25)')
    h = h.replace(OR_, ROSE).replace(OR_.lower(), ROSE)
    if '</svg>' in h:
        h = h.replace('</svg>', SOLEIL + '</svg>', 1)
    return h
