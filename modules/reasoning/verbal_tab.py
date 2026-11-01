"""
Verbal Reasoning tab. Nineteen topics, each at three levels. Your topic list used many different
names for the same skill, so they are grouped by what the question actually asks you to do:

  Jumbled words          (letters to make words, find the word, jumbled words)
  Same or opposite       (similar meanings, same or opposite meanings)
  Odd word out
  Word stages & order    (sequence orders, word stages)
  Number sequences       (sequences)
  Letter sequences
  Alphabet               (the alphabet, alphabetical order)
  Word codes             (word codes)
  Number codes           (number codes, using numbers for letters)
  Word connections       (word connections, word patterns)
  Making new words       (two words to make a new word, one word makes, add a word, making one word from two)
  Missing letters        (one missing letter makes two words, three missing letters make a word)
  Hidden word
  Make sense of sentences (fill in the spaces)
  Definitions & crosswords (using definitions, crossword puzzles)
  Using grids to find information
  Logic word problems    (word problems)
  Algebra
  Mystery number         (find a certain number)

Puzzle banks that depend on checking real English words were verified offline (see verbal_generated.py),
so each of those puzzles has exactly one correct answer.
"""

import random
import re

from modules.english.spelling_tab import YEAR4_WORDS, YEAR5_WORDS
from modules.english.vocabulary_tab import VOCABULARY_WORDS
from modules.reasoning import verbal_data as V
from modules.reasoning import verbal_generated as G
from modules.reasoning.engine import render_reasoning

ORDINALS = ["first", "second", "third", "fourth", "fifth", "sixth", "seventh"]
ALPHABET = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"


# =============================================================================
# HELPERS
# =============================================================================

def choice_q(prompt, correct, wrong, explain, **kw):
    options = list(dict.fromkeys([correct] + list(wrong)))
    random.shuffle(options)
    return {"type": "choice", "prompt": prompt, "choices": options, "answer": correct, "explain": explain, **kw}


def text_q(prompt, answer, explain, accept=(), **kw):
    return {"type": "text", "prompt": prompt, "answer": answer, "accept": list(accept), "explain": explain, **kw}


def number_q(prompt, answer, explain, **kw):
    return {"type": "number", "prompt": prompt, "answer": answer, "explain": explain, **kw}


def shift_word(word, k):
    return "".join(chr((ord(ch) - 65 + k) % 26 + 65) for ch in word)


def mirror_word(word):
    return "".join(chr(90 - (ord(ch) - 65)) for ch in word)


def letters_spaced(text):
    return " ".join(text)


# =============================================================================
# 1. JUMBLED WORDS
# =============================================================================

def gen_jumbled(level):
    word = random.choice(G.ANAGRAMS[level])
    letters = list(word)
    for _ in range(60):
        random.shuffle(letters)
        if "".join(letters) != word:
            break
    hint = {1: f"It has **{len(word)}** letters and starts with **{word[0].upper()}**.",
            2: f"It has **{len(word)}** letters.", 3: f"It has **{len(word)}** letters."}[level]
    return text_q(
        f"Rearrange these letters to make a real word:\n\n**{letters_spaced(''.join(letters).upper())}**",
        word, f"The word is **{word.upper()}**. A good trick is to look for common letter pairs (like TH, CH, SH, ST) "
        "and endings (like -ING, -ER, -LY), then build the word around them.", hint=hint, placeholder="type the word")


# =============================================================================
# 2. SAME OR OPPOSITE MEANINGS
# =============================================================================

WORD_GROUP = {}
for _i, _g in enumerate(V.SYNONYM_GROUPS):
    for _w in _g:
        WORD_GROUP[_w] = _i
ANTONYM_OF = {}
for _a, _b in V.ANTONYM_PAIRS:
    ANTONYM_OF[_a], ANTONYM_OF[_b] = _b, _a


def _other_words(exclude_groups, exclude_words, k):
    pool = [w for w, g in WORD_GROUP.items() if g not in exclude_groups and w not in exclude_words]
    return random.sample(pool, k)


# Groups that are natural opposites of each other: never offered as wrong answers to an "opposite" question
# (otherwise two answers could both be right, e.g. the opposite of "hard" could be "soft" or "easy").
OPPOSITE_GROUPS = {}
for _x, _y in [("big", "small"), ("happy", "sad"), ("fast", "slow"), ("difficult", "easy"), ("old", "new"), ("rich", "poor"),
               ("quiet", "noisy"), ("beautiful", "ugly"), ("hot", "cold"), ("begin", "finish"), ("brave", "scared"),
               ("clever", "strange")]:
    OPPOSITE_GROUPS[WORD_GROUP[_x]] = WORD_GROUP[_y]
    OPPOSITE_GROUPS[WORD_GROUP[_y]] = WORD_GROUP[_x]


def gen_meanings(level):
    mode = {1: "same", 2: "opposite"}.get(level) or random.choice(["same", "opposite"])
    if mode == "same":
        group = random.choice(V.SYNONYM_GROUPS)
        word, correct = random.sample(group, 2)
        gi = WORD_GROUP[word]
        wrong = _other_words({gi}, {word, correct}, 3)
        trap = ANTONYM_OF.get(word)
        if level == 3 and trap and trap not in group and trap not in wrong:
            wrong[0] = trap  # a tempting opposite
        return choice_q(f"Which word means the **same** (or nearly the same) as **{word}**?", correct, wrong,
                        f"**{word}** and **{correct}** have almost the same meaning.")
    a, b = random.choice(V.ANTONYM_PAIRS)
    if random.random() < 0.5:
        a, b = b, a
    banned = {WORD_GROUP.get(a), WORD_GROUP.get(b)} - {None}
    banned |= {OPPOSITE_GROUPS[g] for g in list(banned) if g in OPPOSITE_GROUPS}
    wrong = _other_words(banned, {a, b, ANTONYM_OF.get(a)}, 3)
    if level == 3 and a in WORD_GROUP:
        syn = [w for w in V.SYNONYM_GROUPS[WORD_GROUP[a]] if w != a and w not in wrong]
        if syn:
            wrong[0] = random.choice(syn)  # a tempting word with the SAME meaning
    return choice_q(f"Which word means the **opposite** of **{a}**?", b, wrong,
                    f"**{a}** and **{b}** have opposite meanings.")


# =============================================================================
# 3. ODD WORD OUT
# =============================================================================

def gen_odd(level):
    parents = list(V.ODD_GROUPS)
    if level == 1:
        pa, pb = random.sample(parents, 2)
        sa, sb = random.choice(list(V.ODD_GROUPS[pa])), random.choice(list(V.ODD_GROUPS[pb]))
        same, odd = random.sample(V.ODD_GROUPS[pa][sa], 3), random.choice(V.ODD_GROUPS[pb][sb])
    else:
        pa = random.choice([p for p in parents if len(V.ODD_GROUPS[p]) >= 2])
        sa, sb = random.sample(list(V.ODD_GROUPS[pa]), 2)
        same = random.sample(V.ODD_GROUPS[pa][sa], 3 if level == 2 else 4)
        odd = random.choice(V.ODD_GROUPS[pa][sb])
    words = same + [odd]
    random.shuffle(words)
    return choice_q("Which word is the **odd one out**?", odd, [w for w in words if w != odd],
                    f"{', '.join(same)} all belong together ({sa}). **{odd}** is different ({sb}).")


# =============================================================================
# 4. WORD STAGES / PUTTING WORDS IN ORDER
# =============================================================================

def gen_stages(level):
    pool = [s for s in V.STAGES if (len(s[1]) <= 5 if level == 1 else len(s[1]) >= 4)]
    title, chain = random.choice(pool)
    shown = random.sample(chain, len(chain))
    n = len(chain)
    if level == 1:
        which = random.choice(["first", "last"])
        answer = chain[0] if which == "first" else chain[-1]
        ask = f"Which word comes **{which}**?"
    elif level == 2:
        idx = random.randint(1, n - 2) if n > 2 else 0
        answer, ask = chain[idx], f"Which word comes **{ORDINALS[idx]}**?"
    else:
        i = random.randint(1, n - 2)
        answer, ask = chain[i], f"Which word comes **between {chain[i - 1]} and {chain[i + 1]}**?"
    wrong = random.sample([w for w in chain if w != answer], min(4, n - 1))
    return choice_q(f"These words are about **{title}**, but they are in the wrong order:\n\n**{', '.join(shown)}**\n\n"
                    f"Put them in the right order. {ask}", answer, wrong,
                    "The correct order is: " + " → ".join(f"**{w}**" for w in chain) + f".\n\nSo the answer is **{answer}**.")


# =============================================================================
# 5. NUMBER SEQUENCES
# =============================================================================

def _sequence(level):
    kinds = {1: ["add", "sub"], 2: ["mul", "alt", "inc"], 3: ["fib", "interleave", "square", "muladd", "inc"]}[level]
    kind = random.choice(kinds)
    if kind == "add":
        step = random.randint(2, 9)
        s = random.randint(1, 30)
        return [s + step * i for i in range(6)], f"The numbers go **up by {step}** each time."
    if kind == "sub":
        step = random.randint(2, 9)
        s = random.randint(step * 5 + 2, step * 5 + 40)
        return [s - step * i for i in range(6)], f"The numbers go **down by {step}** each time."
    if kind == "mul":
        f, s = random.choice([2, 3]), random.randint(1, 5)
        return [s * f ** i for i in range(5)], f"Each number is **multiplied by {f}** to get the next one."
    if kind == "alt":
        a, b = random.randint(4, 9), random.randint(1, 3)
        t = [random.randint(5, 20)]
        for i in range(6):
            t.append(t[-1] + (a if i % 2 == 0 else -b))
        return t, f"The pattern is **add {a}, take away {b}**, and then it repeats."
    if kind == "inc":
        d, s = random.randint(1, 3), random.randint(1, 10)
        t = [s]
        for i in range(5):
            t.append(t[-1] + d + i)
        return t, f"The gap grows by 1 each time: **+{d}, +{d + 1}, +{d + 2}**, and so on."
    if kind == "fib":
        a, b = random.randint(1, 5), random.randint(1, 5)
        t = [a, b]
        while len(t) < 7:
            t.append(t[-1] + t[-2])
        return t, "Each number is the **sum of the two numbers before it**."
    if kind == "interleave":
        s1, p, s2, q = random.randint(1, 20), random.randint(2, 5), random.randint(1, 20), random.randint(2, 6)
        t = []
        for i in range(4):
            t += [s1 + p * i, s2 + q * i]
        return t[:7], (f"Two patterns are mixed together. The 1st, 3rd, 5th... numbers go **up by {p}**; "
                       f"the 2nd, 4th, 6th... numbers go **up by {q}**.")
    if kind == "square":
        k = random.randint(1, 5)
        return [(k + i) ** 2 for i in range(6)], "These are **square numbers** (1×1, 2×2, 3×3...)."
    s = random.randint(1, 4)
    t = [s]
    for _ in range(4):
        t.append(t[-1] * 2 + 1)
    return t, "Each number is **doubled, then 1 is added**."


def gen_number_seq(level):
    terms, rule = _sequence(level)
    hide = len(terms) - 1 if level < 3 else random.choice([len(terms) - 1, len(terms) - 1, random.randint(2, len(terms) - 2)])
    shown = [("?" if i == hide else str(t)) for i, t in enumerate(terms)]
    shown = shown[:hide + 1] if hide == len(terms) - 1 else shown
    ask = "What number comes next?" if hide == len(terms) - 1 else "What is the missing number?"
    return number_q(f"{ask}\n\n**{',  '.join(shown)}**", terms[hide],
                    f"{rule}\n\nThe full sequence is: {', '.join(map(str, terms))}. The answer is **{terms[hide]}**.")


# =============================================================================
# 6. LETTER SEQUENCES
# =============================================================================

def gen_letter_seq(level):
    for _ in range(400):
        if level == 1:
            k, d = random.randint(1, 3), random.choice([1, -1])
            s = random.randint(0, 25)
            idx = [s + d * k * i for i in range(6)]
            rule = f"The letters go **{'forward' if d > 0 else 'backward'} by {k}** each time."
        elif level == 2:
            a, b = random.sample([1, 2, 3, 4], 2)
            s = random.randint(0, 25)
            idx = [s]
            for i in range(6):
                idx.append(idx[-1] + (a if i % 2 == 0 else b))
            rule = f"The jumps alternate: **{a} letters, then {b} letters**, and repeat."
        else:
            if random.random() < 0.5:
                s = random.randint(0, 8)
                idx = [s]
                for i in range(6):
                    idx.append(idx[-1] + 1 + i)
                rule = "The jump grows by one each time: **+1, +2, +3, +4...**"
            else:
                s1, s2 = random.randint(0, 10), random.randint(0, 10)
                p, q = random.choice([1, 2, 3]), random.choice([1, 2, -1, -2])
                idx = []
                for i in range(4):
                    idx += [s1 + p * i, s2 + q * i]
                idx = idx[:7]
                rule = (f"Two patterns are mixed together. The 1st, 3rd, 5th... letters go **forward by {p}**; "
                        f"the 2nd, 4th, 6th... go **{'forward' if q > 0 else 'backward'} by {abs(q)}**.")
        shown, answer = idx[:-1], idx[-1]
        if len(set(idx)) == len(idx) and all(0 <= i <= 25 for i in idx):
            letters = [ALPHABET[i] for i in shown]
            return text_q(f"What letter comes next?\n\n**{',  '.join(letters)},  ?**", ALPHABET[answer],
                          f"{rule}\n\nLetter positions: " + ", ".join(f"{ALPHABET[i]}={i + 1}" for i in idx) +
                          f". The next letter is **{ALPHABET[answer]}**.", placeholder="one letter")
    raise RuntimeError("letter sequence failed")


# =============================================================================
# 7. THE ALPHABET AND ALPHABETICAL ORDER
# =============================================================================

def _alpha_order_question(words):
    ordered = sorted(words)
    n = len(ordered)
    if random.random() < 0.5:
        which = random.choice(["first", "last"])
        answer = ordered[0] if which == "first" else ordered[-1]
    else:
        i = random.randint(1, n - 2)
        which, answer = ORDINALS[i], ordered[i]
    return which, answer, ordered


def gen_alphabet(level):
    mode = random.choice(["position", "ordinal"]) if level == 1 else random.choice(["words", "words", "ordinal"]) if level == 2 \
        else random.choice(["words2", "words2", "mirror"])
    if mode == "position":
        n = random.randint(2, 6)
        i = random.randint(0, 25 - n)
        direction = random.choice(["after", "before"])
        start = i + n if direction == "before" else i
        ans = ALPHABET[start - n] if direction == "before" else ALPHABET[start + n]
        return text_q(f"Which letter is **{n} places {direction}** the letter **{ALPHABET[start]}** in the alphabet?", ans,
                      f"{ALPHABET[start]} is letter number {start + 1}. Count {n} places {direction} it to reach **{ans}**.",
                      placeholder="one letter")
    if mode == "ordinal":
        k = random.randint(3, 24)
        return text_q(f"Which letter is the **{k}th** letter of the alphabet?", ALPHABET[k - 1],
                      f"Counting A=1, B=2, C=3... the {k}th letter is **{ALPHABET[k - 1]}**.", placeholder="one letter")
    if mode == "words":
        firsts = random.sample(sorted(G.ALPHA_1), 4)
        words = [random.choice(G.ALPHA_1[f]) for f in firsts]
    elif mode == "words2":
        prefix = random.choice(sorted(G.ALPHA_2))
        words = random.sample(G.ALPHA_2[prefix], random.choice([4, 5]))
    else:
        i = random.randint(2, 11)
        return text_q(f"Imagine the alphabet written **backwards** (Z, Y, X... down to A). Which letter would be in the same "
                      f"place as **{ALPHABET[i]}** is in the normal alphabet?", ALPHABET[25 - i],
                      f"{ALPHABET[i]} is letter number {i + 1} from the start (A). The letter {i + 1} from the end (Z) is **{ALPHABET[25 - i]}**.",
                      placeholder="one letter")
    which, answer, ordered = _alpha_order_question(words)
    wrong = [w for w in words if w != answer]
    return choice_q(f"Put these words in **alphabetical order**. Which word comes **{which}**?\n\n**{', '.join(words)}**",
                    answer, wrong,
                    "Alphabetical order: " + ", ".join(f"**{w}**" for w in ordered) + ". "
                    + ("Compare the first letters; if they match, look at the next letter." if mode == "words"
                       else "These words begin with the same letters, so compare the next letter along."))


# =============================================================================
# 8. WORD CODES (letter codes)
# =============================================================================

CODE_WORDS = ["PLAY", "BOOK", "FISH", "CAKE", "STAR", "MOON", "TREE", "RAIN", "BIRD", "SHIP", "LAMP", "DOOR", "SNOW",
              "KING", "FROG", "WIND", "JUMP", "SAND", "HORSE", "TIGER", "HOUSE", "PLANT", "SMILE", "GREEN", "CLOUD",
              "TRAIN", "BREAD", "LIGHT", "MOUSE", "WATER"]


def _no_wrap(word, k):
    return all(0 <= ord(c) - 65 + k <= 25 for c in word)


def gen_word_code(level):
    if level == 1:
        k = random.randint(1, 3)
        w1, w2 = random.sample([w for w in CODE_WORDS if _no_wrap(w, k)], 2)
        return text_q(f"In a code, **{w1}** is written as **{shift_word(w1, k)}**.\n\nHow is **{w2}** written in the same code?",
                      shift_word(w2, k),
                      f"Compare {w1} and {shift_word(w1, k)}: every letter moves **{k} place{'s' if k > 1 else ''} forward** in the alphabet "
                      f"(for example {w1[0]} → {shift_word(w1, k)[0]}). Do the same to {w2}: **{shift_word(w2, k)}**.", placeholder="the coded word")
    if level == 2:
        k = random.choice([1, 2, 3, 4])
        w1, w2 = random.sample([w for w in CODE_WORDS if _no_wrap(w, k)], 2)
        return text_q(f"In a code, **{w1}** is written as **{shift_word(w1, k)}**.\n\n"
                      f"What word is written as **{shift_word(w2, k)}** in the same code?",
                      w2, f"Every letter moves **{k}** place{'s' if k > 1 else ''} forward to make the code, so to decode we move each letter "
                      f"**{k} place{'s' if k > 1 else ''} back**: {shift_word(w2, k)} → **{w2}**.", placeholder="the real word")
    w1, w2 = random.sample(CODE_WORDS, 2)
    if random.random() < 0.5:
        return text_q(f"In a code, the alphabet is reversed, so A = Z, B = Y, C = X and so on.\n\n**{w1}** is written as **{mirror_word(w1)}**. "
                      f"How is **{w2}** written?", mirror_word(w2),
                      f"Each letter swaps with its mirror partner: A↔Z, B↔Y, C↔X... For {w2}: " +
                      ", ".join(f"{c}→{mirror_word(c)}" for c in w2) + f". The code is **{mirror_word(w2)}**.", placeholder="the coded word")
    k = random.randint(1, 3)
    code = lambda w: shift_word(w[::-1], k)
    return text_q(f"A code does two things: it **reverses** the word, then moves every letter **{k} place{'s' if k > 1 else ''} forward**.\n\n"
                  f"**{w1}** becomes **{code(w1)}**. What does **{w2}** become?", code(w2),
                  f"Step 1: reverse {w2} → {w2[::-1]}. Step 2: move each letter {k} forward → **{code(w2)}**.", placeholder="the coded word")


# =============================================================================
# 9. NUMBER CODES
# =============================================================================

def gen_number_code(level):
    if level == 1:
        w = random.choice(["BAD", "CAB", "FACE", "BEAD", "DEAF", "CAGE", "HEAD", "BIKE", "DAD", "ACE", "BAG", "HEN"])
        vals = [ord(c) - 64 for c in w]
        return number_q(f"If A = 1, B = 2, C = 3 and so on, what is the **total value** of the letters in **{w}**?", sum(vals),
                        " + ".join(f"{c} ({v})" for c, v in zip(w, vals)) + f" = **{sum(vals)}**.")
    if level == 2:
        w = random.choice([c for c in CODE_WORDS if len(c) <= 5])
        codes = " ".join(str(ord(c) - 64) for c in w)
        if random.random() < 0.5:
            return text_q(f"In a code, A = 1, B = 2, C = 3 and so on up to Z = 26.\n\nWrite **{w}** as a number code (put a space between the numbers).",
                          codes, "Replace each letter with its place in the alphabet: " +
                          ", ".join(f"{c}={ord(c) - 64}" for c in w) + f". The code is **{codes}**.", placeholder="e.g. 3 1 20")
        return text_q(f"In a code, A = 1, B = 2, C = 3 and so on up to Z = 26.\n\nWhat word does **{codes}** stand for?", w.lower(),
                      "Turn each number back into a letter: " + ", ".join(f"{ord(c) - 64}={c}" for c in w) + f". The word is **{w}**.",
                      placeholder="the word")
    word = random.choice(["CAT", "DOG", "SUN", "HEN", "PIG", "BEE", "FOX", "OWL", "RAT", "COW", "FISH", "DUCK", "LAMB", "FROG", "BIRD"])
    letters = list(dict.fromkeys(word)) + random.sample([c for c in ALPHABET if c not in word], 2)
    nums = random.sample(range(10, 100), len(letters))
    key = dict(zip(letters, nums))
    shown = list(letters)
    random.shuffle(shown)
    table = "| Letter | " + " | ".join(shown) + " |\n|---|" + "---|" * len(shown) + "\n| Code | " + " | ".join(str(key[c]) for c in shown) + " |"
    if random.random() < 0.5:
        codes = " ".join(str(key[c]) for c in word)
        return text_q(f"Use the code key to write **{word}** as a number code (put a space between the numbers).", codes,
                      "Look up each letter in the key: " + ", ".join(f"{c}={key[c]}" for c in word) + f". The code is **{codes}**.",
                      markdown=table, placeholder="e.g. 12 40 7")
    codes = " ".join(str(key[c]) for c in word)
    return text_q(f"Use the code key to find the word that is written as **{codes}**.", word.lower(),
                  "Find each number in the key: " + ", ".join(f"{key[c]}={c}" for c in word) + f". The word is **{word}**.",
                  markdown=table, placeholder="the word")


# =============================================================================
# 10. WORD CONNECTIONS (analogies)
# =============================================================================

def gen_analogy_words(level):
    a, b, c, ans, domain = random.choice(V.ANALOGIES)
    base = domain.rstrip("0123456789")
    pool = [x[3] for x in V.ANALOGIES if x[4].rstrip("0123456789") != base and x[3] not in (a, b, c, ans)]
    wrong = random.sample(sorted(set(pool)), 3)
    if level == 3:
        wrong[0] = b if b not in (ans,) else wrong[0]
    return choice_q(f"**{a}** is to **{b}** as **{c}** is to ...?", ans, wrong,
                    f"Work out how **{a}** and **{b}** are linked. The same link joins **{c}** and **{ans}**.")


# =============================================================================
# 11. MAKING NEW WORDS (compound words)
# =============================================================================

def gen_compound(level):
    if level == 1:
        first, second, answer = random.choice(G.TWO_LISTS)
        return text_q(f"Pick **one word from each list** to make a new word. Type the new word.\n\n"
                      f"List 1: **{',  '.join(first)}**\n\nList 2: **{',  '.join(second)}**", answer,
                      f"Only one pair makes a real word: **{answer}**.", placeholder="the new word")
    if level == 2:
        a, m, b, distractors = random.choice(G.MIDDLE_WORD)
        return choice_q(f"Find the word that **finishes the first word** and **starts the second word**:\n\n**{a.upper()}  ( ? )  {b.upper()}**",
                        m, random.sample(distractors, 3),
                        f"**{a}{m}** and **{m}{b}** are both real words, so the missing word is **{m}**.")
    direction, trio, ans, distractors = random.choice(G.FAMILIES)
    if direction == "after":
        built = [t + ans for t in trio]
        where = "after"
    else:
        built = [ans + t for t in trio]
        where = "before"
    return choice_q(f"One word can be put **{where}** each of these three words to make three new words. Which word is it?\n\n"
                    f"**{',  '.join(trio)}**", ans, random.sample(distractors, 3),
                    f"Putting **{ans}** {where} each word makes: " + ", ".join(f"**{w}**" for w in built) + ".")


# =============================================================================
# 12. MISSING LETTERS
# =============================================================================

def _definition_bank():
    bank = {}
    for w in YEAR4_WORDS + YEAR5_WORDS:
        bank[w["word"]] = w["definition"]
    for w in VOCABULARY_WORDS:
        bank.setdefault(w["word"], w["meaning"])
    return {w: d for w, d in bank.items() if w.lower() not in d.lower() and len(w) >= 5}


DEF_BANK = _definition_bank()
ACCEPT_ALT = {"centre": ["center"], "favourite": ["favorite"], "marvellous": ["marvelous"]}


def gen_missing_letters(level):
    if level in (1, 2):
        p, letter, s, w1, w2 = random.choice(G.ONE_LETTER)
        prompt = (f"Find **one letter** that finishes the first word **and** starts the second word:\n\n"
                  f"**{p.upper()}  ( ? )  {s.upper()}**")
        explain = f"**{p}{letter}** = {w1} and **{letter}{s}** = {w2}, so the missing letter is **{letter.upper()}**."
        if level == 1:
            wrong = random.sample([c for c in "abcdefghijklmnopqrstuvwxyz" if c != letter], 3)
            return choice_q(prompt, letter.upper(), [c.upper() for c in wrong], explain)
        return text_q(prompt, letter, explain, placeholder="one letter")
    word = random.choice(sorted(DEF_BANK))
    i = random.randint(1, len(word) - 4)
    pattern = word[:i] + " _ _ _ " + word[i + 3:]
    return text_q(f"Three letters are missing from this word. Use the clue to work out the word.\n\n"
                  f"**{pattern.upper()}**\n\nClue: *{DEF_BANK[word]}*", word,
                  f"The word is **{word}**; the missing letters are **{word[i:i + 3].upper()}**.",
                  accept=ACCEPT_ALT.get(word, []), placeholder="the whole word")


# =============================================================================
# 13. HIDDEN WORD
# =============================================================================

def gen_hidden(level):
    ok = {1: lambda h: len(h[1]) == 3, 2: lambda h: len(h[1]) in (3, 4), 3: lambda h: len(h[1]) >= 4}[level]
    pool = [h for h in G.HIDDEN if ok(h)] or G.HIDDEN
    cat, hidden, w1, w2 = random.choice(pool)
    family = G.HIDDEN_CATS[cat]

    # Add a little filler so it reads like a phrase, but never let the filler create a second hidden word.
    before, after = "", ""
    for _ in range(60):
        b, a = random.choice(["the", "a", "my", "this", "our"]), random.choice(["and", "with", "near", "today", "again"])
        squashed = b + w1 + w2 + a
        if [x for x in family if x in squashed] == [hidden] and squashed.count(hidden) == 1:
            before, after = b + " ", " " + a
            break
    phrase = f"{before}{w1} {w2}{after}"

    squashed = phrase.replace(" ", "")
    others = [w for w in family if w != hidden and w not in squashed]
    same_len = [w for w in others if len(w) == len(hidden)]
    wrong = random.sample(same_len if len(same_len) >= 3 else others, 3)
    pos = (w1 + w2).index(hidden)
    k = len(w1) - pos
    return choice_q(f"A hidden **{cat}** is hiding where two neighbouring words meet. Which one is it?\n\n**{phrase}**",
                    hidden, wrong,
                    f"Run the end of **{w1}** into the start of **{w2}**: {w1[:-k]}**{w1[-k:]}**|**{w2[:len(hidden) - k]}**{w2[len(hidden) - k:]} "
                    f"spells **{hidden}**.")


# =============================================================================
# 14. MAKE SENSE OF SENTENCES
# =============================================================================

def gen_cloze(level):
    pool = [c for c in V.CLOZE if (c[0] == level or level == 3)] if level < 3 else list(V.CLOZE)
    _, sentence, correct, wrong = random.choice(pool)
    return choice_q(f"Choose the word that makes the sentence **make sense**:\n\n*{sentence}*", correct, wrong,
                    f"**{correct}** is the only choice that fits both the meaning and the grammar: "
                    f"*{sentence.replace('______', correct)}*")


# =============================================================================
# 15. DEFINITIONS AND CROSSWORD CLUES
# =============================================================================

_STOP = {"that", "this", "with", "from", "have", "been", "which", "something", "someone", "making", "being", "very", "more"}


def _sig(definition):
    return {w for w in re.findall(r"[a-z]{4,}", definition.lower())} - _STOP


def gen_definitions(level):
    word = random.choice(sorted(DEF_BANK))
    definition = DEF_BANK[word]
    if level == 1:
        pool = [w for w in DEF_BANK if w != word and len(_sig(DEF_BANK[w]) & _sig(definition)) == 0]
        wrong = random.sample(pool, 3)
        return choice_q(f"Which word matches this meaning?\n\n*{definition}*", word, wrong,
                        f"The meaning describes **{word}**.")
    if level == 2:
        pattern = word[0] + " " + " ".join("_" * (len(word) - 2)) + " " + word[-1]
        label = f"({len(word)} letters) first and last letters given"
    else:
        pattern = word[0] + " " + " ".join("_" * (len(word) - 1))
        label = f"({len(word)} letters) first letter given"
    return text_q(f"**Crossword clue:** {definition}\n\n**{pattern.upper()}**   {label}", word,
                  f"The answer is **{word}**. It fits the clue and the pattern of letters.",
                  accept=ACCEPT_ALT.get(word, []), placeholder="the word")


# =============================================================================
# 16. USING GRIDS TO FIND INFORMATION
# =============================================================================

def gen_grid(level):
    rows = 3 if level == 1 else 4
    names = random.sample(V.NAMES, rows)
    pets = random.sample(["dog", "cat", "fish", "rabbit", "hamster"], rows)
    fruits = random.sample(["apple", "banana", "grapes", "pear", "plum"], rows)
    stickers = random.sample(range(4, 40), rows)
    people = [{"name": n, "pet": p, "fruit": f, "stickers": s} for n, p, f, s in zip(names, pets, fruits, stickers)]
    if level == 1:
        header, body = "| Name | Pet | Favourite fruit |\n|---|---|---|", "\n".join(f"| {x['name']} | {x['pet']} | {x['fruit']} |" for x in people)
    else:
        header = "| Name | Pet | Favourite fruit | Stickers |\n|---|---|---|---|"
        body = "\n".join(f"| {x['name']} | {x['pet']} | {x['fruit']} | {x['stickers']} |" for x in people)
    table = header + "\n" + body
    if level == 1:
        x = random.choice(people)
        if random.random() < 0.5:
            q = choice_q(f"Use the table to answer. **Who owns the {x['pet']}?**", x["name"], [p["name"] for p in people if p is not x],
                         f"Find the row with {x['pet']} in the Pet column. The name in that row is **{x['name']}**.")
        else:
            q = choice_q(f"Use the table to answer. **Which pet does {x['name']} have?**", x["pet"], [p["pet"] for p in people if p is not x],
                         f"Find {x['name']}'s row and read across to the Pet column: **{x['pet']}**.")
    elif level == 2:
        x, y = random.sample(people, 2)
        kind = random.choice(["fruit", "stickers", "most"])
        if kind == "fruit":
            q = choice_q(f"Use the table to answer. **Which fruit does the person who owns the {x['pet']} like?**", x["fruit"],
                         [p["fruit"] for p in people if p is not x],
                         f"First find the {x['pet']} owner (**{x['name']}**), then read across to Favourite fruit: **{x['fruit']}**.")
        elif kind == "stickers":
            q = number_q(f"Use the table to answer. **How many stickers does the child who likes {x['fruit']} have?**", x["stickers"],
                         f"The child who likes {x['fruit']} is **{x['name']}**, who has **{x['stickers']}** stickers.")
        else:
            best = max(people, key=lambda p: p["stickers"])
            q = choice_q("Use the table to answer. **Who has the most stickers?**", best["name"], [p["name"] for p in people if p is not best],
                         f"The biggest number in the Stickers column is {best['stickers']}, which belongs to **{best['name']}**.")
    else:
        x, y = sorted(random.sample(people, 2), key=lambda p: -p["stickers"])
        if random.random() < 0.5:
            q = number_q(f"Use the table to answer. **How many more stickers does the child who owns the {x['pet']} have than the child "
                         f"who likes {y['fruit']}?**", x["stickers"] - y["stickers"],
                         f"The {x['pet']} owner is **{x['name']}** ({x['stickers']} stickers). The child who likes {y['fruit']} is **{y['name']}** "
                         f"({y['stickers']} stickers). {x['stickers']} − {y['stickers']} = **{x['stickers'] - y['stickers']}**.")
        else:
            q = number_q(f"Use the table to answer. **How many stickers do the owners of the {x['pet']} and the {y['pet']} have altogether?**",
                         x["stickers"] + y["stickers"],
                         f"**{x['name']}** has {x['stickers']} and **{y['name']}** has {y['stickers']}. "
                         f"{x['stickers']} + {y['stickers']} = **{x['stickers'] + y['stickers']}**.")
    q["markdown"] = table
    return q


# =============================================================================
# 17. LOGIC WORD PROBLEMS
# =============================================================================

RELATIONS = [("taller", "shorter", "tallest", "shortest"), ("older", "younger", "oldest", "youngest"),
             ("faster", "slower", "fastest", "slowest"), ("heavier", "lighter", "heaviest", "lightest")]


def gen_logic(level):
    if level < 3:
        n = 3 if level == 1 else 4
        more, less, most, least = random.choice(RELATIONS)
        order = random.sample(V.NAMES, n)  # order[0] has the most
        statements = []
        for i in range(n - 1):
            a, b = order[i], order[i + 1]
            statements.append(f"{a} is {more} than {b}." if random.random() < 0.5 else f"{b} is {less} than {a}.")
        random.shuffle(statements)
        if level == 1 or random.random() < 0.5:
            which = random.choice(["most", "least"])
            answer = order[0] if which == "most" else order[-1]
            ask = f"Who is the **{most if which == 'most' else least}**?"
        else:
            i = random.randint(1, n - 2)
            answer = order[i]
            ask = f"Who is the **{ORDINALS[i]} {most}**?"
        return choice_q(" ".join(statements) + f"\n\n{ask}", answer, [p for p in order if p != answer],
                        f"Put the children in order, from {most} to {least}: " + ", ".join(f"**{p}**" for p in order) + f". So the answer is **{answer}**.")
    kind = random.choice(["age", "sweets"])
    a, b, c = random.sample(V.NAMES, 3)
    if kind == "age":
        small, d = random.randint(3, 8), random.randint(2, 6)
        mid = small * 2
        return number_q(f"{a} is {d} years older than {b}. {b} is twice as old as {c}. {c} is {small} years old.\n\nHow old is {a}?",
                        mid + d, f"{c} is {small}. {b} is twice as old: {small} × 2 = {mid}. {a} is {d} years older than {b}: {mid} + {d} = **{mid + d}**.")
    base, extra = random.randint(5, 15), random.randint(2, 9)
    mid = base + extra
    return number_q(f"{a} has {base} sweets. {b} has {extra} more sweets than {a}. {c} has twice as many sweets as {b}.\n\nHow many sweets does {c} have?",
                    mid * 2, f"{b} has {base} + {extra} = {mid} sweets. {c} has twice as many: {mid} × 2 = **{mid * 2}**.")


# =============================================================================
# 18. ALGEBRA
# =============================================================================

def gen_algebra(level):
    v = random.choice(["n", "x", "a", "y", "p"])
    if level == 1:
        k = random.choice(["add", "sub", "mul", "double"])
        if k == "add":
            n, a = random.randint(1, 20), random.randint(2, 15)
            return number_q(f"Find the value of **{v}**:\n\n**{v} + {a} = {n + a}**", n, f"Take {a} away from both sides: {n + a} − {a} = **{n}**.")
        if k == "sub":
            a = random.randint(2, 12)
            n = random.randint(a + 1, a + 25)   # keep the right-hand side positive
            return number_q(f"Find the value of **{v}**:\n\n**{v} − {a} = {n - a}**", n, f"Add {a} to both sides: {n - a} + {a} = **{n}**.")
        if k == "mul":
            n, a = random.randint(2, 12), random.randint(2, 9)
            return number_q(f"Find the value of **{v}**:\n\n**{a} × {v} = {a * n}**", n, f"Divide both sides by {a}: {a * n} ÷ {a} = **{n}**.")
        n = random.randint(2, 20)
        return number_q(f"Find the value of **{v}**:\n\n**{v} + {v} = {2 * n}**", n, f"Two lots of {v} make {2 * n}, so {v} = {2 * n} ÷ 2 = **{n}**.")
    if level == 2:
        k = random.choice(["two", "sub", "sub2", "eval", "div"])
        n = random.randint(2, 12)
        if k == "two":
            a, b = random.randint(2, 5), random.randint(1, 9)
            return number_q(f"Find the value of **{v}**:\n\n**{a}{v} + {b} = {a * n + b}**", n,
                            f"Take {b} away from both sides: {a}{v} = {a * n}. Then divide by {a}: {a * n} ÷ {a} = **{n}**.")
        if k == "sub":
            a = random.randint(2, 5)
            b = random.randint(1, min(9, a * n - 1))   # keep the right-hand side positive
            return number_q(f"Find the value of **{v}**:\n\n**{a}{v} − {b} = {a * n - b}**", n,
                            f"Add {b} to both sides: {a}{v} = {a * n}. Then divide by {a}: {a * n} ÷ {a} = **{n}**.")
        if k == "sub2":
            a = random.randint(2, 5)
            c = random.randint(1, 9)
            return number_q(f"A number is multiplied by {a}, then {c} is added. The answer is {a * n + c}. What is the number?", n,
                            f"Undo the steps backwards: {a * n + c} − {c} = {a * n}, then {a * n} ÷ {a} = **{n}**.")
        if k == "eval":
            a, b = random.randint(2, 6), random.randint(2, 6)
            m, p = random.randint(2, 4), random.randint(1, 5)
            return number_q(f"If **a = {a}** and **b = {b}**, what is the value of **{m}a + {p}b**?", m * a + p * b,
                            f"Replace the letters with numbers: {m} × {a} + {p} × {b} = {m * a} + {p * b} = **{m * a + p * b}**.")
        a = random.randint(2, 5)
        return number_q(f"Find the value of **{v}**:\n\n**{v} ÷ {a} + 2 = {n + 2}**", n * a,
                        f"Take away 2: {n}. Then multiply by {a}: {n} × {a} = **{n * a}**.")
    k = random.choice(["sumdiff", "both", "word", "mixed"])
    if k == "sumdiff":
        a = random.randint(6, 14)
        b = random.randint(1, a - 1)
        return number_q(f"**a + b = {a + b}** and **a − b = {a - b}**.\n\nWhat is the value of **a**?", a,
                        f"Adding the two equations gives 2a = {a + b} + {a - b} = {2 * a}, so a = {2 * a} ÷ 2 = **{a}**.")
    if k == "both":
        n, a = random.randint(2, 9), random.randint(1, 6)
        return number_q(f"Find the value of **{v}**:\n\n**{v} + {v} + {v} + {a} = {v} + {2 * n + a}**", n,
                        f"Take one {v} from both sides: {v} + {v} + {a} = {2 * n + a}. Take away {a}: 2{v} = {2 * n}, so {v} = **{n}**.")
    if k == "word":
        n = random.randint(4, 15)
        a = random.randint(2, min(9, 2 * n - 1))   # keep the answer positive
        return number_q(f"I think of a number, double it, then subtract {a}. The answer is {2 * n - a}. What was my number?", n,
                        f"Undo the steps backwards: {2 * n - a} + {a} = {2 * n}, then {2 * n} ÷ 2 = **{n}**.")
    n, a, b = random.randint(3, 10), random.randint(2, 4), random.randint(1, 4)
    left_k, right_k = a + b, b
    return number_q(f"Find the value of **{v}**:\n\n**{left_k}{v} = {right_k}{v} + {a * n}**", n,
                    f"Take {right_k}{v} from both sides: {a}{v} = {a * n}. Then divide by {a}: **{v} = {n}**.")


# =============================================================================
# 19. MYSTERY NUMBER
# =============================================================================

def _is_prime(n):
    return n > 1 and all(n % d for d in range(2, int(n ** 0.5) + 1))


def gen_mystery(level):
    limit = {1: 50, 2: 100, 3: 200}[level]
    for _ in range(500):
        n = random.randint(10, limit)
        clues = [("It is **even**.", lambda x: x % 2 == 0), ("It is **odd**.", lambda x: x % 2 == 1)]
        for k in ([2, 3, 4, 5] if level == 1 else [3, 4, 5, 6, 7, 9]):
            clues.append((f"It is a **multiple of {k}**.", lambda x, k=k: x % k == 0))
        lo, hi = random.randint(1, n - 1), random.randint(n + 1, limit + 1)
        clues.append((f"It is **greater than {lo}**.", lambda x, lo=lo: x > lo))
        clues.append((f"It is **less than {hi}**.", lambda x, hi=hi: x < hi))
        clues.append((f"The **digits add up to {sum(map(int, str(n)))}**.", lambda x, s=sum(map(int, str(n))): sum(map(int, str(x))) == s))
        clues.append((f"The **units digit is {n % 10}**.", lambda x, u=n % 10: x % 10 == u))
        if n >= 10:
            clues.append((f"The **tens digit is {(n // 10) % 10}**.", lambda x, t=(n // 10) % 10: (x // 10) % 10 == t))
        if level == 3:
            clues.append(("It is a **prime number**.", _is_prime))
            clues.append(("It is a **square number**.", lambda x: int(x ** 0.5) ** 2 == x))
        true_clues = [c for c in clues if c[1](n)]
        random.shuffle(true_clues)
        chosen, candidates = [], set(range(1, limit + 1))
        for text, test in true_clues:
            new = {x for x in candidates if test(x)}
            if len(new) < len(candidates):
                chosen.append(text)
                candidates = new
            if len(candidates) == 1:
                break
        if len(candidates) == 1 and 2 <= len(chosen) <= 5 and next(iter(candidates)) == n:
            return number_q("I am thinking of a **mystery number**. Use the clues to find it.\n\n" + "\n".join(f"- {c}" for c in chosen), n,
                            "Each clue removes some numbers until only one is left. The mystery number is **" + str(n) + "**.",
                            hint=f"The number is between 1 and {limit}.")
    raise RuntimeError("mystery failed")


# =============================================================================
# TOPICS AND PAGE
# =============================================================================

TOPICS = {
    "🔀 Jumbled words (letters to make words)": gen_jumbled,
    "🟰 Same or opposite meanings": gen_meanings,
    "🚫 Find the odd word": gen_odd,
    "📶 Word stages & putting words in order": gen_stages,
    "🔢 Number sequences": gen_number_seq,
    "🔠 Letter sequences": gen_letter_seq,
    "🔤 The alphabet & alphabetical order": gen_alphabet,
    "🔐 Word codes": gen_word_code,
    "🔑 Number codes (using numbers for letters)": gen_number_code,
    "🔗 Word connections (A is to B as C is to ?)": gen_analogy_words,
    "🧩 Making new words (compound words)": gen_compound,
    "❓ Missing letters": gen_missing_letters,
    "🕵️ Find the hidden word": gen_hidden,
    "✍️ Make sense of sentences (fill in the spaces)": gen_cloze,
    "📖 Definitions & crossword clues": gen_definitions,
    "📊 Using grids to find information": gen_grid,
    "🧠 Logic word problems": gen_logic,
    "🟦 Algebra": gen_algebra,
    "🎯 Find the mystery number": gen_mystery,
}

LESSONS = [
    ("📘 How to tackle verbal reasoning",
     "Verbal reasoning tests how well you can **think with words, letters and numbers**.\n\n"
     "1. **Read the question twice.** Many mistakes happen because a word like *opposite* or *last* was missed.\n"
     "2. **Write things down.** For codes and sequences, write out the alphabet or the numbers.\n"
     "3. **Check your answer** by trying it in the question.\n"
     "4. **Use the hint and the explanation.** After checking, always open *Show Step-by-Step Explanation*. "
     "That's where the learning happens!"),
    ("📗 Handy tools",
     "- **The alphabet with numbers:** A=1, B=2, C=3 ... M=13 ... Z=26. The middle is between M and N.\n"
     "- **Reversed alphabet code:** A↔Z, B↔Y, C↔X, D↔W ...\n"
     "- **Number patterns to look for:** adding or subtracting the same amount, multiplying, differences that grow, "
     "two patterns mixed together, square numbers.\n"
     "- **Compound words:** two words joined together (sun + flower = sunflower).\n"
     "- **Algebra:** a letter stands for a number. Do the **opposite** (inverse) operation to find it."),
]


def render():
    render_reasoning(
        prefix="vr",
        heading="## 💬 Verbal Reasoning",
        caption="Word, letter and number puzzles. Nineteen topics, three levels.",
        topics=TOPICS,
        lessons=LESSONS,
    )
