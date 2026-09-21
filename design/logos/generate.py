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

def _tri_colors(dark: bool):
    """(top, left, right) face fills and matching unlit-LED fills."""
    if dark:
        return ("#7a8496", "#636b7a", "#525a68"), ("#6d7686", "#575e6c", "#484f5c")
    return (SLATE_MID, SLATE, "#3b414b"), ("#4f5663", "#3f454f", "#333944")


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

    (face_top, face_left, face_right), (unlit_top, unlit_left, unlit_right) = _tri_colors(dark)
    text = DARK_TEXT if dark else SLATE

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
    # One lit voxel per face, matching the relative positions used by the
    # 16/24/32 icon variants below (top ~(.25,.25), left ~(.75,.25),
    # right ~(.25,.75) in face-local units).
    lit_top = {(1, 1)}
    lit_left = {(2, 1)}
    lit_right = {(1, 2)}
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
# Small icon variants (16 / 24 / 32 px).
#
# Like the hand-tuned pyscenedetect-24/-32 icons, each size is reconstructed
# on the device pixel grid rather than scaled down: vertices sit on integer
# (or deliberate half-pixel) coordinates so edges land on pixel boundaries,
# and detail is dropped as sizes shrink (fewer LEDs, no claw/antenna at 16px).
# The isometric cube keeps an exact 2:1 slope so diagonals rasterize with a
# consistent stair pattern.
# ---------------------------------------------------------------------------

ICON_SIZES = (16, 24, 32)


def _icon(size: int, body: str) -> str:
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" '
        f'viewBox="0 0 {size} {size}">{body}</svg>'
    )


def _c(x, y, r, fill, extra: str = "") -> str:
    return f'<circle cx="{x}" cy="{y}" r="{r}" fill="{fill}"{extra}/>'


# Per-size cube geometry: rhombus vertices (N/E/S/W of the top face), the
# vertical depth of the side faces, LED dot radii, and explicit device-space
# LED centers per face ((x, y, lit); centers rounded to the nearest half px).
TRI_ICON = {
    32: dict(
        n=(16, 2), e=(30, 9), s=(16, 16), w=(2, 9), depth=14,
        r_unlit=1.4, r_lit=1.8, r_hi=0.7,
        dots=dict(
            top=[(16, 5.5, True), (16, 12.5, False)],
            left=[(12.5, 18, True), (12.5, 25, False)],
            right=[(19.5, 18, False), (19.5, 25, True)],
        ),
    ),
    24: dict(
        n=(12, 2), e=(22, 7), s=(12, 12), w=(2, 7), depth=10,
        r_unlit=1.1, r_lit=1.4, r_hi=None,
        dots=dict(
            top=[(12, 4.5, True), (12, 9.5, False)],
            left=[(9.5, 13.5, True), (9.5, 18.5, False)],
            right=[(14.5, 13.5, False), (14.5, 18.5, True)],
        ),
    ),
    16: dict(
        n=(8, 1), e=(15, 4.5), s=(8, 8), w=(1, 4.5), depth=7,
        r_unlit=None, r_lit=1.1, r_hi=None,
        dots=dict(
            top=[(8, 4.5, True)],
            left=[(4.5, 10, True)],
            right=[(11.5, 10, True)],
        ),
    ),
}


def triclysm_icon_svg(size: int, dark: bool) -> str:
    faces, unlits = _tri_colors(dark)
    g = TRI_ICON[size]
    n, e, s, w, d = g["n"], g["e"], g["s"], g["w"], g["depth"]
    e2, s2, w2 = (e[0], e[1] + d), (s[0], s[1] + d), (w[0], w[1] + d)

    def poly(pts, fill):
        pd = " ".join(f"{x},{y}" for x, y in pts)
        return f'<polygon points="{pd}" fill="{fill}"/>'

    parts = [
        poly([n, e, s, w], faces[0]),
        poly([w, s, s2, w2], faces[1]),
        poly([s, e, e2, s2], faces[2]),
    ]
    for fi, key in enumerate(("top", "left", "right")):
        for x, y, lit in g["dots"][key]:
            if lit:
                parts.append(_c(x, y, g["r_lit"], MINT))
                if g["r_hi"]:
                    parts.append(_c(x, y, g["r_hi"], "#f4fdfa"))
            else:
                parts.append(_c(x, y, g["r_unlit"], unlits[fi]))
    return _icon(size, "".join(parts))


def biopsybot_icon_svg(size: int, dark: bool) -> str:
    if dark:
        tread, body, hub = "#59606d", "#6d7686", "#494f5a"
    else:
        tread, body, hub = SLATE, SLATE_MID, "#363c45"
    metal = TEAL_LIGHT

    def rect(x, y, w, h, rx, fill):
        return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}"/>'

    p = []
    if size == 32:
        p.append(rect(1, 22, 22, 8, 4, tread))  # tread
        for wx in (6, 12, 18):  # road wheels
            p.append(_c(wx, 26, 2.5, hub))
            p.append(_c(wx, 26, 1, metal))
        p.append(rect(2, 17, 22, 5, 1, body))  # deck
        p.append(f'<polygon points="24,17.5 30,21.5 30,24 24,22" fill="{metal}"/>')  # arm
        for d in ("M 27 24 L 26 26.5 L 26.5 28.5", "M 30 24 L 31 26.5 L 30.5 28.5"):  # claw
            p.append(
                f'<path d="{d}" stroke="{tread}" stroke-width="1.2" fill="none" '
                f'stroke-linecap="round" stroke-linejoin="round"/>'
            )
        p.append(  # specimen blob under the claw
            f'<path d="M 24.5 30 Q 26 25.5 28 25.5 Q 30 25.5 31.5 30 Z" '
            f'fill="{MINT}" opacity="0.85"/>'
        )
        p.append(rect(7, 9, 2, 8, 0, body))  # mast
        p.append(rect(3, 3, 12, 7, 1.5, tread))  # head
        p.append(_c(12.5, 6.5, 2.5, MINT))  # eye
        p.append(_c(12.5, 6.5, 1, hub))
        p.append(rect(4, 1.5, 1, 1.5, 0.5, metal))  # antenna
        p.append(_c(4.5, 1.5, 1.5, MINT))
    elif size == 24:
        p.append(rect(1, 16, 17, 6, 3, tread))  # tread
        for wx in (4.5, 9.5, 14.5):  # road wheels
            p.append(_c(wx, 19, 2, hub))
            p.append(_c(wx, 19, 0.75, metal))
        p.append(rect(2, 12, 18, 4, 1, body))  # deck
        p.append(f'<polygon points="19.5,12.5 22.5,16 22.5,18.5 19.5,15.5" fill="{metal}"/>')  # arm
        p.append(  # specimen blob
            f'<path d="M 18.5 22 Q 19.75 18.5 21 18.5 Q 22.25 18.5 23.5 22 Z" '
            f'fill="{MINT}" opacity="0.85"/>'
        )
        p.append(rect(6, 7, 1, 5, 0, body))  # mast
        p.append(rect(2, 2, 10, 6, 1, tread))  # head
        p.append(_c(10, 5, 2, MINT))  # eye
        p.append(_c(10, 5, 0.75, hub))
        p.append(_c(3.5, 1.25, 1.25, MINT))  # antenna light
    else:  # 16
        p.append(rect(1, 11, 13, 4, 2, tread))  # tread
        for wx in (4.5, 10.5):  # road wheels
            p.append(_c(wx, 13, 1.5, hub))
        p.append(rect(2, 8, 13, 3, 1, body))  # deck
        p.append(rect(4, 7, 1, 1, 0, body))  # mast
        p.append(rect(1, 1, 9, 6, 1, tread))  # head
        p.append(_c(7.5, 4, 1.75, MINT))  # eye
    return _icon(size, "".join(p))


def write_ico(name: str, icon_out: str) -> None:
    """Bundle the rendered light-variant PNGs into a multi-size favicon.

    Each size is passed as its own plane via append_images so the hand-tuned
    16/24/32 pixels are preserved exactly (Pillow only resamples for sizes it
    was not given an image for).
    """
    ims = {s: Image.open(os.path.join(icon_out, f"{name}-{s}.png")) for s in ICON_SIZES}
    largest = max(ICON_SIZES)
    path = os.path.join(icon_out, f"{name}.ico")
    ims[largest].save(
        path,
        format="ICO",
        sizes=[(s, s) for s in ICON_SIZES],
        append_images=[ims[s] for s in ICON_SIZES if s != largest],
    )
    print("wrote", path)


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
    icon_out = os.path.join(OUT, "icons")
    os.makedirs(icon_out, exist_ok=True)
    for name, fn in [("triclysm", triclysm_icon_svg), ("biopsybot", biopsybot_icon_svg)]:
        for size in ICON_SIZES:
            for dark in (False, True):
                suffix = "-dark" if dark else ""
                svg = fn(size, dark)
                with open(
                    os.path.join(HERE, f"{name}-{size}{suffix}.svg"), "w", encoding="utf-8"
                ) as f:
                    f.write(svg)
                render(svg, os.path.join(icon_out, f"{name}-{size}{suffix}.png"), size, size)
        write_ico(name, icon_out)
    render_external()


if __name__ == "__main__":
    main()
