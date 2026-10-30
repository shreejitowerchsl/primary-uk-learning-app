"""Abacus (soroban) learning tab: Beginner -> Intermediate -> Advanced."""

import streamlit as st

from modules.helpers import record_attempt, show_feedback
from modules.maths.abacus_engine import (
    draw_abacus_svg,
    generate_direct_add_drill,
    generate_direct_sub_drill,
    generate_small_friend_add_drill,
    generate_small_friend_sub_drill,
    generate_big_friend_add_drill,
    generate_big_friend_sub_drill,
    generate_multi_digit_add_drill,
    generate_multi_digit_sub_drill,
    format_column_reports_markdown,
)


def render():
    st.markdown("## 🧮 Learn the Abacus")
    st.caption("A step-by-step journey from your very first bead to carrying and borrowing like a pro!")

    level = st.radio(
        "Choose your level:", ["🟢 Beginner", "🟡 Intermediate", "🔴 Advanced"],
        horizontal=True, key="abacus_level",
    )

    if level == "🟢 Beginner":
        _render_beginner()
    elif level == "🟡 Intermediate":
        _render_intermediate()
    else:
        _render_advanced()


def _render_beginner():
    with st.expander("📘 Lesson 1: Meet Your Abacus", expanded=True):
        st.markdown(
            """
An **abacus** is one of the oldest calculators in the world — people have used it for
thousands of years, and it's still used today! This app teaches the **soroban**, a
Japanese-style abacus.

Here's what it's made of:

- **The frame** 🟫 — the wooden border that holds everything together.
- **Rods** — the vertical wires that beads slide up and down on. Each rod stands for
  one column of a number (ones, tens, hundreds...), just like in the numbers you
  already write.
- **The beam** — the horizontal bar across the middle. Beads that touch the beam are
  "switched on" and get *counted*. Beads resting away from the beam are "switched off".
- **The heaven bead** 🔴 — there is **one** bead above the beam on each rod, and it is
  worth **5**.
- **The earth beads** 🟢 — there are **four** beads below the beam on each rod, and
  each one is worth **1**.

So the biggest number one single rod can show is 5 + 1 + 1 + 1 + 1 = **9** — exactly
like the biggest digit we ever write in one column!
"""
        )
        st.markdown("**Here is an empty rod (showing 0) next to a rod showing 9:**")
        st.markdown(
            f'<div style="display:flex;gap:2rem;justify-content:center;">'
            f'{draw_abacus_svg(0, min_rods=1)}{draw_abacus_svg(9, min_rods=1)}</div>',
            unsafe_allow_html=True,
        )

    with st.expander("📗 Lesson 2: Place Value on the Abacus"):
        st.markdown(
            """
Just like in the number **347**, where 3 means 300, 4 means 40, and 7 means 7 — each
rod of the abacus represents a place value. The **rightmost rod is always the Ones**,
then moving left: **Tens**, **Hundreds**, **Thousands**, and so on.

Look at the abacus below showing the number **347**:
"""
        )
        st.markdown(
            f'<div style="display:flex;justify-content:center;">{draw_abacus_svg(347)}</div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            "Notice the **Hundreds rod** has heaven bead active (worth 5) plus "
            "two earth beads (2), making 3 hundreds. Can you see the 4 tens and 7 ones?"
        )

    with st.expander("📙 Lesson 3: Try It Yourself — Make a Number!"):
        st.markdown("Type any number from 0 to 999 and watch the abacus set itself up:")
        number_to_show = st.number_input(
            "Number to display:", min_value=0, max_value=999, step=1, key="abacus_show_number"
        )
        st.markdown(
            f'<div style="display:flex;justify-content:center;">'
            f'{draw_abacus_svg(int(number_to_show))}</div>',
            unsafe_allow_html=True,
        )
        st.success(
            f"That's {int(number_to_show)}! Notice how each rod's beads add up to "
            f"exactly the digit shown underneath it."
        )


def _render_intermediate():
    with st.expander("📘 Lesson 4: Direct Addition & Subtraction"):
        st.markdown(
            """
The simplest way to add or subtract on the abacus is called **direct addition** —
you already have enough beads free, so you just slide the beads you need towards
(or away from) the beam. No tricks needed!

**Example:** 3 + 2 → there are already 2 free earth beads to push up, so 3 becomes 5.

**Example:** 6 − 1 → just slide one earth bead away from the beam, so 6 becomes 5.
"""
        )

    with st.expander("📗 Lesson 5: Small Friends — the 5-Complement"):
        st.markdown(
            """
Sometimes you want to add a small number (1, 2, 3 or 4), but there aren't enough
free earth beads left! That's when we use a **Small Friend** — a pair of numbers
that add up to 5:

| Number | Small Friend | Because |
|:---:|:---:|:---|
| 1 | 4 | 1 = 5 − 4 |
| 2 | 3 | 2 = 5 − 3 |
| 3 | 2 | 3 = 5 − 2 |
| 4 | 1 | 4 = 5 − 1 |

**To add** a number using its small friend: push the **heaven bead down** (+5), then
take away its small friend from the earth beads.

**To subtract** a number using its small friend: take the **heaven bead away** (−5),
then add back its small friend in earth beads.

**Example:** 2 + 4 → you only have 3 free earth beads, not enough! So: 4 = 5 − 1.
Push the heaven bead down (+5), remove 1 earth bead (−1). Result: 6.
"""
        )

    st.markdown("### 🎯 Practice Time!")
    drill_choice = st.selectbox(
        "Choose a drill:",
        ["Direct Addition", "Direct Subtraction", "Small Friend Addition", "Small Friend Subtraction"],
        key="abacus_intermediate_drill_choice",
    )

    if st.button("🎲 Generate Practice Question", key="abacus_inter_generate_btn"):
        if drill_choice == "Direct Addition":
            a, b, answer, expl = generate_direct_add_drill()
            op = "+"
        elif drill_choice == "Direct Subtraction":
            a, b, answer, expl = generate_direct_sub_drill()
            op = "−"
        elif drill_choice == "Small Friend Addition":
            a, b, answer, expl = generate_small_friend_add_drill()
            op = "+"
        else:
            a, b, answer, expl = generate_small_friend_sub_drill()
            op = "−"

        st.session_state.abacus_drill_type = drill_choice
        st.session_state.abacus_drill_a = a
        st.session_state.abacus_drill_b = b
        st.session_state.abacus_drill_op = op
        st.session_state.abacus_drill_answer = answer
        st.session_state.abacus_drill_start_svg = draw_abacus_svg(a, min_rods=1)
        st.session_state.abacus_drill_steps = expl
        st.session_state.abacus_drill_feedback = None
        st.session_state["abacus_drill_answer_input"] = 0

    if st.session_state.abacus_drill_a is not None and st.session_state.abacus_drill_type == drill_choice:
        st.markdown(
            f'<div class="question-box">{st.session_state.abacus_drill_a} '
            f'{st.session_state.abacus_drill_op} {st.session_state.abacus_drill_b} = ?</div>',
            unsafe_allow_html=True,
        )
        st.markdown("**Starting position on the rod:**")
        st.markdown(
            f'<div style="display:flex;justify-content:center;">'
            f'{st.session_state.abacus_drill_start_svg}</div>',
            unsafe_allow_html=True,
        )

        user_answer = st.number_input("Your answer:", step=1, value=0, key="abacus_drill_answer_input")
        if st.button("✅ Check Answer", key="abacus_inter_check_btn"):
            is_correct = int(user_answer) == st.session_state.abacus_drill_answer
            message = record_attempt(is_correct)
            if not is_correct:
                message += f" The correct answer was **{st.session_state.abacus_drill_answer}**."
            st.session_state.abacus_drill_feedback = (is_correct, message)

        show_feedback(st.session_state.abacus_drill_feedback)

        with st.expander("💡 Show Step-by-Step Bead Moves"):
            st.markdown(st.session_state.abacus_drill_steps)
            st.markdown("**Final position on the rod:**")
            st.markdown(
                f'<div style="display:flex;justify-content:center;">'
                f'{draw_abacus_svg(st.session_state.abacus_drill_answer, min_rods=1)}</div>',
                unsafe_allow_html=True,
            )
    else:
        st.info("👆 Click **Generate Practice Question** to get started!")


def _render_advanced():
    with st.expander("📘 Lesson 6: Big Friends — the 10-Complement"):
        st.markdown(
            """
What happens if a rod would need to go past 9? There's no room — a rod can only
hold up to 9! This is when we use a **Big Friend**: a pair of numbers that add up
to 10, and we carry into the *next* rod (just like carrying in column addition).

| Number | Big Friend | Because |
|:---:|:---:|:---|
| 1 | 9 | 1 = 10 − 9 |
| 2 | 8 | 2 = 10 − 8 |
| 3 | 7 | 3 = 10 − 7 |
| 4 | 6 | 4 = 10 − 6 |
| 5 | 5 | 5 = 10 − 5 |
| 6 | 4 | 6 = 10 − 4 |
| 7 | 3 | 7 = 10 − 3 |
| 8 | 2 | 8 = 10 − 2 |
| 9 | 1 | 9 = 10 − 1 |

**To add** using a big friend: add **1 bead on the rod to the left** (carry), then
take away that number's big friend from the current rod.

**To subtract** using a big friend: **borrow 1** from the rod to the left (it loses
a bead), then add back that number's big friend on the current rod.

**Example:** 7 + 8 → 8 = 10 − 2. Carry +1 to the next rod, take away 2 from this
rod. 7 becomes 5, and the next rod gains 1 — together that reads as 15!
"""
        )

    with st.expander("📕 Lesson 7: Putting It All Together — Multi-Digit Numbers"):
        st.markdown(
            """
For bigger numbers, we work through the rods one at a time, usually starting from
the **Ones** rod, just like column addition. If a rod needs a Big Friend, the carry
(or borrow) passes to the next rod along, and we solve that rod using whichever
technique it needs — Direct, Small Friend, or Big Friend again!

Try the practice problems below to see a full multi-digit breakdown, rod by rod.
"""
        )

    st.markdown("### 🎯 Practice Time!")
    adv_drill_choice = st.selectbox(
        "Choose a drill:",
        ["Big Friend Addition", "Big Friend Subtraction", "Multi-Digit Addition", "Multi-Digit Subtraction"],
        key="abacus_advanced_drill_choice",
    )

    if st.button("🎲 Generate Practice Question", key="abacus_adv_generate_btn"):
        if adv_drill_choice == "Big Friend Addition":
            a, b, answer, expl = generate_big_friend_add_drill()
            op = "+"
            st.session_state.abacus_drill_steps = expl
        elif adv_drill_choice == "Big Friend Subtraction":
            a, b, answer, expl = generate_big_friend_sub_drill()
            op = "−"
            st.session_state.abacus_drill_steps = expl
        elif adv_drill_choice == "Multi-Digit Addition":
            a, b, answer, reports = generate_multi_digit_add_drill()
            op = "+"
            st.session_state.abacus_drill_steps = format_column_reports_markdown(reports, "+")
        else:
            a, b, answer, reports = generate_multi_digit_sub_drill()
            op = "−"
            st.session_state.abacus_drill_steps = format_column_reports_markdown(reports, "−")

        st.session_state.abacus_drill_type = adv_drill_choice
        st.session_state.abacus_drill_a = a
        st.session_state.abacus_drill_b = b
        st.session_state.abacus_drill_op = op
        st.session_state.abacus_drill_answer = answer
        st.session_state.abacus_drill_start_svg = draw_abacus_svg(a)
        st.session_state.abacus_drill_feedback = None
        st.session_state["abacus_drill_answer_input_adv"] = 0

    if st.session_state.abacus_drill_a is not None and st.session_state.abacus_drill_type == adv_drill_choice:
        st.markdown(
            f'<div class="question-box">{st.session_state.abacus_drill_a} '
            f'{st.session_state.abacus_drill_op} {st.session_state.abacus_drill_b} = ?</div>',
            unsafe_allow_html=True,
        )
        st.markdown("**Starting position (first number):**")
        st.markdown(
            f'<div style="display:flex;justify-content:center;">'
            f'{st.session_state.abacus_drill_start_svg}</div>',
            unsafe_allow_html=True,
        )

        user_answer = st.number_input("Your answer:", step=1, value=0, key="abacus_drill_answer_input_adv")
        if st.button("✅ Check Answer", key="abacus_adv_check_btn"):
            is_correct = int(user_answer) == st.session_state.abacus_drill_answer
            message = record_attempt(is_correct)
            if not is_correct:
                message += f" The correct answer was **{st.session_state.abacus_drill_answer}**."
            st.session_state.abacus_drill_feedback = (is_correct, message)

        show_feedback(st.session_state.abacus_drill_feedback)

        with st.expander("💡 Show Step-by-Step Bead Moves"):
            st.markdown(st.session_state.abacus_drill_steps)
            st.markdown("**Final position (the answer):**")
            st.markdown(
                f'<div style="display:flex;justify-content:center;">'
                f'{draw_abacus_svg(st.session_state.abacus_drill_answer)}</div>',
                unsafe_allow_html=True,
            )
    else:
        st.info("👆 Click **Generate Practice Question** to get started!")

    st.markdown("---")
    st.markdown(
        "**🚀 What comes after this?** Once carrying and borrowing feel easy, the next "
        "abacus skills are multiplication and division on the rods, and eventually "
        "*anzan* — doing all of this in your head by picturing the abacus! Keep practising "
        "and you'll get there. 🌟"
    )
