"""Second round on concept G (the earbud as a fruit): finer glass, four directions."""
import pathlib, make_icons as base

SOFT = '<filter id="soft" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="10"/></filter>'
EXTRA = SOFT + """
<linearGradient id="shade" x1="0" y1="0" x2="0" y2="1"><stop offset=".45" stop-color="#000" stop-opacity="0"/><stop offset="1" stop-color="#000" stop-opacity=".16"/></linearGradient>
<radialGradient id="orangeFruit" cx=".38" cy=".3" r=".8"><stop offset="0" stop-color="#FFC56A"/><stop offset=".55" stop-color="#FF8A1F"/><stop offset="1" stop-color="#D9480F"/></radialGradient>
<linearGradient id="leaf" x1="0" y1="1" x2="1" y2="0"><stop offset="0" stop-color="#2FA84F"/><stop offset="1" stop-color="#8BE36B"/></linearGradient>
<linearGradient id="pod" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#ffffff"/><stop offset="1" stop-color="#E6E8EC"/></linearGradient>
"""

HEAD = "M330 300 C330 200 430 150 520 170 C620 192 660 280 640 360 C620 440 540 470 470 460 C390 450 330 390 330 300 Z"
STEM = "M548 420 C576 412 604 420 612 448 L640 760 C644 800 614 822 584 822 C556 822 534 804 532 772 L520 470 C518 444 528 426 548 420 Z"

def part(d, fill="url(#pod)", opacity=1):
    """Solid glass part: body, bottom shading, bright rim, with the drop shadow."""
    return (f'<g filter="url(#shadow)"><path d="{d}" fill="{fill}" fill-opacity="{opacity}"/>'
            f'<path d="{d}" fill="url(#shade)"/>'
            f'<path d="{d}" fill="none" stroke="url(#rim)" stroke-width="6"/></g>')

def bud(transform="", head_fill="url(#pod)", fruit=False):
    hl = ('<ellipse cx="440" cy="225" rx="78" ry="34" transform="rotate(-18 440 225)" fill="#fff" '
          'fill-opacity=".85" filter="url(#soft)"/>')
    mesh = '' if fruit else ('<ellipse cx="372" cy="318" rx="20" ry="64" transform="rotate(-24 372 318)" '
                             'fill="#2b2b30" fill-opacity=".55"/>')
    peel = ''.join(f'<circle cx="{x}" cy="{y}" r="5" fill="#B9400C" fill-opacity=".35"/>'
                   for x, y in [(420, 330), (470, 380), (540, 350), (500, 300), (580, 300), (450, 420), (560, 410)]) if fruit else ''
    return (f'<g transform="{transform}">' + part(STEM) + part(HEAD, head_fill) + peel + mesh + hl
            + '<path d="M566 470 L600 780" stroke="#fff" stroke-opacity=".7" stroke-width="8" stroke-linecap="round" filter="url(#soft)"/></g>')

def leaf(x, y, k=1.0, rot=0):
    return (f'<g transform="translate({x} {y}) rotate({rot}) scale({k})" filter="url(#shadow)">'
            '<path d="M0 0 C30 -90 120 -140 230 -120 C210 -20 120 30 0 0 Z" fill="url(#leaf)"/>'
            '<path d="M0 0 C70 -40 140 -80 210 -112" fill="none" stroke="#1F7A3A" stroke-opacity=".6" stroke-width="9" stroke-linecap="round"/>'
            '<path d="M0 0 C30 -90 120 -140 230 -120" fill="none" stroke="#fff" stroke-opacity=".5" stroke-width="5"/></g>')

def stalk(d):
    return f'<path d="{d}" fill="none" stroke="#7A4A22" stroke-width="22" stroke-linecap="round" filter="url(#shadow)"/>'

def hang(jx, jy, angle, k):
    """Earbud hanging from its stem tip like a cherry: stem tip at (jx, jy), head below."""
    return f"translate({jx} {jy}) rotate({180 + angle}) scale({k}) translate(-586 -822)"

ORANGE = [(0, "#FFB13B"), (1, "#F2591C")]
DARK = [(0, "#4A5058"), (1, "#1E2226")]

def fit(body, cy, k):
    """Scale the drawing by k around its visual centre cy and put that centre in the middle."""
    return f'<g transform="translate(512 525) scale({k}) translate(-512 -{cy})">{body}</g>'

def icon(bg, body):
    return base.icon(bg, body).replace("</defs>", EXTRA + "</defs>")

concepts = {
    # G1: the original idea, finer: a stalk grows from the top of the earbud, leaf attached to it
    "g1-sprout": icon(ORANGE, fit(stalk("M560 190 C566 150 580 120 600 100")
                      + leaf(596, 108, 0.9, 8) + bud("translate(20 60)"), 490, 0.86)),
    # G2: the earbud's head is an orange fruit, white stem, on FL's dark grey
    "g2-orange-pod": icon(DARK, fit(stalk("M500 175 C504 140 516 112 534 92")
                          + leaf(530, 100, 0.85, 4) + bud("translate(0 50)", "url(#orangeFruit)", fruit=True), 480, 0.86)),
    # G3: a pair of earbuds hanging like cherries from one stalk, on orange
    "g3-cherries": icon(ORANGE, fit(stalk("M512 200 C520 160 540 130 566 112")
                        + leaf(560, 120, 0.8, 0)
                        + bud(hang(500, 205, 24, 0.66)) + bud(hang(524, 205, -24, 0.66)), 380, 1.18)),
    # G4: the cherries on FL's dark grey
    "g4-cherries-dark": icon(DARK, fit(stalk("M512 200 C520 160 540 130 566 112")
                             + leaf(560, 120, 0.8, 0)
                             + bud(hang(500, 205, 24, 0.66)) + bud(hang(524, 205, -24, 0.66)), 380, 1.18)),
}
out = pathlib.Path(__file__).parent
for name, svg in concepts.items():
    (out / f"{name}.svg").write_text(svg)
