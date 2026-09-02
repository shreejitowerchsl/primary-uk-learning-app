"""
Soroban (Japanese-style) abacus engine: SVG rendering plus a genuine
bead-movement simulator implementing the three classic techniques
(Direct, Small Friend / 5-complement, Big Friend / 10-complement).
"""

import random

PLACE_VALUE_NAMES = [
    "Ones", "Tens", "Hundreds", "Thousands", "Ten Thousands", "Hundred Thousands"
]


def draw_abacus_svg(number: int, min_rods: int = 3) -> str:
    """
    Render a soroban-style abacus as an SVG string showing the given number.
    Heaven bead (value 5) sits above the beam; 4 earth beads (value 1 each)
    sit below. Active beads are drawn touching the beam.
    """
    number = max(0, int(number))
    digit_str = str(number)
    if len(digit_str) < min_rods:
        digit_str = digit_str.zfill(min_rods)
    digits = [int(ch) for ch in digit_str]
    n = len(digits)

    rod_spacing = 90
    margin = 55
    width = margin * 2 + rod_spacing * (n - 1) + 20
    frame_top = 25
    frame_bottom = 300
    beam_y = 115
    bead_r = 15
    bead_step = bead_r * 2 - 5

    parts = [
        f'<svg viewBox="0 0 {width} 350" xmlns="http://www.w3.org/2000/svg" '
        f'style="max-width:100%;height:auto;">'
    ]
    parts.append(
        f'<rect x="15" y="{frame_top}" width="{width - 30}" height="{frame_bottom - frame_top}" '
        f'fill="#f4e4c1" stroke="#7a4b1e" stroke-width="4" rx="10"/>'
    )
    parts.append(f'<rect x="15" y="{beam_y - 4}" width="{width - 30}" height="8" fill="#7a4b1e"/>')

    for i, digit in enumerate(digits):
        place_index = n - 1 - i
        x = margin + i * rod_spacing

        parts.append(
            f'<line x1="{x}" y1="{frame_top + 8}" x2="{x}" y2="{frame_bottom - 8}" '
            f'stroke="#5a3a1e" stroke-width="3"/>'
        )

        heaven_active = digit >= 5
        hy = (beam_y - bead_r - 3) if heaven_active else (frame_top + 26)
        parts.append(
            f'<ellipse cx="{x}" cy="{hy}" rx="{bead_r}" ry="{bead_r - 3}" '
            f'fill="#e63946" stroke="#7a1e1e" stroke-width="2"/>'
        )

        active_count = digit % 5
        for j in range(4):
            if j < active_count:
                ey = beam_y + bead_r + 3 + j * bead_step
            else:
                inactive_index = j - active_count
                ey = frame_bottom - 18 - inactive_index * bead_step
            parts.append(
                f'<ellipse cx="{x}" cy="{ey}" rx="{bead_r}" ry="{bead_r - 3}" '
                f'fill="#2a9d8f" stroke="#1b5c53" stroke-width="2"/>'
            )

        parts.append(
            f'<text x="{x}" y="{frame_bottom + 22}" font-size="16" text-anchor="middle" '
            f'fill="#1d3557" font-weight="bold">{digit}</text>'
        )
        if place_index < len(PLACE_VALUE_NAMES):
            parts.append(
                f'<text x="{x}" y="{frame_bottom + 40}" font-size="11" text-anchor="middle" '
                f'fill="#457b9d">{PLACE_VALUE_NAMES[place_index]}</text>'
            )

    parts.append("</svg>")
    return "".join(parts)


def add_single_column(current_value: int, amount: int):
    """
    Simulate adding `amount` (0-10, where 10 covers a digit-9 + carry-in)
    to a single abacus rod currently showing `current_value` (0-9).
    Returns (new_value 0-9, carry_out 0/1, technique_name, explanation_markdown).
    """
    if amount == 0:
        return current_value, 0, "No change", f"Nothing to add on this rod — it stays at **{current_value}**."

    total = current_value + amount

    if total <= 9:
        cur_earth, cur_heaven = current_value % 5, current_value // 5
        amt_earth, amt_heaven = amount % 5, amount // 5

        if (cur_earth + amt_earth <= 4) and (cur_heaven + amt_heaven <= 1):
            return (
                total, 0, "Direct addition",
                f"There's already enough room — just move the beads you need! "
                f"**{current_value} + {amount} = {total}**."
            )
        else:
            complement = 5 - amount
            return (
                total, 0, "Small Friend (5-complement)",
                f"There isn't enough room in the earth beads to add {amount} directly. "
                f"Use the **small friend**: {amount} = 5 − {complement}. "
                f"Push the heaven bead down (**+5**) and take away {complement} earth bead"
                f"{'s' if complement != 1 else ''} (**−{complement}**). "
                f"**{current_value} + {amount} = {total}**."
            )
    else:
        complement = 10 - amount
        new_value = total - 10
        remove_text = (
            f"take away {complement} bead{'s' if complement != 1 else ''} from this rod (**−{complement}**)"
            if complement > 0 else
            "no beads need to be removed from this rod"
        )
        return (
            new_value, 1, "Big Friend (10-complement)",
            f"Adding {amount} here would go past 9! Use the **big friend**: {amount} = 10 − {complement}. "
            f"Add **1 bead on the next rod to the left** (carry), and {remove_text}. "
            f"This rod becomes **{new_value}**, and we carry **1** to the next rod."
        )


def subtract_single_column(current_value: int, amount: int):
    """
    Simulate subtracting `amount` (0-10) from a single abacus rod currently
    showing `current_value` (0-9). Returns
    (new_value 0-9, borrow_out 0/-1, technique_name, explanation_markdown).
    borrow_out == -1 means "borrow 1 from the next rod to the left".
    """
    if amount == 0:
        return current_value, 0, "No change", f"Nothing to take away on this rod — it stays at **{current_value}**."

    if amount <= current_value:
        cur_earth, cur_heaven = current_value % 5, current_value // 5
        amt_earth, amt_heaven = amount % 5, amount // 5
        new_value = current_value - amount

        if cur_earth >= amt_earth and cur_heaven >= amt_heaven:
            return (
                new_value, 0, "Direct subtraction",
                f"There are enough active beads here — just move away the beads you need! "
                f"**{current_value} − {amount} = {new_value}**."
            )
        else:
            complement = 5 - amount
            return (
                new_value, 0, "Small Friend (5-complement)",
                f"There aren't enough earth beads active to take away {amount} directly. "
                f"Use the **small friend**: {amount} = 5 − {complement}. "
                f"Remove the heaven bead (**−5**) and add back {complement} earth bead"
                f"{'s' if complement != 1 else ''} (**+{complement}**). "
                f"**{current_value} − {amount} = {new_value}**."
            )
    else:
        complement = 10 - amount
        new_value = current_value + complement
        add_text = (
            f"add back {complement} bead{'s' if complement != 1 else ''} here (**+{complement}**)"
            if complement > 0 else
            "no beads need to be added back here"
        )
        return (
            new_value, -1, "Big Friend (10-complement)",
            f"We can't take away {amount} from {current_value} on this rod alone! "
            f"**Borrow 1 ten from the rod to the left** (it loses 1 bead), then "
            f"{add_text}, because {amount} = 10 − {complement}. "
            f"This rod becomes **{new_value}**."
        )


def abacus_multi_add(a: int, b: int):
    """Column-by-column addition narration for two whole numbers a + b."""
    length = max(len(str(a)), len(str(b))) + 1
    digits_a = [int(ch) for ch in str(a).zfill(length)][::-1]
    digits_b = [int(ch) for ch in str(b).zfill(length)][::-1]

    carry = 0
    result_digits = []
    column_reports = []

    for i in range(length):
        amount = digits_b[i] + carry
        new_value, carry, technique, expl = add_single_column(digits_a[i], amount)
        result_digits.append(new_value)
        column_reports.append((
            PLACE_VALUE_NAMES[i] if i < len(PLACE_VALUE_NAMES) else f"10^{i}",
            digits_a[i], digits_b[i], carry, technique, expl
        ))

    result = int("".join(str(d) for d in result_digits[::-1])) if any(result_digits) else 0
    return result, column_reports


def abacus_multi_subtract(a: int, b: int):
    """Column-by-column subtraction narration for a - b, assuming a >= b."""
    length = len(str(a))
    digits_a = [int(ch) for ch in str(a).zfill(length)][::-1]
    digits_b = [int(ch) for ch in str(b).zfill(length)][::-1]

    borrow = 0
    result_digits = []
    column_reports = []

    for i in range(length):
        # If the previous (lower-value) column had to borrow, this column
        # must give up one extra unit before subtracting its own digit.
        effective_amount = digits_b[i] + (1 if borrow == -1 else 0)
        new_value, borrow, technique, expl = subtract_single_column(digits_a[i], effective_amount)
        result_digits.append(new_value)
        column_reports.append((
            PLACE_VALUE_NAMES[i] if i < len(PLACE_VALUE_NAMES) else f"10^{i}",
            digits_a[i], digits_b[i], borrow, technique, expl
        ))

    result_str = "".join(str(d) for d in result_digits[::-1]).lstrip("0") or "0"
    return int(result_str), column_reports


def format_column_reports_markdown(reports, operation_symbol) -> str:
    lines = []
    for place_name, a_digit, b_digit, carry_or_borrow, technique, expl in reports:
        carry_note = ""
        if carry_or_borrow == 1:
            carry_note = " *(carries 1 to the next rod)*"
        elif carry_or_borrow == -1:
            carry_note = " *(borrows 1 from the next rod)*"
        lines.append(
            f"**{place_name} rod:** {a_digit} {operation_symbol} {b_digit} → *{technique}*{carry_note}  \n{expl}"
        )
    return "\n\n".join(lines)


# --- Drill (practice question) generators, one per technique ---

def generate_direct_add_drill(max_tries=400):
    for _ in range(max_tries):
        a, b = random.randint(0, 9), random.randint(1, 9)
        new_value, carry, technique, expl = add_single_column(a, b)
        if technique == "Direct addition" and carry == 0:
            return a, b, new_value, expl
    return 2, 1, 3, "Direct addition: 2 + 1 = 3."


def generate_small_friend_add_drill(max_tries=400):
    for _ in range(max_tries):
        a, b = random.randint(0, 4), random.randint(1, 4)
        new_value, carry, technique, expl = add_single_column(a, b)
        if "Small Friend" in technique and carry == 0:
            return a, b, new_value, expl
    return 3, 4, 7, "Small friend: 4 = 5 - 1."


def generate_big_friend_add_drill(max_tries=400):
    for _ in range(max_tries):
        a, b = random.randint(1, 9), random.randint(1, 9)
        new_value, carry, technique, expl = add_single_column(a, b)
        if carry == 1:
            return a, b, new_value, expl
    return 7, 8, 5, "Big friend: 8 = 10 - 2."


def generate_direct_sub_drill(max_tries=400):
    for _ in range(max_tries):
        a = random.randint(1, 9)
        b = random.randint(1, a)
        new_value, borrow, technique, expl = subtract_single_column(a, b)
        if technique == "Direct subtraction" and borrow == 0:
            return a, b, new_value, expl
    return 3, 1, 2, "Direct subtraction: 3 - 1 = 2."


def generate_small_friend_sub_drill(max_tries=400):
    for _ in range(max_tries):
        a = random.randint(5, 9)
        b = random.randint(1, 4)
        if b > a:
            continue
        new_value, borrow, technique, expl = subtract_single_column(a, b)
        if "Small Friend" in technique and borrow == 0:
            return a, b, new_value, expl
    return 6, 4, 2, "Small friend: 4 = 5 - 1."


def generate_big_friend_sub_drill(max_tries=400):
    for _ in range(max_tries):
        a = random.randint(0, 8)
        b = random.randint(a + 1, 9)
        new_value, borrow, technique, expl = subtract_single_column(a, b)
        if borrow == -1:
            return a, b, new_value, expl
    return 3, 7, 6, "Big friend: 7 = 10 - 3."


def generate_multi_digit_add_drill(max_tries=200):
    for _ in range(max_tries):
        a = random.randint(15, 89)
        b = random.randint(15, 89)
        result, reports = abacus_multi_add(a, b)
        techniques_used = {r[4] for r in reports}
        if techniques_used - {"No change", "Direct addition"}:
            return a, b, result, reports
    a, b = 47, 38
    result, reports = abacus_multi_add(a, b)
    return a, b, result, reports


def generate_multi_digit_sub_drill(max_tries=200):
    for _ in range(max_tries):
        a = random.randint(30, 99)
        b = random.randint(15, a)
        result, reports = abacus_multi_subtract(a, b)
        techniques_used = {r[4] for r in reports}
        if techniques_used - {"No change", "Direct subtraction"}:
            return a, b, result, reports
    a, b = 82, 47
    result, reports = abacus_multi_subtract(a, b)
    return a, b, result, reports
