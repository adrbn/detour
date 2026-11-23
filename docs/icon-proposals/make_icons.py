"""Liquid Glass icon concepts for Detour. Each concept is a background + glass layers, so the
chosen one can be rebuilt in Icon Composer from its layers."""
import pathlib

SQUIRCLE = "M230,0 H794 C934,0 1024,90 1024,230 V794 C1024,934 934,1024 794,1024 H230 C90,1024 0,934 0,794 V230 C0,90 90,0 230,0 Z"

DEFS = """
<defs>
  <clipPath id="sq"><path d="{sq}"/></clipPath>
  <linearGradient id="glass" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="#fff" stop-opacity=".95"/><stop offset="1" stop-color="#fff" stop-opacity=".55"/>
  </linearGradient>
  <linearGradient id="rim" x1="0" y1="0" x2="1" y2="1">
    <stop offset="0" stop-color="#fff" stop-opacity="1"/><stop offset=".5" stop-color="#fff" stop-opacity=".15"/><stop offset="1" stop-color="#fff" stop-opacity=".7"/>
  </linearGradient>
  <filter id="shadow" x="-30%" y="-30%" width="160%" height="160%">
    <feGaussianBlur in="SourceAlpha" stdDeviation="22"/><feOffset dy="26"/>
    <feComponentTransfer><feFuncA type="linear" slope=".28"/></feComponentTransfer>
    <feMerge><feMergeNode/><feMergeNode in="SourceGraphic"/></feMerge>
  </filter>
  <radialGradient id="sheen" cx=".3" cy=".1" r=".9">
    <stop offset="0" stop-color="#fff" stop-opacity=".45"/><stop offset=".6" stop-color="#fff" stop-opacity="0"/>
  </radialGradient>
  {bg}
</defs>""".replace("{sq}", SQUIRCLE)

def icon(bg_stops, body):
    bg = '<linearGradient id="bg" x1="0" y1="0" x2="0" y2="1">' + "".join(
        f'<stop offset="{o}" stop-color="{c}"/>' for o, c in bg_stops) + "</linearGradient>"
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1024 1024" width="1024" height="1024">
{DEFS.replace("{bg}", bg)}
<g transform="translate(100 100) scale(0.8047)">
<g clip-path="url(#sq)">
  <rect width="1024" height="1024" fill="url(#bg)"/>
  <rect width="1024" height="1024" fill="url(#sheen)"/>
  {body}
</g>
<path d="{SQUIRCLE}" fill="none" stroke="#fff" stroke-opacity=".35" stroke-width="4"/>
</g>
</svg>"""

def glass(d, width=None, fill=True):
    """One glass element: soft body + bright rim, with a drop shadow."""
    if fill:
        return (f'<g filter="url(#shadow)"><path d="{d}" fill="url(#glass)"/>'
                f'<path d="{d}" fill="none" stroke="url(#rim)" stroke-width="6"/></g>')
    return (f'<g filter="url(#shadow)"><path d="{d}" fill="none" stroke="url(#glass)" stroke-width="{width}" stroke-linecap="round" stroke-linejoin="round"/>'
            f'<path d="{d}" fill="none" stroke="#fff" stroke-opacity=".9" stroke-width="5" stroke-linecap="round" transform="translate(0,-{width*0.28:.0f})"/></g>')

BLUE = [(0, "#3AA0FF"), (1, "#0A5BD8")]
INK = [(0, "#2C2C34"), (1, "#0E0E12")]
SUNSET = [(0, "#FF9F45"), (1, "#E2453B")]  # FL-ish warmth without copying FL's logo
MINT = [(0, "#5BE0C4"), (1, "#0F8F86")]

concepts = {
    # A: the route bends around a muted speaker dot and lands on the right
    "a-route": icon(BLUE,
        '<path d="M430 700 h50 l60 -50 v200 l-60 -50 h-50 Z" fill="#fff" fill-opacity=".28"/>'
        '<path d="M585 715 l70 70 M655 715 l-70 70" stroke="#fff" stroke-opacity=".45" stroke-width="20" stroke-linecap="round"/>'
        + glass("M230 820 C230 430 360 280 512 280 C680 280 790 420 790 640", width=92, fill=False)
        + glass("M710 620 L790 740 L870 620 Z")),
    # B: headphones in glass, a clean waveform passing between the cups
    "b-headphones": icon(INK,
        glass("M250 600 C250 390 370 260 512 260 C654 260 774 390 774 600", width=70, fill=False)
        + glass("M200 590 h120 a30 30 0 0 1 30 30 v170 a30 30 0 0 1 -30 30 h-90 a30 30 0 0 1 -30 -30 Z")
        + glass("M704 590 h120 v200 a30 30 0 0 1 -30 30 h-90 a30 30 0 0 1 -30 -30 v-170 a30 30 0 0 1 30 -30 Z")
        + '<path d="M380 700 q22 -70 44 0 t44 0 t44 0 t44 0 t44 0" fill="none" stroke="#3AA0FF" stroke-width="22" stroke-linecap="round"/>'),
    # C: a road from the source (top left) to the headphones (bottom right), the long way round
    "c-road": icon(SUNSET,
        glass("M300 300 C620 300 760 380 700 520 C640 660 300 560 330 700 C350 800 560 760 724 724", width=74, fill=False)
        + glass("M300 220 a80 80 0 1 1 0 160 a80 80 0 1 1 0 -160 Z")
        + glass("M724 644 a80 80 0 1 1 0 160 a80 80 0 1 1 0 -160 Z")
        + '<path d="M684 734 C684 690 702 668 724 668 C746 668 764 690 764 734" fill="none" stroke="#E2453B" stroke-width="12" stroke-linecap="round"/>'
        '<rect x="676" y="726" width="18" height="34" rx="7" fill="#E2453B"/><rect x="754" y="726" width="18" height="34" rx="7" fill="#E2453B"/>'),
    # D: a single glass "D" whose bowl is a headphone arc, a waveform inside
    "d-letter": icon(MINT,
        glass("M300 250 H500 C690 250 800 370 800 512 C800 654 690 774 500 774 H300 Z")
        + '<path d="M390 512 q30 -110 60 0 t60 0 t60 0 t60 0" fill="none" stroke="#0F8F86" stroke-width="26" stroke-linecap="round"/>'),
}

# FL Studio x AirPods: FL's codes (its orange, step-sequencer pads, a fruit leaf) with a generic
# stemmed earbud. No Image-Line logo, no Apple product drawing.
def earbud(dx=0, dy=0, k=1.0, mesh="#2b2b30"):
    head = "M330 300 C330 200 430 150 520 170 C620 192 660 280 640 360 C620 440 540 470 470 460 C390 450 330 390 330 300 Z"
    stem = "M548 420 C576 412 604 420 612 448 L640 760 C644 800 614 822 584 822 C556 822 534 804 532 772 L520 470 C518 444 528 426 548 420 Z"
    return (f'<g transform="translate({dx} {dy}) scale({k})">' + glass(stem) + glass(head)
            + f'<ellipse cx="372" cy="318" rx="20" ry="64" transform="rotate(-24 372 318)" fill="{mesh}" fill-opacity=".6"/></g>')

def pads(lit, y=850, color="#FF8A1F"):
    out = ""
    for i in range(4):
        x = 150 + i * 190
        on = i in lit
        out += (f'<g filter="url(#shadow)"><rect x="{x}" y="{y}" width="150" height="110" rx="26" '
                f'fill="{color if on else "#fff"}" fill-opacity="{1 if on else .18}"/>'
                f'<rect x="{x}" y="{y}" width="150" height="110" rx="26" fill="none" stroke="url(#rim)" stroke-width="5"/></g>')
    return out

FL_ORANGE = [(0, "#FFB13B"), (1, "#F2591C")]
FL_DARK = [(0, "#4A5058"), (1, "#22262B")]

concepts.update({
    # E: white glass earbud on FL orange
    "e-orange-bud": icon(FL_ORANGE, earbud(dx=20, dy=40)),
    # F: FL's dark UI grey, earbud above a row of step-sequencer pads (two lit orange)
    "f-step-bud": icon(FL_DARK, earbud(dx=70, dy=-10, k=0.92, mesh="#FF8A1F") + pads({0, 2}, y=830)),
    # G: the earbud grows a leaf like a fruit, on orange
    "g-fruit-bud": icon(FL_ORANGE,
        '<g filter="url(#shadow)"><path d="M560 210 C580 120 660 70 760 80 C750 170 680 230 560 210 Z" fill="#5BD15B"/>'
        '<path d="M560 210 C620 160 680 120 740 96" fill="none" stroke="#2E9E3E" stroke-width="10" stroke-linecap="round"/></g>'
        + earbud(dx=10, dy=70)),
})

if __name__ == "__main__":
    out = pathlib.Path(__file__).parent
    for name, svg in concepts.items():
        (out / f"{name}.svg").write_text(svg)
