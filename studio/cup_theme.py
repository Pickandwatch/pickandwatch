"""Charte « NBA Cup » : même mise en page et mêmes polices que la charte papier, en version nuit
(fond encre, texte ivoire) avec l'or du trophée à la place de l'orange, et un motif de tableau à
élimination directe à la place du ballon. Appliquée aux visuels des soirs et matins de NBA Cup."""

INK, PAPER, OR_, GOLD = '#111214', '#F2EEE6', '#F06A2F', '#E9B949'
SUB_NUIT = '#B4AC9F'

# Tableau à élimination : 4 → 2 → 1, en bas à droite, or discret.
BRACKET = ('<g stroke="#E9B949" stroke-opacity="0.22" stroke-width="5" fill="none">'
           '<path d="M760 980 H860 V1060 H760 M760 1140 H860 V1220 H760 M860 1020 H940 V1180 H860 M940 1100 H1050"></path>'
           '<path d="M30 300 H110 M30 380 H110 M110 300 V380"></path></g>')


def cupify(html: str) -> str:
    h = html.replace(INK, '@@INK@@').replace(PAPER, INK).replace('@@INK@@', PAPER)
    h = h.replace('#5C5850', SUB_NUIT).replace('rgba(17,18,20,0.18)', 'rgba(242,238,230,0.22)')
    h = h.replace(OR_, GOLD).replace('#F06A2F'.lower(), GOLD)
    h = h.replace('stroke="#E9B949" stroke-opacity="0.22" stroke-width="6"', 'stroke="#E9B949" stroke-opacity="0.10" stroke-width="6"')
    h = h.replace('</svg>', BRACKET + '</svg>', 1)
    return h
