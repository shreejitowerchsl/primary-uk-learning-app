"""
Coordinates chapter.

Levels
  🟢 Beginner     - first quadrant, grid 0-10
  🟡 Intermediate - first quadrant, grid 0-12, two-direction moves, reflections
  🔴 Advanced     - all four quadrants (negative coordinates), grid -8 to 8

Question types
  📍 Read the coordinates     🔤 Find the point         🔲 Missing corner
  ➡️ Translation              🪞 Reflection             📏 Distance between points
  🧭 Which quadrant?          🎲 Mixed
"""

import random

import streamlit as st

from modules.helpers import record_attempt, show_feedback
from modules.maths.visuals import coordinate_grid_svg, fmt

LEVELS = {
    "🟢 Beginner": {"xmin": 0, "xmax": 10, "ymin": 0, "ymax": 10},
    "🟡 Intermediate": {"xmin": 0, "xmax": 12, "ymin": 0, "ymax": 12},
    "🔴 Advanced": {"xmin": -8, "xmax": 8, "ymin": -8, "ymax": 8},
}
FOUR_QUADRANTS = LEVELS["🔴 Advanced"]
LETTERS = "ABCDEFGH"
COLORS = ["#e63946", "#2a9d8f", "#f4a261", "#6a4c93", "#1d3557", "#118ab2", "#8d6e63", "#43aa8b"]
QUADRANT_CHOICES = [
    "Quadrant 1 (top right)",
    "Quadrant 2 (top left)",
    "Quadrant 3 (bottom left)",
    "Quadrant 4 (bottom right)",
]


def pt(x, y):
    return f"({fmt(x)}, {fmt(y)})"


def _grid(g, **kwargs):
    return coordinate_grid_svg(g["xmin"], g["xmax"], g["ymin"], g["ymax"], **kwargs)


def _nonzero(lo, hi):
    return [v for v in range(lo, hi + 1) if v != 0]


def _random_points(g, k):
    """k distinct points, none on an axis (so they're easy to read)."""
    chosen = set()
    while len(chosen) < k:
        chosen.add((random.choice(_nonzero(g["xmin"], g["xmax"])), random.choice(_nonzero(g["ymin"], g["ymax"]))))
    pts = list(chosen)
    random.shuffle(pts)
    return pts


def _path_text(x, y):
    across = f"**{abs(x)} {'right' if x > 0 else 'left'}**"
    updown = f"**{abs(y)} {'up' if y > 0 else 'down'}**"
    return across, updown


def _result(question, svg, answer_type, answer, steps, solution_svg, choices=None):
    return {
        "question": question, "svg": svg, "answer_type": answer_type, "answer": answer,
        "steps": steps, "solution_svg": solution_svg, "choices": choices,
    }


# =============================================================================
# QUESTION GENERATORS
# =============================================================================

def gen_read(g):
    pts = _random_points(g, 4)
    labelled = [{"x": x, "y": y, "label": LETTERS[i], "color": COLORS[i]} for i, (x, y) in enumerate(pts)]
    target = random.choice(labelled)
    x, y = target["x"], target["y"]
    across, updown = _path_text(x, y)

    steps = f"""
**Remember: the x-coordinate always comes first — "along the corridor, then up the stairs"!**

1. Start at the **origin** (0, 0), where the two axes cross.
2. Move {across} along the x-axis (the horizontal line).
3. Move {updown} parallel to the y-axis (the vertical line).

Point **{target['label']}** is at **{pt(x, y)}**.
"""
    solution_points = [dict(p) for p in labelled]
    for p in solution_points:
        if p["label"] == target["label"]:
            p["label"] = f"{target['label']} {pt(x, y)}"
    guides = [
        {"from": (0, 0), "to": (x, 0), "dashed": True, "arrow": True},
        {"from": (x, 0), "to": (x, y), "dashed": True, "arrow": True},
    ]
    return _result(
        f"What are the coordinates of point {target['label']}?",
        _grid(g, points=labelled), "xy", (x, y), steps,
        _grid(g, points=solution_points, lines=guides),
    )


def gen_find(g):
    pts = _random_points(g, 5)
    target_index = random.randrange(5)
    tx, ty = pts[target_index]

    # Classic mistake: swapping x and y. Make sure that point is on the grid as a distractor.
    swapped = None
    if tx != ty and (ty, tx) not in pts:
        swap_index = random.choice([i for i in range(5) if i != target_index])
        pts[swap_index] = (ty, tx)
        swapped = LETTERS[swap_index]

    labelled = [{"x": x, "y": y, "label": LETTERS[i], "color": COLORS[i]} for i, (x, y) in enumerate(pts)]
    label = LETTERS[target_index]
    across, updown = _path_text(tx, ty)
    swap_note = (
        f"\n⚠️ **Careful!** Point {swapped} is at {pt(ty, tx)} — that's the coordinates the wrong way round."
        if swapped else ""
    )
    steps = f"""
1. Start at the **origin** (0, 0).
2. The first number is x = {fmt(tx)}, so move {across}.
3. The second number is y = {fmt(ty)}, so move {updown}.

You land on point **{label}**.{swap_note}
"""
    guides = [
        {"from": (0, 0), "to": (tx, 0), "dashed": True, "arrow": True},
        {"from": (tx, 0), "to": (tx, ty), "dashed": True, "arrow": True},
    ]
    return _result(
        f"Which point is at {pt(tx, ty)}?",
        _grid(g, points=labelled), "choice", label, steps,
        _grid(g, points=labelled, lines=guides),
        choices=[LETTERS[i] for i in range(5)],
    )


def gen_corner(g):
    w, h = random.randint(2, 6), random.randint(2, 6)
    x1 = random.randint(g["xmin"], g["xmax"] - w)
    y1 = random.randint(g["ymin"], g["ymax"] - h)
    x2, y2 = x1 + w, y1 + h
    verts = [(x1, y1), (x2, y1), (x2, y2), (x1, y2)]  # A, B, C, D go round the rectangle
    hidden = random.randrange(4)
    hx, hy = verts[hidden]
    visible = [(i, verts[i]) for i in [(hidden + k) % 4 for k in (1, 2, 3)]]  # consecutive corners

    same_x = next(i for i, (vx, vy) in visible if vx == hx)
    same_y = next(i for i, (vx, vy) in visible if vy == hy)

    shown_text = ", ".join(f"{LETTERS[i]} = {pt(*v)}" for i, v in visible)
    labelled = [{"x": v[0], "y": v[1], "label": LETTERS[i], "color": COLORS[i]} for i, v in visible]
    question = (
        f"ABCD is a rectangle with its sides parallel to the axes. Three corners are {shown_text}. "
        f"What are the coordinates of corner {LETTERS[hidden]}?"
    )
    steps = f"""
The sides of the rectangle run along the grid lines, so:

- Corner **{LETTERS[hidden]}** is directly above or below corner **{LETTERS[same_x]}**, so it has the **same x-coordinate**: x = **{fmt(hx)}**.
- Corner **{LETTERS[hidden]}** is directly left or right of corner **{LETTERS[same_y]}**, so it has the **same y-coordinate**: y = **{fmt(hy)}**.

Corner **{LETTERS[hidden]}** is at **{pt(hx, hy)}**.
"""
    solution_points = [
        {"x": v[0], "y": v[1], "label": f"{LETTERS[i]} {pt(*v)}" if i == hidden else LETTERS[i],
         "color": COLORS[i], "hollow": i == hidden}
        for i, v in enumerate(verts)
    ]
    return _result(
        question,
        _grid(g, points=labelled, polygon=[v for _, v in visible], closed=False),
        "xy", (hx, hy), steps,
        _grid(g, points=solution_points, polygon=verts, closed=True),
    )


def gen_translate(g, level_name):
    four = g is FOUR_QUADRANTS
    for _ in range(400):
        x = random.choice(_nonzero(g["xmin"], g["xmax"]))
        y = random.choice(_nonzero(g["ymin"], g["ymax"]))
        if level_name.startswith("🟢"):
            amount = random.randint(1, 6)
            if random.random() < 0.5:
                dx, dy = random.choice([-amount, amount]), 0
            else:
                dx, dy = 0, random.choice([-amount, amount])
        elif four:
            dx = random.choice([-1, 1]) * random.randint(2, 9)
            dy = random.choice([-1, 1]) * random.randint(2, 9)
        else:
            dx = random.choice([-1, 1]) * random.randint(1, 7)
            dy = random.choice([-1, 1]) * random.randint(1, 7)
        nx, ny = x + dx, y + dy
        if g["xmin"] <= nx <= g["xmax"] and g["ymin"] <= ny <= g["ymax"]:
            if not four or (x * nx < 0 or y * ny < 0 or random.random() < 0.3):
                break
    else:  # extremely unlikely: use a safe, simple move
        x, y, dx, dy = 2, 3, 3, 2
        nx, ny = x + dx, y + dy

    words = []
    if dx:
        words.append(f"{abs(dx)} {'right' if dx > 0 else 'left'}")
    if dy:
        words.append(f"{abs(dy)} {'up' if dy > 0 else 'down'}")
    move_text = " and ".join(words)

    lines = []
    if dx:
        op = "+" if dx > 0 else "−"
        lines.append(f"- Moving **{'right' if dx > 0 else 'left'}** changes the x-coordinate: "
                     f"{fmt(x)} {op} {abs(dx)} = **{fmt(nx)}**")
    if dy:
        op = "+" if dy > 0 else "−"
        lines.append(f"- Moving **{'up' if dy > 0 else 'down'}** changes the y-coordinate: "
                     f"{fmt(y)} {op} {abs(dy)} = **{fmt(ny)}**")
    steps = f"""
A translation slides a point without turning it.

- **Left / right** changes **x** (right adds, left subtracts).
- **Up / down** changes **y** (up adds, down subtracts).

{chr(10).join(lines)}

The new point **A'** is at **{pt(nx, ny)}**.
"""
    start = {"x": x, "y": y, "label": "A", "color": "#e63946"}
    route = [(x, y)]
    if dx:
        route.append((nx, y))
    if dy:
        route.append((nx, ny))
    arrows = [
        {"from": route[i], "to": route[i + 1], "color": "#f77f00", "arrow": True}
        for i in range(len(route) - 1)
    ]
    solution_points = [
        {"x": x, "y": y, "label": f"A {pt(x, y)}", "color": "#e63946", "hollow": True},
        {"x": nx, "y": ny, "label": f"A' {pt(nx, ny)}", "color": "#2a9d8f"},
    ]
    return _result(
        f"Point A is at {pt(x, y)}. It is translated {move_text}. What are the new coordinates of A?",
        _grid(g, points=[start]), "xy", (nx, ny), steps,
        _grid(g, points=solution_points, lines=arrows),
    )


def gen_reflect(g, level_name):
    four = g is FOUR_QUADRANTS
    for _ in range(500):
        axis = random.choice(["x", "y"])  # mirror line x = m (vertical) or y = m (horizontal)
        if four:
            m = random.randint(-4, 4)
        else:
            m = random.randint(2, g["xmax"] - 2)
        lo, hi = (g["xmin"], g["xmax"]) if axis == "x" else (g["ymin"], g["ymax"])
        v = random.choice([n for n in range(lo, hi + 1) if n != m])
        reflected = 2 * m - v
        other = random.choice(_nonzero(g["ymin"], g["ymax"]) if axis == "x" else _nonzero(g["xmin"], g["xmax"]))
        if lo <= reflected <= hi and abs(v - m) >= 1:
            break
    else:  # extremely unlikely: use a safe, simple reflection
        axis, m, v, other, reflected = "x", 5, 3, 4, 7

    x, y = (v, other) if axis == "x" else (other, v)
    nx, ny = (reflected, y) if axis == "x" else (x, reflected)
    d = abs(v - m)

    if m == 0:
        name = "the y-axis" if axis == "x" else "the x-axis"
    else:
        name = f"the mirror line {axis} = {fmt(m)}"
    lineword = "vertical" if axis == "x" else "horizontal"
    coord = "x" if axis == "x" else "y"

    side = "right" if (reflected > m) else "left"
    if axis == "y":
        side = "above" if reflected > m else "below"
    start_side = ("left" if v < m else "right") if axis == "x" else ("below" if v < m else "above")
    steps = f"""
A reflection flips a point over the mirror line. The point and its image are the **same distance** from the mirror, on opposite sides.

1. The mirror is a **{lineword}** line, so only the **{coord}-coordinate** changes. The other coordinate stays the same.
2. Point P has {coord} = {fmt(v)}. The mirror is at {coord} = {fmt(m)}, so P is **{d}** unit{'s' if d != 1 else ''} {start_side} of the mirror line.
3. The image P' is **{d}** unit{'s' if d != 1 else ''} on the {side} side: {coord} = {fmt(m)} {'+' if reflected > m else '−'} {d} = **{fmt(reflected)}**.

The reflected point **P'** is at **{pt(nx, ny)}**.
"""
    mirror = (axis, m)
    q_points = [{"x": x, "y": y, "label": "P", "color": "#e63946"}]
    s_points = [
        {"x": x, "y": y, "label": f"P {pt(x, y)}", "color": "#e63946"},
        {"x": nx, "y": ny, "label": f"P' {pt(nx, ny)}", "color": "#2a9d8f"},
    ]
    connector = [{"from": (x, y), "to": (nx, ny), "dashed": True, "color": "#6c757d"}]
    return _result(
        f"Point P is at {pt(x, y)}. Reflect P in {name}. What are the coordinates of the image P'?",
        _grid(g, points=q_points, mirror=mirror), "xy", (nx, ny), steps,
        _grid(g, points=s_points, mirror=mirror, lines=connector),
    )


def gen_distance(g):
    horizontal = random.random() < 0.5
    for _ in range(300):
        fixed = random.choice(_nonzero(g["ymin"], g["ymax"]) if horizontal else _nonzero(g["xmin"], g["xmax"]))
        lo, hi = (g["xmin"], g["xmax"]) if horizontal else (g["ymin"], g["ymax"])
        p1, p2 = random.randint(lo, hi), random.randint(lo, hi)
        if abs(p1 - p2) >= 2:
            break
    else:
        fixed, p1, p2 = 2, 1, 6
    if horizontal:
        a, b = (p1, fixed), (p2, fixed)
    else:
        a, b = (fixed, p1), (fixed, p2)
    distance = abs(p1 - p2)
    which = "x" if horizontal else "y"
    same = "y" if horizontal else "x"

    if p1 < 0 < p2 or p2 < 0 < p1:
        negative, positive = (p1, p2) if p1 < 0 else (p2, p1)
        working = (
            f"The points are on opposite sides of zero, so split the distance at 0: "
            f"{abs(negative)} + {positive} = **{distance}**."
        )
    else:
        big, small = max(p1, p2), min(p1, p2)
        working = f"Subtract the smaller from the larger: {fmt(big)} − {operand_neg(small)} = **{distance}**."

    steps = f"""
Both points have the same **{same}-coordinate** ({fmt(fixed)}), so they sit on a **{'horizontal' if horizontal else 'vertical'}** line.

Only the **{which}-coordinates** are different: {fmt(p1)} and {fmt(p2)}.

{working}

The points are **{distance}** units apart.
"""
    labelled = [
        {"x": a[0], "y": a[1], "label": "A", "color": "#e63946"},
        {"x": b[0], "y": b[1], "label": "B", "color": "#2a9d8f"},
    ]
    seg = [{"from": a, "to": b, "color": "#f77f00"}]
    return _result(
        f"A is at {pt(*a)} and B is at {pt(*b)}. How many units apart are A and B?",
        _grid(g, points=labelled), "single", distance, steps,
        _grid(g, points=labelled, lines=seg),
    )


def operand_neg(n):
    return f"({fmt(n)})" if n < 0 else fmt(n)


def gen_quadrant(_g=None):
    g = FOUR_QUADRANTS
    x = random.choice(_nonzero(-8, 8))
    y = random.choice(_nonzero(-8, 8))
    index = (0 if y > 0 else 3) if x > 0 else (1 if y > 0 else 2)
    answer = QUADRANT_CHOICES[index]
    steps = f"""
The axes split the grid into **four quadrants**, numbered **anticlockwise** starting at the top right.

- The x-coordinate is **{fmt(x)}**, which is **{'positive → right' if x > 0 else 'negative → left'}** of the y-axis.
- The y-coordinate is **{fmt(y)}**, which is **{'positive → above' if y > 0 else 'negative → below'}** the x-axis.

So the point is in **{answer}**.
"""
    point = [{"x": x, "y": y, "label": "P", "color": "#e63946"}]
    return _result(
        f"Point P is at {pt(x, y)}. Which quadrant is P in?",
        _grid(g, points=point), "choice", answer, steps,
        _grid(g, points=[{"x": x, "y": y, "label": f"P {pt(x, y)}", "color": "#e63946"}]),
        choices=QUADRANT_CHOICES,
    )


TYPES = {
    "📍 Read the coordinates": lambda g, lvl: gen_read(g),
    "🔤 Find the point": lambda g, lvl: gen_find(g),
    "🔲 Missing corner": lambda g, lvl: gen_corner(g),
    "➡️ Translation": gen_translate,
    "🪞 Reflection": gen_reflect,
    "📏 Distance between points": lambda g, lvl: gen_distance(g),
    "🧭 Which quadrant?": lambda g, lvl: gen_quadrant(g),
}
MIXED = "🎲 Mixed"

# Which types "Mixed" picks from, per level.
MIXED_POOL = {
    "🟢 Beginner": ["📍 Read the coordinates", "🔤 Find the point", "🔲 Missing corner",
                    "➡️ Translation", "📏 Distance between points"],
    "🟡 Intermediate": ["📍 Read the coordinates", "🔤 Find the point", "🔲 Missing corner",
                        "➡️ Translation", "🪞 Reflection", "📏 Distance between points"],
    "🔴 Advanced": list(TYPES.keys()),
}


def generate(level, question_type):
    if question_type == MIXED:
        question_type = random.choice(MIXED_POOL[level])
    return TYPES[question_type](LEVELS[level], level)


# =============================================================================
# LESSON
# =============================================================================

def _render_lesson():
    with st.expander("📘 Lesson 1: What are coordinates?"):
        st.markdown(
            """
**Coordinates** tell you exactly where a point is on a grid. They are written in brackets as **(x, y)**.

- The **x-coordinate** (first) tells you how far to go **across** (along the horizontal axis).
- The **y-coordinate** (second) tells you how far to go **up** (along the vertical axis).

A memory trick: **"along the corridor, then up the stairs"** 🏃‍♀️🪜

Everything starts from the **origin**, (0, 0), where the axes cross. In the grid below, point **A is at (2, 3)**
and point **B is at (5, 1)**.
"""
        )
        st.markdown(
            coordinate_grid_svg(
                0, 6, 0, 6,
                points=[{"x": 2, "y": 3, "label": "A (2, 3)", "color": "#e63946"},
                        {"x": 5, "y": 1, "label": "B (5, 1)", "color": "#2a9d8f"}],
                lines=[{"from": (0, 0), "to": (2, 0), "dashed": True, "arrow": True},
                       {"from": (2, 0), "to": (2, 3), "dashed": True, "arrow": True}],
            ),
            unsafe_allow_html=True,
        )

    with st.expander("📗 Lesson 2: Negative coordinates and the four quadrants"):
        st.markdown(
            """
If the axes carry on past zero, the grid has **four quadrants**, numbered **anticlockwise** from the top right:

| Quadrant | x | y | Example |
|:---:|:---:|:---:|:---:|
| 1 (top right) | positive | positive | (3, 2) |
| 2 (top left) | **negative** | positive | (−3, 2) |
| 3 (bottom left) | **negative** | **negative** | (−3, −2) |
| 4 (bottom right) | positive | **negative** | (3, −2) |

Negative x means **left** of the y-axis. Negative y means **below** the x-axis.
"""
        )
        st.markdown(
            coordinate_grid_svg(
                -4, 4, -4, 4,
                points=[{"x": 3, "y": 2, "label": "1", "color": "#e63946"},
                        {"x": -3, "y": 2, "label": "2", "color": "#2a9d8f"},
                        {"x": -3, "y": -2, "label": "3", "color": "#f4a261"},
                        {"x": 3, "y": -2, "label": "4", "color": "#6a4c93"}],
            ),
            unsafe_allow_html=True,
        )

    with st.expander("📙 Lesson 3: Translation, reflection and distance"):
        st.markdown(
            """
- **Translation** slides a point. **Right/left** changes **x**, **up/down** changes **y**.
  Moving a point **3 right and 2 up** changes (1, 4) to (4, 6).
- **Reflection** flips a point over a **mirror line**. The image is the **same distance** from the mirror on
  the other side. Reflecting in a vertical line changes only **x**; in a horizontal line only **y**.
- **Distance** between two points on the same horizontal or vertical line: find the difference between the
  coordinates that change. If the points are on opposite sides of zero, **add** the two distances from 0.
"""
        )


# =============================================================================
# RENDER
# =============================================================================

def render():
    st.markdown("## 📍 Coordinates")
    st.caption("Read, plot, move and flip points on a grid — from the first quadrant up to negative coordinates.")
    _render_lesson()

    col1, col2 = st.columns(2)
    with col1:
        level = st.selectbox("Level:", list(LEVELS.keys()), key="co_level")
    with col2:
        question_type = st.selectbox("Question type:", [MIXED] + list(TYPES.keys()), key="co_type")

    if question_type == "🧭 Which quadrant?":
        st.caption("Quadrant questions always use the full four-quadrant grid.")

    combo = (level, question_type)
    if st.session_state.co_last_combo != combo:
        st.session_state.co_question = None
        st.session_state.co_feedback = None
        st.session_state.co_last_combo = combo

    if st.button("🎲 Generate Question", key="co_generate_btn"):
        q = generate(level, question_type)
        st.session_state.co_qid += 1
        st.session_state.co_question = q["question"]
        st.session_state.co_svg = q["svg"]
        st.session_state.co_answer_type = q["answer_type"]
        st.session_state.co_answer = q["answer"]
        st.session_state.co_choices = q["choices"]
        st.session_state.co_steps = q["steps"]
        st.session_state.co_solution_svg = q["solution_svg"]
        st.session_state.co_feedback = None

    if st.session_state.co_question is None:
        st.info("👆 Click **Generate Question** to get started!")
        return

    st.markdown(
        f'<div class="word-box">📍 <strong>Question:</strong><br>{st.session_state.co_question}</div>',
        unsafe_allow_html=True,
    )
    st.markdown(st.session_state.co_svg, unsafe_allow_html=True)

    qid = st.session_state.co_qid
    answer_type = st.session_state.co_answer_type

    if answer_type == "xy":
        cx, cy = st.columns(2)
        with cx:
            gx = st.number_input("x (across):", step=1, value=0, key=f"co_x_{qid}")
        with cy:
            gy = st.number_input("y (up / down):", step=1, value=0, key=f"co_y_{qid}")
    elif answer_type == "single":
        gsingle = st.number_input("Your answer (units):", step=1, value=0, min_value=0, key=f"co_single_{qid}")
    else:
        gchoice = st.radio("Choose your answer:", st.session_state.co_choices, index=None,
                           horizontal=(answer_type == "choice" and len(st.session_state.co_choices) <= 5),
                           key=f"co_choice_{qid}")

    if st.button("✅ Check Answer", key="co_check_btn"):
        answer = st.session_state.co_answer
        if answer_type == "xy":
            is_correct = (int(gx), int(gy)) == answer
            shown = pt(*answer)
        elif answer_type == "single":
            is_correct = int(gsingle) == answer
            shown = str(answer)
        else:
            if gchoice is None:
                st.warning("Pick an answer first!")
                is_correct = None
            else:
                is_correct = gchoice == answer
                shown = answer
        if is_correct is not None:
            message = record_attempt(is_correct)
            if not is_correct:
                message += f" The correct answer was **{shown}**."
            st.session_state.co_feedback = (is_correct, message)

    show_feedback(st.session_state.co_feedback)

    with st.expander("💡 Show Step-by-Step Solution"):
        st.markdown(st.session_state.co_steps)
        st.markdown(st.session_state.co_solution_svg, unsafe_allow_html=True)
