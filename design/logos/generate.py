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
import math
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


# ---------------------------------------------------------------------------
# bcastell.com site mark & favicons (Option D floating SVG + Option A card).
#
# Floating mark (bcastell.svg -> static/img/favicon.svg) uses CSS
# prefers-color-scheme so tabs adapt cleanly to light/dark browser chrome.
# Dark card (bcastell-badge.svg -> favicon.ico & apple-touch-icon.png) keeps
# guaranteed contrast on iOS home screens, Firefox New Tab tiles, and legacy
# .ico consumers.
# ---------------------------------------------------------------------------

SITE_BG_TOP = "#1e252e"
SITE_BG_BOT = "#12161c"
SITE_BORDER = "#333c47"
SITE_BLUE_DARK = "#58a6ff"
SITE_GREY_DARK = "#dce3ec"
SITE_BLUE_LIGHT = "#0b6bcb"
SITE_GREY_LIGHT = "#2b333d"

SITE_ICO_SIZES = (16, 24, 32, 48, 64, 128, 256)


def _circle_intersect_right(cx1, cy1, r1, cx2, cy2, r2):
    """Return the rightmost intersection point of two circles."""
    dx = cx2 - cx1
    dy = cy2 - cy1
    d = math.hypot(dx, dy)
    a = (r1 * r1 - r2 * r2 + d * d) / (2 * d)
    h = math.sqrt(max(0.0, r1 * r1 - a * a))
    mx = cx1 + a * dx / d
    my = cy1 + a * dy / d
    p1 = (mx + h * dy / d, my - h * dx / d)
    p2 = (mx - h * dy / d, my + h * dx / d)
    return p1 if p1[0] >= p2[0] else p2


def _bc_b_path(x0, y0, w, h, stem=15.0, bar=12.5, corner_r=3.0) -> str:
    """Geometric sans-serif 'B' path (evenodd) with optically balanced bowls."""
    r1 = h * 0.245
    r2 = h * 0.285
    w_top = w * 0.92
    w_bot = w

    cx1 = x0 + w_top - r1
    cy1 = y0 + r1
    cx2 = x0 + w_bot - r2
    cy2 = y0 + h - r2
    ix, iy = _circle_intersect_right(cx1, cy1, r1, cx2, cy2, r2)

    outer = (
        f"M {x0:.2f} {y0 + corner_r:.2f} "
        f"Q {x0:.2f} {y0:.2f} {x0 + corner_r:.2f} {y0:.2f} "
        f"L {cx1:.2f} {y0:.2f} "
        f"A {r1:.2f} {r1:.2f} 0 0 1 {ix:.2f} {iy:.2f} "
        f"A {r2:.2f} {r2:.2f} 0 0 1 {cx2:.2f} {y0 + h:.2f} "
        f"L {x0 + corner_r:.2f} {y0 + h:.2f} "
        f"Q {x0:.2f} {y0 + h:.2f} {x0:.2f} {y0 + h - corner_r:.2f} Z"
    )

    mid_y = iy
    t_top = y0 + bar
    t_bot = mid_y - bar * 0.48
    tr = (t_bot - t_top) / 2.0
    t_cx = x0 + w_top - stem * 0.94 - tr
    in_top = (
        f"M {x0 + stem:.2f} {t_top:.2f} "
        f"L {t_cx:.2f} {t_top:.2f} "
        f"A {tr:.2f} {tr:.2f} 0 0 1 {t_cx:.2f} {t_bot:.2f} "
        f"L {x0 + stem:.2f} {t_bot:.2f} Z"
    )

    b_top = mid_y + bar * 0.50
    b_bot = y0 + h - bar
    br = (b_bot - b_top) / 2.0
    b_cx = x0 + w_bot - stem * 0.94 - br
    in_bot = (
        f"M {x0 + stem:.2f} {b_top:.2f} "
        f"L {b_cx:.2f} {b_top:.2f} "
        f"A {br:.2f} {br:.2f} 0 0 1 {b_cx:.2f} {b_bot:.2f} "
        f"L {x0 + stem:.2f} {b_bot:.2f} Z"
    )
    return f"{outer} {in_top} {in_bot}"


def _bc_c_path(x0, y0, w, h, stroke_x=14.8, stroke_y=12.8) -> str:
    """Geometric stadium 'C' path with balanced vertical/horizontal weight."""
    r = w * 0.50
    cx = x0 + r
    cy_top = y0 + r
    cy_bot = y0 + h - r
    ang = math.radians(15)

    ox1 = cx + r * math.cos(-ang)
    oy1 = cy_top + r * math.sin(-ang)
    ox2 = cx + r * math.cos(ang)
    oy2 = cy_bot + r * math.sin(ang)

    rxi = r - stroke_x
    ryi = r - stroke_y
    ix1 = cx + rxi * math.cos(-ang)
    iy1 = cy_top + ryi * math.sin(-ang)
    ix2 = cx + rxi * math.cos(ang)
    iy2 = cy_bot + ryi * math.sin(ang)

    return (
        f"M {ox1:.2f} {oy1:.2f} "
        f"A {r:.2f} {r:.2f} 0 0 0 {x0:.2f} {cy_top:.2f} "
        f"L {x0:.2f} {cy_bot:.2f} "
        f"A {r:.2f} {r:.2f} 0 0 0 {ox2:.2f} {oy2:.2f} "
        f"L {ix2:.2f} {iy2:.2f} "
        f"A {rxi:.2f} {ryi:.2f} 0 0 1 {x0 + stroke_x:.2f} {cy_bot:.2f} "
        f"L {x0 + stroke_x:.2f} {cy_top:.2f} "
        f"A {rxi:.2f} {ryi:.2f} 0 0 1 {ix1:.2f} {iy1:.2f} Z"
    )


def bcastell_floating_svg() -> str:
    """Floating BC favicon SVG with prefers-color-scheme light/dark colors."""
    b_d = _bc_b_path(10, 20, 50, 88, stem=15.0, bar=12.5, corner_r=3.0)
    c_d = _bc_c_path(68, 19.5, 50, 89, stroke_x=14.8, stroke_y=12.8)
    return (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 128 128">\n'
        "  <style>\n"
        f"    .b {{ fill: {SITE_BLUE_LIGHT}; }}\n"
        f"    .c {{ fill: {SITE_GREY_LIGHT}; }}\n"
        "    @media (prefers-color-scheme: dark) {\n"
        f"      .b {{ fill: {SITE_BLUE_DARK}; }}\n"
        f"      .c {{ fill: {SITE_GREY_DARK}; }}\n"
        "    }\n"
        "  </style>\n"
        f'  <path class="b" fill="{SITE_BLUE_LIGHT}" fill-rule="evenodd" d="{b_d}"/>\n'
        f'  <path class="c" fill="{SITE_GREY_LIGHT}" d="{c_d}"/>\n'
        "</svg>\n"
    )


def bcastell_badge_svg(full_bleed: bool = False, compact: bool = False) -> str:
    """Dark site-palette card containing the BC mark.

    - Default: rounded card with subtle border (used for 32-256px .ico planes).
    - compact=True: tighter padding and larger letters for crisp 16/24px tabs.
    - full_bleed=True: opaque square with no rounded corners or border, sized
      for apple-touch-icon.png so iOS and Firefox New Tab apply their own mask
      cleanly without corner artifacts.
    """
    if compact:
        b_d = _bc_b_path(12, 20, 48, 88, stem=14.5, bar=12.0, corner_r=2.5)
        c_d = _bc_c_path(68, 19.5, 48, 89, stroke_x=14.2, stroke_y=12.2)
        rect = '<rect x="0" y="0" width="128" height="128" rx="22" fill="url(#bg)"/>'
    elif full_bleed:
        b_d = _bc_b_path(19, 27, 43, 74, stem=12.5, bar=10.5, corner_r=2.5)
        c_d = _bc_c_path(68, 26.5, 42, 75, stroke_x=12.2, stroke_y=10.8)
        rect = '<rect x="0" y="0" width="128" height="128" fill="url(#bg)"/>'
    else:
        b_d = _bc_b_path(19, 27, 43, 74, stem=12.5, bar=10.5, corner_r=2.5)
        c_d = _bc_c_path(68, 26.5, 42, 75, stroke_x=12.2, stroke_y=10.8)
        rect = (
            f'<rect x="4" y="4" width="120" height="120" rx="26" '
            f'fill="url(#bg)" stroke="{SITE_BORDER}" stroke-width="2.5"/>'
        )
    return (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 128 128">\n'
        "  <defs>\n"
        '    <linearGradient id="bg" x1="0" y1="0" x2="0" y2="1">\n'
        f'      <stop offset="0%" stop-color="{SITE_BG_TOP}"/>\n'
        f'      <stop offset="100%" stop-color="{SITE_BG_BOT}"/>\n'
        "    </linearGradient>\n"
        "  </defs>\n"
        f"  {rect}\n"
        f'  <path fill="{SITE_BLUE_DARK}" fill-rule="evenodd" d="{b_d}"/>\n'
        f'  <path fill="{SITE_GREY_DARK}" d="{c_d}"/>\n'
        "</svg>\n"
    )


def render_site_icons() -> None:
    """Write bcastell.com master SVGs and export favicon.svg, .ico, and touch icon."""
    img_dir = os.path.join(REPO, "static", "img")
    static_dir = os.path.join(REPO, "static")

    floating = bcastell_floating_svg()
    badge = bcastell_badge_svg()
    badge_compact = bcastell_badge_svg(compact=True)
    touch_svg = bcastell_badge_svg(full_bleed=True)

    for path, content in [
        (os.path.join(HERE, "bcastell.svg"), floating),
        (os.path.join(HERE, "bcastell-badge.svg"), badge),
        (os.path.join(img_dir, "favicon.svg"), floating),
    ]:
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        print("wrote", path)

    # 180x180 opaque apple-touch-icon.png (iOS home screen + Firefox New Tab tile).
    render(touch_svg, os.path.join(img_dir, "apple-touch-icon.png"), 180, 180)

    # Multi-size favicon.ico (16-256px) at /img/favicon.ico and root /favicon.ico.
    planes = {}
    for s in SITE_ICO_SIZES:
        src = badge_compact if s <= 24 else badge
        png = resvg_py.svg_to_bytes(svg_string=src, width=s, height=s, skip_system_fonts=True)
        planes[s] = Image.open(io.BytesIO(bytes(png))).convert("RGBA")

    largest = max(SITE_ICO_SIZES)
    append_imgs = [planes[s] for s in SITE_ICO_SIZES if s != largest]
    for ico_path in (
        os.path.join(img_dir, "favicon.ico"),
        os.path.join(static_dir, "favicon.ico"),
    ):
        planes[largest].save(
            ico_path,
            format="ICO",
            sizes=[(s, s) for s in SITE_ICO_SIZES],
            append_images=append_imgs,
        )
        print("wrote", ico_path)


def main() -> None:
    os.makedirs(OUT, exist_ok=True)
    render_site_icons()
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
