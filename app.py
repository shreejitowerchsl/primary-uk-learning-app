"""
Year 4/5 Learning Adventure
-----------------------------
An interactive Streamlit learning app for a UK Year 4/5 pupil, in two sections:

  🔢 MATHS    Addition & Subtraction (positive + negative numbers), Multiplication,
              Division, Powers, Word Problems, Coordinates, Abacus
  📚 ENGLISH  Vocabulary (study, quiz, word search), Spelling (Year 4 & 5)
  🧠 REASONING Verbal Reasoning (19 topics), Non-Verbal Reasoning (9 topics)

Run locally with:  streamlit run app.py
See README.md for how to deploy this to Streamlit Community Cloud.
"""

import streamlit as st

from modules.state import init_session_state
from modules.maths import (
    abacus_tab,
    addsub_tab,
    coordinates_tab,
    division_tab,
    multiplication_tab,
    powers_tab,
    word_problems_tab,
)
from modules.english import spelling_tab, vocabulary_tab
from modules.reasoning import nonverbal_tab, verbal_tab

# =============================================================================
# PAGE CONFIG & STYLING
# =============================================================================

st.set_page_config(
    page_title="Year 4/5 Learning Adventure",
    page_icon="🧮",
    layout="wide",
)

st.markdown(
    """
    <style>
    .stApp {
        background: linear-gradient(180deg, #eef7ff 0%, #fdfdfd 60%);
    }
    .block-container { max-width: 1050px; }
    .big-title {
        font-size: 2.2rem;
        font-weight: 800;
        text-align: center;
        color: #1d3557;
        margin-bottom: 0.1rem;
    }
    .sub-title {
        text-align: center;
        color: #457b9d;
        font-size: 1.1rem;
        margin-bottom: 1.2rem;
    }
    .question-box {
        background-color: #ffffff;
        border: 3px solid #a8dadc;
        border-radius: 18px;
        padding: 1.2rem;
        text-align: center;
        font-size: 1.8rem;
        font-weight: 800;
        color: #1d3557;
        margin: 1rem 0;
        box-shadow: 0 4px 10px rgba(0,0,0,0.06);
    }
    .word-box {
        background-color: #fff8e8;
        border: 3px solid #ffd166;
        border-radius: 18px;
        padding: 1.2rem 1.4rem;
        font-size: 1.15rem;
        color: #6d4c00;
        margin: 1rem 0;
        line-height: 1.5;
    }
    div.stButton > button {
        border-radius: 14px;
        font-weight: 700;
        padding: 0.5rem 1.2rem;
        border: none;
    }
    div.stButton > button:first-child {
        background-color: #ffb703;
        color: #1d3557;
    }
    .streak-badge {
        display:inline-block;
        background-color:#06d6a0;
        color:white;
        padding: 0.25rem 0.9rem;
        border-radius: 999px;
        font-weight:700;
        font-size:0.95rem;
    }
    section[data-testid="stSidebar"] {
        background-color: #f1faee;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# =============================================================================
# SESSION STATE
# =============================================================================

init_session_state()

# =============================================================================
# HEADER & SIDEBAR
# =============================================================================

st.markdown('<div class="big-title">🎓 Year 4/5 Learning Adventure</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="sub-title">Maths, English and Reasoning practice — all in one place! 🚀</div>',
    unsafe_allow_html=True,
)

def _score_badge(correct, attempted):
    st.markdown(f'<span class="streak-badge">{correct} / {attempted} correct</span>', unsafe_allow_html=True)
    if attempted > 0:
        st.progress(correct / attempted)


with st.sidebar:
    st.markdown("### 🌟 Your Score")
    st.markdown("**🔢 Maths**")
    _score_badge(st.session_state.score_maths_correct, st.session_state.score_maths_attempted)
    st.markdown("**📚 English**")
    _score_badge(st.session_state.score_english_correct, st.session_state.score_english_attempted)
    st.markdown("**🧠 Reasoning**")
    _score_badge(st.session_state.score_reasoning_correct, st.session_state.score_reasoning_attempted)
    st.markdown("---")
    st.markdown(
        "**How to use this app:**\n"
        "1. Pick **Maths**, **English** or **Reasoning** at the top.\n"
        "2. Choose a topic tab.\n"
        "3. Click **Generate Question**, type your answer, then **Check Answer**.\n"
        "4. Stuck? Open **Show Step-by-Step Solution**!"
    )

# =============================================================================
# THREE MAIN SECTIONS: MATHS, ENGLISH and REASONING
# =============================================================================

section_maths, section_english, section_reasoning = st.tabs(["🔢  MATHS", "📚  ENGLISH", "🧠  REASONING"])

with section_maths:
    (
        tab_addsub,
        tab_mult,
        tab_div,
        tab_pow,
        tab_word_problems,
        tab_coords,
        tab_abacus,
    ) = st.tabs(
        [
            "➕➖ Addition & Subtraction",
            "✖️ Multiplication",
            "➗ Division",
            "⬆️ Powers",
            "📖 Word Problems",
            "📍 Coordinates",
            "🧮 Abacus",
        ]
    )
    with tab_addsub:
        addsub_tab.render()
    with tab_mult:
        multiplication_tab.render()
    with tab_div:
        division_tab.render()
    with tab_pow:
        powers_tab.render()
    with tab_word_problems:
        word_problems_tab.render()
    with tab_coords:
        coordinates_tab.render()
    with tab_abacus:
        abacus_tab.render()

with section_english:
    tab_vocab, tab_spelling = st.tabs(["📚 Vocabulary", "✏️ Spelling"])
    with tab_vocab:
        vocabulary_tab.render()
    with tab_spelling:
        spelling_tab.render()

with section_reasoning:
    tab_verbal, tab_nonverbal = st.tabs(["💬 Verbal Reasoning", "🔷 Non-Verbal Reasoning"])
    with tab_verbal:
        verbal_tab.render()
    with tab_nonverbal:
        nonverbal_tab.render()

# =============================================================================
# FOOTER
# =============================================================================

st.markdown("---")
st.caption("Made with ❤️ for Year 4/5 learners. Keep practising — you're getting better every day!")
