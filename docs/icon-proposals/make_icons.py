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

out = pathlib.Path(__file__).parent
for name, svg in concepts.items():
    (out / f"{name}.svg").write_text(svg)

cells = "".join(
    f'<figure><img src="{n}.svg"><figcaption>{n.split("-")[0].upper()} · {n.split("-",1)[1]}</figcaption></figure>'
    for n in concepts)
for theme, bg, fg in [("dark", "#1c1c1e", "#f5f5f7"), ("light", "#ffffff", "#1d1d1f")]:
    (out / f"sheet-{theme}.html").write_text(f"""<!doctype html><meta charset=utf-8>
<style>body{{margin:0;background:{bg};color:{fg};font:600 26px -apple-system,sans-serif;display:grid;
grid-template-columns:repeat(4,1fr);gap:40px;padding:60px}}figure{{margin:0;text-align:center}}
img{{width:100%}}figcaption{{margin-top:14px;opacity:.8}}
.small{{grid-column:1/-1;display:flex;gap:48px;justify-content:center;align-items:center}}
.small img{{width:64px}}.small img.s32{{width:32px}}</style>
{cells}<div class=small>{"".join(f'<img src="{n}.svg"><img class=s32 src="{n}.svg">' for n in concepts)}</div>""")
