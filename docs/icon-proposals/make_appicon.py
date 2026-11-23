"""Writes Resources/AppIcon.icon (Icon Composer document) from concept G1, the sprouting earbud.
Layers are flat shapes; macOS adds the Liquid Glass light, depth and the dark/tinted variants."""
import json, pathlib

FIT = "translate(512 525) scale(0.86) translate(-512 -490)"  # same framing as the G1 proposal
HEAD = "M330 300 C330 200 430 150 520 170 C620 192 660 280 640 360 C620 440 540 470 470 460 C390 450 330 390 330 300 Z"
STEM = "M548 420 C576 412 604 420 612 448 L640 760 C644 800 614 822 584 822 C556 822 534 804 532 772 L520 470 C518 444 528 426 548 420 Z"

def svg(body):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="1024" height="1024" viewBox="0 0 1024 1024">'
            f'<g transform="{FIT}">{body}</g></svg>')

layers = {
    "stalk": svg('<path d="M560 190 C566 150 580 120 600 100" fill="none" stroke="#7A4A22" stroke-width="22" stroke-linecap="round"/>'),
    "leaf": svg('<g transform="translate(596 108) rotate(8) scale(0.9)">'
                '<path d="M0 0 C30 -90 120 -140 230 -120 C210 -20 120 30 0 0 Z" fill="#4CC25E"/>'
                '<path d="M0 0 C70 -40 140 -80 210 -112" fill="none" stroke="#1F7A3A" stroke-width="9" stroke-linecap="round"/></g>'),
    "earbud": svg(f'<g transform="translate(20 60)"><path d="{STEM}" fill="#FFFFFF"/><path d="{HEAD}" fill="#FFFFFF"/></g>'),
    "mesh": svg('<g transform="translate(20 60)"><ellipse cx="372" cy="318" rx="20" ry="64" '
                'transform="rotate(-24 372 318)" fill="#2B2B30"/></g>'),
}

def p3(hex_):
    """sRGB hex to a display-p3 colour string (linearise, convert primaries, re-encode)."""
    lin = [(c / 12.92) if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
           for c in (int(hex_[i:i + 2], 16) / 255 for i in (1, 3, 5))]
    m = [(0.8225, 0.1774, 0.0), (0.0332, 0.9669, 0.0), (0.0171, 0.0724, 0.9108)]
    out = [sum(a * b for a, b in zip(row, lin)) for row in m]
    enc = [12.92 * c if c <= 0.0031308 else 1.055 * c ** (1 / 2.4) - 0.055 for c in out]
    return "display-p3:" + ",".join(f"{max(0, min(1, c)):.5f}" for c in enc) + ",1.00000"

def group(*names, shadow=0.5, translucency=0.4):
    return {"layers": [{"glass": True, "image-name": f"{n}.svg", "name": n} for n in names],
            "shadow": {"kind": "neutral", "opacity": shadow},
            "translucency": {"enabled": True, "value": translucency}}

doc = {
    "fill": {"linear-gradient": [p3("#FFB13B"), p3("#F2591C")],
             "orientation": {"start": {"x": 0.5, "y": 0}, "stop": {"x": 0.5, "y": 1}}},
    "groups": [group("mesh", shadow=0.2, translucency=0.0), group("earbud", translucency=0.25), group("leaf", "stalk")],
    "supported-platforms": {"squares": ["macOS"]},
}

root = pathlib.Path(__file__).resolve().parents[2] / "Resources" / "AppIcon.icon"
(root / "Assets").mkdir(parents=True, exist_ok=True)
for name, content in layers.items():
    (root / "Assets" / f"{name}.svg").write_text(content)
(root / "icon.json").write_text(json.dumps(doc, indent=2) + "\n")
print("wrote", root)
