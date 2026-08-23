"""Generate project logos for bcastell.com.

Authors the Triclysm and Biopsy Bot logo SVGs (light + dark variants) in the
same style as the PySceneDetect / DVR-Scan logos (flat slate icon, mint
accents, Roboto Slab wordmark), renders them to PNG, and also renders the
PySceneDetect / DVR-Scan logos from their sibling repos onto the same
960x550 canvas.

Run from the repo root with a venv that has resvg-py and pillow:
    uv venv .venv && uv pip install --python .venv resvg-py pillow
    .venv/Scripts/python design/logos/generate.py

Fonts: design/logos/fonts/ holds static instances of Roboto Slab (OFL).
"""

import io
import os
import re

import resvg_py
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", ".."))
OUT = os.path.join(REPO, "static", "img", "projects")
FONT_FILES = [
    os.path.join(HERE, "fonts", "RobotoSlab-Regular.ttf"),
    os.path.join(HERE, "fonts", "RobotoSlab-Bold.ttf"),
]
PSD_REPO = os.path.join(REPO, "..", "PySceneDetect")
DVR_REPO = os.path.join(REPO, "..", "DVR-Scan")

W, H = 960, 550  # matches dvr-scan-logo.svg / 2x the 480x275 shown on the site

# Palette (sampled from dvr-scan-logo.svg)
SLATE = "#474d57"
SLATE_MID = "#59606d"
TEAL = "#607372"
TEAL_LIGHT = "#87a0a0"
MINT = "#c6f1e7"
DARK_TEXT = "#e0e8f0"  # wordmark color on dark backgrounds (from PSD darkmode)


def render(svg: str, out_path: str, width: int = W, height: int = H) -> None:
    png = resvg_py.svg_to_bytes(
        svg_string=svg,
        width=width,
        height=height,
        font_files=FONT_FILES,
        skip_system_fonts=True,
    )
    with open(out_path, "wb") as f:
        f.write(bytes(png))
    print("wrote", out_path)


def wordmark(text: str, fill: str, size: int = 120, x: int = 45, y: int = 520) -> str:
    # The DVR-Scan / PySceneDetect SVGs claim Regular, but the official rasters
    # were exported with a bold face; Roboto Slab Bold ~120px matches them.
    return (
        f'<text x="{x}" y="{y}" font-family="Roboto Slab" font-weight="700" '
        f'font-size="{size}" fill="{fill}">{text}</text>'
    )


# ---------------------------------------------------------------------------
# Triclysm: flat isometric LED cube, some voxels lit mint.
# ---------------------------------------------------------------------------

def triclysm_svg(dark: bool) -> str:
    # Isometric cube: top vertex N, side vertices E/W, front vertex S.
    cx, a, b = 250, 155, 78  # center x, half-width, half-height of top rhombus
    top_y = 42
    n = (cx, top_y)
    e = (cx + a, top_y + b)
    w = (cx - a, top_y + b)
    s = (cx, top_y + 2 * b)
    depth = 155
    e2 = (e[0], e[1] + depth)
    w2 = (w[0], w[1] + depth)
    s2 = (s[0], s[1] + depth)

    if dark:
        face_top, face_left, face_right = "#7a8496", "#636b7a", "#525a68"
        unlit_top, unlit_left, unlit_right = "#6d7686", "#575e6c", "#484f5c"
        text = DARK_TEXT
    else:
        face_top, face_left, face_right = SLATE_MID, SLATE, "#3b414b"
        unlit_top, unlit_left, unlit_right = "#4f5663", "#3f454f", "#333944"
        text = SLATE

    def poly(pts, fill):
        d = " ".join(f"{x},{y}" for x, y in pts)
        return f'<polygon points="{d}" fill="{fill}"/>'

    parts = [
        poly([n, e, s, w], face_top),
        poly([w, s, s2, w2], face_left),
        poly([s, e, e2, s2], face_right),
    ]

    grid = [(i + 0.5) / 4 for i in range(4)]
    # (face origin, u-corner, v-corner, unlit fill, lit cells)
    lit_top = {(0, 2), (2, 1), (3, 3)}
    lit_left = {(1, 1), (3, 2), (0, 3)}
    lit_right = {(2, 0), (1, 2), (3, 3)}
    faces = [
        (n, e, w, unlit_top, lit_top),
        (w, s, w2, unlit_left, lit_left),
        (s, e, s2, unlit_right, lit_right),
    ]
    # LEDs are drawn as unit-space circles inside a group transformed onto each
    # face plane, so they foreshorten with the surface, and clipped to the face
    # polygon so glows never bleed past the cube edges.
    defs = []
    for fi, (o, u, v, unlit, lit) in enumerate(faces):
        uv = (u[0] - o[0], u[1] - o[1])
        vv = (v[0] - o[0], v[1] - o[1])
        far = (o[0] + uv[0] + vv[0], o[1] + uv[1] + vv[1])
        pts = f"{o[0]},{o[1]} {u[0]},{u[1]} {far[0]},{far[1]} {v[0]},{v[1]}"
        defs.append(f'<clipPath id="face{fi}"><polygon points="{pts}"/></clipPath>')
        leds = []
        for i, tu in enumerate(grid):
            for j, tv in enumerate(grid):
                is_lit = (i, j) in lit
                fill = MINT if is_lit else unlit
                if is_lit:
                    # soft glow halo behind lit voxels
                    leds.append(
                        f'<circle cx="{tu}" cy="{tv}" r="0.16" fill="{MINT}" opacity="0.35"/>'
                    )
                leds.append(f'<circle cx="{tu}" cy="{tv}" r="0.075" fill="{fill}"/>')
                if is_lit:
                    leds.append(f'<circle cx="{tu}" cy="{tv}" r="0.034" fill="#f4fdfa"/>')
        matrix = f"matrix({uv[0]} {uv[1]} {vv[0]} {vv[1]} {o[0]} {o[1]})"
        parts.append(
            f'<g clip-path="url(#face{fi})"><g transform="{matrix}">'
            + "".join(leds)
            + "</g></g>"
        )

    parts.insert(0, "<defs>" + "".join(defs) + "</defs>")
    parts.append(wordmark("Triclysm", text))
    body = "\n".join(parts)
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}">{body}</svg>'


# ---------------------------------------------------------------------------
# Biopsy Bot: flat side-view tracked robot with camera mast and syringe arm.
# ---------------------------------------------------------------------------

def biopsybot_svg(dark: bool) -> str:
    if dark:
        tread, body, hub = "#59606d", "#6d7686", "#494f5a"
        text = DARK_TEXT
        metal = TEAL_LIGHT
    else:
        tread, body, hub = SLATE, SLATE_MID, "#363c45"
        text = SLATE
        metal = TEAL_LIGHT

    parts = []
    # Tank tread: stadium outline with road wheels.
    parts.append(
        f'<rect x="80" y="230" width="330" height="120" rx="60" fill="{tread}"/>'
    )
    for wx in (145, 245, 345):
        parts.append(f'<circle cx="{wx}" cy="290" r="36" fill="{hub}"/>')
        parts.append(f'<circle cx="{wx}" cy="290" r="14" fill="{metal}"/>')
    # Chassis (plexiglass deck) above the treads.
    parts.append(f'<rect x="95" y="160" width="290" height="70" rx="10" fill="{body}"/>')
    # Angled aluminum front extension holding the sampling arm.
    parts.append(
        f'<polygon points="385,165 470,215 470,260 385,230" fill="{metal}"/>'
    )
    # Camera mast at the rear.
    parts.append(f'<rect x="148" y="80" width="14" height="80" fill="{body}"/>')
    parts.append(f'<rect x="112" y="40" width="90" height="52" rx="10" fill="{tread}"/>')
    parts.append(f'<circle cx="184" cy="66" r="14" fill="{MINT}"/>')
    parts.append(f'<circle cx="184" cy="66" r="6" fill="{hub}"/>')
    # antenna
    parts.append(f'<rect x="120" y="14" width="6" height="26" rx="3" fill="{metal}"/>')
    parts.append(f'<circle cx="123" cy="12" r="7" fill="{MINT}"/>')
    # Grabber at the front: actuator on the extension, simple two-finger claw.
    parts.append(f'<rect x="446" y="218" width="42" height="24" rx="7" fill="{tread}"/>')  # actuator
    for d in ("M 455 240 L 441 264 L 449 290", "M 479 240 L 493 264 L 485 290"):
        parts.append(
            f'<path d="{d}" stroke="{tread}" stroke-width="12" fill="none" '
            f'stroke-linecap="round" stroke-linejoin="round"/>'
        )
    # Jello blob under the needle.
    parts.append(
        f'<path d="M 430 330 q 12 -48 41 -48 q 29 0 41 48 q -41 14 -82 0 z" '
        f'fill="{MINT}" opacity="0.85"/>'
    )
    parts.append(wordmark("Biopsy Bot", text))
    body_svg = "\n".join(parts)
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}">{body_svg}</svg>'


# ---------------------------------------------------------------------------
# PySceneDetect / DVR-Scan: render from sibling repos onto the same canvas.
# ---------------------------------------------------------------------------

def compose_contain(png_bytes: bytes, out_path: str) -> None:
    """Fit a rendered logo into the 960x550 canvas (left-aligned, centered)."""
    img = Image.open(io.BytesIO(bytes(png_bytes))).convert("RGBA")
    scale = min(W / img.width, H / img.height)
    img = img.resize((round(img.width * scale), round(img.height * scale)), Image.LANCZOS)
    canvas = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    canvas.paste(img, (0, (H - img.height) // 2), img)
    canvas.save(out_path)
    print("wrote", out_path)


def render_external() -> None:
    psd_light = os.path.join(PSD_REPO, "packaging", "logo", "pyscenedetect-logo.svg")
    psd_dark = os.path.join(PSD_REPO, "dist", "logo", "pyscenedetect-logo-darkmode.svg")
    dvr_light = os.path.join(DVR_REPO, "docs", "assets", "dvr-scan-logo.svg")

    for src, name in [(psd_light, "pyscenedetect.png"), (psd_dark, "pyscenedetect-dark.png")]:
        svg = open(src, encoding="utf-8").read()
        # resvg renders these fully transparent due to an Inkscape powermask;
        # the mask is a no-op visually, so strip mask references before rendering.
        svg = re.sub(r'\bmask="url\([^)]*\)"', "", svg)
        # The SVG styles say Regular but the official rasters are bold.
        svg = svg.replace("font-family:'Roboto Slab'", "font-weight:bold;font-family:'Roboto Slab'")
        png = resvg_py.svg_to_bytes(
            svg_string=svg, width=1024, height=480,
            font_files=FONT_FILES, skip_system_fonts=True,
        )
        compose_contain(png, os.path.join(OUT, name))

    svg = open(dvr_light, encoding="utf-8").read()
    # The SVG wordmark style says Regular but the official raster is bold.
    svg = svg.replace("font-weight:normal", "font-weight:bold")
    render(svg, os.path.join(OUT, "dvr-scan.png"))
    # Dark variant: icon keeps the exact original colors; only the wordmark
    # switches to a light fill so it stays readable on dark backgrounds.
    dark = re.sub(
        r"<text.*?</text>",
        lambda m: m.group(0).replace(SLATE, DARK_TEXT),
        svg,
        flags=re.S,
    )
    render(dark, os.path.join(OUT, "dvr-scan-dark.png"))


def main() -> None:
    os.makedirs(OUT, exist_ok=True)
    for name, fn in [("triclysm", triclysm_svg), ("biopsybot", biopsybot_svg)]:
        for dark in (False, True):
            suffix = "-dark" if dark else ""
            svg = fn(dark)
            with open(os.path.join(HERE, f"{name}{suffix}.svg"), "w", encoding="utf-8") as f:
                f.write(svg)
            render(svg, os.path.join(OUT, f"{name}{suffix}.png"))
    render_external()


if __name__ == "__main__":
    main()
