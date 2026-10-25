"""Édition Halloween (nuit du 31 octobre), version 2 : sobre et éditoriale, dans l'esprit des
motifs au trait de la charte (ballon, terrain). Pas de clip-art.

- Couvertures (programme du soir, récapitulatif des verdicts) : version nuit de la charte (fond encre,
  texte ivoire), l'orange de la marque gardé comme seule couleur — c'est déjà l'orange citrouille —,
  une toile d'araignée et un croissant de lune dessinés au trait fin, et la mention
  « ÉDITION HALLOWEEN · 31.10 ».
- Slides de match (couleurs des équipes) et cartes de verdict : seulement la toile au trait, très
  discrète, dans le coin haut droit.
"""
import math

INK, PAPER, SUB = '#111214', '#F2EEE6', '#5C5850'


def web(cx: float, cy: float, r: float, a0: float, a1: float, color: str, op: float, sw: float = 3) -> str:
    """Toile d'araignée au trait, ancrée dans un coin : rayons + fils qui pendent entre les rayons."""
    n, rings = 7, 6
    angs = [math.radians(a0 + (a1 - a0) * k / (n - 1)) for k in range(n)]
    p = [f'M{cx:.0f} {cy:.0f} L{cx + r * math.cos(a):.0f} {cy + r * math.sin(a):.0f}' for a in angs]
    for j in range(1, rings + 1):
        rr = r * j / (rings + 0.6)
        pts = [(cx + rr * math.cos(a), cy + rr * math.sin(a)) for a in angs]
        d = f'M{pts[0][0]:.0f} {pts[0][1]:.0f}'
        for (x1, y1), (x2, y2) in zip(pts, pts[1:]):
            mx, my = (x1 + x2) / 2, (y1 + y2) / 2
            qx, qy = mx + (cx - mx) * 0.12, my + (cy - my) * 0.12   # le fil pend vers le centre
            d += f' Q{qx:.0f} {qy:.0f} {x2:.0f} {y2:.0f}'
        p.append(d)
    return (f'<g stroke="{color}" stroke-opacity="{op}" stroke-width="{sw}" fill="none" stroke-linecap="round">'
            + ''.join(f'<path d="{x}"></path>' for x in p) + '</g>')


def moon(cx: float, cy: float, r: float, color: str, op: float) -> str:
    """Croissant de lune au trait."""
    return (f'<g stroke="{color}" stroke-opacity="{op}" stroke-width="4" fill="none">'
            f'<path d="M{cx} {cy - r} A{r} {r} 0 1 0 {cx} {cy + r} A{r * 0.78:.0f} {r * 0.78:.0f} 0 1 1 {cx} {cy - r} Z"></path></g>')


def _overlay(html: str, svg: str) -> str:
    i = html.find('isolation: isolate')
    if i < 0:
        return html
    j = html.find('>', i) + 1
    return html[:j] + svg + html[j:]


def edition(html: str, w: int = 1080, h: int = 1350, cover: bool = False, story: bool = False, light: bool = False) -> str:
    if cover:
        # version nuit de la charte, l'orange reste l'orange
        html = html.replace(INK, '@@I@@').replace(PAPER, INK).replace('@@I@@', PAPER)
        html = html.replace(SUB, '#B4AC9F').replace('rgba(17,18,20,0.18)', 'rgba(242,238,230,0.22)')
        top = 250 if story else 0
        deco = (f'<svg width="{w}" height="{h}" viewBox="0 0 {w} {h}" fill="none" style="position: absolute; left: 0; top: 0; z-index: 0; pointer-events: none">'
                f'{web(w, top, 430, 90, 180, "#F06A2F", 0.30, 3)}{moon(150, top + 150 if story else 150, 70, "#F2EEE6", 0.22)}</svg>')
        tag = ('<div style="position: absolute; left: 0; right: 0; bottom: ' + ('200' if story else '46') + 'px; text-align: center; '
               "font-family: 'IBM Plex Mono', monospace; font-weight: 500; font-size: 20px; letter-spacing: 6px; color: #F06A2F; z-index: 2\">"
               'ÉDITION HALLOWEEN · 31.10</div>')
        return _overlay(html, deco + tag)
    color, op = ('#F06A2F', 0.35) if light else ('rgba(242,238,230,1)', 0.16)   # fond papier : toile orange
    deco = (f'<svg width="{w}" height="{h}" viewBox="0 0 {w} {h}" fill="none" style="position: absolute; left: 0; top: 0; z-index: 3; pointer-events: none">'
            f'{web(w, 0, 260, 90, 180, color, op, 2.5)}</svg>')
    return _overlay(html, deco)
