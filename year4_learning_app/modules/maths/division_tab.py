"""Division practice tab: 3/4-digit dividends by a 1- or 2-digit divisor."""

import random

import streamlit as st

from modules.helpers import short_division_steps, record_attempt, show_feedback


def generate_division_question():
    digits = random.choice([3, 4])
    if digits == 3:
        dividend = random.randint(100, 999)
        divisor = random.randint(2, 9)
    else:
        dividend = random.randint(1000, 9999)
        divisor = random.randint(2, 12)

    quotient, remainder, steps = short_division_steps(dividend, divisor)
    return dividend, divisor, quotient, remainder, steps


def render():
    st.markdown("## ➗ Division Practice")
    st.caption("3 or 4-digit numbers divided by a 1- or 2-digit number, using the bus-stop method.")

    if st.button("🎲 Generate Question", key="div_generate_btn"):
        dividend, divisor, quotient, remainder, steps = generate_division_question()
        st.session_state.div_dividend = dividend
        st.session_state.div_divisor = divisor
        st.session_state.div_quotient = quotient
        st.session_state.div_remainder = remainder
        st.session_state.div_steps = steps
        st.session_state.div_feedback = None
        st.session_state["div_quotient_input"] = 0
        st.session_state["div_remainder_input"] = 0

    if st.session_state.div_dividend is not None:
        st.markdown(
            f'<div class="question-box">{st.session_state.div_dividend} ÷ '
            f'{st.session_state.div_divisor} = ?</div>',
            unsafe_allow_html=True,
        )

        col1, col2 = st.columns(2)
        with col1:
            quotient_guess = st.number_input(
                "Quotient (the whole-number answer):", step=1, value=0, key="div_quotient_input"
            )
        with col2:
            remainder_guess = st.number_input(
                "Remainder (0 if none):", step=1, value=0, key="div_remainder_input"
            )

        if st.button("✅ Check Answer", key="div_check_btn"):
            is_correct = (
                int(quotient_guess) == st.session_state.div_quotient
                and int(remainder_guess) == st.session_state.div_remainder
            )
            message = record_attempt(is_correct)
            if not is_correct:
                message += (
                    f" The correct answer was **{st.session_state.div_quotient} "
                    f"remainder {st.session_state.div_remainder}**."
                )
            st.session_state.div_feedback = (is_correct, message)

        show_feedback(st.session_state.div_feedback)

        with st.expander("💡 Show Step-by-Step Solution"):
            st.markdown(st.session_state.div_steps)
    else:
        st.info("👆 Click **Generate Question** to get started!")
