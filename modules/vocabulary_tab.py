"""
English Vocabulary tab.

  * Study (flashcards) and Quiz modes can pull brand-new words from the
    internet (by topic and Year level) - or use the built-in word bank below,
    which is also the fallback whenever the internet isn't available.
  * Search a Word mode looks up any word online and shows its meanings,
    example sentences, synonyms and sentence starters.
"""

import random
import re

import streamlit as st

from modules.helpers import record_attempt, show_feedback
from modules.web_words import (
    LEVEL_SETTINGS,
    SURPRISE_ME,
    TOPICS,
    WebLookupError,
    clean_word,
    get_new_card,
    is_blocked,
    lookup_word,
    mask_word,
    sentence_frames,
    suggest_words,
)

MODE_STUDY = "📖 Study (Flashcards)"
MODE_QUIZ = "❓ Quiz Me"
MODE_SEARCH = "🔍 Search a Word"
SEEN_LIMIT = 60  # how many online words to remember per session

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



# =============================================================================
# SMALL HELPERS
# =============================================================================

def _builtin_card(entry=None):
    """Flashcard dict from the built-in word bank (random one if none given)."""
    entry = entry or random.choice(VOCABULARY_WORDS)
    return {
        "word": entry["word"], "meaning": entry["meaning"], "example": entry["example"],
        "pos": "", "phonetic": "", "audio": "", "source": "built-in",
    }


def _remember(card):
    seen = st.session_state.vocab_seen_cards
    seen.append(card)
    del seen[:-SEEN_LIMIT]


def _fetch_web_card():
    """Get a fresh online word, or None if the internet isn't available."""
    st.session_state.vocab_web_error = None
    seen_words = [c["word"] for c in st.session_state.vocab_seen_cards]
    try:
        with st.spinner("🌐 Searching the internet for a new word..."):
            card = get_new_card(
                st.session_state.vocab_topic, st.session_state.vocab_level, exclude=seen_words
            )
    except WebLookupError:
        st.session_state.vocab_web_error = "offline"
        return None
    if card is None:
        st.session_state.vocab_web_error = "nocard"
        return None
    _remember(card)
    return card


def _sentence_uses_word(sentence, word):
    stem = word[:-1] if len(word) > 4 and word.endswith(("e", "y")) else word
    return re.search(rf"\b{re.escape(stem)}\w*", sentence, re.IGNORECASE) is not None


def render():
    st.markdown("## 📚 English Vocabulary")
    st.caption("Build your word power — new words from the internet, plus a word detective to look up any word!")

    mode = st.radio(
        "Choose a mode:", [MODE_STUDY, MODE_QUIZ, MODE_SEARCH], horizontal=True, key="vocab_mode"
    )

    if mode == MODE_SEARCH:
        _render_search()
        return

    use_web = _render_source_controls()
    if mode == MODE_STUDY:
        _render_study(use_web)
    else:
        _render_quiz(use_web)


def _render_source_controls():
    use_web = st.checkbox(
        "🌐 Get brand-new words from the internet",
        key="vocab_use_web",
        help="Turn this off to practise with the built-in word list (works without internet).",
    )
    if use_web:
        col1, col2 = st.columns(2)
        with col1:
            st.selectbox("Word level:", list(LEVEL_SETTINGS.keys()), key="vocab_level")
        with col2:
            st.selectbox("Topic:", [SURPRISE_ME] + TOPICS, key="vocab_topic")
    else:
        st.caption("Using the built-in word list (works offline).")
    return use_web


# =============================================================================
# STUDY MODE
# =============================================================================

def _render_study(use_web):
    if use_web:
        _study_web()
    else:
        _study_builtin()


def _study_web():
    if st.button("🌐 Get a New Word", key="vocab_web_new_btn"):
        card = _fetch_web_card()
        if card is None:
            if st.session_state.vocab_web_error == "offline":
                st.warning("I couldn't reach the internet just now, so here's a word from the built-in list instead.")
            else:
                st.warning("I couldn't find a good new word this time, so here's one from the built-in list.")
            card = _builtin_card()
        st.session_state.vocab_online_card = card
        st.session_state.vocab_reveal = False

    card = st.session_state.vocab_online_card
    if card is None:
        st.info("👆 Click **Get a New Word** to discover a new word!")
    else:
        _show_card(card)

    seen = st.session_state.vocab_seen_cards
    if seen:
        with st.expander(f"🗂️ New words I've met this session ({len(seen)})"):
            st.markdown(", ".join(f"**{c['word']}**" for c in reversed(seen)))


def _study_builtin():
    total = len(VOCABULARY_WORDS)
    idx = st.session_state.vocab_index % total
    st.markdown(f"**Word {idx + 1} of {total}**")
    _show_card(_builtin_card(VOCABULARY_WORDS[idx]))

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


def _show_card(card):
    st.markdown(
        f'<div class="question-box" style="font-size:1.8rem;">{card["word"]}</div>',
        unsafe_allow_html=True,
    )
    details = [d for d in (f"*{card['pos']}*" if card.get("pos") else "", card.get("phonetic", "")) if d]
    if details:
        st.caption(" · ".join(details))
    if card.get("audio"):
        st.audio(card["audio"])

    with st.expander("💡 Show Meaning & Example", expanded=st.session_state.vocab_reveal):
        st.markdown(f"**Meaning:** {card['meaning']}")
        if card.get("example"):
            st.markdown(f"**Example sentence:** *{card['example']}*")
        else:
            st.markdown("**Try it yourself! Sentence starters:**")
            for frame in sentence_frames(card["word"], card.get("pos", "")):
                st.markdown(f"- {frame}")

    st.button(
        "🔍 See more examples of this word",
        key=f"vocab_more_{card['word']}",
        on_click=_open_in_search,
        args=(card["word"],),
    )


# =============================================================================
# QUIZ MODE
# =============================================================================

def _render_quiz(use_web):
    if st.button("🎲 Generate Question", key="vocab_quiz_generate_btn"):
        _new_quiz_question(use_web)

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
            example = st.session_state.vocab_quiz_example
            if example:
                st.markdown(f"*{example}*")
            else:
                st.markdown("No example sentence for this one — try using the word in your own sentence!")
    else:
        st.info("👆 Click **Generate Question** to get started!")


def _new_quiz_question(use_web):
    correct = None
    if use_web:
        correct = _fetch_web_card()
        if correct is None:
            st.warning("I couldn't get a new word from the internet, so this question uses the built-in list.")
    if correct is None:
        correct = _builtin_card()

    # Wrong answers come from the built-in bank plus words met online this session.
    pool = {w["word"]: _builtin_card(w) for w in VOCABULARY_WORDS}
    for seen_card in st.session_state.vocab_seen_cards:
        pool[seen_card["word"]] = seen_card
    pool.pop(correct["word"], None)
    distractors = random.sample(list(pool.values()), 3)

    options = [mask_word(correct["meaning"], correct["word"])] + [
        mask_word(d["meaning"], d["word"]) for d in distractors
    ]
    # Guard against two identical meanings appearing as options.
    options = list(dict.fromkeys(options))
    while len(options) < 4:
        extra = random.choice(list(pool.values()))
        extra_meaning = mask_word(extra["meaning"], extra["word"])
        if extra_meaning not in options:
            options.append(extra_meaning)
    random.shuffle(options)

    st.session_state.vocab_quiz_word = correct["word"]
    st.session_state.vocab_quiz_example = correct.get("example", "")
    st.session_state.vocab_quiz_correct_meaning = mask_word(correct["meaning"], correct["word"])
    st.session_state.vocab_quiz_options = options
    st.session_state.vocab_quiz_feedback = None
    st.session_state["vocab_quiz_choice"] = None


# =============================================================================
# SEARCH A WORD
# =============================================================================

def _offline_result(word):
    """If the internet is down, still answer for words in the built-in bank."""
    for entry in VOCABULARY_WORDS:
        if entry["word"] == word:
            return {
                "word": word, "phonetic": "", "audio": "", "offline": True,
                "meanings": [{
                    "part_of_speech": "",
                    "definitions": [{"definition": entry["meaning"], "example": entry["example"]}],
                    "synonyms": [], "antonyms": [],
                }],
            }
    return None


def _do_search(raw):
    st.session_state.vocab_search_result = None
    st.session_state.vocab_search_error = None
    st.session_state.vocab_search_suggestions = []
    st.session_state.vocab_own_feedback = None
    st.session_state["vocab_own_sentence"] = ""

    word = clean_word(raw)
    if word is None:
        st.session_state.vocab_search_error = "Please type one word, using letters only (no spaces)."
        return
    if is_blocked(word):
        st.session_state.vocab_search_error = "Let's look up a different word instead! 🙂"
        return

    try:
        result = lookup_word(word)
    except WebLookupError:
        result = _offline_result(word)
        if result is None:
            st.session_state.vocab_search_error = (
                "I couldn't reach the online dictionary. Check the internet connection and try again."
            )
            return

    if result is None:
        st.session_state.vocab_search_error = f"I couldn't find \"{word}\". Check the spelling and try again!"
        try:
            st.session_state.vocab_search_suggestions = suggest_words(word)
        except WebLookupError:
            pass
        return

    st.session_state.vocab_search_result = result


def _search_for(word):
    st.session_state["vocab_search_input"] = word
    _do_search(word)


def _open_in_search(word):
    st.session_state["vocab_mode"] = MODE_SEARCH
    _search_for(word)


def _render_search():
    st.markdown("### 🔍 Word Detective")
    st.caption("Type any word to find out what it means and how to use it in a sentence.")

    with st.form("vocab_search_form"):
        st.text_input("Word to look up:", key="vocab_search_input", placeholder="e.g. enormous")
        submitted = st.form_submit_button("🔍 Search")
    if submitted:
        _do_search(st.session_state.vocab_search_input)

    error = st.session_state.vocab_search_error
    result = st.session_state.vocab_search_result

    if error:
        st.warning(error)
        suggestions = st.session_state.vocab_search_suggestions
        if suggestions:
            st.markdown("**Did you mean...?**")
            cols = st.columns(len(suggestions))
            for col, suggestion in zip(cols, suggestions):
                with col:
                    st.button(
                        suggestion, key=f"vocab_suggest_{suggestion}",
                        on_click=_search_for, args=(suggestion,),
                    )
    elif result is None:
        st.info("Type a word above and press **Search**.")

    if result:
        _show_search_result(result)


def _show_search_result(result):
    word = result["word"]
    st.markdown(f"## {word}")
    details = [result["phonetic"]] if result.get("phonetic") else []
    if result.get("offline"):
        details.append("(from the built-in list — you're offline)")
    if details:
        st.caption(" · ".join(details))
    if result.get("audio"):
        st.audio(result["audio"])

    example_count = 0
    for meaning in result["meanings"][:4]:
        if meaning["part_of_speech"]:
            st.markdown(f"**{meaning['part_of_speech']}**")
        for number, d in enumerate(meaning["definitions"][:3], start=1):
            st.markdown(f"{number}. {d['definition']}")
            if d["example"]:
                example_count += 1
                st.markdown(f"> ✏️ *{d['example']}*")

    synonyms = list(dict.fromkeys(s for m in result["meanings"] for s in m["synonyms"]))[:8]
    antonyms = list(dict.fromkeys(a for m in result["meanings"] for a in m["antonyms"]))[:8]
    if synonyms:
        st.markdown("🔁 **Similar words:** " + ", ".join(synonyms))
    if antonyms:
        st.markdown("↔️ **Opposite words:** " + ", ".join(antonyms))

    if example_count == 0:
        st.info("No example sentences were found for this word — use the sentence starters below to make your own!")

    with st.expander("🧩 Sentence starters — use the word yourself", expanded=example_count < 2):
        first_pos = result["meanings"][0]["part_of_speech"]
        for frame in sentence_frames(word, first_pos):
            st.markdown(f"- {frame}")

    st.markdown("### ✍️ Your turn!")
    own = st.text_input(f"Write your own sentence using “{word}”:", key="vocab_own_sentence")
    if st.button("Check my sentence", key="vocab_own_check_btn"):
        if len(own.split()) < 4:
            st.session_state.vocab_own_feedback = ("warn", "Try a longer sentence — at least 4 words!")
        elif not _sentence_uses_word(own, word):
            st.session_state.vocab_own_feedback = ("info", f"Good try! Can you include the word “{word}” in your sentence?")
        else:
            st.session_state.vocab_own_feedback = ("ok", "🌟 Great sentence! You used the word really well.")

    feedback = st.session_state.vocab_own_feedback
    if feedback:
        kind, message = feedback
        {"ok": st.success, "warn": st.warning, "info": st.info}[kind](message)
