"""
English Vocabulary tab: a Year 4/5-appropriate "tier 2" word bank with
kid-friendly meanings and example sentences, in a flashcard Study mode and
a multiple-choice Quiz mode.
"""

import random

import streamlit as st

from modules.helpers import record_attempt, show_feedback

VOCABULARY_WORDS = [
    {"word": "enormous", "meaning": "extremely large in size", "example": "The blue whale is an enormous animal."},
    {"word": "furious", "meaning": "extremely angry", "example": "Dad was furious when the dog ate his dinner."},
    {"word": "cautious", "meaning": "being very careful to avoid danger or mistakes",
     "example": "She was cautious crossing the busy road."},
    {"word": "generous", "meaning": "willing to give more of something than is strictly necessary",
     "example": "It was generous of him to share his lunch."},
    {"word": "peculiar", "meaning": "strange or unusual", "example": "There was a peculiar smell coming from the shed."},
    {"word": "reluctant", "meaning": "unwilling and hesitant to do something",
     "example": "The cat was reluctant to come out of its box."},
    {"word": "exhausted", "meaning": "extremely tired", "example": "After the long walk, we were completely exhausted."},
    {"word": "curious", "meaning": "eager to know or learn something",
     "example": "The curious kitten explored every corner of the room."},
    {"word": "mysterious", "meaning": "difficult to understand or explain; full of mystery",
     "example": "A mysterious light appeared in the sky."},
    {"word": "ancient", "meaning": "very old; from a long time ago", "example": "The museum has an ancient Roman coin."},
    {"word": "brilliant", "meaning": "extremely clever, or shining very brightly",
     "example": "She had a brilliant idea for the school play."},
    {"word": "terrified", "meaning": "extremely frightened", "example": "He was terrified of the dark basement."},
    {"word": "magnificent", "meaning": "extremely beautiful or impressive",
     "example": "The castle had a magnificent view over the valley."},
    {"word": "miserable", "meaning": "very unhappy or uncomfortable",
     "example": "The rain made everyone feel miserable at the picnic."},
    {"word": "delighted", "meaning": "feeling great pleasure or happiness",
     "example": "She was delighted with her birthday present."},
    {"word": "gigantic", "meaning": "extremely large; huge", "example": "A gigantic spider crawled across the ceiling."},
    {"word": "vast", "meaning": "extremely large in area or amount",
     "example": "The desert stretched out as a vast, empty land."},
    {"word": "gloomy", "meaning": "dark or dull, or feeling sad", "example": "The sky looked grey and gloomy before the storm."},
    {"word": "hesitant", "meaning": "slow to act because of feeling unsure",
     "example": "He was hesitant to raise his hand in class."},
    {"word": "fatigued", "meaning": "very tired, especially from hard work",
     "example": "The runners looked fatigued after the marathon."},
    {"word": "ferocious", "meaning": "very fierce or violent", "example": "The ferocious storm knocked down several trees."},
    {"word": "astonished", "meaning": "greatly surprised or amazed",
     "example": "We were astonished by the magician's final trick."},
    {"word": "determined", "meaning": "having made a firm decision and being unwilling to give up",
     "example": "She was determined to finish the race, even with a sore leg."},
    {"word": "ridiculous", "meaning": "deserving or inviting mockery; absurd",
     "example": "It was ridiculous to think the dog could talk."},
    {"word": "fortunate", "meaning": "lucky; having good things happen",
     "example": "We were fortunate the rain stopped just before the match."},
    {"word": "marvellous", "meaning": "wonderful; extremely good",
     "example": "We had a marvellous time at the theme park."},
    {"word": "disastrous", "meaning": "extremely unsuccessful or causing great damage",
     "example": "The picnic was disastrous after the storm arrived."},
    {"word": "cramped", "meaning": "too small in space; uncomfortably crowded",
     "example": "The tent felt cramped once all four of us climbed in."},
    {"word": "grateful", "meaning": "feeling or showing thanks",
     "example": "I am very grateful for your help with my homework."},
    {"word": "reckless", "meaning": "acting without thinking about danger or consequences",
     "example": "It was reckless to ride a bike without a helmet."},
]


def render():
    st.markdown("## 📚 English Vocabulary")
    st.caption("Build up your word power — great words to use in your own writing!")

    mode = st.radio("Choose a mode:", ["📖 Study (Flashcards)", "❓ Quiz Me"], horizontal=True, key="vocab_mode")

    if mode == "📖 Study (Flashcards)":
        _render_study()
    else:
        _render_quiz()


def _render_study():
    words = VOCABULARY_WORDS
    total = len(words)
    idx = st.session_state.vocab_index % total
    card = words[idx]

    st.markdown(f"**Word {idx + 1} of {total}**")
    st.markdown(
        f'<div class="question-box" style="font-size:1.8rem;">{card["word"]}</div>',
        unsafe_allow_html=True,
    )

    with st.expander("💡 Show Meaning & Example", expanded=st.session_state.vocab_reveal):
        st.markdown(f"**Meaning:** {card['meaning']}")
        st.markdown(f"**Example sentence:** *{card['example']}*")

    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("⬅️ Previous", key="vocab_prev_btn"):
            st.session_state.vocab_index = (idx - 1) % total
            st.session_state.vocab_reveal = False
            st.rerun()
    with col2:
        if st.button("🔀 Random Word", key="vocab_random_btn"):
            st.session_state.vocab_index = random.randint(0, total - 1)
            st.session_state.vocab_reveal = False
            st.rerun()
    with col3:
        if st.button("Next ➡️", key="vocab_next_btn"):
            st.session_state.vocab_index = (idx + 1) % total
            st.session_state.vocab_reveal = False
            st.rerun()


def _render_quiz():
    if st.button("🎲 Generate Question", key="vocab_quiz_generate_btn"):
        correct_card = random.choice(VOCABULARY_WORDS)
        distractors = random.sample(
            [w for w in VOCABULARY_WORDS if w["word"] != correct_card["word"]], 3
        )
        options = [correct_card["meaning"]] + [d["meaning"] for d in distractors]
        random.shuffle(options)

        st.session_state.vocab_quiz_word = correct_card["word"]
        st.session_state.vocab_quiz_example = correct_card["example"]
        st.session_state.vocab_quiz_correct_meaning = correct_card["meaning"]
        st.session_state.vocab_quiz_options = options
        st.session_state.vocab_quiz_feedback = None
        st.session_state["vocab_quiz_choice"] = None

    if st.session_state.vocab_quiz_word is not None:
        st.markdown(
            f'<div class="question-box">What does <em>"{st.session_state.vocab_quiz_word}"</em> mean?</div>',
            unsafe_allow_html=True,
        )
        choice = st.radio(
            "Choose the best meaning:",
            st.session_state.vocab_quiz_options,
            key="vocab_quiz_choice",
            index=None,
        )

        if st.button("✅ Check Answer", key="vocab_quiz_check_btn"):
            if choice is None:
                st.warning("Pick an answer first!")
            else:
                is_correct = choice == st.session_state.vocab_quiz_correct_meaning
                message = record_attempt(is_correct)
                if not is_correct:
                    message += f" The correct meaning was: **{st.session_state.vocab_quiz_correct_meaning}**."
                st.session_state.vocab_quiz_feedback = (is_correct, message)

        show_feedback(st.session_state.vocab_quiz_feedback)

        with st.expander("💡 Show Example Sentence"):
            st.markdown(f"*{st.session_state.vocab_quiz_example}*")
    else:
        st.info("👆 Click **Generate Question** to get started!")
