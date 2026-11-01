"""
Shared interface for the Verbal and Non-Verbal Reasoning tabs.

A topic generator takes a level (1, 2 or 3) and returns a question dict:

    type           "choice" | "text" | "number"
    prompt         the question (simple **bold** markdown allowed)
    visual         optional HTML/SVG shown under the prompt
    markdown       optional markdown shown under the prompt (e.g. a table)
    choices        list of answer choices (for "choice")
    option_svgs    optional pictures for the choices (shown in a row, labelled A, B, C...)
    answer         the correct answer
    accept         optional extra accepted answers (for "text")
    explain        the worked explanation (markdown)
    solution_visual optional picture shown with the explanation
    hint           optional hint
"""

import random
import re

import streamlit as st

from modules.helpers import record_attempt, show_feedback

LEVELS = ["🟢 Beginner", "🟡 Intermediate", "🔴 Advanced"]
MIXED = "🎲 Mixed (all topics)"


def normalize(text):
    """Lower-case and tidy punctuation/spacing so '3, 1, 20' and '3 1 20' match."""
    text = str(text).lower().strip()
    text = re.sub(r"[,;:\-_/]", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def _html(text):
    text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)
    return text.replace("\n", "<br>")


def generate(topics, topic, level_label):
    """Make a question, retrying if a generator can't build one. Returns None only if all retries fail."""
    level = LEVELS.index(level_label) + 1
    for _ in range(8):
        name = random.choice(list(topics)) if topic == MIXED else topic
        try:
            q = topics[name](level)
        except Exception:  # a generator hit an unlucky random draw: just try again
            continue
        q["topic_name"] = name
        return q
    return None


def is_correct(q, guess):
    if q["type"] == "number":
        return int(guess) == q["answer"]
    if q["type"] == "text":
        accepted = {normalize(q["answer"])} | {normalize(a) for a in q.get("accept", [])}
        return normalize(guess) in accepted
    return guess == q["answer"]


def render_reasoning(prefix, heading, caption, topics, lessons=()):
    state = st.session_state
    st.markdown(heading)
    st.caption(caption)

    for title, body in lessons:
        with st.expander(title):
            st.markdown(body)

    col1, col2 = st.columns([3, 2])
    with col1:
        topic = st.selectbox("Topic:", [MIXED] + list(topics), key=f"{prefix}_topic")
    with col2:
        level = st.selectbox("Level:", LEVELS, key=f"{prefix}_level")

    combo = (topic, level)
    if state[f"{prefix}_last_combo"] != combo:
        state[f"{prefix}_q"] = None
        state[f"{prefix}_feedback"] = None
        state[f"{prefix}_last_combo"] = combo

    if st.button("🎲 New Question", key=f"{prefix}_generate_btn"):
        q = generate(topics, topic, level)
        if q is None:
            st.error("Sorry, I couldn't make a question just now. Please try again!")
        else:
            state[f"{prefix}_qid"] += 1
            state[f"{prefix}_q"] = q
            state[f"{prefix}_feedback"] = None

    q = state[f"{prefix}_q"]
    if q is None:
        st.info("👆 Click **New Question** to get started!")
        return

    qid = state[f"{prefix}_qid"]
    if topic == MIXED:
        st.caption(f"Topic: {q['topic_name']}")

    st.markdown(f'<div class="word-box">{_html(q["prompt"])}</div>', unsafe_allow_html=True)
    if q.get("visual"):
        st.markdown(q["visual"], unsafe_allow_html=True)
    if q.get("markdown"):
        st.markdown(q["markdown"])
    if q.get("hint"):
        with st.expander("💭 Need a hint?"):
            st.markdown(q["hint"])

    key = f"{prefix}_answer_{qid}"
    if q["type"] == "choice":
        if q.get("option_svgs"):
            cols = st.columns(len(q["option_svgs"]))
            for col, svg in zip(cols, q["option_svgs"]):
                with col:
                    st.markdown(svg, unsafe_allow_html=True)
        guess = st.radio("Your answer:", q["choices"], index=None, key=key,
                         horizontal=bool(q.get("option_svgs")) or len(q["choices"]) <= 5)
    elif q["type"] == "number":
        guess = st.number_input("Your answer:", step=1, value=0, key=key)
    else:
        guess = st.text_input("Type your answer:", key=key, placeholder=q.get("placeholder", ""))

    if st.button("✅ Check Answer", key=f"{prefix}_check_btn"):
        if q["type"] == "choice" and guess is None:
            st.warning("Pick an answer first!")
        elif q["type"] == "text" and not str(guess).strip():
            st.warning("Type your answer first!")
        else:
            right = is_correct(q, guess)
            message = record_attempt(right, subject="reasoning")
            if not right:
                message += f" The correct answer was **{q['answer']}**."
            state[f"{prefix}_feedback"] = (right, message)

    show_feedback(state[f"{prefix}_feedback"])

    with st.expander("💡 Show Step-by-Step Explanation"):
        st.markdown(q["explain"])
        if q.get("solution_visual"):
            st.markdown(q["solution_visual"], unsafe_allow_html=True)
