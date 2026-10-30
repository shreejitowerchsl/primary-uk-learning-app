"""
Word Problems tab: Multiplication, Division, and two-step Mixed problems,
each with Beginner / Intermediate / Advanced levels, using UK contexts
(pence/pounds, football teams, crates, school items, coaches, bakeries...).
"""

import random

import streamlit as st

from modules.helpers import multiplication_steps, short_division_steps, record_attempt, show_feedback

OPERATIONS = ["✖️ Multiplication", "➗ Division", "🔀 Mixed (Two-Step)"]
LEVELS = ["🟢 Beginner", "🟡 Intermediate", "🔴 Advanced"]


# =============================================================================
# MULTIPLICATION WORD PROBLEMS
# =============================================================================

def _mult_beginner():
    templates = [
        ("There are {b} bags of marbles. Each bag has {a} marbles. How many marbles are there in total?",
         (3, 12), (2, 9), "marbles"),
        ("A classroom has {b} tables, and {a} children sit at each table. How many children are there altogether?",
         (4, 8), (3, 8), "children"),
        ("Sam collects football stickers. He has {b} packets, and each packet contains {a} stickers. "
         "How many stickers does Sam have?", (5, 10), (3, 9), "stickers"),
        ("A tuck shop sells chocolate bars for {a}p each. How much would {b} bars cost, in pence?",
         (10, 30), (2, 9), "pence"),
    ]
    text_tpl, a_range, b_range, unit = random.choice(templates)
    a, b = random.randint(*a_range), random.randint(*b_range)
    question = text_tpl.format(a=a, b=b)
    answer = a * b
    steps = f"""
**Turning the words into an equation:** we need **{b} groups of {a}**.

### {a} × {b} = ?

{multiplication_steps(a, b)}

**Answer: {answer} {unit}**
"""
    return question, answer, steps


def _mult_intermediate():
    templates = [
        ("A school buys {b} boxes of pencils. Each box contains {a} pencils. "
         "How many pencils are there in total?", (12, 30), (4, 18), "pencils"),
        ("Entry to the museum costs £{a} per child. A school books tickets for {b} children. "
         "How much does the school pay in total, in pounds?", (3, 9), (15, 30), "pounds"),
        ("A bakery bakes {b} trays of buns. Each tray holds {a} buns. "
         "How many buns does the bakery bake in total?", (12, 36), (5, 15), "buns"),
        ("There are {b} crates of oranges delivered to the greengrocer's. Each crate contains {a} oranges. "
         "How many oranges are delivered in total?", (20, 45), (8, 25), "oranges"),
    ]
    text_tpl, a_range, b_range, unit = random.choice(templates)
    a, b = random.randint(*a_range), random.randint(*b_range)
    question = text_tpl.format(a=a, b=b)
    answer = a * b
    steps = f"""
**Turning the words into an equation:** we need **{b} groups of {a}**.

### {a} × {b} = ?

{multiplication_steps(a, b)}

**Answer: {answer} {unit}**
"""
    return question, answer, steps


def _mult_advanced():
    templates = [
        ("A factory produces {a} toy cars every day. How many toy cars does it produce in {b} days?",
         (120, 350), (12, 28), "toy cars"),
        ("A stadium has {b} stands. Each stand holds {a} spectators. "
         "How many spectators can the stadium hold in total?", (150, 480), (11, 24), "spectators"),
        ("A printing company prints {a} leaflets every hour. How many leaflets does it print "
         "in {b} hours?", (210, 620), (14, 36), "leaflets"),
    ]
    text_tpl, a_range, b_range, unit = random.choice(templates)
    a, b = random.randint(*a_range), random.randint(*b_range)
    question = text_tpl.format(a=a, b=b)
    answer = a * b
    steps = f"""
**Turning the words into an equation:** we need **{b} groups of {a}**.

### {a} × {b} = ?

{multiplication_steps(a, b)}

**Answer: {answer} {unit}**
"""
    return question, answer, steps


# =============================================================================
# DIVISION WORD PROBLEMS
# =============================================================================

def _div_beginner():
    templates = [
        ("{a} sweets are shared equally between {b} friends. How many sweets does each friend get?", "sweets"),
        ("A gardener plants {a} flowers in {b} equal rows. How many flowers are in each row?", "flowers"),
        ("{a} football cards are shared equally among {b} collectors. How many cards does each collector get?",
         "cards"),
    ]
    text_tpl, unit = random.choice(templates)
    b = random.randint(2, 10)
    quotient = random.randint(2, 12)
    a = quotient * b  # exact division, no remainder, for a gentle first step
    question = text_tpl.format(a=a, b=b)
    _, _, steps_md = short_division_steps(a, b)
    steps = f"""
**Turning the words into an equation:** {a} shared into {b} equal groups is:

### {a} ÷ {b} = ?

{steps_md}

**Answer: {quotient} {unit} each**
"""
    return question, quotient, 0, steps, "quotient_remainder"


def _div_intermediate():
    templates = [
        ("A shop has {a} apples to pack into bags of {b}. How many full bags can be made, "
         "and how many apples are left over?", "apples", "bags"),
        ("{a} pupils are put into teams of {b} for sports day. How many full teams are there, "
         "and how many pupils are left without a team?", "pupils", "teams"),
        ("A market trader has {a} eggs to put into boxes of {b}. How many full boxes can be made, "
         "and how many eggs are left over?", "eggs", "boxes"),
    ]
    text_tpl, item_unit, group_unit = random.choice(templates)
    a = random.randint(100, 300)
    b = random.randint(3, 9)
    question = text_tpl.format(a=a, b=b)
    quotient, remainder, steps_md = short_division_steps(a, b)
    steps = f"""
**Turning the words into an equation:**

### {a} ÷ {b} = ?

{steps_md}

**Answer: {quotient} {group_unit}, with {remainder} {item_unit} left over**
"""
    return question, quotient, remainder, steps, "quotient_remainder"


def _div_advanced():
    use_ceiling = random.choice([True, False])
    if use_ceiling:
        a = random.randint(150, 480)
        b = random.randint(28, 45)
        question = (
            f"A school is organising a trip for {a} pupils. Each coach holds {b} pupils. "
            f"How many coaches are needed so that every pupil has a seat, "
            f"even if the last coach isn't full?"
        )
        quotient, remainder, steps_md = short_division_steps(a, b)
        coaches_needed = quotient + (1 if remainder else 0)
        steps = f"""
**Turning the words into an equation:**

### {a} ÷ {b} = ?

{steps_md}

Because {remainder} pupils are left over, we need **one more coach** for them —
we always round UP for "how many are needed" problems like this one.

**Answer: {coaches_needed} coaches**
"""
        return question, coaches_needed, None, steps, "single"
    else:
        a = random.randint(1000, 4000)
        b = random.randint(12, 45)
        question = (
            f"A biscuit factory has {a} biscuits to pack into boxes of {b}. "
            f"How many full boxes can be made, and how many biscuits are left over?"
        )
        quotient, remainder, steps_md = short_division_steps(a, b)
        steps = f"""
**Turning the words into an equation:**

### {a} ÷ {b} = ?

{steps_md}

**Answer: {quotient} boxes, with {remainder} biscuits left over**
"""
        return question, quotient, remainder, steps, "quotient_remainder"


# =============================================================================
# MIXED TWO-STEP WORD PROBLEMS (Multiplication + Division combined)
# =============================================================================

def _mixed_mult_then_div(a_range, b_range, n_range, item_unit):
    a, b, n = random.randint(*a_range), random.randint(*b_range), random.randint(*n_range)
    total = a * b
    quotient, remainder, div_steps_md = short_division_steps(total, n)
    question = (
        f"A bakery bakes {b} trays of {item_unit}, with {a} {item_unit} on each tray. "
        f"The {item_unit} are then shared equally between {n} local schools. "
        f"How many {item_unit} does each school get, and are there any left over?"
    )
    steps = f"""
**Step 1 — Multiply to find the total.** {b} trays of {a} {item_unit} each:

### {a} × {b} = ?

{multiplication_steps(a, b)}

**Step 2 — Divide the total between the schools.**

### {total} ÷ {n} = ?

{div_steps_md}

**Answer: {quotient} {item_unit} per school, with {remainder} left over**
"""
    return question, quotient, remainder, steps, "quotient_remainder"


def _mixed_div_then_mult(total_range, per_box_range, price_range):
    total = random.randint(*total_range)
    per_box = random.randint(*per_box_range)
    price = random.randint(*price_range)
    boxes, leftover, div_steps_md = short_division_steps(total, per_box)
    money = boxes * price
    question = (
        f"A factory makes {total} chocolate bars. They are packed into boxes of {per_box}. "
        f"Each full box is sold for £{price}. How much money will the full boxes raise "
        f"altogether, in pounds? (Any leftover bars that don't fill a box aren't sold.)"
    )
    steps = f"""
**Step 1 — Divide to find how many full boxes can be made.**

### {total} ÷ {per_box} = ?

{div_steps_md}

So {boxes} full boxes can be made ({leftover} bars are left over and not sold).

**Step 2 — Multiply the number of boxes by the price.**

### {boxes} × £{price} = ?

{multiplication_steps(boxes, price)}

**Answer: £{money}**
"""
    return question, money, None, steps, "single"


def _mixed_beginner():
    if random.choice([True, False]):
        return _mixed_mult_then_div((4, 10), (3, 6), (2, 6), "buns")
    return _mixed_div_then_mult((20, 60), (4, 8), (2, 5))


def _mixed_intermediate():
    if random.choice([True, False]):
        return _mixed_mult_then_div((8, 20), (5, 12), (3, 9), "muffins")
    return _mixed_div_then_mult((100, 300), (6, 15), (3, 9))


def _mixed_advanced():
    if random.choice([True, False]):
        return _mixed_mult_then_div((15, 40), (10, 25), (6, 15), "flapjacks")
    return _mixed_div_then_mult((500, 2000), (12, 40), (5, 20))


def _wrap_single(func):
    """Adapt a (question, answer, steps) generator to the common 5-tuple shape."""
    def inner():
        question, answer, steps = func()
        return question, answer, None, steps, "single"
    return inner


GENERATORS = {
    ("✖️ Multiplication", "🟢 Beginner"): _wrap_single(_mult_beginner),
    ("✖️ Multiplication", "🟡 Intermediate"): _wrap_single(_mult_intermediate),
    ("✖️ Multiplication", "🔴 Advanced"): _wrap_single(_mult_advanced),
    ("➗ Division", "🟢 Beginner"): _div_beginner,
    ("➗ Division", "🟡 Intermediate"): _div_intermediate,
    ("➗ Division", "🔴 Advanced"): _div_advanced,
    ("🔀 Mixed (Two-Step)", "🟢 Beginner"): _mixed_beginner,
    ("🔀 Mixed (Two-Step)", "🟡 Intermediate"): _mixed_intermediate,
    ("🔀 Mixed (Two-Step)", "🔴 Advanced"): _mixed_advanced,
}


def render():
    st.markdown("## 📖 Word Problems: Multiplication & Division")
    st.caption("Real-life UK problems — from easy times-table sharing up to two-step challenges.")

    col1, col2 = st.columns(2)
    with col1:
        operation = st.selectbox("Operation:", OPERATIONS, key="wp_operation")
    with col2:
        level = st.selectbox("Level:", LEVELS, key="wp_level")

    combo = (operation, level)
    if st.session_state.wp_last_combo != combo:
        st.session_state.wp_question = None
        st.session_state.wp_feedback = None
        st.session_state.wp_last_combo = combo

    if st.button("🎲 Generate Word Problem", key="wp_generate_btn"):
        question, answer, remainder, steps, answer_type = GENERATORS[combo]()
        st.session_state.wp_question = question
        st.session_state.wp_answer = answer
        st.session_state.wp_remainder = remainder
        st.session_state.wp_steps = steps
        st.session_state.wp_answer_type = answer_type
        st.session_state.wp_feedback = None
        st.session_state["wp_answer_input"] = 0
        st.session_state["wp_remainder_input"] = 0

    if st.session_state.wp_question is not None:
        st.markdown(
            f'<div class="word-box">📖 <strong>Problem:</strong><br>{st.session_state.wp_question}</div>',
            unsafe_allow_html=True,
        )

        if st.session_state.wp_answer_type == "quotient_remainder":
            colq, colr = st.columns(2)
            with colq:
                answer_guess = st.number_input(
                    "Your answer (whole number part):", step=1, value=0, key="wp_answer_input"
                )
            with colr:
                remainder_guess = st.number_input(
                    "Left over / remainder (0 if none):", step=1, value=0, key="wp_remainder_input"
                )
        else:
            answer_guess = st.number_input("Your answer:", step=1, value=0, key="wp_answer_input")
            remainder_guess = None

        if st.button("✅ Check Answer", key="wp_check_btn"):
            if st.session_state.wp_answer_type == "quotient_remainder":
                is_correct = (
                    int(answer_guess) == st.session_state.wp_answer
                    and int(remainder_guess) == st.session_state.wp_remainder
                )
            else:
                is_correct = int(answer_guess) == st.session_state.wp_answer

            message = record_attempt(is_correct)
            if not is_correct:
                if st.session_state.wp_answer_type == "quotient_remainder":
                    message += (
                        f" The correct answer was **{st.session_state.wp_answer}**, "
                        f"remainder **{st.session_state.wp_remainder}**."
                    )
                else:
                    message += f" The correct answer was **{st.session_state.wp_answer}**."
            st.session_state.wp_feedback = (is_correct, message)

        show_feedback(st.session_state.wp_feedback)

        with st.expander("💡 Show Step-by-Step Solution"):
            st.markdown(st.session_state.wp_steps)
    else:
        st.info("👆 Click **Generate Word Problem** to get started!")
