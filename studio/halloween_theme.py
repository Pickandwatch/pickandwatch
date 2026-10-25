"""Petit thème Halloween (nuit du 31 octobre) : chauves-souris en vol en haut à droite et une
citrouille en bas à gauche, ajoutées par-dessus n'importe quel visuel (carrousel, story),
sans toucher à la charte ni au contenu. Le bandeau « NUIT D'HALLOWEEN » est ajouté sur la couverture."""

BAT = ("M0 0 C6 -6 12 -6 16 -2 C18 -6 21 -8 24 -8 C22 -5 22 -3 24 0 C27 -3 31 -3 34 0 "
       "C31 2 29 5 29 9 C26 6 22 6 19 9 C18 6 17 4 16 4 C15 4 14 6 13 9 C10 6 6 6 3 9 "
       "C3 5 1 2 -2 0 C1 -3 5 -3 8 0 C10 -3 10 -5 8 -8 C11 -8 14 -6 16 -2")


def _bats(w: int, color: str, k: float = 1.0, y0: int = 0) -> str:
    # par défaut dans la marge du haut (0-70 px), là où il n'y a jamais de texte
    spots = [(w - 340, 38, 2.0, -8), (w - 235, 16, 1.5, 10), (w - 150, 44, 1.7, -4), (w - 450, 14, 1.2, 14), (190, 26, 1.4, 6)]
    return "".join(f'<path d="{BAT}" transform="translate({x} {y0 + y * k}) rotate({r}) scale({s * k})" fill="{color}"></path>'
                   for x, y, s, r in spots)


def _pumpkin(x: int, y: int) -> str:
    return (f'<g transform="translate({x} {y})">'
            '<ellipse cx="0" cy="0" rx="46" ry="38" fill="#F06A2F"></ellipse>'
            '<ellipse cx="-22" cy="2" rx="22" ry="34" fill="#E05A20"></ellipse>'
            '<ellipse cx="22" cy="2" rx="22" ry="34" fill="#E05A20"></ellipse>'
            '<ellipse cx="0" cy="0" rx="16" ry="38" fill="#F06A2F"></ellipse>'
            '<rect x="-5" y="-50" width="10" height="16" rx="3" fill="#3A5A2A"></rect>'
            '<path d="M-22 -8 L-12 -16 L-6 -6 Z M22 -8 L12 -16 L6 -6 Z" fill="#111214"></path>'
            '<path d="M-24 10 Q0 30 24 10 L16 14 L8 8 L0 16 L-8 8 L-16 14 Z" fill="#111214"></path></g>')


def halloweenify(html: str, w: int = 1080, h: int = 1350, dark: bool = False, story: bool = False) -> str:
    color = "rgba(242,238,230,0.6)" if dark else "rgba(17,18,20,0.6)"
    if story:  # story 1080x1920 : grandes marges libres en haut (0-250) et en bas (1640-1920)
        bats, pk = _bats(w, color, 2.4, 40), f'<g transform="translate({w // 2} {h - 150}) scale(1.3)">{_pumpkin(0, 0)}</g>'
    else:
        bats, pk = _bats(w, color), f'<g transform="translate({w - 46} {h - 30}) scale(0.5)">{_pumpkin(0, 0)}</g>'
    deco = (f'<svg width="{w}" height="{h}" viewBox="0 0 {w} {h}" fill="none" '
            f'style="position: absolute; left: 0; top: 0; z-index: 3; pointer-events: none">{bats}{pk}</svg>')
    # dans le cadre principal du visuel (premier <div style="position: relative; isolation: isolate; …">)
    i = html.find('isolation: isolate')
    if i < 0:
        return html
    j = html.find('>', i) + 1
    return html[:j] + deco + html[j:]
