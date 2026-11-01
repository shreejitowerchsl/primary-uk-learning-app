"""
SVG drawing primitives for the Non-Verbal Reasoning tab.

Everything returns single-line SVG strings (no newlines) so they can be shown with
st.markdown(svg, unsafe_allow_html=True).
"""

import math

INK = "#1d3557"
FILL_COLOR = {"black": "#1d3557", "white": "#ffffff", "grey": "#a9b8cc"}
SHAPES = ["circle", "square", "triangle", "star", "diamond", "pentagon"]
FILLS = ["black", "white", "grey"]
ACCENT = "#f77f00"
PIECE = "#457b9d"

CUBE_COLORS = {
    "red": "#e63946", "blue": "#1d6fb8", "green": "#2a9d8f",
    "yellow": "#ffd166", "purple": "#8e5bd0", "grey": "#9aa5b1",
}


# =============================================================================
# SHAPES AND FIGURES
# =============================================================================

def fig(shape="circle", fill="black", size="large", count=1, rot=0):
    """A figure: 1-3 identical shapes, with a fill, a size and (for triangles/arrows) a rotation."""
    return {"shape": shape, "fill": fill, "size": size, "count": count, "rot": rot}


def _rotate(points, cx, cy, deg):
    a = math.radians(deg)
    out = []
    for x, y in points:
        dx, dy = x - cx, y - cy
        out.append((cx + dx * math.cos(a) - dy * math.sin(a), cy + dx * math.sin(a) + dy * math.cos(a)))
    return out


def _regular(n, cx, cy, r, rot=0):
    pts = []
    for i in range(n):
        a = math.radians(rot + i * 360 / n)
        pts.append((cx + r * math.sin(a), cy - r * math.cos(a)))
    return pts


def _pts(points):
    return " ".join(f"{x:.1f},{y:.1f}" for x, y in points)


def shape_svg(shape, cx, cy, r, fill="black", rot=0):
    style = f'fill="{FILL_COLOR[fill]}" stroke="{INK}" stroke-width="2.5" stroke-linejoin="round"'
    if shape == "circle":
        return f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r:.1f}" {style}/>'
    if shape == "square":
        return f'<polygon points="{_pts(_regular(4, cx, cy, r * 1.2, rot + 45))}" {style}/>'
    if shape == "triangle":
        return f'<polygon points="{_pts(_regular(3, cx, cy + r * 0.12, r * 1.2, rot))}" {style}/>'
    if shape == "pentagon":
        return f'<polygon points="{_pts(_regular(5, cx, cy, r * 1.12, rot))}" {style}/>'
    if shape == "diamond":
        pts = [(cx, cy - r * 1.3), (cx + r * 0.85, cy), (cx, cy + r * 1.3), (cx - r * 0.85, cy)]
        return f'<polygon points="{_pts(_rotate(pts, cx, cy, rot))}" {style}/>'
    if shape == "star":
        pts = []
        for i in range(10):
            a = math.radians(rot + i * 36)
            rr = r * 1.3 if i % 2 == 0 else r * 0.58
            pts.append((cx + rr * math.sin(a), cy - rr * math.cos(a)))
        return f'<polygon points="{_pts(pts)}" {style}/>'
    if shape == "arrow":
        pts = [(0, -1.3), (0.95, 0), (0.38, 0), (0.38, 1.15), (-0.38, 1.15), (-0.38, 0), (-0.95, 0)]
        pts = [(cx + x * r, cy + y * r) for x, y in pts]
        return f'<polygon points="{_pts(_rotate(pts, cx, cy, rot))}" {style}/>'
    raise ValueError(shape)


_RADIUS = {1: {"large": 25, "small": 13}, 2: {"large": 17, "small": 10}, 3: {"large": 13, "small": 8}}
_SPOTS = {1: [(50, 50)], 2: [(29, 50), (71, 50)], 3: [(50, 27), (27, 70), (73, 70)]}


def figure_group(f):
    """The shapes of one figure, drawn inside a 100x100 cell."""
    r = _RADIUS[f["count"]][f["size"]]
    return "".join(shape_svg(f["shape"], x, y, r, f["fill"], f["rot"]) for x, y in _SPOTS[f["count"]])


def tile_svg(inner, label=None, width=100):
    """A single 100x100 tile with an optional A/B/C... label underneath."""
    height = 122 if label else 100
    text = (
        f'<text x="50" y="117" text-anchor="middle" font-size="19" font-weight="bold" fill="{INK}">{label}</text>'
        if label else ""
    )
    return (
        f'<svg viewBox="0 0 100 {height}" xmlns="http://www.w3.org/2000/svg" '
        f'style="max-width:{width}px;width:100%;height:auto;">'
        f'<rect x="1.5" y="1.5" width="97" height="97" rx="8" fill="#ffffff" stroke="#8d99ae" stroke-width="2"/>'
        f'{inner}{text}</svg>'
    )


def figure_tile(f, label=None, width=100):
    return tile_svg(figure_group(f), label, width)


def question_tile(label=None, width=100):
    return tile_svg(f'<text x="50" y="68" text-anchor="middle" font-size="56" font-weight="bold" fill="{ACCENT}">?</text>',
                    label, width)


def row_html(svgs, gap=10, extra=""):
    """Lay several SVGs out in a row (single line of HTML)."""
    cells = "".join(f'<div style="flex:0 1 110px;min-width:70px">{s}</div>' if not s.startswith("<div") else s for s in svgs)
    return (f'<div style="display:flex;flex-wrap:wrap;gap:{gap}px;align-items:center;'
            f'justify-content:center;margin:8px 0;{extra}">{cells}</div>')


def big_html(svg, width=300):
    """Show one larger picture (matrix, net, big cube...) centred, without shrinking it to tile size."""
    return (f'<div style="display:flex;justify-content:center;margin:8px 0;flex:1 1 100%">'
            f'<div style="width:{width}px;max-width:100%">{svg}</div></div>')


def text_cell(text, size=26):
    return (f'<div style="flex:0 0 auto;font-size:{size}px;font-weight:800;color:{INK};padding:0 4px">{text}</div>')


# =============================================================================
# MATRIX (3x3 grid of figures with one missing)
# =============================================================================

def matrix_svg(figs, missing=(2, 2), cell=100, gap=8):
    """figs: dict {(row, col): figure}. The cell at `missing` is drawn as a '?'."""
    size = cell * 3 + gap * 2
    parts = [f'<svg viewBox="0 0 {size} {size}" xmlns="http://www.w3.org/2000/svg" style="max-width:330px;width:100%;height:auto;">']
    for r in range(3):
        for c in range(3):
            x, y = c * (cell + gap), r * (cell + gap)
            parts.append(f'<g transform="translate({x},{y})"><rect x="1.5" y="1.5" width="97" height="97" rx="8" fill="#fff" '
                         f'stroke="#8d99ae" stroke-width="2"/>')
            if (r, c) == missing:
                parts.append(f'<text x="50" y="68" text-anchor="middle" font-size="56" font-weight="bold" fill="{ACCENT}">?</text>')
            else:
                parts.append(figure_group(figs[(r, c)]))
            parts.append("</g>")
    parts.append("</svg>")
    return "".join(parts)


# =============================================================================
# GRID PATTERNS (rotation) AND POLYOMINO PIECES
# =============================================================================

def pattern_svg(cells, n, accent=None, label=None, width=100):
    """A shape made of filled squares on an n x n grid; `accent` is one cell drawn in orange."""
    step = 80 / n
    parts = []
    for r in range(n):
        for c in range(n):
            x, y = 10 + c * step, 10 + r * step
            parts.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{step:.1f}" height="{step:.1f}" fill="none" stroke="#dfe5ec" stroke-width="1"/>')
    for r, c in sorted(cells):
        x, y = 10 + c * step, 10 + r * step
        colour = ACCENT if (r, c) == accent else PIECE
        parts.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{step:.1f}" height="{step:.1f}" fill="{colour}" stroke="#ffffff" stroke-width="1.5"/>')
    return tile_svg("".join(parts), label, width)


def piece_svg(cells, label=None, width=100, colour=PIECE):
    """A polyomino piece scaled to fit a tile."""
    rows = [r for r, c in cells]
    cols = [c for r, c in cells]
    h, w = max(rows) - min(rows) + 1, max(cols) - min(cols) + 1
    step = min(20, 80 / max(h, w))   # same square size for every piece, so size is never a clue
    ox = 50 - w * step / 2
    oy = 50 - h * step / 2
    parts = []
    for r, c in sorted(cells):
        x, y = ox + (c - min(cols)) * step, oy + (r - min(rows)) * step
        parts.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{step:.1f}" height="{step:.1f}" fill="{colour}" stroke="#ffffff" stroke-width="1.5"/>')
    return tile_svg("".join(parts), label, width)


def hole_svg(width_cells, height_cells, hole, size=240):
    """A rectangle of grey squares with a gap (the `hole` cells) drawn as a dashed white hole."""
    step = min(size / max(width_cells, height_cells), 56)
    w, h = width_cells * step, height_cells * step
    parts = [f'<svg viewBox="0 0 {w + 8:.0f} {h + 8:.0f}" xmlns="http://www.w3.org/2000/svg" style="max-width:{w + 8:.0f}px;width:100%;height:auto;">']
    for r in range(height_cells):
        for c in range(width_cells):
            x, y = 4 + c * step, 4 + r * step
            if (r, c) in hole:
                parts.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{step:.1f}" height="{step:.1f}" fill="#fff8e1" stroke="{ACCENT}" stroke-width="2" stroke-dasharray="5 3"/>')
            else:
                parts.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{step:.1f}" height="{step:.1f}" fill="#b8c4d2" stroke="#ffffff" stroke-width="2"/>')
    parts.append("</svg>")
    return "".join(parts)


# =============================================================================
# LINE FIGURES (embedded figures)
# =============================================================================

def edges_svg(edges, n=4, label=None, width=100, colour=INK, show_dots=True, highlight=()):
    """Unit edges ((x1,y1),(x2,y2)) on an (n+1) x (n+1) lattice of points. `highlight` edges are drawn in orange."""
    step = 80 / n
    highlight = set(highlight)
    parts = []
    if show_dots:
        for i in range(n + 1):
            for j in range(n + 1):
                parts.append(f'<circle cx="{10 + i * step:.1f}" cy="{10 + j * step:.1f}" r="1.8" fill="#b8c4d2"/>')
    ordered = [e for e in sorted(edges) if e not in highlight] + [e for e in sorted(edges) if e in highlight]
    for e in ordered:
        (x1, y1), (x2, y2) = e
        stroke = ACCENT if e in highlight else colour
        parts.append(f'<line x1="{10 + x1 * step:.1f}" y1="{10 + y1 * step:.1f}" x2="{10 + x2 * step:.1f}" y2="{10 + y2 * step:.1f}" '
                     f'stroke="{stroke}" stroke-width="3.6" stroke-linecap="round"/>')
    return tile_svg("".join(parts), label, width)


# =============================================================================
# OVERLAPPING SHAPES AND DOTS
# =============================================================================

def venn_svg(layout, dot=None, shapes=("circle", "square", "triangle"), label=None, width=100):
    """layout: {'circle': (cx, cy, r), 'square': (x, y, w), 'triangle': [(x,y)x3]}"""
    parts = []
    if "circle" in shapes:
        cx, cy, r = layout["circle"]
        parts.append(f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="rgba(230,57,70,0.16)" stroke="#e63946" stroke-width="2.5"/>')
    if "square" in shapes:
        x, y, w = layout["square"]
        parts.append(f'<rect x="{x}" y="{y}" width="{w}" height="{w}" fill="rgba(42,157,143,0.16)" stroke="#2a9d8f" stroke-width="2.5"/>')
    if "triangle" in shapes:
        pts = " ".join(f"{x},{y}" for x, y in layout["triangle"])
        parts.append(f'<polygon points="{pts}" fill="rgba(244,162,97,0.22)" stroke="#d97706" stroke-width="2.5" stroke-linejoin="round"/>')
    if dot:
        parts.append(f'<circle cx="{dot[0]}" cy="{dot[1]}" r="4.6" fill="#111" stroke="#ffffff" stroke-width="1.5"/>')
    return tile_svg("".join(parts), label, width)


# =============================================================================
# CUBES AND NETS
# =============================================================================

_PIPS = {
    1: [(0.5, 0.5)],
    2: [(0.27, 0.27), (0.73, 0.73)],
    3: [(0.27, 0.27), (0.5, 0.5), (0.73, 0.73)],
    4: [(0.27, 0.27), (0.73, 0.27), (0.27, 0.73), (0.73, 0.73)],
    5: [(0.27, 0.27), (0.73, 0.27), (0.5, 0.5), (0.27, 0.73), (0.73, 0.73)],
    6: [(0.27, 0.22), (0.73, 0.22), (0.27, 0.5), (0.73, 0.5), (0.27, 0.78), (0.73, 0.78)],
}
_TOP = "matrix(36 18 -36 18 50 12)"
_LEFT = "matrix(36 18 0 40 14 30)"
_RIGHT = "matrix(36 -18 0 40 50 48)"


def _face(points, fill):
    return f'<polygon points="{points}" fill="{fill}" stroke="{INK}" stroke-width="2.4" stroke-linejoin="round"/>'


def cube_svg(top, left, right, label=None, width=100, pips=False):
    """An isometric cube showing three faces. Faces are colour names, or pip counts when pips=True."""
    parts = []
    faces = [
        ("50,12 86,30 50,48 14,30", _TOP, top),
        ("14,30 50,48 50,88 14,70", _LEFT, left),
        ("50,48 86,30 86,70 50,88", _RIGHT, right),
    ]
    for polygon, matrix, value in faces:
        if pips:
            parts.append(_face(polygon, "#fdfdfd"))
            dots = "".join(f'<circle cx="{x}" cy="{y}" r="0.085" fill="#1d3557"/>' for x, y in _PIPS[value])
            parts.append(f'<g transform="{matrix}">{dots}</g>')
        else:
            parts.append(_face(polygon, CUBE_COLORS[value]))
    return tile_svg("".join(parts), label, width)


def net_svg(cells, width=260):
    """cells: {(col, row): colour_name} laid out as a cube net."""
    cols = [c for c, r in cells]
    rows = [r for c, r in cells]
    w, h = max(cols) - min(cols) + 1, max(rows) - min(rows) + 1
    step = 40
    parts = [f'<svg viewBox="0 0 {w * step + 8} {h * step + 8}" xmlns="http://www.w3.org/2000/svg" style="max-width:{width}px;width:100%;height:auto;">']
    for (c, r), colour in cells.items():
        x, y = 4 + (c - min(cols)) * step, 4 + (r - min(rows)) * step
        parts.append(f'<rect x="{x}" y="{y}" width="{step}" height="{step}" fill="{CUBE_COLORS[colour]}" stroke="{INK}" stroke-width="2.4"/>')
    parts.append("</svg>")
    return "".join(parts)
