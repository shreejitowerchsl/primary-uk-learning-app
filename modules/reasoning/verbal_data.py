"""
Hand-written banks for the Verbal Reasoning tab (synonyms, opposites, odd-one-out groups,
word stages, analogies and sentence completions). The puzzle banks that depend on checking
real English words live in verbal_generated.py.
"""

# -----------------------------------------------------------------------------
# SAME MEANING groups: any two words in one group mean (nearly) the same thing.
# -----------------------------------------------------------------------------
SYNONYM_GROUPS = [
    ["big", "large", "huge", "enormous", "giant", "vast"],
    ["small", "tiny", "little", "miniature"],
    ["happy", "glad", "cheerful", "joyful", "delighted", "pleased"],
    ["sad", "unhappy", "gloomy", "miserable", "sorrowful", "glum"],
    ["fast", "quick", "rapid", "speedy", "swift"],
    ["slow", "sluggish", "leisurely", "unhurried"],
    ["angry", "furious", "cross", "annoyed", "irate", "enraged"],
    ["scared", "frightened", "afraid", "terrified", "fearful", "petrified"],
    ["clever", "smart", "intelligent", "wise", "gifted"],
    ["brave", "bold", "fearless", "courageous", "daring", "heroic"],
    ["tired", "weary", "exhausted", "sleepy", "drowsy"],
    ["begin", "start", "commence", "initiate"],
    ["finish", "complete", "conclude", "terminate"],
    ["gaze", "stare", "glance", "peep", "glimpse"],
    ["shout", "yell", "scream", "bellow", "roar", "holler"],
    ["stroll", "wander", "amble", "saunter"],
    ["sprint", "dash", "race", "bolt"],
    ["throw", "toss", "hurl", "fling", "chuck", "lob"],
    ["devour", "gobble", "munch", "consume"],
    ["cold", "chilly", "freezing", "icy", "frosty", "bitter"],
    ["hot", "boiling", "scorching", "roasting", "sweltering"],
    ["wet", "damp", "soaked", "soggy", "drenched", "moist"],
    ["dirty", "filthy", "grubby", "muddy", "grimy", "mucky"],
    ["strange", "odd", "peculiar", "unusual", "weird"],
    ["beautiful", "pretty", "lovely", "gorgeous", "attractive", "stunning"],
    ["ugly", "hideous", "unsightly", "grotesque", "repulsive"],
    ["difficult", "hard", "tough", "tricky", "challenging", "demanding"],
    ["easy", "simple", "effortless", "straightforward", "elementary"],
    ["important", "vital", "essential", "crucial", "significant"],
    ["old", "ancient", "elderly", "aged", "antique"],
    ["new", "modern", "fresh", "recent", "novel", "latest"],
    ["rich", "wealthy", "affluent", "prosperous"],
    ["poor", "penniless", "needy", "impoverished", "destitute"],
    ["friend", "pal", "mate", "companion", "buddy", "chum"],
    ["quiet", "silent", "hushed", "peaceful", "soundless"],
    ["noisy", "loud", "deafening", "booming", "thunderous"],
    ["hungry", "starving", "famished", "ravenous", "peckish"],
    ["help", "assist", "aid", "support"],
    ["choose", "select", "pick", "elect"],
    ["tidy", "neat", "orderly", "organised"],
    ["shiny", "gleaming", "glossy", "sparkling", "glittering"],
]

# -----------------------------------------------------------------------------
# OPPOSITES
# -----------------------------------------------------------------------------
ANTONYM_PAIRS = [
    ("hot", "cold"), ("big", "small"), ("fast", "slow"), ("happy", "sad"), ("hard", "soft"),
    ("early", "late"), ("full", "empty"), ("wet", "dry"), ("old", "young"), ("rich", "poor"),
    ("strong", "weak"), ("clean", "dirty"), ("noisy", "quiet"), ("thick", "thin"), ("wide", "narrow"),
    ("tall", "short"), ("near", "far"), ("deep", "shallow"), ("sharp", "blunt"), ("smooth", "rough"),
    ("sweet", "sour"), ("true", "false"), ("love", "hate"), ("buy", "sell"), ("win", "lose"),
    ("arrive", "depart"), ("accept", "refuse"), ("increase", "decrease"), ("ancient", "modern"),
    ("expand", "shrink"), ("victory", "defeat"), ("generous", "selfish"), ("polite", "rude"),
    ("brave", "cowardly"), ("always", "never"), ("above", "below"), ("inside", "outside"),
    ("forward", "backward"), ("difficult", "easy"), ("bright", "dim"), ("rapid", "gradual"),
    ("asleep", "awake"), ("careful", "careless"), ("lend", "borrow"), ("question", "answer"),
    ("guilty", "innocent"), ("simple", "complicated"), ("rare", "common"), ("float", "sink"),
    ("tight", "loose"),
]

# -----------------------------------------------------------------------------
# ODD ONE OUT: parent -> subgroup -> words.  Every word appears only once overall.
# -----------------------------------------------------------------------------
ODD_GROUPS = {
    "animals": {
        "mammals": ["dog", "cat", "horse", "cow", "lion", "rabbit", "elephant", "tiger"],
        "birds": ["eagle", "owl", "robin", "sparrow", "penguin", "parrot", "swan", "duck"],
        "fish": ["salmon", "trout", "cod", "shark", "tuna", "haddock", "herring", "mackerel"],
        "insects": ["ant", "bee", "wasp", "beetle", "fly", "ladybird", "butterfly", "moth"],
    },
    "food": {
        "fruit": ["apple", "banana", "pear", "grape", "plum", "cherry", "melon", "peach"],
        "vegetables": ["carrot", "pea", "potato", "onion", "cabbage", "leek", "turnip", "sprout"],
        "drinks": ["milk", "juice", "water", "tea", "coffee", "lemonade", "squash", "cocoa"],
        "meat": ["beef", "pork", "lamb", "ham", "bacon", "sausage", "turkey", "chicken"],
    },
    "clothes": {
        "footwear": ["sock", "shoe", "boot", "sandal", "slipper", "trainer"],
        "tops": ["shirt", "jumper", "jacket", "coat", "blouse", "cardigan"],
        "headwear": ["hat", "cap", "helmet", "beret", "bonnet", "turban"],
    },
    "transport": {
        "road": ["car", "bus", "lorry", "van", "taxi", "bicycle"],
        "water": ["boat", "ship", "ferry", "yacht", "canoe", "raft"],
        "air": ["plane", "helicopter", "jet", "glider", "balloon", "airship"],
    },
    "school": {
        "equipment": ["pencil", "pen", "ruler", "rubber", "crayon", "scissors"],
        "subjects": ["maths", "history", "geography", "music", "science", "art"],
    },
    "home": {
        "rooms": ["kitchen", "bedroom", "bathroom", "lounge", "hall", "attic"],
        "furniture": ["table", "chair", "sofa", "bed", "desk", "wardrobe"],
    },
    "nature": {
        "trees": ["oak", "ash", "elm", "pine", "beech", "willow"],
        "flowers": ["rose", "daisy", "tulip", "poppy", "lily", "daffodil"],
        "weather": ["rain", "snow", "wind", "fog", "hail", "sleet"],
    },
    "colours and shapes": {
        "colours": ["red", "blue", "green", "yellow", "purple", "pink"],
        "shapes": ["circle", "square", "triangle", "oval", "hexagon", "pentagon"],
    },
    "body": {
        "head": ["eye", "ear", "nose", "mouth", "chin", "cheek"],
        "limbs": ["arm", "leg", "hand", "foot", "knee", "elbow"],
    },
    "fun": {
        "instruments": ["piano", "guitar", "violin", "drum", "flute", "trumpet"],
        "sports": ["football", "tennis", "cricket", "rugby", "swimming", "hockey"],
    },
    "buildings and places": {
        "buildings": ["house", "school", "church", "castle", "library", "hospital"],
        "landscape": ["mountain", "valley", "river", "forest", "desert", "island"],
    },
}

# -----------------------------------------------------------------------------
# WORD STAGES: words that must go in one fixed order.
# -----------------------------------------------------------------------------
STAGES = [
    ("a butterfly's life", ["egg", "caterpillar", "chrysalis", "butterfly"]),
    ("a frog's life", ["spawn", "tadpole", "froglet", "frog"]),
    ("a plant growing", ["seed", "shoot", "bud", "flower"]),
    ("a tree growing", ["acorn", "seedling", "sapling", "tree"]),
    ("a person growing up", ["baby", "toddler", "child", "teenager", "adult"]),
    ("schooling", ["nursery", "infant", "junior", "secondary", "university"]),
    ("the day", ["dawn", "morning", "noon", "afternoon", "evening", "midnight"]),
    ("meals", ["breakfast", "lunch", "dinner", "supper"]),
    ("size, smallest to biggest", ["tiny", "small", "medium", "large", "huge"]),
    ("speed, slowest to fastest", ["crawl", "walk", "jog", "run", "sprint"]),
    ("loudness, quietest to loudest", ["whisper", "murmur", "talk", "shout", "scream"]),
    ("temperature, coldest to hottest", ["freezing", "cold", "cool", "warm", "hot", "boiling"]),
    ("rain, lightest to heaviest", ["drizzle", "shower", "rain", "downpour"]),
    ("water flowing to the sea", ["trickle", "stream", "river", "sea"]),
    ("a chick growing", ["egg", "chick", "chicken"]),
    ("units of time, shortest to longest", ["second", "minute", "hour", "day", "week", "month", "year"]),
    ("units of length, shortest to longest", ["millimetre", "centimetre", "metre", "kilometre"]),
    ("the school week", ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]),
    ("the first months of the year", ["January", "February", "March", "April", "May", "June"]),
    ("the last months of the year", ["July", "August", "September", "October", "November", "December"]),
    ("making a cake", ["mix", "pour", "bake", "cool", "ice"]),
    ("planting a seed", ["dig", "sow", "water", "wait", "pick"]),
]

# -----------------------------------------------------------------------------
# ANALOGIES:  a is to b as c is to ?   (answer, domain)
# Distractors are taken from other domains so only one answer fits.
# -----------------------------------------------------------------------------
ANALOGIES = [
    ("hand", "glove", "foot", "sock", "clothes"),
    ("bird", "nest", "bee", "hive", "homes"),
    ("dog", "kennel", "horse", "stable", "homes2"),
    ("puppy", "dog", "kitten", "cat", "young"),
    ("calf", "cow", "lamb", "sheep", "young2"),
    ("teacher", "school", "doctor", "hospital", "workplace"),
    ("chef", "kitchen", "farmer", "farm", "workplace2"),
    ("pen", "write", "knife", "cut", "tool"),
    ("brush", "paint", "spade", "dig", "tool2"),
    ("eye", "see", "ear", "hear", "senses"),
    ("nose", "smell", "tongue", "taste", "senses2"),
    ("day", "night", "summer", "winter", "opposite"),
    ("up", "down", "in", "out", "opposite2"),
    ("tall", "short", "wide", "narrow", "opposite3"),
    ("fish", "swim", "bird", "fly", "movement"),
    ("cow", "milk", "hen", "egg", "produce"),
    ("bee", "honey", "sheep", "wool", "produce2"),
    ("page", "book", "brick", "wall", "part"),
    ("finger", "hand", "toe", "foot", "part2"),
    ("leaf", "tree", "feather", "bird", "part3"),
    ("king", "queen", "prince", "princess", "gender"),
    ("man", "woman", "boy", "girl", "gender2"),
    ("uncle", "aunt", "nephew", "niece", "gender3"),
    ("author", "book", "artist", "painting", "creator"),
    ("chef", "meal", "builder", "house", "creator2"),
    ("second", "minute", "minute", "hour", "time"),
    ("ice", "cold", "fire", "hot", "property"),
    ("sugar", "sweet", "lemon", "sour", "property2"),
    ("snow", "white", "grass", "green", "colour"),
    ("kilometre", "distance", "kilogram", "weight", "measure"),
    ("thermometer", "temperature", "clock", "time", "instrument"),
    ("sofa", "sit", "bed", "sleep", "use"),
    ("lion", "roar", "dog", "bark", "sound"),
    ("cat", "purr", "duck", "quack", "sound2"),
    ("cold", "shiver", "hungry", "eat", "reaction"),
    ("seed", "plant", "egg", "chick", "grows"),
    ("sheep", "flock", "cow", "herd", "group"),
    ("fish", "shoal", "wolf", "pack", "group2"),
    ("sun", "day", "moon", "night", "sky"),
]

# -----------------------------------------------------------------------------
# SENTENCE COMPLETION (make sense of sentences / fill in the spaces)
# level 1 = pick the word that makes sense, level 2 = grammar
# -----------------------------------------------------------------------------
CLOZE = [
    (1, "A pair of ______ is used to cut paper.", "scissors", ["pillow", "saucepan", "umbrella"]),
    (1, "The sun ______ in the east.", "rises", ["swims", "cooks", "paints"]),
    (1, "We put up an umbrella when it ______.", "rains", ["sings", "tastes", "grows"]),
    (1, "The baker ______ fresh bread every morning.", "bakes", ["drinks", "flies", "reads"]),
    (1, "Please close the ______ because it is cold.", "window", ["pencil", "banana", "whisper"]),
    (1, "The ______ shone brightly in the night sky.", "stars", ["shoes", "soup", "rugs"]),
    (1, "We heard thunder, so we ______ inside.", "stayed", ["swam", "planted", "washed"]),
    (1, "The ______ flew south for the winter.", "birds", ["rocks", "tables", "cars"]),
    (1, "I need a ______ to dig the garden.", "spade", ["sponge", "sock", "saucer"]),
    (1, "She was ______ because she had lost her purse.", "upset", ["purple", "slippery", "seven"]),
    (1, "The teacher asked the class to be ______.", "quiet", ["yellow", "round", "wet"]),
    (1, "The ______ of the book was torn.", "cover", ["cheese", "whisper", "thunder"]),
    (1, "Fish live in water and breathe through ______.", "gills", ["wings", "feathers", "paws"]),
    (1, "You can see your face in a ______.", "mirror", ["blanket", "ladder", "kettle"]),
    (1, "We use a ______ to find out the time.", "clock", ["fork", "bucket", "ladder"]),
    (1, "The farmer milked the ______ in the barn.", "cow", ["chair", "bicycle", "pencil"]),
    (1, "It was so cold that the pond turned to ______.", "ice", ["toast", "sand", "wool"]),
    (1, "Dad put petrol in the ______ before the journey.", "car", ["kettle", "teapot", "wardrobe"]),
    (2, "Yesterday, we ______ to the seaside.", "went", ["go", "going", "goes"]),
    (2, "My brother is ______ than me.", "taller", ["tall", "tallest", "tallness"]),
    (2, "This is the ______ cake I have ever eaten.", "best", ["good", "better", "well"]),
    (2, "There ______ three apples in the bowl.", "are", ["is", "am", "be"]),
    (2, "He ______ his bike to school yesterday.", "rode", ["ride", "riding", "rides"]),
    (2, "Last night I ______ a strange noise.", "heard", ["hear", "hearing", "hears"]),
    (2, "He felt ______ after running the marathon.", "exhausted", ["exhaust", "exhausting", "exhausts"]),
    (2, "He ran ______ to catch the bus.", "quickly", ["quick", "quickness", "quicken"]),
    (2, "The ______ lion roared at the visitors.", "fierce", ["fiercely", "fierceness", "fiercing"]),
    (2, "She is taller ______ her brother.", "than", ["then", "that", "those"]),
    (2, "The children ______ playing in the park when it began to rain.", "were", ["was", "is", "be"]),
    (2, "Tomorrow we ______ visit the museum.", "will", ["was", "did", "had"]),
    (2, "I have ______ my homework, so I can play now.", "finished", ["finish", "finishes", "finishing"]),
    (2, "Please give the books to ______.", "them", ["they", "their", "theirs"]),
    (2, "She ______ the piano beautifully last Saturday.", "played", ["play", "plays", "playing"]),
]

NAMES = ["Anna", "Ben", "Chloe", "Dev", "Ella", "Femi", "Gus", "Hana", "Isla", "Jack", "Kai", "Lily",
         "Maya", "Noah", "Omar", "Priya", "Ravi", "Sam", "Tara", "Zoe"]
