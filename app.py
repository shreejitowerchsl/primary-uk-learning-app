"""
Year 4/5 Learning Adventure
-----------------------------
An interactive Streamlit learning app for a UK Year 4/5 pupil, covering:
  - Multiplication, Division, Powers (maths)
  - Word Problems (Multiplication & Division, leveled Beginner/Intermediate/Advanced)
  - Learn the Abacus (Beginner/Intermediate/Advanced)
  - English Vocabulary (Study + Quiz)
  - Spelling Practice (Year 4 & Year 5 UK word lists)

Run locally with:  streamlit run app.py
See README.md for how to deploy this to Streamlit Community Cloud.
"""

import streamlit as st

from modules.state import init_session_state
from modules import (
    multiplication_tab,
    division_tab,
    powers_tab,
    abacus_tab,
    word_problems_tab,
    vocabulary_tab,
    spelling_tab,
)

# =============================================================================
# PAGE CONFIG & STYLING
# =============================================================================

st.set_page_config(
    page_title="Year 4/5 Learning Adventure",
    page_icon="🧮",
    layout="centered",
)

st.markdown(
    """
    <style>
    .stApp {
        background: linear-gradient(180deg, #eef7ff 0%, #fdfdfd 60%);
    }
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
    '<div class="sub-title">Maths, the abacus, vocabulary and spelling — all in one place! 🚀</div>',
    unsafe_allow_html=True,
)

with st.sidebar:
    st.markdown("### 🌟 Your Score")
    attempted = st.session_state.score_attempted
    correct = st.session_state.score_correct
    st.markdown(f'<span class="streak-badge">{correct} / {attempted} correct</span>', unsafe_allow_html=True)
    if attempted > 0:
        st.progress(correct / attempted)
    st.markdown("---")
    st.markdown(
        "**How to use this app:**\n"
        "1. Pick a topic tab.\n"
        "2. Click **Generate Question**.\n"
        "3. Type your answer and click **Check Answer**.\n"
        "4. Stuck? Open **Show Step-by-Step Solution**!"
    )

# =============================================================================
# TABS
# =============================================================================

(
    tab_mult,
    tab_div,
    tab_pow,
    tab_word_problems,
    tab_abacus,
    tab_vocab,
    tab_spelling,
) = st.tabs(
    [
        "✖️ Multiplication",
        "➗ Division",
        "⬆️ Powers",
        "📖 Word Problems",
        "🧮 Learn the Abacus",
        "📚 Vocabulary",
        "✏️ Spelling",
    ]
)

with tab_mult:
    multiplication_tab.render()

with tab_div:
    division_tab.render()

with tab_pow:
    powers_tab.render()

with tab_word_problems:
    word_problems_tab.render()

with tab_abacus:
    abacus_tab.render()

with tab_vocab:
    vocabulary_tab.render()

with tab_spelling:
    spelling_tab.render()

# =============================================================================
# FOOTER
# =============================================================================

st.markdown("---")
st.caption("Made with ❤️ for Year 4/5 learners. Keep practising — you're getting better every day!")
