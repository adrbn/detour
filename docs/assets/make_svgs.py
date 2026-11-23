"""Writes every SVG of the README: hero (dark + light), buttons and feature cards, in every language.

Stdlib only. Run from anywhere: python3 docs/assets/make_svgs.py
Real inputs live in readme-src/: the app icon rendered by Icon Composer, and samples of the
measured Detour output of a 1 kHz test tone. The texts drawn in the images are in i18n/<code>.json;
English files have no suffix, the others end in -<code> (card-menu-ja.svg).
"""
import base64, json, math, pathlib

HERE = pathlib.Path(__file__).parent
SRC = HERE / "readme-src"
FONT = "-apple-system, BlinkMacSystemFont, 'SF Pro Text', 'Segoe UI', 'Helvetica Neue', Helvetica, Arial, sans-serif"
ORANGE, ORANGE_DEEP = "#FF9A2E", "#F2591C"
ICON = "data:image/png;base64," + base64.b64encode((SRC / "icon-256.png").read_bytes()).decode()
TONE = json.loads((SRC / "tone-out.json").read_text())["samples"]

# Earbud outline from the app icon, centred on its own bounding box (about 330x650 units).
HEAD = "M330 300 C330 200 430 150 520 170 C620 192 660 280 640 360 C620 440 540 470 470 460 C390 450 330 390 330 300 Z"
STEM = "M548 420 C576 412 604 420 612 448 L640 760 C644 800 614 822 584 822 C556 822 534 804 532 772 L520 470 C518 444 528 426 548 420 Z"


def earbud(x, y, k, stroke="none", mirror=False):
    sx = -k if mirror else k
    line = f'stroke="{stroke}" stroke-width="{2 / k:.0f}"'
    return (f'<g transform="translate({x} {y}) scale({sx} {k}) translate(-485 -495)">'
            f'<path d="{STEM}" fill="#fff" {line}/><path d="{HEAD}" fill="#fff" {line}/>'
            f'<ellipse cx="372" cy="318" rx="20" ry="64" transform="rotate(-24 372 318)" fill="#2B2B30"/></g>')


def speaker(x, y, k, color):
    """A speaker with a slash: muted."""
    return (f'<g transform="translate({x} {y}) scale({k})" fill="none" stroke="{color}" stroke-width="5" '
            'stroke-linejoin="round" stroke-linecap="round">'
            '<path d="M-30 -12 H-14 L6 -30 V30 L-14 12 H-30 Z" fill="' + color + '" fill-opacity=".12"/>'
            '<path d="M18 -18 L40 18 M40 -18 L18 18"/></g>')


def wave(points, x0, y0, w, h):
    """Polyline path of samples in [-1, 1] across width w, centred on y0."""
    n = len(points) - 1
    return "M" + " L".join(f"{x0 + w * i / n:.1f} {y0 - v * h:.1f}" for i, v in enumerate(points))


def clean_wave(n=144):
    peak = max(abs(v) for v in TONE)
    return [v / peak for v in TONE[:n]]


def crackly_wave(n=144):
    """Illustration of the broken sound (not a measurement): the same tone with clicks and wobble."""
    out = []
    for i, v in enumerate(clean_wave(n)):
        wob = math.sin(i * 0.11) * 0.18
        click = 0.95 if i in (23, 24, 61, 97, 98, 128) else 0
        out.append(max(-1, min(1, v * (0.8 + wob) + (click if i % 2 else -click))))
    return out


def text_width(text, size, bold=False):
    """Rough rendered width: CJK and Hangul are about 1 em wide, other letters about half."""
    return sum(size if ord(c) >= 0x2E80 else size * (.56 if bold else .47) for c in text)


def fit(text, size, max_width, bold=False):
    """The font size that keeps the text within max_width, never above size."""
    return round(min(size, size * max_width / text_width(text, size, bold)), 1)


def svg(w, h, body, label, defs=""):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" '
            f'role="img" aria-label="{label}"><defs>{defs}</defs>{body}</svg>')


# ---------------------------------------------------------------- buttons

BUTTON_GLYPHS = {"download": "down", "how": "info", "feedback": "bubble", "kofi": "cup"}
GLYPHS = {
    "down": '<circle r="13"/><path d="M0 -6.5V6M-5 1.5L0 6.5L5 1.5"/>',
    "info": '<circle r="13"/><path d="M0 -1V7"/><circle cy="-6" r=".6" fill="currentColor"/>',
    "bubble": '<path d="M-12 -9 H12 V7 H-2 L-8 12 V7 H-12 Z"/>',
    "cup": '<path d="M-11 -6 H7 V5 A7 7 0 0 1 0 12 H-4 A7 7 0 0 1 -11 5 Z M7 -2 H10 A4 4 0 0 1 10 6 H7"/>',
}


def button(title, sub, glyph, primary):
    # The small line is medium weight: counted like bold, as the buttons were measured.
    w = round(64 + max(text_width(title, 19, True), text_width(sub, 12.5, True)) + 26)
    fill = "url(#bg)" if primary else "#1c1c1e"
    accent = "#fff" if primary else ORANGE
    defs = (f'<linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{ORANGE}"/>'
            f'<stop offset="1" stop-color="{ORANGE_DEEP}"/></linearGradient>')
    body = (f'<rect width="{w}" height="64" rx="16" fill="{fill}"/>'
            f'<rect x=".5" y=".5" width="{w - 1}" height="63" rx="15.5" fill="none" stroke="#fff" stroke-opacity=".18"/>'
            f'<g transform="translate(36 32)" fill="none" stroke="{accent}" color="{accent}" stroke-width="2.4" '
            f'stroke-linecap="round" stroke-linejoin="round">{GLYPHS[glyph]}</g>'
            f'<g font-family="{FONT}" fill="#fff"><text x="64" y="29" font-size="19" font-weight="700">{title}</text>'
            f'<text x="64" y="47" font-size="12.5" font-weight="500" fill-opacity=".8">{sub}</text></g>')
    return svg(w, 64, body, f"{title}, {sub}", defs)


# ---------------------------------------------------------------- cards

CW, CH = 540, 400
CARD_BG = "#161618"


def card(title, sub, art, label):
    body = (f'<rect width="{CW}" height="{CH}" rx="28" fill="{CARD_BG}"/>'
            f'<rect x=".5" y=".5" width="{CW - 1}" height="{CH - 1}" rx="27.5" fill="none" stroke="#fff" stroke-opacity=".08"/>'
            f'{art}<g font-family="{FONT}"><text x="36" y="318" font-size="{fit(title, 42, CW - 72, True)}" font-weight="700" fill="#fff">{title}</text>'
            f'<text x="36" y="362" font-size="{fit(sub, 27, CW - 72)}" fill="#fff" fill-opacity=".62">{sub}</text></g>')
    return svg(CW, CH, body, label)


def card_clean(t, lang):
    """The broken waveform crossfades into the measured clean one, 8 s loop."""
    bad, good = wave(crackly_wave(), 36, 150, 468, 80), wave(clean_wave(), 36, 150, 468, 80)
    fade = 'dur="8s" repeatCount="indefinite" keyTimes="0;.4;.5;.9;1"'
    art = (f'<path d="M36 150 H504" stroke="#fff" stroke-opacity=".08" stroke-width="2"/>'
           f'<g opacity="1"><animate attributeName="opacity" values="1;1;0;0;1" {fade}/>'
           f'<path d="{bad}" fill="none" stroke="#FF5F57" stroke-width="3.5" stroke-linejoin="round"/>'
           f'<text x="36" y="60" font-family="{FONT}" font-size="{fit(t["bad"], 26, CW - 72)}" fill="#FF5F57">{t["bad"]}</text></g>'
           f'<g opacity="0"><animate attributeName="opacity" values="0;0;1;1;0" {fade}/>'
           f'<path d="{good}" fill="none" stroke="{ORANGE}" stroke-width="3.5" stroke-linejoin="round"/>'
           f'<text x="36" y="60" font-family="{FONT}" font-size="{fit(t["good"], 26, CW - 72)}" fill="{ORANGE}">{t["good"]}</text></g>')
    return card(t["title"], t["sub"], art, t["label"])


def card_pitch(t, lang):
    """A tuner needle wobbles, then settles on the note: 9 s loop."""
    cx, cy, r = 270, 250, 170
    ticks = "".join(
        f'<line x1="{cx + (r - (18 if a % 30 == 0 else 9)) * math.sin(math.radians(a)):.1f}" '
        f'y1="{cy - (r - (18 if a % 30 == 0 else 9)) * math.cos(math.radians(a)):.1f}" '
        f'x2="{cx + r * math.sin(math.radians(a)):.1f}" y2="{cy - r * math.cos(math.radians(a)):.1f}" '
        f'stroke="#fff" stroke-opacity="{.7 if a == 0 else .25}" stroke-width="{4 if a == 0 else 2.5}" stroke-linecap="round"/>'
        for a in range(-60, 61, 10))
    art = (ticks + f'<g><animateTransform attributeName="transform" type="rotate" dur="9s" repeatCount="indefinite" '
           f'values="-34 {cx} {cy};22 {cx} {cy};-14 {cx} {cy};8 {cx} {cy};-3 {cx} {cy};0 {cx} {cy};0 {cx} {cy};-34 {cx} {cy}" '
           f'keyTimes="0;.1;.2;.3;.38;.45;.92;1" calcMode="spline" '
           f'keySplines=".4 0 .6 1;.4 0 .6 1;.4 0 .6 1;.4 0 .6 1;.4 0 .6 1;0 0 1 1;.4 0 .6 1"/>'
           f'<line x1="{cx}" y1="{cy}" x2="{cx}" y2="{cy - r + 26}" stroke="{ORANGE}" stroke-width="6" stroke-linecap="round"/></g>'
           f'<circle cx="{cx}" cy="{cy}" r="10" fill="{ORANGE}"/>')
    return card(t["title"], t["sub"], art, t["label"])


def card_ears(t, lang):
    """Earbuds lift out (the sound stops), drop back in (it resumes): 8 s loop."""
    keys = 'dur="8s" repeatCount="indefinite" keyTimes="0;.25;.35;.6;.7;1" calcMode="spline" keySplines="0 0 1 1;.4 0 .6 1;0 0 1 1;.4 0 .6 1;0 0 1 1"'
    bars = "".join(f'<rect x="{300 + i * 22}" y="{150 - h}" width="12" height="{2 * h}" rx="6" fill="{ORANGE}"/>'
                   for i, h in enumerate([20, 44, 70, 38, 58, 26, 48, 18]))
    art = (f'<g><animateTransform attributeName="transform" type="translate" values="0 0;0 0;0 -40;0 -40;0 0;0 0" {keys}/>'
           f'<g opacity="1"><animate attributeName="opacity" values="1;1;.35;.35;1;1" {keys}/>'
           f'{earbud(150, 150, 0.22)}{earbud(230, 150, 0.22, mirror=True)}</g></g>'
           f'<g transform-origin="390 150"><animateTransform attributeName="transform" type="scale" '
           f'values="1 1;1 1;1 .04;1 .04;1 1;1 1" {keys}/>{bars}</g>')
    return card(t["title"], t["sub"], art, t["label"])


def card_silent(t, lang):
    """The muted Mac speakers on the left, the sound travelling to an earbud on the right."""
    dots = "".join(
        f'<circle cx="200" cy="150" r="7" fill="{ORANGE}" opacity="0"><animate attributeName="cx" values="200;370" dur="2.4s" '
        f'begin="{i * 0.6}s" repeatCount="indefinite"/><animate attributeName="opacity" values="0;1;1;0" '
        f'keyTimes="0;.15;.85;1" dur="2.4s" begin="{i * 0.6}s" repeatCount="indefinite"/></circle>'
        for i in range(4))
    art = (speaker(120, 150, 1.7, "#fff") + dots + earbud(430, 150, 0.24))
    return card(t["title"], t["sub"], art, t["label"])


def menu_crop(state, part, lang):
    """A piece of a real capture of the menu (scripts/readme-shots.sh), as a JPEG data URI.

    part "status": the switch and the status row; part "pickers": the App and Output rows.
    The rows below the status are the same height in every state, so they are cut from the bottom."""
    from PIL import Image  # image prep only
    import io
    folder = "states" if lang == "en" else f"states-{lang}"
    img = Image.open(SRC / folder / f"{state}-dark.png").convert("RGB")
    w, h = img.size
    box = (0, 0, w, h - MENU_BOTTOM) if part == "status" else (0, h - MENU_BOTTOM + 2, w, h - MENU_QUIT)
    out = io.BytesIO()
    img.crop(box).save(out, "JPEG", quality=86)
    return "data:image/jpeg;base64," + base64.b64encode(out.getvalue()).decode(), box[2] - box[0], box[3] - box[1]


MENU_BOTTOM, MENU_QUIT = 224, 78  # px at 2x: from the status divider down, and the Quit row


def crossfade(shots, y, key, dur=12, fade=.05):
    """Real captures shown one after the other, top-aligned and centred, with a short crossfade."""
    n, out = len(shots), ""
    for i, (href, w, h) in enumerate(shots):
        k = (CW - 72) / w
        start, end = i / n, (i + 1) / n
        if i == 0:
            times, values = [0, end - fade, end, 1 - fade, 1], "1;1;0;0;1"
        elif i == n - 1:
            times, values = [0, start - fade, start, 1 - fade, 1], "0;0;1;1;0"
        else:
            times, values = [0, start - fade, start, end - fade, end, 1], "0;0;1;1;0;0"
        out += (f'<g opacity="{1 if i == 0 else 0}"><animate attributeName="opacity" values="{values}" '
                f'keyTimes="{";".join(f"{t:.3f}" for t in times)}" dur="{dur}s" repeatCount="indefinite"/>'
                f'<clipPath id="{key}{i}"><rect x="36" y="{y}" width="{w * k:.0f}" height="{h * k:.0f}" rx="18"/></clipPath>'
                f'<image href="{href}" x="36" y="{y}" width="{w * k:.0f}" height="{h * k:.0f}" clip-path="url(#{key}{i})"/></g>')
    return out


def card_menu(t, lang):
    """The top of the real menu going through three states: 12 s loop."""
    shots = [menu_crop(s, "status", lang) for s in ("sending", "waiting-app", "app-on-headphones")]
    return card(t["title"], t["sub"], crossfade(shots, 30, "menu"), t["label"])


def card_apps(t, lang):
    """The real App and Output pickers with three different apps picked: 12 s loop."""
    shots = [menu_crop(s, "pickers", lang) for s in ("sending", "sending-music", "sending-safari")]
    return card(t["title"], t["sub"], crossfade(shots, 90, "apps"), t["label"])


CARDS = {"clean": card_clean, "pitch": card_pitch, "ears": card_ears, "silent": card_silent,
         "menu": card_menu, "apps": card_apps}


# ---------------------------------------------------------------- hero

def hero(dark, labels, alt):
    """The signal path: FL Studio, the muted speakers, Detour, the cushion, the AirPods."""
    W, H = 1600, 480
    bg, fg, dim = ("#0d1117", "#ffffff", .55) if dark else ("#ffffff", "#1c1c1e", .6)
    node_bg = "#161b22" if dark else "#f2f2f4"
    y = 190
    # The path the sound travels, with the measured tone moving along it.
    seg = clean_wave(72)
    tone = wave(seg + seg[1:] + seg[1:], 0, 0, 480, 26)
    flow = (f'<path d="M300 {y} H1310" stroke="{fg}" stroke-opacity=".12" stroke-width="3"/>'
            f'<clipPath id="lane"><rect x="300" y="{y - 40}" width="1010" height="80"/></clipPath>'
            f'<g clip-path="url(#lane)">'
            + "".join(f'<path d="{tone}" transform="translate({x0} {y})" fill="none" stroke="{ORANGE}" stroke-width="3">'
                      f'<animateTransform attributeName="transform" type="translate" from="{x0} {y}" to="{x0 + 320} {y}" '
                      f'dur="4s" repeatCount="indefinite"/></path>' for x0 in (-20, 460, 940)) + '</g>')
    # Captions sit under five centres; two neighbours that would touch shrink together.
    centres = [210, 540, 805, 1110, 1400]

    def row_sizes(texts, size, bold):
        k = [1.0] * len(texts)
        widths = [text_width(t, size, bold) for t in texts]
        for i in range(len(texts) - 1):
            room = centres[i + 1] - centres[i] - 16
            need = (widths[i] * k[i] + widths[i + 1] * k[i + 1]) / 2
            if need > room:
                k[i], k[i + 1] = k[i] * room / need, k[i + 1] * room / need
        return [round(size * f, 1) if f < 1 else size for f in k]
    title_sizes = dict(zip(centres, row_sizes(labels[0::2], 34, True)))
    sub_sizes = dict(zip(centres, row_sizes(labels[1::2], 27, False)))

    def caption(x, title, sub):
        return (f'<text x="{x}" y="{y + 160}" text-anchor="middle" font-size="{title_sizes[x]}" font-weight="700" fill="{fg}">{title}</text>'
                f'<text x="{x}" y="{y + 200}" text-anchor="middle" font-size="{sub_sizes[x]}" fill="{fg}" fill-opacity="{dim}">{sub}</text>')

    def node(x, title, sub, art):
        return (f'<rect x="{x - 110}" y="{y - 110}" width="220" height="220" rx="44" fill="{node_bg}"/>{art}' + caption(x, title, sub))
    fl_art = (f'<g fill="{ORANGE}">' + "".join(
        f'<rect x="{150 + i * 26}" y="{y - h}" width="16" height="{2 * h}" rx="8"/>'
        for i, h in enumerate([22, 46, 70, 40, 58])) + '</g>')
    cushion = (f'<rect x="1030" y="{y - 22}" width="160" height="44" rx="22" fill="none" stroke="{fg}" stroke-opacity=".25" stroke-width="3"/>'
               f'<rect x="1036" y="{y - 16}" width="100" height="32" rx="16" fill="{ORANGE}">'
               f'<animate attributeName="width" values="100;112;94;106;100" dur="6s" repeatCount="indefinite" calcMode="spline" '
               f'keySplines=".4 0 .6 1;.4 0 .6 1;.4 0 .6 1;.4 0 .6 1"/></rect>')
    body = (f'<rect width="{W}" height="{H}" fill="{bg}"/>{flow}<g font-family="{FONT}">'
            + node(210, labels[0], labels[1], fl_art)
            + node(540, labels[2], labels[3], speaker(540, y, 2.2, fg))
            + f'<rect x="{1110 - 140}" y="{y - 110}" width="280" height="220" rx="44" fill="{node_bg}"/>{cushion}'
            + caption(1110, labels[6], labels[7])
            + node(1400, labels[8], labels[9], earbud(1400, y, 0.27, stroke="none" if dark else "#c7c7cc"))
            + f'<image href="{ICON}" x="{805 - 90}" y="{y - 90}" width="180" height="180"/>'
            + caption(805, labels[4], labels[5])
            + '</g>')
    return svg(W, H, body, alt)


if __name__ == "__main__":
    count = 0
    for path in sorted((HERE / "i18n").glob("*.json")):
        lang, t = path.stem, json.loads(path.read_text())
        suffix = "" if lang == "en" else f"-{lang}"
        for name, (title, sub) in t["buttons"].items():
            (HERE / "buttons" / f"{name}{suffix}.svg").write_text(
                button(title, sub, BUTTON_GLYPHS[name], name == "download"))
        for name, make in CARDS.items():
            (HERE / f"card-{name}{suffix}.svg").write_text(make(t["cards"][name], lang))
        (HERE / f"hero{suffix}.svg").write_text(hero(True, t["hero"], t["hero_alt"]))
        (HERE / f"hero-light{suffix}.svg").write_text(hero(False, t["hero"], t["hero_alt"]))
        count += len(t["buttons"]) + len(CARDS) + 2
    print("wrote", count, "SVGs")
