"""
SVG visuals for the maths tabs:
  * number_line_svg      - a number line with a start point, an end point and a jump arrow
  * coordinate_grid_svg  - a coordinate grid with points, shapes, mirror lines and arrows

Everything is returned as a single-line SVG string so it can be shown with
st.markdown(svg, unsafe_allow_html=True).
"""

MINUS = "\u2212"


def fmt(n):
    """Format an integer with a proper minus sign."""
    return f"{MINUS}{abs(n)}" if n < 0 else str(n)


def number_line_svg(start, end):
    """Number line from just below the smaller of (start, end, 0) to just above the larger."""
    lo = min(start, end, 0) - 2
    hi = max(start, end, 0) + 2
    span = hi - lo

    if span <= 26:
        label_step = 1
    elif span <= 60:
        label_step = 5
    elif span <= 130:
        label_step = 10
    else:
        label_step = 20

    width, margin, axis_y, height = 720, 30, 105, 190

    def x(n):
        return margin + (n - lo) * (width - 2 * margin) / span

    parts = [
        f'<svg viewBox="0 0 {width} {height}" xmlns="http://www.w3.org/2000/svg" '
        f'style="max-width:100%;height:auto;">',
        '<defs><marker id="nlarrow" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="4.5" '
        'markerHeight="4.5" orient="auto"><path d="M0 0 L10 5 L0 10 z" fill="#f77f00"/></marker></defs>',
        # negative side tinted blue, positive side tinted yellow
        f'<rect x="{x(lo):.1f}" y="{axis_y - 60}" width="{x(0) - x(lo):.1f}" height="95" fill="#e8f1ff"/>',
        f'<rect x="{x(0):.1f}" y="{axis_y - 60}" width="{x(hi) - x(0):.1f}" height="95" fill="#fff8e1"/>',
        f'<text x="{x(lo) + 6:.1f}" y="{axis_y - 44}" font-size="12" fill="#457b9d">negative numbers</text>',
        f'<text x="{x(hi) - 6:.1f}" y="{axis_y - 44}" font-size="12" fill="#b08900" '
        f'text-anchor="end">positive numbers</text>',
        f'<line x1="{x(lo):.1f}" y1="{axis_y}" x2="{x(hi):.1f}" y2="{axis_y}" stroke="#1d3557" stroke-width="3"/>',
    ]

    for n in range(lo, hi + 1):
        major = n % label_step == 0
        tick = 9 if major else 5
        colour = "#e63946" if n == 0 else "#1d3557"
        parts.append(
            f'<line x1="{x(n):.1f}" y1="{axis_y - tick}" x2="{x(n):.1f}" y2="{axis_y + tick}" '
            f'stroke="{colour}" stroke-width="{3 if n == 0 else 1.5}"/>'
        )
        if major:
            weight = "bold" if n == 0 else "normal"
            parts.append(
                f'<text x="{x(n):.1f}" y="{axis_y + 28}" font-size="13" text-anchor="middle" '
                f'fill="{colour}" font-weight="{weight}">{fmt(n)}</text>'
            )

    if start != end:
        arch = 38 + min(30, abs(x(end) - x(start)) / 10)
        parts.append(
            f'<path d="M{x(start):.1f} {axis_y - 12} Q{(x(start) + x(end)) / 2:.1f} {axis_y - 12 - arch:.1f} '
            f'{x(end):.1f} {axis_y - 12}" fill="none" stroke="#f77f00" stroke-width="3.5" '
            f'marker-end="url(#nlarrow)"/>'
        )

    parts.append(f'<circle cx="{x(start):.1f}" cy="{axis_y}" r="7" fill="#457b9d" stroke="#1d3557" stroke-width="2"/>')
    parts.append(f'<circle cx="{x(end):.1f}" cy="{axis_y}" r="7" fill="#2a9d8f" stroke="#1b5c53" stroke-width="2"/>')
    if start == end:
        parts.append(
            f'<text x="{x(start):.1f}" y="{axis_y + 50}" font-size="13" text-anchor="middle" '
            f'fill="#1b5c53" font-weight="bold">start = end = {fmt(start)}</text>'
        )
    else:
        parts.append(
            f'<text x="{x(start):.1f}" y="{axis_y + 50}" font-size="13" text-anchor="middle" '
            f'fill="#1d3557" font-weight="bold">start {fmt(start)}</text>'
        )
        parts.append(
            f'<text x="{x(end):.1f}" y="{axis_y + 66}" font-size="13" text-anchor="middle" '
            f'fill="#1b5c53" font-weight="bold">answer {fmt(end)}</text>'
        )
    parts.append("</svg>")
    return "".join(parts)


def coordinate_grid_svg(xmin, xmax, ymin, ymax, points=None, polygon=None, closed=True,
                        mirror=None, lines=None):
    """
    Draw a coordinate grid.

    points  : list of dicts {x, y, label, color, hollow}
    polygon : list of (x, y) vertices drawn as an outline (closed or open)
    mirror  : ("x", m) for the vertical line x = m, or ("y", m) for y = m
    lines   : list of dicts {from, to, color, dashed, arrow} for guide lines / arrows
    """
    points = points or []
    lines = lines or []
    x_range, y_range = xmax - xmin, ymax - ymin
    cell = max(22, min(40, 520 // max(x_range, y_range)))
    ml, mr, mt, mb = 38, 26, 18, 34
    width = ml + x_range * cell + mr
    height = mt + y_range * cell + mb

    def sx(v):
        return ml + (v - xmin) * cell

    def sy(v):
        return mt + (ymax - v) * cell

    parts = [
        f'<svg viewBox="0 0 {width} {height}" xmlns="http://www.w3.org/2000/svg" '
        f'style="max-width:{width}px;width:100%;height:auto;">',
        '<defs>'
        '<marker id="cgarrow" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="4.5" markerHeight="4.5" '
        'orient="auto"><path d="M0 0 L10 5 L0 10 z" fill="#f77f00"/></marker>'
        '<marker id="cgguide" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="4.5" markerHeight="4.5" '
        'orient="auto"><path d="M0 0 L10 5 L0 10 z" fill="#6c757d"/></marker>'
        '</defs>',
        f'<rect x="{sx(xmin)}" y="{sy(ymax)}" width="{x_range * cell}" height="{y_range * cell}" fill="#ffffff"/>',
    ]

    # Grid lines and tick labels
    for xv in range(xmin, xmax + 1):
        parts.append(
            f'<line x1="{sx(xv)}" y1="{sy(ymax)}" x2="{sx(xv)}" y2="{sy(ymin)}" stroke="#d0d7de" stroke-width="1"/>'
        )
        parts.append(
            f'<text x="{sx(xv)}" y="{sy(ymin) + 16}" font-size="12" text-anchor="middle" fill="#1d3557">{fmt(xv)}</text>'
        )
    for yv in range(ymin, ymax + 1):
        parts.append(
            f'<line x1="{sx(xmin)}" y1="{sy(yv)}" x2="{sx(xmax)}" y2="{sy(yv)}" stroke="#d0d7de" stroke-width="1"/>'
        )
        parts.append(
            f'<text x="{sx(xmin) - 7}" y="{sy(yv) + 4}" font-size="12" text-anchor="end" fill="#1d3557">{fmt(yv)}</text>'
        )

    # Axes
    parts.append(
        f'<line x1="{sx(0)}" y1="{sy(ymax)}" x2="{sx(0)}" y2="{sy(ymin)}" stroke="#1d3557" stroke-width="2.5"/>'
    )
    parts.append(
        f'<line x1="{sx(xmin)}" y1="{sy(0)}" x2="{sx(xmax)}" y2="{sy(0)}" stroke="#1d3557" stroke-width="2.5"/>'
    )
    parts.append(
        f'<text x="{sx(xmax) + 8}" y="{sy(0) + 5}" font-size="14" font-style="italic" font-weight="bold" '
        f'fill="#1d3557">x</text>'
    )
    parts.append(
        f'<text x="{sx(0) + 8}" y="{sy(ymax) - 4}" font-size="14" font-style="italic" font-weight="bold" '
        f'fill="#1d3557">y</text>'
    )

    # Mirror line
    if mirror:
        axis, m = mirror
        if axis == "x":
            parts.append(
                f'<line x1="{sx(m)}" y1="{sy(ymax)}" x2="{sx(m)}" y2="{sy(ymin)}" stroke="#e63946" '
                f'stroke-width="3" stroke-dasharray="8 5"/>'
            )
            parts.append(
                f'<text x="{sx(m) + 5}" y="{sy(ymax) + 14}" font-size="12" fill="#e63946" '
                f'font-weight="bold">mirror x = {fmt(m)}</text>'
            )
        else:
            parts.append(
                f'<line x1="{sx(xmin)}" y1="{sy(m)}" x2="{sx(xmax)}" y2="{sy(m)}" stroke="#e63946" '
                f'stroke-width="3" stroke-dasharray="8 5"/>'
            )
            parts.append(
                f'<text x="{sx(xmax) - 5}" y="{sy(m) - 6}" font-size="12" fill="#e63946" '
                f'font-weight="bold" text-anchor="end">mirror y = {fmt(m)}</text>'
            )

    # Shape outline
    if polygon:
        coords = " ".join(f"{sx(px)},{sy(py)}" for px, py in polygon)
        if closed:
            parts.append(
                f'<polygon points="{coords}" fill="rgba(69,123,157,0.18)" stroke="#457b9d" stroke-width="3"/>'
            )
        else:
            parts.append(f'<polyline points="{coords}" fill="none" stroke="#457b9d" stroke-width="3"/>')

    # Guide lines / arrows
    for ln in lines:
        (x1, y1), (x2, y2) = ln["from"], ln["to"]
        colour = ln.get("color", "#6c757d")
        dash = ' stroke-dasharray="5 4"' if ln.get("dashed") else ""
        marker = ""
        if ln.get("arrow"):
            marker = ' marker-end="url(#cgarrow)"' if colour == "#f77f00" else ' marker-end="url(#cgguide)"'
        px1, py1, px2, py2 = sx(x1), sy(y1), sx(x2), sy(y2)
        if ln.get("arrow"):
            length = ((px2 - px1) ** 2 + (py2 - py1) ** 2) ** 0.5
            if length > 14:  # pull the end back so the arrowhead sits beside the dot, not under it
                px2 -= (px2 - px1) / length * 11
                py2 -= (py2 - py1) / length * 11
        parts.append(
            f'<line x1="{px1:.1f}" y1="{py1:.1f}" x2="{px2:.1f}" y2="{py2:.1f}" stroke="{colour}" '
            f'stroke-width="2.5"{dash}{marker}/>'
        )

    # Points on top
    for p in points:
        colour = p.get("color", "#e63946")
        if p.get("hollow"):
            parts.append(
                f'<circle cx="{sx(p["x"])}" cy="{sy(p["y"])}" r="7" fill="#ffffff" stroke="{colour}" '
                f'stroke-width="2.5" stroke-dasharray="3 2"/>'
            )
        else:
            parts.append(
                f'<circle cx="{sx(p["x"])}" cy="{sy(p["y"])}" r="7" fill="{colour}" stroke="#ffffff" stroke-width="1.5"/>'
            )
        if p.get("label"):
            # Keep labels inside the picture: flip left near the right edge, drop below near the top.
            near_right = p["x"] > xmin + 0.6 * x_range
            near_top = p["y"] >= ymax - 0.06 * y_range
            tx = sx(p["x"]) + (-10 if near_right else 10)
            ty = sy(p["y"]) + (20 if near_top else -9)
            anchor = "end" if near_right else "start"
            common = f'x="{tx}" y="{ty}" font-size="14" font-weight="bold" text-anchor="{anchor}"'
            # white halo layer underneath, coloured text on top (works in every renderer)
            parts.append(f'<text {common} fill="#ffffff" stroke="#ffffff" stroke-width="4">{p["label"]}</text>')
            parts.append(f'<text {common} fill="{colour}">{p["label"]}</text>')

    parts.append("</svg>")
    return "".join(parts)
