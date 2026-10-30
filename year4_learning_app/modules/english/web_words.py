"""
Internet word services for the Vocabulary and Spelling tabs.

Two free services, neither needing an API key:
  * Datamuse (api.datamuse.com)       - finds words related to a topic, with
                                         how common each word is.
  * Free Dictionary API               - meanings, example sentences, phonetics
    (api.dictionaryapi.dev)             and pronunciation audio for a word.

Everything here fails safely: network problems raise WebLookupError so the
tabs can fall back to their built-in word lists instead of crashing.
"""

import random
import re
from urllib.parse import quote

import requests
import streamlit as st

DICTIONARY_URL = "https://api.dictionaryapi.dev/api/v2/entries/en/{word}"
DATAMUSE_WORDS_URL = "https://api.datamuse.com/words"
DATAMUSE_SUGGEST_URL = "https://api.datamuse.com/sug"
REQUEST_TIMEOUT = 6
HEADERS = {"User-Agent": "Year4LearningApp/1.0 (educational app)"}
MAX_TRIES = 10  # how many candidate words to try before giving up

SURPRISE_ME = "🎲 Surprise me"

TOPICS = [
    "adventure", "animals", "nature", "weather", "feelings", "school", "space",
    "ocean", "history", "mystery", "music", "sport", "food", "travel",
    "science", "family", "garden", "castle",
]

# How common a word is is measured by Datamuse as "occurrences per million
# words". Year 4 gets friendlier, more common words; Year 5 gets trickier ones.
LEVEL_SETTINGS = {
    "Year 4": {"min_freq": 2.0, "max_freq": 60.0, "min_len": 5, "max_len": 9},
    "Year 5": {"min_freq": 0.5, "max_freq": 10.0, "min_len": 6, "max_len": 12},
}

# A small safety net for a children's app. It is deliberately basic: adults
# should still supervise open dictionary searches.
BLOCKED_WORDS = {
    "sex", "sexy", "sexual", "porn", "porno", "nude", "naked", "penis", "vagina",
    "fuck", "fucking", "shit", "bitch", "bastard", "slut", "whore", "rape",
    "cocaine", "heroin", "meth", "nazi",
}

# Dictionary definitions we don't want to show a child.
_AVOID_IN_DEFINITION = (
    "obsolete", "archaic", "vulgar", "offensive", "derogatory", "slang",
    "dated", "rare", "dialect", "sexual", "genitals",
)
_AVOID_PREFIXES = (
    "alternative", "plural of", "past tense", "past participle", "present participle",
    "third-person", "simple past", "comparative form", "superlative form",
    "misspelling", "initialism", "abbreviation", "eye dialect", "obsolete",
)


class WebLookupError(Exception):
    """Raised when the internet (or a word service) can't be reached."""


# =============================================================================
# LOW-LEVEL HELPERS
# =============================================================================

def _get_json(url, params=None):
    """GET a URL and return parsed JSON, None for 404, or raise WebLookupError."""
    try:
        response = requests.get(url, params=params, headers=HEADERS, timeout=REQUEST_TIMEOUT)
    except requests.RequestException as exc:
        raise WebLookupError(str(exc)) from exc

    if response.status_code == 404:
        return None
    if response.status_code != 200:
        raise WebLookupError(f"Unexpected status {response.status_code}")
    try:
        return response.json()
    except ValueError as exc:
        raise WebLookupError("Could not read the response") from exc


def clean_word(raw):
    """Return a lower-case single word, or None if the input isn't a valid word."""
    word = (raw or "").strip().lower()
    if re.fullmatch(r"[a-z][a-z'\-]{1,29}", word):
        return word
    return None


def is_blocked(word):
    return word.lower() in BLOCKED_WORDS


def mask_word(text, word):
    """Replace the word (and simple endings like -s/-ed/-ly) in text with ____."""
    if not text:
        return text
    return re.sub(rf"\b{re.escape(word)}\w*", "____", text, flags=re.IGNORECASE)


def blank_out(sentence, word):
    """Blank the exact word in a sentence for a spelling test, or None if absent."""
    pattern = re.compile(rf"\b{re.escape(word)}\b", re.IGNORECASE)
    if not sentence or not pattern.search(sentence):
        return None
    return pattern.sub("_____", sentence, count=1)


def sentence_frames(word, part_of_speech=""):
    """Sentence starters that help a child build their own sentence with the word."""
    pos = (part_of_speech or "").lower()
    if pos.startswith("noun"):
        frames = [
            "The {w} was ... because ...",
            "Yesterday I saw a {w} and ...",
            "Everybody wanted to talk about the {w} because ...",
        ]
    elif pos.startswith("verb"):
        frames = [
            "We decided to {w} because ...",
            "I would love to {w} when ...",
            "She didn't want to {w} until ...",
        ]
    elif pos.startswith("adj"):
        frames = [
            "It was a very {w} day because ...",
            "He felt {w} when ...",
            "Everyone noticed how {w} the ... was.",
        ]
    elif pos.startswith("adv"):
        frames = [
            "She walked {w} across the ...",
            "He answered {w} when ...",
            "They {w} finished the ...",
        ]
    else:
        frames = [
            "Can you use '{w}' to describe something that happened today?",
            "Write a sentence about your weekend using '{w}'.",
            "Think of a story character who might say '{w}'. What would they say?",
        ]
    return [f.format(w=word) for f in frames]


# =============================================================================
# DICTIONARY LOOKUP
# =============================================================================

def _fix_audio_url(url):
    if url.startswith("//"):
        return "https:" + url
    return url


def _parse_entries(word, data):
    """Turn the Free Dictionary API response into a simple, tidy dict."""
    phonetic = ""
    audio_urls = []
    meanings_by_pos = {}

    for entry in data:
        phonetic = phonetic or entry.get("phonetic", "") or ""
        for ph in entry.get("phonetics", []) or []:
            phonetic = phonetic or ph.get("text", "") or ""
            url = ph.get("audio") or ""
            if url:
                audio_urls.append(_fix_audio_url(url))

        for meaning in entry.get("meanings", []) or []:
            pos = meaning.get("partOfSpeech", "") or ""
            bucket = meanings_by_pos.setdefault(
                pos,
                {"part_of_speech": pos, "definitions": [], "synonyms": [], "antonyms": []},
            )
            for d in meaning.get("definitions", []) or []:
                bucket["definitions"].append(
                    {"definition": d.get("definition", "") or "", "example": d.get("example", "") or ""}
                )
                bucket["synonyms"].extend(d.get("synonyms", []) or [])
                bucket["antonyms"].extend(d.get("antonyms", []) or [])
            bucket["synonyms"].extend(meaning.get("synonyms", []) or [])
            bucket["antonyms"].extend(meaning.get("antonyms", []) or [])

    # Prefer British pronunciation audio for UK pupils.
    def _is_uk(url):
        lowered = url.lower()
        return "-uk" in lowered or "_gb_" in lowered or "/gb/" in lowered

    audio = next((u for u in audio_urls if _is_uk(u)), audio_urls[0] if audio_urls else "")

    meanings = []
    for bucket in meanings_by_pos.values():
        bucket["synonyms"] = list(dict.fromkeys(bucket["synonyms"]))
        bucket["antonyms"] = list(dict.fromkeys(bucket["antonyms"]))
        if bucket["definitions"]:
            meanings.append(bucket)

    if not meanings:
        return None
    return {"word": word, "phonetic": phonetic, "audio": audio, "meanings": meanings, "offline": False}


@st.cache_data(ttl=86400, show_spinner=False)
def lookup_word(word):
    """Look a word up online. Returns a dict, or None if the word isn't found."""
    data = _get_json(DICTIONARY_URL.format(word=quote(word)))
    if not data or not isinstance(data, list):
        return None
    return _parse_entries(word, data)


@st.cache_data(ttl=86400, show_spinner=False)
def suggest_words(word):
    """'Did you mean...?' suggestions for a word that wasn't found."""
    data = _get_json(DATAMUSE_SUGGEST_URL, {"s": word, "max": 5}) or []
    suggestions = []
    for item in data:
        w = str(item.get("word", "")).lower()
        if re.fullmatch(r"[a-z]+", w) and w != word and w not in BLOCKED_WORDS:
            suggestions.append(w)
    return suggestions[:4]


# =============================================================================
# FINDING NEW WORDS
# =============================================================================

@st.cache_data(ttl=3600, show_spinner=False)
def fetch_topic_candidates(topic, min_freq, max_freq, min_len, max_len):
    """Words related to a topic that suit the chosen level (by length and how common they are)."""
    data = _get_json(DATAMUSE_WORDS_URL, {"ml": topic, "md": "fp", "max": 400}) or []
    words = []
    for item in data:
        w = str(item.get("word", "")).lower()
        if not re.fullmatch(r"[a-z]+", w):
            continue
        if not (min_len <= len(w) <= max_len) or w in BLOCKED_WORDS:
            continue
        tags = item.get("tags", []) or []
        if "prop" in tags:  # skip names of people and places
            continue
        freq = None
        for tag in tags:
            if tag.startswith("f:"):
                try:
                    freq = float(tag[2:])
                except ValueError:
                    pass
        if freq is None or not (min_freq <= freq <= max_freq):
            continue
        words.append(w)
    return words


def _is_kid_friendly_definition(text):
    lowered = text.strip().lower()
    if not (8 <= len(lowered) <= 200):
        return False
    if lowered.startswith(_AVOID_PREFIXES):
        return False
    return not any(label in lowered for label in _AVOID_IN_DEFINITION)


def make_card(entry):
    """Turn a looked-up entry into a simple flashcard dict (or None if unsuitable)."""
    candidates = []
    for meaning in entry["meanings"]:
        for d in meaning["definitions"]:
            text = d["definition"].strip()
            if _is_kid_friendly_definition(text):
                candidates.append(
                    {"meaning": text, "example": d["example"].strip(), "pos": meaning["part_of_speech"]}
                )
    if not candidates:
        return None

    chosen = next((c for c in candidates if c["example"]), candidates[0])
    return {
        "word": entry["word"],
        "meaning": chosen["meaning"],
        "example": chosen["example"],
        "pos": chosen["pos"],
        "phonetic": entry["phonetic"],
        "audio": entry["audio"],
        "source": "internet",
    }


def get_new_card(topic, level, exclude=()):
    """
    Find a brand-new word online. Returns a flashcard dict, or None if no
    suitable word turned up. Raises WebLookupError if the internet is unreachable.
    """
    exclude = {w.lower() for w in exclude}
    settings = LEVEL_SETTINGS.get(level, LEVEL_SETTINGS["Year 4"])
    topics = TOPICS if topic == SURPRISE_ME else [topic]
    tried = set()

    for _ in range(MAX_TRIES):
        chosen_topic = random.choice(topics)
        candidates = [
            w for w in fetch_topic_candidates(
                chosen_topic, settings["min_freq"], settings["max_freq"],
                settings["min_len"], settings["max_len"],
            )
            if w not in exclude and w not in tried
        ]
        if not candidates:
            continue
        word = random.choice(candidates)
        tried.add(word)
        entry = lookup_word(word)
        if not entry:
            continue
        card = make_card(entry)
        if card:
            return card
    return None
