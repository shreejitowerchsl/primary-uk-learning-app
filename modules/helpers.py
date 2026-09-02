"""
Shared helpers used by every learning tab: encouragement messages, score
tracking, and the maths explanation helpers (multiplication breakdown and
short/'bus stop' division) that several tabs reuse.
"""

import random

import streamlit as st

# =============================================================================
# ENCOURAGEMENT MESSAGES & SCORE TRACKING
# =============================================================================

CORRECT_MESSAGES = [
    "🎉 Brilliant! You got it right!",
    "⭐ Fantastic work — that's correct!",
    "🥳 Superstar skills! Well done!",
    "✅ Spot on! You're on fire!",
    "🏆 Amazing job, that's exactly right!",
    "🚀 Wonderful! Keep it up!",
]

INCORRECT_MESSAGES = [
    "Not quite — but keep trying, you're doing great! 💪",
    "So close! Have another go. 🔍",
    "Not this time — check your steps below and try again! 📝",
    "Almost there! Give it one more try. 🌟",
    "Keep going — mistakes help us learn! 🙂",
]


def record_attempt(is_correct: bool) -> str:
    """Update the running score and return an encouraging message."""
    st.session_state.score_attempted += 1
    if is_correct:
        st.session_state.score_correct += 1
        return random.choice(CORRECT_MESSAGES)
    return random.choice(INCORRECT_MESSAGES)


def show_feedback(feedback):
    """Render a stored (is_correct, message) feedback tuple, if present."""
    if feedback is None:
        return
    is_correct, message = feedback
    if is_correct:
        st.success(message)
    else:
        st.error(message)


# =============================================================================
# SHARED MATHS EXPLANATION HELPERS
# =============================================================================

def multiplication_steps(a: int, b: int) -> str:
    """
    Build a markdown explanation of a x b by splitting b into its place-value
    parts (e.g. 236 -> 200 + 30 + 6) and multiplying each part by a.
    This naturally produces the grid method for a 1-digit multiplier, and
    the long-multiplication partial-product rows (with placeholder zeros)
    for 2- and 3-digit multipliers.
    """
    b_str = str(b)
    n = len(b_str)
    lines = []
    partial_values = []

    for i, digit_char in enumerate(b_str):
        digit = int(digit_char)
        place_value = 10 ** (n - 1 - i)
        part = digit * place_value
        if part == 0:
            continue
        product = a * part
        partial_values.append(product)

        note = ""
        if place_value == 100:
            note = "  *(hundreds row — ends in two zeros)*"
        elif place_value == 10:
            note = "  *(tens row — ends in a zero)*"

        lines.append(f"- {a} × {part} = **{product}**{note}")

    answer = a * b
    split_display = " + ".join(
        str(int(d) * 10 ** (n - 1 - i)) for i, d in enumerate(b_str) if int(d) != 0
    )
    addition_display = " + ".join(str(v) for v in partial_values)
    steps_block = "\n".join(lines)

    return f"""
Split **{b}** by place value: {b} = {split_display}

{steps_block}

Now add the partial products together:

**{addition_display} = {answer}**

### So {a} × {b} = **{answer}**
"""


def short_division_steps(dividend: int, divisor: int):
    """
    Perform the short division ('bus stop') method digit by digit and
    return (quotient, remainder, markdown_steps).
    """
    digits = str(dividend)
    lines = []
    carry = 0
    quotient_digits = []

    for i, digit_char in enumerate(digits):
        digit = int(digit_char)
        current = carry * 10 + digit
        q_digit = current // divisor
        rem = current % divisor
        quotient_digits.append(str(q_digit))

        if i == 0:
            lines.append(
                f"- Look at the first digit: **{digit}**. "
                f"{digit} ÷ {divisor} = {q_digit} remainder {rem}."
            )
        else:
            lines.append(
                f"- Carry the {carry} and bring down the next digit to make **{current}**. "
                f"{current} ÷ {divisor} = {q_digit} remainder {rem}."
            )
        carry = rem

    quotient_str = "".join(quotient_digits).lstrip("0") or "0"
    quotient = int(quotient_str)
    remainder = carry

    lines_block = "\n".join(lines)
    if remainder:
        answer_line = f"**Answer: {quotient} remainder {remainder}**"
    else:
        answer_line = f"**Answer: {quotient} (no remainder — it divides exactly!)**"

    steps_md = f"""
We'll use the short division ('bus stop') method for **{dividend} ÷ {divisor}**.

{lines_block}

{answer_line}
"""
    return quotient, remainder, steps_md
