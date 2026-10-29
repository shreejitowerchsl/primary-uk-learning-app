"""Central definition and initialisation of every st.session_state key used
by the app, so switching tabs never loses in-progress work."""

import copy

import streamlit as st

from modules.web_words import SURPRISE_ME

DEFAULTS = {
    # --- global score tracking ---
    "score_correct": 0,
    "score_attempted": 0,

    # --- Multiplication module ---
    "mult_category": "2-Digit x 1-Digit",
    "mult_last_category": None,
    "mult_question_text": None,
    "mult_equation": None,
    "mult_answer": None,
    "mult_steps": None,
    "mult_feedback": None,
    "mult_unit": "",

    # --- Division module ---
    "div_dividend": None,
    "div_divisor": None,
    "div_quotient": None,
    "div_remainder": None,
    "div_steps": None,
    "div_feedback": None,

    # --- Powers module ---
    "pow_base": None,
    "pow_exp": None,
    "pow_answer": None,
    "pow_steps": None,
    "pow_feedback": None,

    # --- Abacus module ---
    "abacus_level": "🟢 Beginner",
    "abacus_show_number": 5,
    "abacus_drill_type": None,
    "abacus_drill_a": None,
    "abacus_drill_b": None,
    "abacus_drill_op": None,
    "abacus_drill_answer": None,
    "abacus_drill_start_svg": None,
    "abacus_drill_steps": None,
    "abacus_drill_feedback": None,

    # --- Word Problems module ---
    "wp_operation": "✖️ Multiplication",
    "wp_level": "🟢 Beginner",
    "wp_last_combo": None,
    "wp_question": None,
    "wp_answer": None,
    "wp_remainder": None,
    "wp_steps": None,
    "wp_answer_type": "single",
    "wp_feedback": None,

    # --- Vocabulary module ---
    "vocab_mode": "📖 Study (Flashcards)",
    "vocab_use_web": True,
    "vocab_level": "Year 4",
    "vocab_topic": SURPRISE_ME,
    "vocab_index": 0,
    "vocab_reveal": False,
    "vocab_online_card": None,
    "vocab_web_error": None,
    "vocab_seen_cards": [],
    "vocab_quiz_word": None,
    "vocab_quiz_example": None,
    "vocab_quiz_correct_meaning": None,
    "vocab_quiz_options": None,
    "vocab_quiz_feedback": None,
    "vocab_search_input": "",
    "vocab_search_result": None,
    "vocab_search_error": None,
    "vocab_search_suggestions": [],
    "vocab_own_sentence": "",
    "vocab_own_feedback": None,

    # --- Spelling module ---
    "spell_year_group": "Year 4",
    "spell_mode": "📖 Study",
    "spell_use_web": True,
    "spell_topic": SURPRISE_ME,
    "spell_study_index": 0,
    "spell_online_card": None,
    "spell_seen_words": [],
    "spell_test_word": None,
    "spell_test_definition": None,
    "spell_test_sentence": None,
    "spell_test_audio": None,
    "spell_test_phonetic": None,
    "spell_test_source": None,
    "spell_test_year_group": None,
    "spell_test_feedback": None,
}


def init_session_state():
    for key, value in DEFAULTS.items():
        if key not in st.session_state:
            # deepcopy so list defaults are never shared between users' sessions
            st.session_state[key] = copy.deepcopy(value)
