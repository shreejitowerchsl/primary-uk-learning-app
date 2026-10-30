"""Powers (exponents) practice tab: base^2, base^3, base^4."""

import random

import streamlit as st

from modules.helpers import record_attempt, show_feedback


def generate_power_question():
    exponent = random.choice([2, 3, 4])
    base = random.randint(1, 5) if exponent == 4 else random.randint(1, 12)
    answer = base ** exponent
    chain_display = " × ".join([str(base)] * exponent)

    lines = []
    running_value = base
    for _ in range(2, exponent + 1):
        previous_value = running_value
        running_value *= base
        lines.append(f"- {previous_value} × {base} = **{running_value}**")
    lines_block = "\n".join(lines)

    steps = f"""
**{base}^{exponent}** means multiplying {base} by itself {exponent} times.

{base}^{exponent} = {chain_display}

{lines_block}

### So {base}^{exponent} = **{answer}**
"""
    return base, exponent, answer, steps


def render():
    st.markdown("## ⬆️ Powers Practice")
    st.caption("Calculate a number raised to the power of 2, 3, or 4 — great Year 4/5 extension work!")

    if st.button("🎲 Generate Question", key="pow_generate_btn"):
        base, exponent, answer, steps = generate_power_question()
        st.session_state.pow_base = base
        st.session_state.pow_exp = exponent
        st.session_state.pow_answer = answer
        st.session_state.pow_steps = steps
        st.session_state.pow_feedback = None
        st.session_state["pow_answer_input"] = 0

    if st.session_state.pow_base is not None:
        st.markdown(
            f'<div class="question-box">{st.session_state.pow_base}'
            f'<sup>{st.session_state.pow_exp}</sup> = ?</div>',
            unsafe_allow_html=True,
        )

        user_answer = st.number_input("Your answer:", step=1, value=0, key="pow_answer_input")

        if st.button("✅ Check Answer", key="pow_check_btn"):
            is_correct = int(user_answer) == st.session_state.pow_answer
            message = record_attempt(is_correct)
            if not is_correct:
                message += f" The correct answer was **{st.session_state.pow_answer}**."
            st.session_state.pow_feedback = (is_correct, message)

        show_feedback(st.session_state.pow_feedback)

        with st.expander("💡 Show Step-by-Step Solution"):
            st.markdown(st.session_state.pow_steps)
    else:
        st.info("👆 Click **Generate Question** to get started!")
