"""
Non-Verbal Reasoning tab. Nine topics, each at three levels:

  🔍 Similarity      🔳 Matrices      ↔️ Analogy        🔄 Rotation       🧱 Combining pieces
  🕵️ Embedded figure 🎯 Placing dots  🎲 Dice and cubes 🔐 Codes

Every question has exactly one correct answer, which the generators guarantee by construction
and re-check (for example, by trying every rotation, every translation or every cube view).
Each question dict also carries a `debug` entry so the test-suite can verify answers independently.
"""

import random
from functools import lru_cache

from modules.reasoning import nvr_draw as D
from modules.reasoning.engine import render_reasoning

LETTERS = "ABCDE"
DIRS = {0: "up", 90: "right", 180: "down", 270: "left"}
ATTRS = ["shape", "fill", "size", "count"]
DOMAIN = {"shape": D.SHAPES, "fill": D.FILLS, "size": ["small", "large"], "count": [1, 2, 3], "rot": [0, 90, 180, 270]}


# =============================================================================
# HELPERS
# =============================================================================

def norm(f):
    """Triangles show their rotation; every other shape looks the same at any rotation."""
    f = dict(f)
    if f["shape"] != "triangle":
        f["rot"] = 0
    return f


def fkey(f):
    n = norm(f)
    return (n["shape"], n["fill"], n["size"], n["count"], n["rot"])


def mk(**kw):
    base = {"shape": "circle", "fill": "black", "size": "large", "count": 1, "rot": 0}
    base.update(kw)
    return D.fig(**norm(base))


def mc(prompt, visual, items, correct, make, explain, solution_visual=None, debug=None, hint=None):
    """Multiple choice with picture options labelled A, B, C..."""
    items = list(items)
    random.shuffle(items)
    idx = items.index(correct)
    letter = LETTERS[idx]
    return {
        "type": "choice", "prompt": prompt, "visual": visual,
        "choices": list(LETTERS[:len(items)]),
        "option_svgs": [make(it, LETTERS[i]) for i, it in enumerate(items)],
        "answer": letter, "explain": explain.replace("{ans}", letter),
        "solution_visual": solution_visual, "hint": hint,
        "debug": dict(debug or {}, items=items, correct_index=idx),
    }


def fig_tile(f, label=None):
    return D.figure_tile(f, label)


# =============================================================================
# 1. SIMILARITY
# =============================================================================

def _rand_fig(fixed, rot_mode=False):
    f = {a: random.choice(DOMAIN[a]) for a in ATTRS}
    f["rot"] = random.choice(DOMAIN["rot"]) if rot_mode else 0
    if rot_mode:
        f["shape"] = "triangle"
    f.update(fixed)
    return mk(**f)


def _describe(attr, value):
    if attr == "shape":
        return f"all are {value}s"
    if attr == "fill":
        return {"black": "all are black", "white": "all are white (empty)", "grey": "all are grey"}[value]
    if attr == "size":
        return f"all are {value}"
    if attr == "count":
        return "all have " + ("1 shape" if value == 1 else f"{value} shapes")
    return f"all point {DIRS[value]}"


def odd_candidates(figs, attrs):
    out = set()
    for i, f in enumerate(figs):
        for a in attrs:
            others = {g[a] for j, g in enumerate(figs) if j != i}
            if len(others) == 1 and f[a] not in others:
                out.add(i)
    return out


def _pick_rule(level):
    if level == 1:
        return [random.choice(["shape", "fill", "count"])]
    if level == 2:
        return [random.choice(["shape", "fill", "size", "count", "rot"])]
    return random.sample(ATTRS, 2)


def _similarity_odd(level):
    for _ in range(400):
        attrs = _pick_rule(level)
        rot_mode = attrs == ["rot"]
        vals = {a: random.choice(DOMAIN[a]) for a in attrs}
        normals = [_rand_fig(vals, rot_mode) for _ in range(4)]
        a = random.choice(attrs)
        odd_vals = dict(vals)
        odd_vals[a] = random.choice([v for v in DOMAIN[a] if v != vals[a]])
        odd = _rand_fig(odd_vals, rot_mode)
        figs = normals + [odd]
        if len({fkey(f) for f in figs}) < 5:
            continue
        check_attrs = ATTRS + (["rot"] if rot_mode else [])
        if odd_candidates(figs, check_attrs) != {4}:
            continue
        rule = " and ".join(_describe(x, vals[x]) for x in attrs)
        return mc(
            "Which figure is the odd one out?", None, figs, odd, fig_tile,
            f"Four of the figures follow the same rule: **{rule}**. Figure **{{ans}}** breaks the rule, so it is the odd one out.",
            debug={"kind": "odd", "figs": figs, "attrs": check_attrs, "rule_attrs": attrs},
        )
    raise RuntimeError("similarity odd failed")


def _similarity_belongs(level):
    for _ in range(400):
        attrs = _pick_rule(level)
        rot_mode = attrs == ["rot"]
        vals = {a: random.choice(DOMAIN[a]) for a in attrs}
        group = [_rand_fig(vals, rot_mode) for _ in range(3)]
        if len({fkey(f) for f in group}) < 3:
            continue
        check_attrs = ATTRS + (["rot"] if rot_mode else [])
        constants = {a: group[0][a] for a in check_attrs if len({g[a] for g in group}) == 1}
        correct = _rand_fig({**constants}, rot_mode)
        wrong = []
        tries = 0
        while len(wrong) < (4 if level == 3 else 3) and tries < 200:
            tries += 1
            change = [random.choice(attrs)] if len(attrs) == 1 or random.random() < 0.6 else list(attrs)
            fixed = {}
            for a in change:
                fixed[a] = random.choice([v for v in DOMAIN[a] if v != vals[a]])
            for a in attrs:
                fixed.setdefault(a, vals[a])
            d = _rand_fig(fixed, rot_mode)
            if fkey(d) == fkey(correct) or fkey(d) in {fkey(w) for w in wrong}:
                continue
            wrong.append(d)
        if len(wrong) < (4 if level == 3 else 3):
            continue
        rule = " and ".join(_describe(x, vals[x]) for x in attrs)
        visual = D.row_html([fig_tile(f) for f in group])
        return mc(
            "Which figure belongs with these three?", visual, [correct] + wrong, correct, fig_tile,
            f"The three figures in the group all have the same rule: **{rule}**. Only figure **{{ans}}** follows it too.",
            debug={"kind": "belongs", "group": group, "constants": constants, "rule_attrs": attrs, "vals": vals},
        )
    raise RuntimeError("similarity belongs failed")


def gen_similarity(level):
    return random.choice([_similarity_odd, _similarity_belongs])(level)


# =============================================================================
# 2. MATRICES
# =============================================================================

def _cell_value(rule, vals, r, c):
    return {"const": vals[0], "row": vals[r], "col": vals[c],
            "latin_a": vals[(r + c) % 3], "latin_b": vals[(r + 2 * c) % 3]}[rule]


_RULE_TEXT = {
    "const": "never changes",
    "row": "changes from row to row (every row has its own one, repeated across the row)",
    "col": "changes from column to column (every column has its own one, repeated down the column)",
    "latin_a": "uses three different ones, and each one appears exactly once in every row and every column",
    "latin_b": "uses three different ones, and each one appears exactly once in every row and every column",
}
_ATTR_NAME = {"shape": "shape", "fill": "shading", "count": "number of shapes"}


def gen_matrix(level):
    attrs = ["shape", "fill", "count"]
    random.shuffle(attrs)
    roles = {1: ["row", "col", "const"],
             2: [random.choice(["latin_a"]), random.choice(["row", "col"]), "const"],
             3: ["latin_a", "latin_b", random.choice(["row", "col"])]}[level]
    rules = dict(zip(attrs, roles))
    vals = {}
    for a in attrs:
        pool = {"shape": D.SHAPES, "fill": D.FILLS, "count": [1, 2, 3]}[a]
        vals[a] = random.sample(pool, 3)

    def cell(r, c):
        v = {a: _cell_value(rules[a], vals[a], r, c) for a in attrs}
        return mk(shape=v["shape"], fill=v["fill"], count=v["count"], size="large")

    cells = {(r, c): cell(r, c) for r in range(3) for c in range(3)}
    answer = cells[(2, 2)]

    wrong, tries = [], 0
    need = 4 if level == 3 else 3
    while len(wrong) < need and tries < 300:
        tries += 1
        v = {"shape": answer["shape"], "fill": answer["fill"], "count": answer["count"]}
        for a in random.sample(attrs, random.choice([1, 1, 2])):
            v[a] = random.choice([x for x in vals[a] if x != v[a]])
        d = mk(shape=v["shape"], fill=v["fill"], count=v["count"], size="large")
        if fkey(d) != fkey(answer) and fkey(d) not in {fkey(w) for w in wrong}:
            wrong.append(d)

    lines = [f"- The **{_ATTR_NAME[a]}** {_RULE_TEXT[rules[a]]}." for a in attrs]
    explain = ("Look for the pattern in the rows and columns:\n\n" + "\n".join(lines) +
               "\n\nApplying these rules to the missing square gives figure **{ans}**.")
    q = mc("Which figure completes the grid?", D.big_html(D.matrix_svg(cells), 320), [answer] + wrong, answer, fig_tile,
           explain, solution_visual=D.big_html(D.matrix_svg({**cells, (2, 2): answer}, missing=(9, 9)), 320),
           debug={"kind": "matrix", "cells": cells, "rules": rules, "vals": vals})
    return q


# =============================================================================
# 3. ANALOGY  (A is to B as C is to ?)
# =============================================================================

def _t_invert(f):
    return {**f, "fill": {"black": "white", "white": "black"}[f["fill"]]} if f["fill"] in ("black", "white") else None


def _t_grey(f):
    return {**f, "fill": "grey"} if f["fill"] != "grey" else None


def _t_grow(f):
    return {**f, "size": "large"} if f["size"] == "small" else None


def _t_shrink(f):
    return {**f, "size": "small"} if f["size"] == "large" else None


def _t_add(f):
    return {**f, "count": f["count"] + 1} if f["count"] < 3 else None


def _t_remove(f):
    return {**f, "count": f["count"] - 1} if f["count"] > 1 else None


def _t_rot90(f):
    return {**f, "rot": (f["rot"] + 90) % 360} if f["shape"] == "triangle" else None


def _t_rot180(f):
    return {**f, "rot": (f["rot"] + 180) % 360} if f["shape"] == "triangle" else None


TRANSFORMS = {
    "invert": (_t_invert, "swaps black and white", "fill"),
    "grey": (_t_grey, "becomes grey", "fill"),
    "grow": (_t_grow, "gets bigger", "size"),
    "shrink": (_t_shrink, "gets smaller", "size"),
    "add": (_t_add, "gains one more shape", "count"),
    "remove": (_t_remove, "loses one shape", "count"),
    "rot90": (_t_rot90, "turns 90° clockwise", "rot"),
    "rot180": (_t_rot180, "turns 180°", "rot"),
}


def _apply(names, f):
    for n in names:
        f = TRANSFORMS[n][0](f)
        if f is None:
            return None
    return norm(f)


def gen_analogy(level):
    for _ in range(600):
        if level == 1:
            names = [random.choice(["invert", "grey", "grow", "shrink", "add", "remove"])]
        elif level == 2:
            cats = random.sample(["fill", "size", "count"], 2)
            pool = {"fill": ["invert", "grey"], "size": ["grow", "shrink"], "count": ["add", "remove"]}
            names = [random.choice(pool[c]) for c in cats]
        else:
            names = [random.choice(["rot90", "rot180"]), random.choice(["invert", "grey", "grow", "shrink", "add", "remove"])]
        rot_mode = any(n.startswith("rot") for n in names)
        a_fig = dict(_rand_fig({}, rot_mode))
        changed_attrs = {TRANSFORMS[n][2] for n in names}
        # C copies A on every attribute the rule changes, and differs on the others.
        c_fig = dict(a_fig)
        for attr in ("shape", "fill", "size", "count", "rot"):
            if attr not in changed_attrs and not (rot_mode and attr == "shape"):
                c_fig[attr] = random.choice(DOMAIN[attr])
        c_fig = norm(c_fig)
        a_fig = norm(a_fig)
        b_fig, ans = _apply(names, a_fig), _apply(names, c_fig)
        if b_fig is None or ans is None or fkey(a_fig) == fkey(c_fig) or fkey(a_fig) == fkey(b_fig):
            continue

        wrong = {fkey(c_fig): c_fig}
        if len(names) > 1:
            for n in names:
                part = _apply([n], c_fig)
                if part:
                    wrong[fkey(part)] = part
        for other in TRANSFORMS:
            if other not in names:
                alt = _apply([other], c_fig)
                if alt:
                    wrong[fkey(alt)] = alt
                alt2 = _apply(names + [other], c_fig) if TRANSFORMS[other][2] not in changed_attrs else None
                if alt2:
                    wrong[fkey(alt2)] = alt2
        bad = dict(ans)
        bad["shape"] = random.choice([s for s in D.SHAPES if s != ans["shape"]])
        wrong[fkey(norm(bad))] = norm(bad)
        wrong.pop(fkey(ans), None)
        need = 4 if level == 3 else 3
        if len(wrong) < need:
            continue
        wrong_figs = random.sample(list(wrong.values()), need)

        rule = " and ".join(f"the shape {TRANSFORMS[n][1]}" for n in names)
        visual = D.row_html([fig_tile(a_fig), D.text_cell("→"), fig_tile(b_fig), D.text_cell("is like"),
                             fig_tile(c_fig), D.text_cell("→"), D.question_tile()], gap=8)
        explain = (f"Look at how the first shape changes into the second: **{rule}**.\n\n"
                   f"Do exactly the same to the third shape and you get figure **{{ans}}**.")
        return mc("Which figure completes the second pair?", visual, [ans] + wrong_figs, ans, fig_tile, explain,
                  debug={"kind": "analogy", "names": names, "A": a_fig, "B": b_fig, "C": c_fig, "ans": ans})
    raise RuntimeError("analogy failed")


# =============================================================================
# 4. ROTATION
# =============================================================================

def rot_cw(cells, n):
    return frozenset((c, n - 1 - r) for r, c in cells)


def reflect(cells, n):
    return frozenset((r, n - 1 - c) for r, c in cells)


def sym_image(cells, accent, n, k):
    """k = 0..3: rotate k quarter-turns clockwise; k = 4..7: mirror first, then rotate (k-4) turns."""
    c, a = cells, accent
    if k >= 4:
        c, a = reflect(c, n), (a[0], n - 1 - a[1])
    for _ in range(k % 4):
        c, a = rot_cw(c, n), (a[1], n - 1 - a[0])
    return frozenset(c), a


def _random_pattern(n, k):
    for _ in range(2000):
        cells = {(random.randrange(n), random.randrange(n))}
        while len(cells) < k:
            r, c = random.choice(sorted(cells))
            dr, dc = random.choice([(1, 0), (-1, 0), (0, 1), (0, -1)])
            if 0 <= r + dr < n and 0 <= c + dc < n:
                cells.add((r + dr, c + dc))
        accent = random.choice(sorted(cells))
        images = {sym_image(frozenset(cells), accent, n, s) for s in range(8)}
        if len(images) == 8:
            return frozenset(cells), accent
    raise RuntimeError("pattern failed")


def gen_rotation(level):
    n, k = {1: (3, 5), 2: (4, 6), 3: (4, 7)}[level]
    cells, accent = _random_pattern(n, k)
    img = lambda s: sym_image(cells, accent, n, s)
    start = D.pattern_svg(cells, n, accent, label="Start")
    make = lambda item, label: D.pattern_svg(item[0], n, item[1], label)
    visual = D.row_html([start])
    if level == 1:
        items = [img(1), img(2), img(3), img(5)]
        prompt = "Which picture shows the shape turned **90° clockwise** (a quarter turn to the right)?"
        explain = ("Turn the page a quarter turn to the right in your head: the top row moves to the right-hand side. "
                   "The coloured square is a good marker to follow. Picture **{ans}** matches. "
                   "The others are turned by a different amount, or flipped over like a mirror image.")
        correct = img(1)
    elif level == 2:
        rot_k = random.choice([1, 2, 3])
        items = [img(rot_k)] + [img(s) for s in (4, 5, 6, 7)]
        prompt = "Only one picture shows the same shape **turned** (rotated). The others are flipped over. Which is it?"
        explain = ("A turned shape can be turned back to match the start. The others are mirror images "
                   "(flipped over), which no amount of turning can match. Picture **{ans}** is the turned one.")
        correct = img(rot_k)
    else:
        rot_k, words = random.choice([(2, "180° (a half turn)"), (3, "270° clockwise (the same as 90° anticlockwise)")])
        others = [x for x in (1, 2, 3) if x != rot_k]
        items = [img(rot_k)] + [img(o) for o in others] + random.sample([img(s) for s in (4, 5, 6, 7)], 2)
        prompt = f"Which picture shows the shape turned **{words}**?"
        explain = ("Follow the coloured square as the shape turns. Picture **{ans}** is the only one turned by exactly "
                   "this amount; the others are turned by a different amount or flipped over.")
        correct = img(rot_k)
    return mc(prompt, visual, items, correct, make, explain,
              debug={"kind": "rotation", "cells": cells, "accent": accent, "n": n, "correct": correct})


# =============================================================================
# 5. COMBINING PIECES  (which piece fills the gap?)
# =============================================================================

def _norm_cells(cells):
    mr, mc_ = min(r for r, c in cells), min(c for r, c in cells)
    return frozenset((r - mr, c - mc_) for r, c in cells)


def _rot_cells(cells):
    return _norm_cells({(c, -r) for r, c in cells})


def _canon(cells):
    best, cur = None, _norm_cells(cells)
    for _ in range(4):
        form = tuple(sorted(cur))
        best = form if best is None or form < best else best
        cur = _rot_cells(cur)
    return best


def _mirror(cells):
    return _norm_cells({(r, -c) for r, c in cells})


def _connected(cells):
    cells = set(cells)
    if not cells:
        return False
    seen, stack = set(), [next(iter(cells))]
    while stack:
        r, c = stack.pop()
        if (r, c) in seen:
            continue
        seen.add((r, c))
        for dr, dc in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
            if (r + dr, c + dc) in cells:
                stack.append((r + dr, c + dc))
    return seen == cells


def _neighbours(cells):
    return {(r + dr, c + dc) for r, c in cells for dr, dc in [(1, 0), (-1, 0), (0, 1), (0, -1)]} - set(cells)


def gen_pieces(level):
    w, h, k = {1: (4, 3, 4), 2: (4, 4, 5), 3: (5, 4, 6)}[level]
    everything = {(r, c) for r in range(h) for c in range(w)}
    for _ in range(3000):
        hole = {(random.randrange(h), random.randrange(w))}
        while len(hole) < k:
            r, c = random.choice(sorted(hole))
            dr, dc = random.choice([(1, 0), (-1, 0), (0, 1), (0, -1)])
            if (r + dr, c + dc) in everything:
                hole.add((r + dr, c + dc))
        if not _connected(everything - hole):
            continue
        if level == 3 and _canon(_mirror(hole)) == _canon(hole):
            continue  # at level 3 we want a piece that is different from its mirror image
        break
    else:
        raise RuntimeError("hole failed")

    target = _canon(hole)
    forms = {target}
    wrong = []
    if level == 3:
        wrong.append(_mirror(hole))
        forms.add(_canon(_mirror(hole)))
    tries = 0
    need = 4 if level == 3 else 3
    while len(wrong) < need and tries < 2000:
        tries += 1
        piece = set(hole)
        piece.remove(random.choice(sorted(piece)))
        piece.add(random.choice(sorted(_neighbours(piece))))
        if len(piece) != k or not _connected(piece):
            continue
        if _canon(piece) in forms:
            continue
        forms.add(_canon(piece))
        wrong.append(frozenset(piece))
    if len(wrong) < need:
        raise RuntimeError("pieces failed")

    correct = _norm_cells(hole)
    if level > 1:
        for _ in range(random.choice([1, 2, 3])):
            correct = _rot_cells(correct)
    items = [correct] + [_norm_cells(wp) for wp in wrong]
    explain = (f"Count the squares in the gap: there are **{k}**. The piece has to fill the gap exactly, "
               "so its shape must match the gap " + ("." if level == 1 else "once it has been turned round (pieces can be turned, but not flipped over). ") +
               "Only piece **{ans}** fits; the others have the wrong shape.")
    return mc("Which piece fits exactly into the gap?", D.big_html(D.hole_svg(w, h, hole), 300), items, correct,
              lambda cells, label: D.piece_svg(cells, label), explain,
              debug={"kind": "pieces", "hole": frozenset(hole), "w": w, "h": h, "correct": correct})


# =============================================================================
# 6. EMBEDDED FIGURE
# =============================================================================

def _edge(p, q):
    return tuple(sorted((p, q)))


@lru_cache(maxsize=None)
def _lattice_edges(n):
    out = set()
    for x in range(n + 1):
        for y in range(n + 1):
            for dx, dy in [(1, 0), (0, 1), (1, 1), (1, -1)]:
                x2, y2 = x + dx, y + dy
                if 0 <= x2 <= n and 0 <= y2 <= n:
                    out.add(_edge((x, y), (x2, y2)))
    return sorted(out)


def _random_target(k):
    moves = [(1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (-1, -1), (1, -1), (-1, 1)]
    for _ in range(1000):
        cur, used = (random.randint(0, 3), random.randint(0, 3)), set()
        for _ in range(k):
            opts = [(cur[0] + dx, cur[1] + dy) for dx, dy in moves
                    if 0 <= cur[0] + dx <= 3 and 0 <= cur[1] + dy <= 3
                    and _edge(cur, (cur[0] + dx, cur[1] + dy)) not in used]
            if not opts:
                break
            nxt = random.choice(opts)
            used.add(_edge(cur, nxt))
            cur = nxt
        if len(used) == k:
            xs = {p[0] for e in used for p in e}
            ys = {p[1] for e in used for p in e}
            if max(xs) - min(xs) >= 2 and max(ys) - min(ys) >= 2:
                return frozenset(used)
    raise RuntimeError("target failed")


def _shift(edges, dx, dy):
    return frozenset(_edge((a[0] + dx, a[1] + dy), (b[0] + dx, b[1] + dy)) for a, b in edges)


def contains(figure, target, n=4):
    for dx in range(-n, n + 1):
        for dy in range(-n, n + 1):
            moved = _shift(target, dx, dy)
            if all(0 <= p[0] <= n and 0 <= p[1] <= n for e in moved for p in e) and moved <= figure:
                return True
    return False


def gen_embedded(level):
    k, extras, n_opts = {1: (4, 3, 4), 2: (5, 4, 4), 3: (6, 5, 5)}[level]
    lattice = _lattice_edges(4)

    def place(shape_edges):
        for _ in range(100):
            moved = _shift(shape_edges, random.randint(0, 1), random.randint(0, 1))
            if all(0 <= p[0] <= 4 and 0 <= p[1] <= 4 for e in moved for p in e):
                pool = [e for e in lattice if e not in moved]
                return moved | frozenset(random.sample(pool, extras)), moved
        raise RuntimeError

    for _ in range(400):
        target = _random_target(k)
        correct, placed = place(target)
        wrong, seen = [], {correct}
        tries = 0
        while len(wrong) < n_opts - 1 and tries < 400:
            tries += 1
            t = set(target)
            t.remove(random.choice(sorted(t)))
            pts = {p for e in t for p in e}
            cands = [e for e in _lattice_edges(3) if e not in t and e not in target and (e[0] in pts or e[1] in pts)]
            if not cands:
                continue
            t.add(random.choice(cands))
            fig_edges, _ = place(frozenset(t))
            if fig_edges in seen or contains(fig_edges, target):
                continue
            seen.add(fig_edges)
            wrong.append(fig_edges)
        if len(wrong) == n_opts - 1:
            break
    else:
        raise RuntimeError("embedded failed")

    visual = D.row_html([D.text_cell("Find this shape:", 20), D.edges_svg(target, 4, colour=D.ACCENT)])
    solution = D.big_html(D.edges_svg(correct, 4, highlight=placed, width=170), 170)
    explain = ("The shape is hidden inside one figure, drawn in the **same size and the same direction** "
               "(it may be in a different place). Figure **{ans}** contains it; its other lines are only there to hide it. "
               "In the other figures, one part of the shape is missing or different.")
    return mc("Which figure has the shape hidden inside it?", visual, [correct] + wrong, correct,
              lambda edges, label: D.edges_svg(edges, 4, label), explain, solution_visual=solution,
              debug={"kind": "embedded", "target": target, "correct": correct})


# =============================================================================
# 7. PLACING DOTS
# =============================================================================

_BASE_LAYOUTS = [
    {"circle": (44, 32, 26), "square": (39, 21, 46), "triangle": [(9, 66), (77, 66), (39, 22)]},
    {"circle": (42, 44, 26), "square": (39, 39, 38), "triangle": [(8, 79), (74, 79), (37, 20)]},
]


def _flip(layout, horizontal, vertical):
    fx = (lambda x: 100 - x) if horizontal else (lambda x: x)
    fy = (lambda y: 100 - y) if vertical else (lambda y: y)
    cx, cy, r = layout["circle"]
    sx, sy, w = layout["square"]
    return {
        "circle": (fx(cx), fy(cy), r),
        "square": (min(fx(sx), fx(sx + w)), min(fy(sy), fy(sy + w)), w),
        "triangle": [(fx(x), fy(y)) for x, y in layout["triangle"]],
    }


LAYOUTS = [_flip(b, h, v) for b in _BASE_LAYOUTS for h in (False, True) for v in (False, True)]


def _inside(layout, x, y):
    cx, cy, r = layout["circle"]
    sx, sy, w = layout["square"]
    (x1, y1), (x2, y2), (x3, y3) = layout["triangle"]
    d = (y2 - y3) * (x1 - x3) + (x3 - x2) * (y1 - y3)
    a = ((y2 - y3) * (x - x3) + (x3 - x2) * (y - y3)) / d
    b = ((y3 - y1) * (x - x3) + (x1 - x3) * (y - y3)) / d
    return ((x - cx) ** 2 + (y - cy) ** 2 <= r * r, sx <= x <= sx + w and sy <= y <= sy + w, a >= 0 and b >= 0 and 1 - a - b >= 0)


@lru_cache(maxsize=None)
def _safe_points(layout_index, used):
    """Points whose region stays the same 5 units away in 8 directions, grouped by region."""
    layout = LAYOUTS[layout_index]
    mask = lambda t: tuple(v and i in used for i, v in enumerate(t))
    out = {}
    for x in range(10, 91, 2):
        for y in range(10, 91, 2):
            t = mask(_inside(layout, x, y))
            if all(mask(_inside(layout, x + dx, y + dy)) == t
                   for dx, dy in [(5, 0), (-5, 0), (0, 5), (0, -5), (4, 4), (-4, 4), (4, -4), (-4, -4)]):
                out.setdefault(t, []).append((x, y))
    return out


_SHAPE_WORDS = ["circle", "square", "triangle"]


def _region_words(triple, used):
    inside = [f"the {_SHAPE_WORDS[i]}" for i in used if triple[i]]
    outside = [f"the {_SHAPE_WORDS[i]}" for i in used if not triple[i]]
    if not inside:
        return "outside all of the shapes"
    if not outside:
        return "inside all of the shapes" if len(used) > 2 else "inside both shapes"
    return f"inside {' and '.join(inside)}, but outside {' and '.join(outside)}"


def gen_dots(level):
    used = (0, 1) if level == 1 else (0, 1, 2)
    for _ in range(100):
        li = random.randrange(len(LAYOUTS))
        safe = _safe_points(li, used)
        regions = [t for t, pts in safe.items() if len(pts) >= 3]
        needed = 2 ** len(used)
        if len(regions) < needed:
            continue
        target = random.choice(regions)
        if level == 3:
            wanted = [t for t in regions if sum(t) in (0, 2)]
            target = random.choice(wanted or regions)
        n_opts = 4 if level == 1 else 5
        others = random.sample([t for t in regions if t != target], n_opts - 1)
        break
    else:
        raise RuntimeError("dots failed")

    layout = LAYOUTS[li]
    shapes = tuple(_SHAPE_WORDS[i] for i in used)
    items = [(t, random.choice(safe[t])) for t in [target] + others]
    correct = items[0]
    solution = D.big_html(D.venn_svg(layout, correct[1], shapes, width=170), 170)
    explain = ("Check each dot one shape at a time. A dot is correct only if it is in the right place for **every** shape. "
               "Dot **{ans}** is " + _region_words(target, used) + ". "
               "The other dots are in different places.")
    return mc(f"Which dot is {_region_words(target, used)}?", None, items, correct,
              lambda it, label: D.venn_svg(layout, it[1], shapes, label), explain, solution_visual=solution,
              debug={"kind": "dots", "layout": layout, "used": used, "target": target,
                     "items": items, "shapes": shapes})


# =============================================================================
# 8. DICE AND CUBES
# =============================================================================

def _cross(a, b):
    return (a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0])


def _dot(a, b):
    return sum(x * y for x, y in zip(a, b))


def _matvec(m, v):
    return tuple(sum(m[i][j] * v[j] for j in range(3)) for i in range(3))


def _matmul(a, b):
    return tuple(tuple(sum(a[i][k] * b[k][j] for k in range(3)) for j in range(3)) for i in range(3))


def _fold(e):
    """Rotation that folds a flap across an edge pointing in direction e: z -> e and e -> -z."""
    u, w = e, (0, 0, 1)
    v = _cross(w, u)
    cols = []
    for b in [(1, 0, 0), (0, 1, 0), (0, 0, 1)]:
        cols.append(tuple(-_dot(b, u) * w[i] + _dot(b, v) * v[i] + _dot(b, w) * u[i] for i in range(3)))
    return tuple(tuple(cols[j][i] for j in range(3)) for i in range(3))


def fold_net(cells):
    """Fold a net (list of (col,row)) into a cube with the pictures on the OUTSIDE.
    Returns {cell: outward normal} in a right-handed frame (x right, y up, z towards the viewer)."""
    cellset, base = set(cells), cells[0]
    mats, queue = {base: ((1, 0, 0), (0, 1, 0), (0, 0, 1))}, [base]
    while queue:
        cur = queue.pop(0)
        for dc, dr in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
            nb = (cur[0] + dc, cur[1] + dr)
            if nb in cellset and nb not in mats:
                mats[nb] = _matmul(mats[cur], _fold((dc, -dr, 0)))
                queue.append(nb)
    return {cell: _matvec(m, (0, 0, 1)) for cell, m in mats.items()}


_NETS = [
    [(1, 0), (0, 1), (1, 1), (2, 1), (3, 1), (1, 2)],
    [(0, 0), (0, 1), (1, 1), (2, 1), (3, 1), (3, 2)],
    [(0, 0), (0, 1), (1, 1), (2, 1), (3, 1), (2, 2)],
    [(1, 0), (0, 1), (1, 1), (2, 1), (3, 1), (0, 2)],
    [(0, 0), (1, 0), (1, 1), (2, 1), (2, 2), (3, 2)],
    [(0, 0), (1, 0), (1, 1), (2, 1), (3, 1), (1, 2)],
    [(0, 0), (1, 0), (2, 0), (2, 1), (3, 1), (4, 1)],
]
VALID_NETS = [n for n in _NETS if len(set(fold_net(n).values())) == 6]
COLOURS = list(D.CUBE_COLORS)


def cube_views(normals_to_colour):
    """All colour triples (top, left, right) that can be seen on this cube."""
    views = set()
    dirs = list(normals_to_colour)
    for t in dirs:
        for l in dirs:
            for r in dirs:
                if _dot(t, _cross(l, r)) == 1:
                    views.add((normals_to_colour[t], normals_to_colour[l], normals_to_colour[r]))
    return views


def _gen_dice_basic():
    pips = random.sample([random.choice([1, 6]), random.choice([2, 5]), random.choice([3, 4])], 3)
    if random.random() < 0.5:
        a = random.randint(1, 6)
        return {"type": "number", "prompt": f"On a normal dice, the numbers on opposite faces always add up to **7**. "
                f"The number on the **top** is **{a}**. What number is on the **bottom**?",
                "visual": None, "answer": 7 - a,
                "explain": f"Opposite faces add to 7, so the bottom is 7 − {a} = **{7 - a}**.", "debug": {"kind": "dice_basic"}}
    top, left, right = pips
    return {"type": "number", "prompt": "The numbers on all six faces of a dice add up to **21** (1+2+3+4+5+6). "
            "Three faces can be seen. What is the **total of the three faces you cannot see**?",
            "visual": D.big_html(D.cube_svg(top, left, right, width=170, pips=True), 170), "answer": 21 - sum(pips),
            "explain": f"The visible faces show {top} + {left} + {right} = {sum(pips)}. "
                       f"The hidden faces make 21 − {sum(pips)} = **{21 - sum(pips)}**.", "debug": {"kind": "dice_basic"}}


def _random_net_cube():
    net = random.choice(VALID_NETS)
    cells = list(net)
    random.shuffle(cells)  # also randomises which cell is the base of the folding
    colours = random.sample(COLOURS, 6)
    colour_of = dict(zip(net, colours))
    normals = fold_net(cells)
    return net, colour_of, {normals[c]: colour_of[c] for c in net}


def _gen_dice_opposite():
    net, colour_of, by_normal = _random_net_cube()
    x = random.choice(list(colour_of.values()))
    nx = next(n for n, c in by_normal.items() if c == x)
    opposite = by_normal[(-nx[0], -nx[1], -nx[2])]
    options = [opposite] + random.sample([c for c in by_normal.values() if c not in (x, opposite)], 3)
    random.shuffle(options)
    return {"type": "choice", "prompt": f"This net folds up into a cube (with the colours on the outside). "
            f"Which colour is on the face **opposite the {x} face**?", "visual": D.big_html(D.net_svg(colour_of), 260),
            "choices": options, "answer": opposite,
            "explain": f"When the net is folded, the {x} face and the **{opposite}** face end up on opposite sides of the cube. "
                       "In a net, opposite faces are never next to each other, and there is always exactly one square between them in a straight row.",
            "debug": {"kind": "dice_opposite", "by_normal": by_normal, "x": x}}


def _gen_dice_cube():
    net, colour_of, by_normal = _random_net_cube()
    views = cube_views(by_normal)
    opp = {c: by_normal[(-n[0], -n[1], -n[2])] for n, c in by_normal.items()}
    t, l, r = random.choice(sorted(views))
    candidates = [(t, r, l), (t, l, opp[r]), (opp[t], l, r), (t, opp[l], r), (l, t, r), (t, opp[t], r)]
    invalid = [v for v in dict.fromkeys(candidates) if v not in views and len(set(v)) == 3]
    wrong = random.sample(invalid, 3)
    correct = (t, l, r)
    return mc("This net folds up into a cube (with the colours on the outside). Which cube can be made from it?",
              D.big_html(D.net_svg(colour_of), 260), [correct] + wrong, correct,
              lambda v, label: D.cube_svg(v[0], v[1], v[2], label),
              "Fold the net in your head. Faces that touch along an edge in the net touch on the cube, and the order "
              "of the three visible colours matters (going round the corner). Cube **{ans}** is the only one that can be made; "
              "the others have two colours that would be on opposite faces, or have the colours in the wrong order (a mirror image).",
              debug={"kind": "dice_cube", "views": views, "by_normal": by_normal})


def gen_dice(level):
    return [_gen_dice_basic, _gen_dice_opposite, _gen_dice_cube][level - 1]()


# =============================================================================
# 9. CODES
# =============================================================================

_CODE_DOMAINS = {
    "shape": ["circle", "square", "triangle"],
    "fill": ["black", "white", "grey"],
    "count": [1, 2, 3],
}


def gen_codes(level):
    attr_names = {1: ["shape", "fill"], 2: ["shape", "fill"], 3: ["shape", "fill", "count"]}[level]
    domains = {a: list(_CODE_DOMAINS[a]) if level > 1 or a == "shape" else ["black", "white"] for a in attr_names}
    letters = random.sample("ABCDEFGHJKLMNPQRSTUVWXYZ", sum(len(domains[a]) for a in attr_names))
    code, i = {}, 0
    for a in attr_names:
        for v in domains[a]:
            code[(a, v)] = letters[i]
            i += 1

    base = {a: random.choice(domains[a]) for a in attr_names}
    other = {a: random.choice([v for v in domains[a] if v != base[a]]) for a in attr_names}

    def figure(vals):
        full = {"shape": "circle", "fill": "black", "count": 1}
        full.update(vals)
        return mk(shape=full["shape"], fill=full["fill"], count=full["count"], size="large")

    def code_of(vals):
        return "".join(code[(a, vals[a])] for a in attr_names)

    examples = [dict(base)]
    for a in attr_names:
        e = dict(base)
        e[a] = other[a]
        examples.append(e)
    question_vals = dict(other)
    examples = examples[:len(attr_names) + 1]
    # The question figure mixes the 'other' values, so every value it needs appears in an example.
    answer_code = code_of(question_vals)

    ex_tiles = [D.tile_svg(D.figure_group(figure(e)), code_of(e)) for e in examples]
    random.shuffle(ex_tiles)

    if random.random() < 0.5:
        # find the code of a new figure
        q_tile = D.tile_svg(D.figure_group(figure(question_vals)), None)
        visual = D.row_html(ex_tiles + [D.text_cell("→")] + [q_tile])
        wrong = set()
        for _ in range(200):
            c = list(answer_code)
            pos = random.randrange(len(c))
            c[pos] = random.choice([x for x in letters if x != c[pos]])
            if random.random() < 0.4 and len(c) > 1:
                c[0], c[1] = c[1], c[0]
            w = "".join(c)
            if w != answer_code:
                wrong.add(w)
            if len(wrong) >= 4:
                break
        options = [answer_code] + random.sample(sorted(wrong), 3)
        random.shuffle(options)
        meaning = ", ".join(f"**{code[(a, v)]}** = {v if a != 'count' else str(v) + ' shape(s)'}" for a in attr_names for v in domains[a] if (a, v) in code and v in (base[a], other[a]))
        return {"type": "choice", "prompt": "Each figure has a code. Work out the rule, then find the code for the last figure.",
                "visual": visual, "choices": options, "answer": answer_code,
                "explain": f"Compare the figures: when only one feature changes, only one letter of the code changes. "
                           f"That tells us {meaning}. The last figure needs the code **{answer_code}**.",
                "debug": {"kind": "codes_a", "code": code, "attr_names": attr_names, "examples": examples, "q": question_vals}}

    # find the figure that matches a code
    distract = []
    for _ in range(300):
        v = dict(question_vals)
        for a in random.sample(attr_names, random.choice([1, 2] if len(attr_names) > 1 else [1])):
            v[a] = random.choice([x for x in domains[a] if x != v[a]])
        if code_of(v) != answer_code and v not in distract:
            distract.append(v)
        if len(distract) >= 3:
            break
    correct = figure(question_vals)
    items = [correct] + [figure(v) for v in distract[:3]]
    if len({fkey(f) for f in items}) < 4:
        return gen_codes(level)
    visual = D.row_html(ex_tiles + [D.text_cell("→"), D.text_cell(f"<span style='border:3px solid {D.ACCENT};border-radius:10px;padding:6px 12px'>{answer_code}</span>")])
    meaning = ", ".join(f"**{code[(a, v)]}** = {v if a != 'count' else str(v) + ' shape(s)'}" for a in attr_names for v in domains[a] if v in (base[a], other[a]))
    return mc(f"Each figure has a code. Which figure has the code **{answer_code}**?", visual, items, correct, fig_tile,
              f"Compare the figures: each letter of the code stands for one feature. That tells us {meaning}. "
              f"So the code {answer_code} is figure **{{ans}}**.",
              debug={"kind": "codes_b", "code": code, "attr_names": attr_names, "answer_code": answer_code,
                     "items": items, "correct": correct})


# =============================================================================
# TOPICS AND PAGE
# =============================================================================

TOPICS = {
    "🔍 Similarity (odd one out / belongs with)": gen_similarity,
    "🔳 Matrices (complete the grid)": gen_matrix,
    "↔️ Analogy (A is to B as C is to ?)": gen_analogy,
    "🔄 Rotation": gen_rotation,
    "🧱 Combining pieces (which piece fits?)": gen_pieces,
    "🕵️ Embedded figure (find the hidden shape)": gen_embedded,
    "🎯 Placing dots": gen_dots,
    "🎲 Dice and cubes (nets)": gen_dice,
    "🔐 Codes": gen_codes,
}

LESSONS = [
    ("📘 How to tackle non-verbal reasoning",
     "Non-verbal reasoning uses **pictures instead of words**. Each question has a hidden rule, and your job is to spot it.\n\n"
     "1. **Look at one feature at a time:** shape, shading (black / white / grey), size, number of shapes, position, direction.\n"
     "2. **Ask: what changes? what stays the same?**\n"
     "3. **Test the rule** on every option, then **cross out** the ones that break it.\n\n"
     "*Tip: if you can't see the rule, try covering up all the features except one.*"),
    ("📗 What each topic asks",
     "- **Similarity:** which figure is different, or which belongs with a group?\n"
     "- **Matrices:** the pattern runs along the rows and down the columns. Find the missing square.\n"
     "- **Analogy:** work out how the first shape changes into the second, then do the same to the third.\n"
     "- **Rotation:** turn a shape round (a quarter turn is 90°). Beware of mirror images. They can't be made by turning.\n"
     "- **Combining pieces:** which piece fits exactly into the gap?\n"
     "- **Embedded figure:** find the shape hidden inside a busier drawing (same size, same direction).\n"
     "- **Placing dots:** a dot must be in the right place for *every* shape (inside or outside each one).\n"
     "- **Dice and cubes:** fold a net in your head. Opposite faces of a dice add up to 7.\n"
     "- **Codes:** each letter stands for one feature of the picture."),
]


def render():
    render_reasoning(
        prefix="nvr",
        heading="## 🔷 Non-Verbal Reasoning",
        caption="Spot the hidden rule in shapes and patterns. Nine topics, three levels.",
        topics=TOPICS,
        lessons=LESSONS,
    )
