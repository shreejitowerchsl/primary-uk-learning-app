"""
Addition & Subtraction tab.

  * Column addition / subtraction with positive whole numbers (carrying and exchanging)
  * Negative numbers on a number line: Beginner, Intermediate, Advanced
  * Word problems with negative numbers (temperatures, lifts, diving, money, scores)

Every question comes with a worked, step-by-step solution (and a number line
for the negative-number questions).
"""

import random

import streamlit as st

from modules.helpers import record_attempt, show_feedback
from modules.maths.visuals import fmt, number_line_svg

PLACE_NAMES = ["Ones", "Tens", "Hundreds", "Thousands", "Ten thousands"]
OP_SYMBOL = {"+": "+", "-": "\u2212"}


# =============================================================================
# FORMATTING HELPERS
# =============================================================================

def operand(n):
    """A number as the second part of a sum: negatives get brackets, e.g. (−3)."""
    return f"({fmt(n)})" if n < 0 else fmt(n)


def expression(a, op, b):
    return f"{fmt(a)} {OP_SYMBOL[op]} {operand(b)}"


def vertical_layout(a, b, result, op):
    """A monospace column layout of a sum, for the worked solution."""
    width = max(len(str(a)), len(str(b)), len(str(result))) + 2
    rows = [
        str(a).rjust(width),
        f"{OP_SYMBOL[op]} " + str(b).rjust(width - 2),
        "-" * width,
        str(result).rjust(width),
    ]
    return "```\n" + "\n".join(rows) + "\n```"


# =============================================================================
# COLUMN ADDITION / SUBTRACTION (positive numbers)
# =============================================================================

def column_addition_steps(a, b):
    n = max(len(str(a)), len(str(b)))
    da = [int(c) for c in str(a).zfill(n)][::-1]
    db = [int(c) for c in str(b).zfill(n)][::-1]

    lines, carry = [], 0
    for i in range(n):
        total = da[i] + db[i] + carry
        digit, new_carry = total % 10, total // 10
        carried = f" + {carry} (carried)" if carry else ""
        if new_carry:
            lines.append(
                f"- **{PLACE_NAMES[i]}:** {da[i]} + {db[i]}{carried} = {total} → "
                f"write **{digit}** and carry **{new_carry}** to the next column."
            )
        else:
            lines.append(f"- **{PLACE_NAMES[i]}:** {da[i]} + {db[i]}{carried} = {total} → write **{digit}**.")
        carry = new_carry
    if carry:
        lines.append(f"- The last carry of **{carry}** is written at the front.")

    result = a + b
    return f"""
Add the columns from the **right** (the ones) to the **left**.

{vertical_layout(a, b, result, "+")}

{chr(10).join(lines)}

### {a} + {b} = **{result}**
"""


def column_subtraction_steps(a, b):
    """a >= b. Shows exchanging ('borrowing') whenever the top digit is too small."""
    n = len(str(a))
    top = [int(c) for c in str(a)][::-1]
    bottom = [int(c) for c in str(b).zfill(n)][::-1]

    lines = []
    for i in range(n):
        t, btm = top[i], bottom[i]
        if t < btm:
            k = i + 1
            while top[k] == 0:
                k += 1
            top[k] -= 1
            for m in range(i + 1, k):
                top[m] = 9
            original = t
            t += 10
            if k == i + 1:
                exchange = (
                    f"{original} is smaller than {btm}, so exchange: take 1 from the {PLACE_NAMES[k]} column "
                    f"(it becomes {top[k]}) and add 10 here, making {t}."
                )
            else:
                exchange = (
                    f"{original} is smaller than {btm}, and the next column is 0, so go along to the "
                    f"{PLACE_NAMES[k]} column: take 1 from it (it becomes {top[k]}), the zeros in between "
                    f"become 9s, and add 10 here, making {t}."
                )
            lines.append(f"- **{PLACE_NAMES[i]}:** {exchange} Then {t} − {btm} = **{t - btm}**.")
        else:
            lines.append(f"- **{PLACE_NAMES[i]}:** {t} − {btm} = **{t - btm}**.")

    result = a - b
    return f"""
Subtract the columns from the **right** (the ones) to the **left**. If a top digit is too small,
we **exchange** (borrow) from the next column.

{vertical_layout(a, b, result, "-")}

{chr(10).join(lines)}

### {a} − {b} = **{result}**
"""


def gen_column_addition():
    digits = random.choice([3, 4])
    low, high = 10 ** (digits - 1), 10 ** digits - 1
    a, b = random.randint(low, high), random.randint(low, high)
    return {
        "question": f"{a:,} + {b:,}",
        "answer": a + b,
        "steps": column_addition_steps(a, b),
        "svg": None,
        "is_word": False,
    }


def gen_column_subtraction():
    digits = random.choice([3, 4])
    low, high = 10 ** (digits - 1), 10 ** digits - 1
    a = random.randint(low + 100, high)
    b = random.randint(low, a - 1)
    return {
        "question": f"{a:,} \u2212 {b:,}",
        "answer": a - b,
        "steps": column_subtraction_steps(a, b),
        "svg": None,
        "is_word": False,
    }


# =============================================================================
# NEGATIVE NUMBERS (number line method)
# =============================================================================

def integer_answer(a, op, b):
    return a + b if op == "+" else a - b


def integer_steps(a, op, b):
    """Worked solution for a ± b where a and b can be positive or negative."""
    ans = integer_answer(a, op, b)
    n = abs(b)

    if b < 0 and op == "+":
        step1 = (
            f"**Step 1 — Adding a negative number is the same as subtracting.**  \n"
            f"{expression(a, op, b)} becomes **{fmt(a)} − {n}**."
        )
        direction = "left"
    elif b < 0 and op == "-":
        step1 = (
            f"**Step 1 — Subtracting a negative number is the same as adding** "
            f"(two minus signs make a plus).  \n"
            f"{expression(a, op, b)} becomes **{fmt(a)} + {n}**."
        )
        direction = "right"
    elif op == "+":
        step1 = (
            f"**Step 1 — Adding a positive number moves you RIGHT** along the number line "
            f"(the number gets bigger)."
        )
        direction = "right"
    else:
        step1 = (
            f"**Step 1 — Subtracting a positive number moves you LEFT** along the number line "
            f"(the number gets smaller)."
        )
        direction = "left"

    plural = "step" if n == 1 else "steps"
    step2 = f"**Step 2 — Start at {fmt(a)} and move {n} {plural} {direction}.**  \n"

    if direction == "right" and a < 0 and ans > 0:
        step2 += (
            f"It takes {abs(a)} steps to get from {fmt(a)} up to 0, then {n - abs(a)} more steps "
            f"past zero, landing on {fmt(ans)}."
        )
    elif direction == "left" and a > 0 and ans < 0:
        step2 += (
            f"It takes {a} steps to get from {a} down to 0, then {n - a} more steps below zero, "
            f"landing on {fmt(ans)}."
        )
    elif ans == 0:
        step2 += "You land exactly on **0**."
    elif direction == "left" and a <= 0:
        step2 += (
            f"You are already on or below zero, so moving left makes the number "
            f"**more negative**: {abs(a)} + {n} = {abs(a) + n}, so the answer is {fmt(ans)}."
        )
    elif direction == "right" and a < 0:
        step2 += f"Moving right brings you **closer to zero**, landing on {fmt(ans)}."
    else:
        step2 += f"You land on {fmt(ans)}."

    return f"""
{step1}

{step2}

### {expression(a, op, b)} = **{fmt(ans)}**
"""


def _integer_question(a, op, b, is_word=False, text=None, story=None):
    ans = integer_answer(a, op, b)
    steps = integer_steps(a, op, b)
    if story:
        steps = f"**Turn the story into a calculation:** {expression(a, op, b)}\n\n" + steps
    return {
        "question": text or f"{expression(a, op, b)}",
        "answer": ans,
        "steps": steps,
        "svg": number_line_svg(a, ans),
        "is_word": is_word,
    }


def gen_negatives_beginner():
    a = random.randint(-10, 10)
    b = random.randint(1, 10)
    op = random.choice(["+", "-"])
    return _integer_question(a, op, b)


def gen_negatives_intermediate():
    """Always crosses zero, with larger numbers."""
    for _ in range(200):
        a = random.randint(-50, 50)
        b = random.randint(5, 60)
        op = random.choice(["+", "-"])
        ans = integer_answer(a, op, b)
        if a * ans < 0:  # start and end are on opposite sides of zero
            return _integer_question(a, op, b)
    return _integer_question(-23, "+", 40)


def gen_negatives_advanced():
    """Adding and subtracting negative numbers."""
    a = random.randint(-20, 20)
    b = random.choice([n for n in range(-15, 16) if n != 0])
    if random.random() < 0.65:
        b = -abs(b)
    op = random.choice(["+", "-"])
    return _integer_question(a, op, b)


# =============================================================================
# WORD PROBLEMS WITH NEGATIVE NUMBERS
# =============================================================================

def gen_negative_word_problem():
    kind = random.choice(["temp_rise", "temp_fall", "lift", "diver", "bank", "difference", "score"])

    if kind == "temp_rise":
        a, b = -random.randint(2, 12), random.randint(3, 18)
        text = (f"At 6 am the temperature was {fmt(a)}°C. By midday it had risen by {b} degrees. "
                f"What was the temperature at midday, in °C?")
        return _integer_question(a, "+", b, True, text, story=True)

    if kind == "temp_fall":
        a = random.randint(1, 10)
        b = random.randint(a + 2, a + 14)
        text = (f"At noon the temperature in a mountain village was {a}°C. During the night it fell by "
                f"{b} degrees. What was the night-time temperature, in °C?")
        return _integer_question(a, "-", b, True, text, story=True)

    if kind == "lift":
        a = random.randint(1, 6)
        b = random.randint(a + 1, a + 4)
        text = (f"A lift is on floor {a} of a building that has basement floors. Basement floors are "
                f"negative numbers, so the first basement is floor −1. The lift goes down {b} floors. "
                f"Which floor is it on now?")
        return _integer_question(a, "-", b, True, text, story=True)

    if kind == "diver":
        depth = random.randint(3, 15)
        move = random.randint(2, 12)
        if random.random() < 0.5:
            text = (f"A diver is {depth} metres below sea level, which we write as {fmt(-depth)}. She swims "
                    f"down another {move} metres. What number shows her new position?")
            return _integer_question(-depth, "-", move, True, text, story=True)
        text = (f"A diver is {depth} metres below sea level, which we write as {fmt(-depth)}. She swims "
                f"up {move} metres. What number shows her new position?")
        return _integer_question(-depth, "+", move, True, text, story=True)

    if kind == "bank":
        a = random.randint(5, 40)
        b = random.randint(a + 3, a + 30)
        text = (f"Priya has £{a} in her account. She buys a game for £{b}. Write her new balance as a "
                f"number, in pounds. (A negative balance means she owes money.)")
        return _integer_question(a, "-", b, True, text, story=True)

    if kind == "difference":
        cold, warm = random.randint(2, 15), random.randint(1, 20)
        text = (f"In Oslo the temperature is {fmt(-cold)}°C and in Rome it is {warm}°C. "
                f"How many degrees warmer is Rome than Oslo?")
        return _integer_question(warm, "-", -cold, True, text, story=True)

    a, b = -random.randint(3, 12), random.randint(5, 18)
    text = (f"In a quiz game, Team Red has {fmt(a)} points after losing points for wrong answers. "
            f"They then win {b} points. What is their new score?")
    return _integer_question(a, "+", b, True, text, story=True)


CATEGORIES = {
    "Column Addition (positive numbers)": gen_column_addition,
    "Column Subtraction (positive numbers)": gen_column_subtraction,
    "🟢 Negative Numbers — Beginner (number line)": gen_negatives_beginner,
    "🟡 Negative Numbers — Intermediate (crossing zero)": gen_negatives_intermediate,
    "🔴 Negative Numbers — Advanced (adding & subtracting negatives)": gen_negatives_advanced,
    "🌡️ Word Problems with Negative Numbers": gen_negative_word_problem,
}


# =============================================================================
# LESSON
# =============================================================================

def _render_lesson():
    with st.expander("📘 Lesson: Negative numbers and the number line"):
        st.markdown(
            """
A **negative number** is a number **below zero**. You see them on thermometers when it's freezing
(−3°C), in lifts with basement floors, and when someone owes money.

On a number line, **numbers get bigger as you go RIGHT** and **smaller as you go LEFT**.
Zero is in the middle (the red mark).
"""
        )
        st.markdown(number_line_svg(-3, 4), unsafe_allow_html=True)
        st.markdown(
            """
**Four rules to remember**

| Calculation | What it means | Example |
|:---|:---|:---|
| **+ a positive** | move **right** | −2 + 5 = 3 |
| **− a positive** | move **left** | 2 − 5 = −3 |
| **+ a negative** | same as **subtracting** | 4 + (−3) = 4 − 3 = 1 |
| **− a negative** | same as **adding** | 4 − (−3) = 4 + 3 = 7 |

💡 **Tip:** when you cross zero, split the jump in two — first get to 0, then use the steps that are left.
"""
        )

    with st.expander("📗 Lesson: Column addition and subtraction"):
        st.markdown(
            """
For bigger positive numbers, line the digits up in **columns** (ones under ones, tens under tens...).

- **Addition:** start at the ones. If a column adds up to 10 or more, write the ones digit and
  **carry** the 1 to the next column.
- **Subtraction:** start at the ones. If the top digit is too small, **exchange**: take 1 from the next
  column to the left and add 10 to this one.
"""
        )


# =============================================================================
# RENDER
# =============================================================================

def render():
    st.markdown("## ➕➖ Addition & Subtraction")
    st.caption("Positive and negative numbers — from column methods to number lines through zero.")
    _render_lesson()

    category = st.selectbox("Choose a topic:", list(CATEGORIES.keys()), key="as_category")
    if st.session_state.as_last_category != category:
        st.session_state.as_question = None
        st.session_state.as_feedback = None
        st.session_state.as_last_category = category

    if st.button("🎲 Generate Question", key="as_generate_btn"):
        q = CATEGORIES[category]()
        st.session_state.as_qid += 1
        st.session_state.as_question = q["question"]
        st.session_state.as_is_word = q["is_word"]
        st.session_state.as_answer = q["answer"]
        st.session_state.as_steps = q["steps"]
        st.session_state.as_svg = q["svg"]
        st.session_state.as_feedback = None

    if st.session_state.as_question is None:
        st.info("👆 Click **Generate Question** to get started!")
        return

    if st.session_state.as_is_word:
        st.markdown(
            f'<div class="word-box">📖 <strong>Problem:</strong><br>{st.session_state.as_question}</div>',
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            f'<div class="question-box">{st.session_state.as_question} = ?</div>',
            unsafe_allow_html=True,
        )

    guess = st.number_input(
        "Your answer (use a minus sign for negative numbers):",
        step=1, value=0, key=f"as_answer_input_{st.session_state.as_qid}",
    )

    if st.button("✅ Check Answer", key="as_check_btn"):
        is_correct = int(guess) == st.session_state.as_answer
        message = record_attempt(is_correct)
        if not is_correct:
            message += f" The correct answer was **{fmt(st.session_state.as_answer)}**."
        st.session_state.as_feedback = (is_correct, message)

    show_feedback(st.session_state.as_feedback)

    with st.expander("💡 Show Step-by-Step Solution"):
        st.markdown(st.session_state.as_steps)
        if st.session_state.as_svg:
            st.markdown("**On the number line:**")
            st.markdown(st.session_state.as_svg, unsafe_allow_html=True)
