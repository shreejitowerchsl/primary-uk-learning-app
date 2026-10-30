"""Multiplication practice tab: 5 categories from 2x1 up to Year 4 word problems."""

import random

import streamlit as st

from modules.helpers import multiplication_steps, record_attempt, show_feedback

WORD_PROBLEM_TEMPLATES = [
    {
        "text": "A school buys {b} boxes of pencils. Each box contains {a} pencils. "
                "How many pencils are there in total?",
        "a_range": (12, 30), "b_range": (4, 18), "unit": "pencils",
    },
    {
        "text": "A toy shop orders {b} boxes of action figures. Each box holds {a} figures. "
                "How many action figures does the shop order in total?",
        "a_range": (45, 150), "b_range": (3, 9), "unit": "action figures",
    },
    {
        "text": "Tickets to the school summer fair cost {a}p each. "
                "If {b} tickets are sold, how much money is collected, in pence?",
        "a_range": (15, 85), "b_range": (12, 40), "unit": "pence",
    },
    {
        "text": "A football league has {b} teams. Each team has {a} players. "
                "How many players are there altogether?",
        "a_range": (11, 18), "b_range": (6, 20), "unit": "players",
    },
    {
        "text": "A bakery bakes {b} trays of buns for the school bake sale. "
                "Each tray holds {a} buns. How many buns does the bakery bake in total?",
        "a_range": (12, 36), "b_range": (5, 15), "unit": "buns",
    },
    {
        "text": "There are {b} crates of apples delivered to the greengrocer's. "
                "Each crate contains {a} apples. How many apples are delivered in total?",
        "a_range": (20, 60), "b_range": (8, 25), "unit": "apples",
    },
    {
        "text": "A cinema has {b} rows of seats. Each row has {a} seats. "
                "How many seats are there in the cinema?",
        "a_range": (14, 32), "b_range": (10, 25), "unit": "seats",
    },
]


def generate_2x1():
    a, b = random.randint(11, 99), random.randint(2, 9)
    return f"{a} × {b}", a * b, multiplication_steps(a, b), ""


def generate_2x2():
    a, b = random.randint(11, 99), random.randint(11, 99)
    return f"{a} × {b}", a * b, multiplication_steps(a, b), ""


def generate_3x2():
    a, b = random.randint(100, 999), random.randint(11, 99)
    return f"{a} × {b}", a * b, multiplication_steps(a, b), ""


def generate_3x3():
    a, b = random.randint(100, 999), random.randint(100, 999)
    return f"{a} × {b}", a * b, multiplication_steps(a, b), ""


def generate_word_problem():
    template = random.choice(WORD_PROBLEM_TEMPLATES)
    a = random.randint(*template["a_range"])
    b = random.randint(*template["b_range"])
    question_text = template["text"].format(a=a, b=b)
    answer = a * b
    unit = template["unit"]

    steps = f"""
**Step 1 — Turn the words into an equation.**

The problem describes **{b} groups of {a}**, so the calculation we need is:

### {a} × {b} = ?

**Step 2 — Work it out.**

{multiplication_steps(a, b)}

**Step 3 — Answer the question in context.**

The answer is **{answer} {unit}**.
"""
    return question_text, answer, steps, unit


MULTIPLICATION_CATEGORIES = {
    "2-Digit x 1-Digit": generate_2x1,
    "2-Digit x 2-Digit": generate_2x2,
    "3-Digit x 2-Digit": generate_3x2,
    "3-Digit x 3-Digit": generate_3x3,
    "Year 4 Word Problems": generate_word_problem,
}


def render():
    st.markdown("## ✖️ Multiplication Practice")

    category = st.selectbox(
        "Choose a category:", list(MULTIPLICATION_CATEGORIES.keys()), key="mult_category"
    )

    if st.session_state.mult_last_category != category:
        st.session_state.mult_question_text = None
        st.session_state.mult_answer = None
        st.session_state.mult_steps = None
        st.session_state.mult_feedback = None
        st.session_state.mult_unit = ""
        st.session_state.mult_last_category = category

    if st.button("🎲 Generate Question", key="mult_generate_btn"):
        question_text, answer, steps, unit = MULTIPLICATION_CATEGORIES[category]()
        st.session_state.mult_question_text = question_text
        st.session_state.mult_answer = answer
        st.session_state.mult_steps = steps
        st.session_state.mult_unit = unit
        st.session_state.mult_feedback = None
        st.session_state["mult_answer_input"] = 0

    if st.session_state.mult_question_text is not None:
        if category == "Year 4 Word Problems":
            st.markdown(
                f'<div class="word-box">📖 <strong>Word Problem:</strong><br>'
                f'{st.session_state.mult_question_text}</div>',
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                f'<div class="question-box">{st.session_state.mult_question_text} = ?</div>',
                unsafe_allow_html=True,
            )

        user_answer = st.number_input("Your answer:", step=1, value=0, key="mult_answer_input")

        if st.button("✅ Check Answer", key="mult_check_btn"):
            is_correct = int(user_answer) == st.session_state.mult_answer
            message = record_attempt(is_correct)
            if not is_correct:
                message += f" The correct answer was **{st.session_state.mult_answer}**."
            st.session_state.mult_feedback = (is_correct, message)

        show_feedback(st.session_state.mult_feedback)

        with st.expander("💡 Show Step-by-Step Solution"):
            st.markdown(st.session_state.mult_steps)
    else:
        st.info("👆 Click **Generate Question** to get started!")
