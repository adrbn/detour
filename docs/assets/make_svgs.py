"""Writes every SVG of the README: hero (dark + light), buttons, feature cards (en + fr).

Stdlib only. Run from anywhere: python3 docs/assets/make_svgs.py
Real inputs live in readme-src/: the app icon rendered by Icon Composer, and samples of the
measured Detour output of a 1 kHz test tone.
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


def svg(w, h, body, label, defs=""):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" '
            f'role="img" aria-label="{label}"><defs>{defs}</defs>{body}</svg>')


# ---------------------------------------------------------------- buttons

BUTTONS = {
    "download": ("Download for macOS", "Free · macOS 14.2 or later", "down"),
    "download-fr": ("Télécharger pour macOS", "Gratuit · macOS 14.2 ou plus récent", "down"),
    "how": ("How it works", "Why AirPods crackle", "info"),
    "how-fr": ("Comment ça marche", "Pourquoi les AirPods craquent", "info"),
    "feedback": ("Feedback", "Report a bug or suggest an app", "bubble"),
    "feedback-fr": ("Vos retours", "Un bug, une app à ajouter", "bubble"),
    "kofi": ("Buy me a coffee", "on Ko-fi", "cup"),
    "kofi-fr": ("M'offrir un café", "sur Ko-fi", "cup"),
}
GLYPHS = {
    "down": '<circle r="13"/><path d="M0 -6.5V6M-5 1.5L0 6.5L5 1.5"/>',
    "info": '<circle r="13"/><path d="M0 -1V7"/><circle cy="-6" r=".6" fill="currentColor"/>',
    "bubble": '<path d="M-12 -9 H12 V7 H-2 L-8 12 V7 H-12 Z"/>',
    "cup": '<path d="M-11 -6 H7 V5 A7 7 0 0 1 0 12 H-4 A7 7 0 0 1 -11 5 Z M7 -2 H10 A4 4 0 0 1 10 6 H7"/>',
}


def button(title, sub, glyph, primary):
    w = round(64 + max(len(title) * 10.6, len(sub) * 7.0) + 26)
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
            f'{art}<g font-family="{FONT}"><text x="36" y="318" font-size="42" font-weight="700" fill="#fff">{title}</text>'
            f'<text x="36" y="362" font-size="27" fill="#fff" fill-opacity=".62">{sub}</text></g>')
    return svg(CW, CH, body, label)


def card_clean(t):
    """The broken waveform crossfades into the measured clean one, 8 s loop."""
    bad, good = wave(crackly_wave(), 36, 150, 468, 80), wave(clean_wave(), 36, 150, 468, 80)
    fade = 'dur="8s" repeatCount="indefinite" keyTimes="0;.4;.5;.9;1"'
    art = (f'<path d="M36 150 H504" stroke="#fff" stroke-opacity=".08" stroke-width="2"/>'
           f'<g opacity="1"><animate attributeName="opacity" values="1;1;0;0;1" {fade}/>'
           f'<path d="{bad}" fill="none" stroke="#FF5F57" stroke-width="3.5" stroke-linejoin="round"/>'
           f'<text x="36" y="60" font-family="{FONT}" font-size="26" fill="#FF5F57">{t["bad"]}</text></g>'
           f'<g opacity="0"><animate attributeName="opacity" values="0;0;1;1;0" {fade}/>'
           f'<path d="{good}" fill="none" stroke="{ORANGE}" stroke-width="3.5" stroke-linejoin="round"/>'
           f'<text x="36" y="60" font-family="{FONT}" font-size="26" fill="{ORANGE}">{t["good"]}</text></g>')
    return card(t["title"], t["sub"], art, t["label"])


def card_pitch(t):
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


def card_ears(t):
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


def card_silent(t):
    """The muted Mac speakers on the left, the sound travelling to an earbud on the right."""
    dots = "".join(
        f'<circle cx="200" cy="150" r="7" fill="{ORANGE}" opacity="0"><animate attributeName="cx" values="200;370" dur="2.4s" '
        f'begin="{i * 0.6}s" repeatCount="indefinite"/><animate attributeName="opacity" values="0;1;1;0" '
        f'keyTimes="0;.15;.85;1" dur="2.4s" begin="{i * 0.6}s" repeatCount="indefinite"/></circle>'
        for i in range(4))
    art = (speaker(120, 150, 1.7, "#fff") + dots + earbud(430, 150, 0.24))
    return card(t["title"], t["sub"], art, t["label"])


CARDS = {
    "clean": (card_clean, {
        "en": dict(title="No crackles", sub="Clean from the first note", bad="FL Studio on AirPods",
                   good="Through Detour (measured)", label="A waveform with crackles becomes a clean waveform"),
        "fr": dict(title="Pas de craquements", sub="Propre dès la première note", bad="FL Studio sur les AirPods",
                   good="Avec Detour (mesuré)", label="Une forme d'onde qui craque devient propre")}),
    "pitch": (card_pitch, {
        "en": dict(title="The right pitch", sub="1 kHz in, 1000.4 Hz out",
                   label="A tuner needle settles exactly on the note"),
        "fr": dict(title="La bonne hauteur", sub="1 kHz joué, 1000,4 Hz mesuré",
                   label="L'aiguille d'un accordeur se pose exactement sur la note")}),
    "ears": (card_ears, {
        "en": dict(title="Out and back in", sub="The sound returns within a second",
                   label="AirPods taken out and put back, the sound resumes"),
        "fr": dict(title="Retirés, remis", sub="De retour en moins d’une seconde",
                   label="AirPods retirés puis remis, le son reprend")}),
    "silent": (card_silent, {
        "en": dict(title="Silent speakers", sub="Even while your AirPods are out",
                   label="The Mac speakers stay silent while you listen"),
        "fr": dict(title="Haut-parleurs muets", sub="Même AirPods retirés",
                   label="Les haut-parleurs du Mac restent muets pendant l'écoute")}),
}


# ---------------------------------------------------------------- hero

def hero(dark, lang="en"):
    """The signal path: FL Studio, the muted speakers, Detour, the cushion, the AirPods."""
    W, H = 1600, 480
    bg, fg, dim = ("#0d1117", "#ffffff", .55) if dark else ("#ffffff", "#1c1c1e", .6)
    node_bg = "#161b22" if dark else "#f2f2f4"
    labels = {"en": ("FL Studio", "plays on the speakers", "Mac speakers", "muted", "Detour",
                     "menu bar app", "100 ms cushion", "absorbs Bluetooth bursts", "AirPods", "clean, right pitch"),
              "fr": ("FL Studio", "joue sur les haut-parleurs", "Haut-parleurs", "coupés", "Detour",
                     "barre des menus", "Réserve de 100 ms", "absorbe les à-coups", "AirPods", "propre, bonne hauteur")}[lang]
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
    def caption(x, title, sub):
        return (f'<text x="{x}" y="{y + 160}" text-anchor="middle" font-size="34" font-weight="700" fill="{fg}">{title}</text>'
                f'<text x="{x}" y="{y + 200}" text-anchor="middle" font-size="27" fill="{fg}" fill-opacity="{dim}">{sub}</text>')

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
    return svg(W, H, body, "FL Studio's sound leaves the muted Mac speakers and reaches AirPods clean through Detour")


if __name__ == "__main__":
    for name, (title, sub, glyph) in BUTTONS.items():
        (HERE / "buttons" / f"{name}.svg").write_text(button(title, sub, glyph, name.startswith("download")))
    for name, (make, texts) in CARDS.items():
        (HERE / f"card-{name}.svg").write_text(make(texts["en"]))
        (HERE / f"card-{name}-fr.svg").write_text(make(texts["fr"]))
    (HERE / "hero.svg").write_text(hero(True))
    (HERE / "hero-light.svg").write_text(hero(False))
    (HERE / "hero-fr.svg").write_text(hero(True, "fr"))
    (HERE / "hero-light-fr.svg").write_text(hero(False, "fr"))
    print("wrote", len(BUTTONS) + 2 * len(CARDS) + 4, "SVGs")
