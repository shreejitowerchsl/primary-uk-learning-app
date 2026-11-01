"""
OFFLINE builder (not used when the app runs).

Re-creates modules/reasoning/verbal_generated.py. It checks every word puzzle against a full English word list so
that each one has exactly ONE correct answer.

Needs:  pip install wordfreq english-words
Run:    python tools/build_verbal_data.py
"""
import random, itertools, pprint
from collections import defaultdict
from wordfreq import zipf_frequency, top_n_list
from english_words import get_english_words_set

random.seed(2026)
web2_lower = get_english_words_set(['web2'], lower=True, alpha=True)
web2_orig = get_english_words_set(['web2'], lower=False, alpha=True)   # keeps capitals -> proper nouns excluded
top = {w for w in top_n_list('en', 250000) if w.isalpha() and w.isascii()}
BROAD = set(web2_lower) | top                                        # anything that could be a real word
BAD = {"sex","sexy","porn","nude","naked","penis","vagina","fuck","shit","bitch","bastard","slut","whore","rape",
       "cocaine","heroin","meth","nazi","damn","hell","piss","crap","ass","arse","bum","poo","wee","gay","dick",
       "cock","tit","tits","boob","drug","drugs","kill","murder","suicide","dead","death","die","hate","stupid","idiot","fat"}

def zipf(w): return zipf_frequency(w, "en")
BAD_SUB = ("alcohol", "asylum", "burial", "berlin", "london", "paris", "beer", "wine", "vodka", "cigar", "gambl", "casino", "tobacco", "corpse", "grave", "weapon", "terror", "sex", "porn", "naked", "kill", "murder", "suicide", "drug", "nazi", "slave", "bomb", "gun", "gay")
EXACT_BAD = {"lynch", "harper", "murphy", "smith", "hong", "bishop", "monk", "orthodox", "catholic", "democrat", "republican",
             "butt", "dude", "tattoo", "deadly", "buck", "marry", "sheriff", "pension", "iconic", "township", "premiere", "silicon",
             "vaccine", "police", "guilty", "fury", "guilt", "gun", "quest", "swept"}

# --- reviewed by hand: unsuitable themes, politics, brands, names, and American spellings (this is a UK app) ---
EXACT_BAD |= set('''
audit coup crazy didnt drunk dumb fraud holy jerk pussy punk prof theft toxic trump tumor ugly vinyl widow wound wreck sworn
cease civil guild petty quit absurd attack ballot bullet brazil chrome cooper creepy defeat deputy equity expose facial fiscal
female horror immune impose legacy matrix newton pledge policy potter rookie suffer tragic tribal victim wright zombie beaten
china york dating evil debt injury yeah non sub army navy
labour favor flavor harbor behavior neighbor favorite defense offense judgment aluminum program activist advocacy advocate
attorney betting bleeding bullying chronic civilian clinical colonel colonial corrupt criminal custody deficit disorder embassy
execute explicit feminine feminist genetic genocide hostage illegal infantry invasion judicial kissing lawsuit lottery massacre
massage mortgage nominee offshore pathetic petition pregnant prisoner prophet republic rhetoric robbery superman syndrome
tactical twitter violence warfare worship finland pacific intimate welfare mandate defender abuse adult
'''.split())


def clean(w):
    """Everyday lower-case word: not a name/place, nothing unsuitable."""
    return (w in web2_orig and w.islower() and w.isascii() and w.capitalize() not in web2_orig
            and w not in BAD and w not in EXACT_BAD and not any(b in w for b in BAD_SUB))
def common(w, lo=4.0): return clean(w) and zipf(w) >= lo
def valid_broad(w): return w in BROAD or zipf(w) >= 1.8

POOL = sorted(w for w in sorted(web2_orig) if clean(w) and 3 <= len(w) <= 8 and zipf(w) >= 4.2)
print("common pool:", len(POOL))

out = {}

# ---------------- 1. ANAGRAMS (unique answer) ----------------
by_letters = defaultdict(set)
for w in sorted(BROAD):
    if 4 <= len(w) <= 8:
        by_letters[''.join(sorted(w))].add(w)
cand = [w for w in sorted(web2_orig) if clean(w) and 4 <= len(w) <= 8 and 3.9 <= zipf(w) <= 5.6
        and not w.endswith(("ed", "s")) and not (w.endswith("ing") and len(w) < 7) and len(set(w)) >= 3 and len(by_letters[''.join(sorted(w))]) == 1 and ''.join(sorted(w)) != w]
buckets = {1: [w for w in cand if len(w) in (4, 5)], 2: [w for w in cand if len(w) == 6], 3: [w for w in cand if len(w) in (7, 8)]}
import os
if os.environ.get("DUMP_POOL"):
    for k, v in buckets.items():
        print(f"POOL L{k} ({len(v)}):", " ".join(sorted(v)))
out["ANAGRAMS"] = {k: sorted(random.sample(v, min(70, len(v)))) for k, v in buckets.items()}
print("anagrams:", {k: len(v) for k, v in out["ANAGRAMS"].items()}, "of", {k: len(v) for k, v in buckets.items()})

# ---------------- 2. ONE LETTER makes two words ----------------
four_five = [w for w in POOL if len(w) == 4 and zipf(w) >= 4.5 and not w.endswith(("s", "ed"))]
by_first = defaultdict(list)
for w in four_five: by_first[w[0]].append(w)
items = []
for w1 in four_five:
    L = w1[-1]
    P = w1[:-1]
    for w2 in by_first[L]:
        S = w2[1:]
        if w2 == w1 or P == S: continue
        works = [x for x in "abcdefghijklmnopqrstuvwxyz" if valid_broad(P + x) and valid_broad(x + S)]
        if works == [L]:
            items.append((P, L, S, w1, w2))
random.shuffle(items)
seen_p, seen_s, picked = defaultdict(int), defaultdict(int), []
for it in items:
    if seen_p[it[0]] < 1 and seen_s[it[2]] < 1 and it[1] not in "xzqj":
        seen_p[it[0]] += 1; seen_s[it[2]] += 1; picked.append(it)
    if len(picked) >= 90: break
out["ONE_LETTER"] = picked
print("one-letter items:", len(items), "->", len(picked))

# ---------------- 3. HIDDEN words ----------------
CATS = {
 "animal": "ant ape bat bee cat cod cow dog eel elk emu fox hen hog owl pig ram rat yak lion bear deer duck frog goat lamb mole mule seal swan toad wolf crab hawk tiger zebra horse mouse sheep camel snake".split(),
 "part of the body": "arm ear eye hip jaw leg lip rib toe chin hand knee neck nose shin palm foot heel back thumb ankle elbow heart teeth".split(),
 "colour": "red tan blue pink gold grey green black brown white".split(),
 "number": "one two six ten four five nine seven eight".split(),
}
fillers = [w for w in POOL if len(w) in (3, 4, 5, 6, 7) and zipf(w) >= 4.6]
hidden = []
for cat, words in CATS.items():
    for H in words:
        found = []
        for k in range(1, len(H)):
            head, tail = H[:k], H[k:]
            lefts = [w for w in fillers if w.endswith(head) and H not in w and len(w) >= 3]
            rights = [w for w in fillers if w.startswith(tail) and H not in w and len(w) >= 3]
            for a in lefts:
                for b in rights:
                    s = a + b
                    if s.count(H) != 1: continue
                    if any(x in s for x in words if x != H): continue
                    found.append((cat, H, a, b))
        random.shuffle(found)
        hidden.extend(found[:3])
random.shuffle(hidden)
out["HIDDEN"] = hidden
print("hidden items:", len(hidden), {c: sum(1 for h in hidden if h[0] == c) for c in CATS})
out["HIDDEN_CATS"] = CATS

# ---------------- 4. COMPOUND WORDS ----------------
FIRSTS = {
 "sun": "flower light shine set rise burn glasses stroke tan beam", "moon": "light beam shine walk stone",
 "star": "fish light ship dust board", "rain": "coat drop bow fall storm forest water", "snow": "man ball flake storm drop fall board plough",
 "wind": "mill fall screen surf sock", "thunder": "storm bolt cloud clap", "ice": "cream berg cube pack skate",
 "sea": "side shell weed gull horse food shore bed", "sand": "castle paper storm bag box pit stone",
 "fire": "work place man fly side light arm engine", "water": "fall melon proof mill wheel colour way front",
 "air": "port plane line craft bag mail field", "foot": "ball step print path note bridge wear hold",
 "hand": "bag shake book writing rail cuff ball made", "head": "line light phone band ache master lamp",
 "eye": "ball brow lash lid sight witness", "ear": "ring drum phone shot", "finger": "nail print tip",
 "tooth": "paste brush pick ache", "back": "pack yard bone ground fire hand", "arm": "chair band pit",
 "book": "case shelf mark worm shop keeper", "news": "paper agent reader stand", "key": "board hole ring stone",
 "door": "bell step mat way knob post", "cup": "board cake", "play": "ground time mate house room",
 "class": "room mate work", "home": "work made sick land page", "black": "board bird berry smith out",
 "blue": "bell berry bird print bottle", "green": "house grocer fly land", "red": "coat head wood neck breast",
 "white": "board wash", "grand": "father mother stand child parent son", "day": "light break dream time",
 "night": "time mare fall gown", "over": "coat take look flow head board hear", "under": "ground wear stand line water",
 "out": "side door line break", "side": "walk line show ways car", "butter": "fly cup milk scotch",
 "tea": "pot spoon cup bag time", "egg": "cup shell plant", "pop": "corn star", "pea": "nut cock",
 "honey": "moon comb suckle bee", "bed": "room time spread bug", "bath": "room tub robe water",
 "dog": "house fish", "cat": "walk fish nap", "horse": "shoe back power", "bird": "cage song bath seed",
 "bee": "hive keeper", "cow": "boy bell", "pig": "pen sty tail", "sheep": "dog skin", "farm": "yard house land",
 "gold": "fish smith mine", "silver": "smith ware", "rail": "way road", "road": "side work map",
 "motor": "way bike boat cycle", "post": "man box card code", "pocket": "money knife", "paper": "back clip weight work",
 "note": "book pad", "pen": "knife friend", "pencil": "case sharpener", "school": "yard boy girl bag house work master",
 "tree": "house top trunk", "flower": "pot bed", "grass": "hopper land", "wall": "paper flower", "table": "cloth spoon top",
 "lamp": "shade post light", "candle": "light stick", "shoe": "lace maker box", "cross": "word roads walk bow",
 "land": "mark slide lord scape", "mountain": "side top", "hill": "side top", "river": "bank bed side", "lake": "side",
 "camp": "fire site", "life": "boat guard time style", "sky": "light line scraper", "birth": "day mark place",
 "time": "table keeper", "week": "end day", "dust": "bin pan", "milk": "man shake", "fruit": "cake salad",
 "apple": "pie sauce", "lime": "light stone", "spider": "web man", "jelly": "fish", "shell": "fish", "work": "shop book bench", "shop": "keeper lift", "super": "market", "goal": "keeper post", "basket": "ball",
 "base": "ball", "net": "ball work", "hair": "brush cut band dryer pin", "knee": "cap", "lunch": "box time",
 "break": "fast down through", "dinner": "time", "bus": "stop", "ball": "room park point", "light": "house weight",
 "house": "work hold keeper boat", "man": "kind hole power", "pot": "hole", "port": "hole", "board": "room walk",
 "boat": "house", "fall": "out", "work": "shop book bench man", "step": "mother father ladder", "print": "out",
}
pairs = []
for a, bs in FIRSTS.items():
    for b in bs.split():
        w = a + b
        if (w in web2_lower or zipf(w) >= 2.3) and a in BROAD and b in BROAD and len(a) >= 2 and len(b) >= 2:
            pairs.append((a, b))
pairs = sorted(set(pairs))
print("verified compounds:", len(pairs), "of", sum(len(v.split()) for v in FIRSTS.values()))
PAIRSET = set(pairs)
out["COMPOUNDS"] = pairs

def is_compound(a, b): return (a, b) in PAIRSET or valid_broad(a + b) and (a + b) in BROAD
firsts = defaultdict(set); seconds = defaultdict(set)
for a, b in pairs: firsts[a].add(b); seconds[b].add(a)

# 4a. middle word: A (m) B with A+m and m+B both compounds
triples = []
for m in sorted(set(seconds) & set(firsts)):
    if zipf(m) < 3.3: continue
    for a in sorted(seconds[m]):
        for b in sorted(firsts[m]):
            if a == b or a + m == m + b: continue
            triples.append((a, m, b))
pool_words = sorted({w for p in pairs for w in p if zipf(w) >= 3.5 and len(w) <= 7})
mid = []
for a, m, b in triples:
    safe = [d for d in pool_words if d not in (a, b, m) and not (valid_broad(a + d) and valid_broad(d + b))
            and not (a + d in BROAD or d + b in BROAD)]
    if len(safe) >= 6:
        mid.append((a, m, b, random.sample(safe, 5)))
random.shuffle(mid)
out["MIDDLE_WORD"] = mid[:90]
print("middle-word triples:", len(triples), "->", len(mid[:90]))

# 4b. two lists, exactly one valid pairing
lists = []
tries = 0
plist = list(pairs)
while len(lists) < 70 and tries < 20000:
    tries += 1
    (a1, b1) = random.choice(plist)
    others_a = random.sample(sorted(firsts), 2); others_b = random.sample(sorted(seconds), 2)
    A = [a1] + [x for x in others_a if x != a1]; B = [b1] + [x for x in others_b if x != b1]
    if len(A) != 3 or len(B) != 3 or len(set(A + B)) != 6: continue
    valid = [(x, y) for x in A for y in B if (x + y) in BROAD or zipf(x + y) >= 1.8]
    if valid == [(a1, b1)]:
        random.shuffle(A); random.shuffle(B)
        lists.append((A, B, a1 + b1))
out["TWO_LISTS"] = lists
print("two-list items:", len(lists))

# 4c. one word goes with all three (after / before)
fam = []
for b, As in seconds.items():
    if len(As) >= 3 and zipf(b) >= 3.3:
        for trio in itertools.combinations(sorted(As), 3):
            fam.append(("after", list(trio), b))
for a, Bs in firsts.items():
    if len(Bs) >= 3 and zipf(a) >= 3.3:
        for trio in itertools.combinations(sorted(Bs), 3):
            fam.append(("before", list(trio), a))
random.shuffle(fam)
fam_ok = []
for direction, trio, ans in fam:
    if direction == "after":
        safe = [d for d in pool_words if d != ans and d not in trio and sum(valid_broad(t + d) for t in trio) <= 1]
    else:
        safe = [d for d in pool_words if d != ans and d not in trio and sum(valid_broad(d + t) for t in trio) <= 1]
    if len(safe) >= 6:
        fam_ok.append((direction, trio, ans, random.sample(safe, 5)))
    if len(fam_ok) >= 90: break
out["FAMILIES"] = fam_ok
print("word families:", len(fam_ok))

# ---------------- 5. ALPHABETICAL ORDER groups ----------------
alpha_pool = sorted({w for v in buckets.values() for w in v if 4 <= len(w) <= 8 and zipf(w) >= 4.2})
g1 = defaultdict(list); g2 = defaultdict(list)
for w in sorted(alpha_pool):
    g1[w[0]].append(w); g2[w[:2]].append(w)
out["ALPHA_1"] = {k: random.sample(v, min(14, len(v))) for k, v in g1.items() if len(v) >= 6}
two = {k: v for k, v in g2.items() if len(v) >= 6}
out["ALPHA_2"] = {k: random.sample(v, min(12, len(v))) for k, v in random.sample(sorted(two.items()), min(40, len(two)))}
print("alpha groups:", len(out["ALPHA_1"]), len(out["ALPHA_2"]))

# ---------------- write ----------------
with open(str(__import__("pathlib").Path(__file__).resolve().parents[1] / "modules" / "reasoning" / "verbal_generated.py"), "w") as f:
    f.write('"""\nVerified puzzle banks for the Verbal Reasoning tab.\n\nGenerated offline by checking every puzzle against a full English word list so that each one has\nexactly ONE valid answer. Do not edit by hand.\n"""\n\n')
    for k, v in out.items():
        f.write(f"{k} = " + pprint.pformat(v, width=110, compact=True) + "\n\n")
print("written")
