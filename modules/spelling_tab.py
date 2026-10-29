"""
Spelling tab: Study and Spelling Test modes.

Words come from two places:
  * the internet - a brand-new word every question (with a definition, a
    sentence clue when one is available, and British pronunciation audio), or
  * the built-in Year 4 / Year 5 lists below (inspired by the UK National
    Curriculum spelling lists), which are also the offline fallback.

Note: the built-in lists are a curated practice subset, not a verbatim
reproduction of the official DfE document - for the complete official lists,
see the National Curriculum in England, English programme of study (Appendix 1).
"""

import random

import streamlit as st

from modules.helpers import record_attempt, show_feedback
from modules.web_words import (
    SURPRISE_ME,
    TOPICS,
    WebLookupError,
    blank_out,
    get_new_card,
    mask_word,
)

SEEN_LIMIT = 60

YEAR4_WORDS = [
    {"word": "accident", "definition": "something that happens unexpectedly and unintentionally",
     "sentence": "It was an {blank} when he spilled the juice."},
    {"word": "actually", "definition": "used to emphasise that something is true, especially if surprising",
     "sentence": "I didn't think I'd like it, but I {blank} loved the film."},
    {"word": "address", "definition": "the details of where a person lives or a place is",
     "sentence": "Please write your {blank} on the envelope."},
    {"word": "arrive", "definition": "to reach a place, especially at the end of a journey",
     "sentence": "We will {blank} at the station at noon."},
    {"word": "believe", "definition": "to accept that something is true",
     "sentence": "I {blank} you when you say you tried your best."},
    {"word": "breath", "definition": "the air taken into or let out of the lungs",
     "sentence": "She took a deep {blank} before diving in."},
    {"word": "build", "definition": "to make something by putting parts together",
     "sentence": "The children plan to {blank} a sandcastle."},
    {"word": "busy", "definition": "having a lot to do",
     "sentence": "The market was very {blank} on Saturday morning."},
    {"word": "calendar", "definition": "a chart showing the days, weeks and months of a year",
     "sentence": "We marked the trip on the {blank}."},
    {"word": "caught", "definition": "past tense of catch — took hold of something moving",
     "sentence": "She {blank} the ball with one hand."},
    {"word": "centre", "definition": "the middle point of something",
     "sentence": "The fountain stands in the {blank} of the square."},
    {"word": "certain", "definition": "completely sure about something",
     "sentence": "I am {blank} that I locked the door."},
    {"word": "circle", "definition": "a perfectly round shape",
     "sentence": "Draw a {blank} around the correct answer."},
    {"word": "complete", "definition": "having every part; finished",
     "sentence": "Please {blank} the form before you leave."},
    {"word": "different", "definition": "not the same as another thing",
     "sentence": "Each snowflake is {blank} from the others."},
    {"word": "difficult", "definition": "needing a lot of effort or skill; not easy",
     "sentence": "That maths question was quite {blank}."},
    {"word": "early", "definition": "before the usual or expected time",
     "sentence": "We arrived {blank} for the concert."},
    {"word": "earth", "definition": "the planet we live on, or the soil in the ground",
     "sentence": "Plants grow well in rich, dark {blank}."},
    {"word": "enough", "definition": "as much as is needed",
     "sentence": "Do we have {blank} chairs for everyone?"},
    {"word": "experience", "definition": "knowledge gained from doing something, or an event you have lived through",
     "sentence": "Visiting the castle was an amazing {blank}."},
    {"word": "favourite", "definition": "liked more than any other",
     "sentence": "Chocolate ice cream is my {blank} flavour."},
    {"word": "group", "definition": "a number of people or things together",
     "sentence": "Get into a {blank} of four for the activity."},
    {"word": "guard", "definition": "to protect or watch over something, or a person who does this",
     "sentence": "The soldier stood on {blank} outside the gate."},
    {"word": "heart", "definition": "the organ that pumps blood around the body",
     "sentence": "Exercise is good for your {blank}."},
    {"word": "history", "definition": "the study of past events",
     "sentence": "We are learning about Roman {blank} this term."},
    {"word": "imagine", "definition": "to form a picture or idea in your mind",
     "sentence": "Close your eyes and {blank} a sunny beach."},
    {"word": "increase", "definition": "to become or make something greater in size or amount",
     "sentence": "The shop will {blank} its prices next month."},
    {"word": "knowledge", "definition": "information and understanding gained through learning or experience",
     "sentence": "Her {blank} of dinosaurs is amazing."},
    {"word": "library", "definition": "a building or room containing books to read or borrow",
     "sentence": "We borrowed three books from the {blank}."},
    {"word": "natural", "definition": "existing in nature; not made or caused by people",
     "sentence": "Honey is a {blank} sweetener."},
]

YEAR5_WORDS = [
    {"word": "accommodate", "definition": "to provide space or lodging for someone",
     "sentence": "The hotel can {blank} up to 200 guests."},
    {"word": "according", "definition": "as stated by, or in a way that matches",
     "sentence": "{blank} to the weather forecast, it will rain tomorrow."},
    {"word": "achieve", "definition": "to successfully complete or reach a goal",
     "sentence": "She worked hard to {blank} her personal best."},
    {"word": "amateur", "definition": "a person who does an activity for enjoyment, not as their job",
     "sentence": "He plays for an {blank} football team on Sundays."},
    {"word": "apparent", "definition": "clearly seen or understood; obvious",
     "sentence": "It was {blank} that she had practised a lot."},
    {"word": "appreciate", "definition": "to recognise the value of something, or to be grateful for it",
     "sentence": "I really {blank} your help with my homework."},
    {"word": "available", "definition": "able to be used or obtained",
     "sentence": "Tickets are still {blank} for Saturday's show."},
    {"word": "average", "definition": "the usual or typical amount",
     "sentence": "Find the {blank} of these five numbers."},
    {"word": "awkward", "definition": "causing difficulty or embarrassment; not smooth or comfortable",
     "sentence": "There was an {blank} silence after the joke fell flat."},
    {"word": "bargain", "definition": "something bought for less than its usual value",
     "sentence": "The coat was a real {blank} in the sale."},
    {"word": "category", "definition": "a group of things sharing similar features",
     "sentence": "Sort the animals into the correct {blank}."},
    {"word": "cemetery", "definition": "a place where dead people are buried",
     "sentence": "The old {blank} is behind the church."},
    {"word": "committee", "definition": "a group of people chosen to organise or discuss something",
     "sentence": "The school {blank} planned the summer fair."},
    {"word": "communicate", "definition": "to share or exchange information or ideas",
     "sentence": "Astronauts {blank} with mission control using radios."},
    {"word": "community", "definition": "a group of people living in the same area or sharing something in common",
     "sentence": "The whole {blank} came together to clean the park."},
    {"word": "conscious", "definition": "awake and aware of what is happening",
     "sentence": "The patient was fully {blank} after the operation."},
    {"word": "curiosity", "definition": "a strong desire to know or learn something",
     "sentence": "Her {blank} led her to open every drawer in the room."},
    {"word": "definite", "definition": "certain; without any doubt",
     "sentence": "We need a {blank} answer by Friday."},
    {"word": "determine", "definition": "to find out or decide something firmly",
     "sentence": "Scientists will {blank} the cause of the problem."},
    {"word": "embarrass", "definition": "to make someone feel awkward or ashamed",
     "sentence": "It can {blank} people when their phone rings loudly."},
    {"word": "environment", "definition": "the natural world, or the surroundings in which something exists",
     "sentence": "We should protect the {blank} by recycling."},
    {"word": "equipment", "definition": "the tools or items needed for a particular purpose",
     "sentence": "The gym has lots of new {blank}."},
    {"word": "especially", "definition": "more than usual; in particular",
     "sentence": "I love fruit, {blank} strawberries."},
    {"word": "exaggerate", "definition": "to make something seem larger, better or worse than it really is",
     "sentence": "Don't {blank} how big the fish was!"},
    {"word": "familiar", "definition": "well known; easily recognised",
     "sentence": "That tune sounds very {blank} to me."},
    {"word": "foreign", "definition": "from or belonging to a country that is not your own",
     "sentence": "She can speak three {blank} languages."},
    {"word": "frequently", "definition": "happening often",
     "sentence": "He {blank} visits his grandmother at the weekend."},
    {"word": "government", "definition": "the group of people who officially govern a country",
     "sentence": "The {blank} announced a new road safety plan."},
    {"word": "guarantee", "definition": "a firm promise that something will happen or be done",
     "sentence": "The shop gave a two-year {blank} on the laptop."},
    {"word": "immediately", "definition": "at once; without any delay",
     "sentence": "Please come here {blank}."},
]

WORD_LISTS = {"Year 4": YEAR4_WORDS, "Year 5": YEAR5_WORDS}



def render():
    st.markdown("## ✏️ Spelling Practice")
    st.caption("New words from the internet, plus built-in Year 4 and Year 5 UK word lists.")

    col1, col2 = st.columns(2)
    with col1:
        year_group = st.selectbox("Word list / level:", list(WORD_LISTS.keys()), key="spell_year_group")
    with col2:
        mode = st.radio("Mode:", ["📖 Study", "✏️ Spelling Test"], horizontal=True, key="spell_mode")

    use_web = st.checkbox(
        "🌐 Get brand-new words from the internet",
        key="spell_use_web",
        help="Turn this off to practise with the built-in Year 4/5 lists (works without internet).",
    )
    if use_web:
        st.selectbox("Topic:", [SURPRISE_ME] + TOPICS, key="spell_topic")

    words = WORD_LISTS[year_group]
    if mode == "📖 Study":
        _render_study(words, year_group, use_web)
    else:
        _render_test(words, year_group, use_web)


def _fetch_web_card(year_group):
    """A fresh online word for this year group, or None if unavailable."""
    try:
        with st.spinner("🌐 Searching the internet for a new word..."):
            card = get_new_card(
                st.session_state.spell_topic, year_group, exclude=st.session_state.spell_seen_words
            )
    except WebLookupError:
        st.warning("I couldn't reach the internet just now, so I'm using the built-in list instead.")
        return None
    if card is None:
        st.warning("I couldn't find a good new word this time, so I'm using the built-in list instead.")
        return None
    seen = st.session_state.spell_seen_words
    seen.append(card["word"])
    del seen[:-SEEN_LIMIT]
    return card


# =============================================================================
# STUDY MODE
# =============================================================================

def _render_study(words, year_group, use_web):
    if use_web:
        _study_web(year_group)
    else:
        _study_builtin(words, year_group)


def _study_web(year_group):
    if st.button("🌐 Get a New Word", key="spell_web_new_btn"):
        card = _fetch_web_card(year_group)
        if card is None:
            entry = random.choice(WORD_LISTS[year_group])
            card = {
                "word": entry["word"], "meaning": entry["definition"],
                "example": entry["sentence"].format(blank=entry["word"]),
                "phonetic": "", "audio": "",
            }
        st.session_state.spell_online_card = card

    card = st.session_state.spell_online_card
    if card is None:
        st.info("👆 Click **Get a New Word** to study a brand-new word!")
        return

    st.markdown(f'<div class="question-box">{card["word"]}</div>', unsafe_allow_html=True)
    if card.get("phonetic"):
        st.caption(card["phonetic"])
    if card.get("audio"):
        st.audio(card["audio"])
    st.markdown(f"**Meaning:** {card['meaning']}")
    if card.get("example"):
        st.markdown(f"**Example:** *{card['example']}*")
    st.markdown("**Look, say, cover, write, check!** Try spelling it without peeking, then check. ✍️")


def _study_builtin(words, year_group):
    total = len(words)
    idx = st.session_state.spell_study_index % total
    card = words[idx]

    st.markdown(f"**{year_group} word list — word {idx + 1} of {total}**")
    st.markdown(f'<div class="question-box">{card["word"]}</div>', unsafe_allow_html=True)
    st.markdown(f"**Meaning:** {card['definition']}")
    example_sentence = card["sentence"].format(blank=f"**{card['word']}**")
    st.markdown(f"**Example:** {example_sentence}")

    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("⬅️ Previous", key="spell_prev_btn"):
            st.session_state.spell_study_index = (idx - 1) % total
            st.rerun()
    with col2:
        if st.button("🔀 Random Word", key="spell_random_btn"):
            st.session_state.spell_study_index = random.randint(0, total - 1)
            st.rerun()
    with col3:
        if st.button("Next ➡️", key="spell_next_btn"):
            st.session_state.spell_study_index = (idx + 1) % total
            st.rerun()


# =============================================================================
# TEST MODE
# =============================================================================

def _set_test_question(word, definition, sentence, audio, phonetic, source, year_group):
    st.session_state.spell_test_word = word
    st.session_state.spell_test_definition = definition
    st.session_state.spell_test_sentence = sentence
    st.session_state.spell_test_audio = audio
    st.session_state.spell_test_phonetic = phonetic
    st.session_state.spell_test_source = source
    st.session_state.spell_test_year_group = year_group
    st.session_state.spell_test_feedback = None
    st.session_state["spell_test_input"] = ""


def _new_builtin_question(words, year_group):
    card = random.choice(words)
    _set_test_question(
        card["word"], card["definition"], card["sentence"].format(blank="_____"),
        "", "", "built-in", year_group,
    )


def _new_web_question(words, year_group):
    card = _fetch_web_card(year_group)
    if card is None:
        _new_builtin_question(words, year_group)
        return
    word = card["word"]
    sentence = blank_out(card["example"], word) or ""
    _set_test_question(
        word, mask_word(card["meaning"], word), sentence,
        card.get("audio", ""), card.get("phonetic", ""), "internet", year_group,
    )


def _render_test(words, year_group, use_web):
    clicked = st.button("🎲 New Spelling Question", key="spell_test_generate_btn")
    source = "internet" if use_web else "built-in"
    stale = (
        st.session_state.spell_test_word is None
        or st.session_state.spell_test_year_group != year_group
        or st.session_state.spell_test_source != source
    )

    if clicked:
        if use_web:
            _new_web_question(words, year_group)
        else:
            _new_builtin_question(words, year_group)
    elif stale:
        if use_web:
            # Don't hit the internet until the pupil asks for a word.
            st.session_state.spell_test_word = None
            st.info("👆 Click **New Spelling Question** to fetch a brand-new word!")
            return
        _new_builtin_question(words, year_group)

    word = st.session_state.spell_test_word
    st.markdown("**Read the clue below, then type the correctly spelled word.**")

    clue = f"📝 <strong>Definition:</strong> {st.session_state.spell_test_definition}"
    if st.session_state.spell_test_sentence:
        clue += f"<br><br>🖊️ <strong>Sentence:</strong> {st.session_state.spell_test_sentence}"
    st.markdown(f'<div class="word-box">{clue}</div>', unsafe_allow_html=True)

    if st.session_state.spell_test_audio:
        st.markdown("🔊 **Listen to the word:**")
        st.audio(st.session_state.spell_test_audio)

    with st.expander("💡 Need a hint?"):
        st.markdown(f"It starts with **{word[0]}** and has **{len(word)}** letters.")
        if st.session_state.spell_test_phonetic:
            st.markdown(f"Sounds like: {st.session_state.spell_test_phonetic}")

    typed_word = st.text_input("Type the word here:", key="spell_test_input")

    if st.button("✅ Check Spelling", key="spell_test_check_btn"):
        is_correct = typed_word.strip().lower() == word.lower()
        message = record_attempt(is_correct)
        if not is_correct:
            message += f" The correct spelling was **{word}**."
        st.session_state.spell_test_feedback = (is_correct, message)

    show_feedback(st.session_state.spell_test_feedback)
