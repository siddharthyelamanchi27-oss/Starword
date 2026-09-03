import streamlit as st
import random
import json
import requests

st.set_page_config(page_title="STARWORD: FIVE EXPLORERS", page_icon="⭐", layout="centered")

GEMINI_MODEL = "gemini-flash-latest"
GEMINI_URL = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent"

# ----------------------------------------------------------------------------
# THEME / STYLE
# ----------------------------------------------------------------------------
st.markdown("""
<style>
.stApp { background-color: #0a0a0f; }
h1, h2, h3, p, label, span, div { color: #f0f0ff; }
.big-word {
    font-size: 64px; font-weight: 800; text-align: center;
    padding: 20px; border-radius: 16px; margin: 10px 0 20px 0;
    letter-spacing: 3px;
}
.big-sentence {
    font-size: 32px; font-weight: 700; text-align: center;
    padding: 16px; border-radius: 16px; margin: 10px 0 16px 0;
}
@keyframes zapshake {
    0% { transform: translate(0,0); } 20% { transform: translate(-4px,2px); }
    40% { transform: translate(4px,-2px); } 60% { transform: translate(-3px,0); }
    80% { transform: translate(3px,1px); } 100% { transform: translate(0,0); }
}
.monster-box { text-align: center; padding: 10px 0 4px 0; }
.monster-emoji { font-size: 90px; animation: zapshake 0.4s ease-in-out; }
.hp-bar-bg {
    width: 260px; height: 16px; background: #2a2a35; border-radius: 8px;
    margin: 6px auto; overflow: hidden; border: 1px solid #444;
}
.hp-bar-fill {
    height: 100%; background: linear-gradient(90deg,#ff3050,#ff9050);
    transition: width 0.3s ease;
}
.boss-tag {
    display:inline-block; padding: 4px 12px; border-radius: 999px;
    font-size: 12px; font-weight: 800; letter-spacing: 1px; margin-bottom: 10px;
}
.story-box {
    background: #15151f; border-radius: 14px; padding: 22px; font-size: 22px;
    line-height: 1.6; margin-bottom: 16px;
}
div.stButton > button {
    font-size: 20px; font-weight: 700; border-radius: 12px; padding: 14px 10px;
    width: 100%; border: 2px solid #333;
}
</style>
""", unsafe_allow_html=True)

# ----------------------------------------------------------------------------
# GAME DATA
# ----------------------------------------------------------------------------
EXPLORERS = {
    "COMET CAT":     {"power": "STAR CLAWS",      "color": "#FF3050", "desc": "Fast and fearless — great streak bonuses."},
    "STAR GUARDIAN": {"power": "AURORA STAFF",    "color": "#00F0FF", "desc": "Steady and wise — extra energy to start."},
    "GEAR BOT":      {"power": "SPARK WRENCH",    "color": "#50FF50", "desc": "Loves gadgets — earns bonus shards."},
    "SHADOW FOX":    {"power": "MOON DAGGER",     "color": "#FF00C8", "desc": "Sneaky and quick — extra hints."},
    "NOVA DRIFTER":  {"power": "SINGULARITY ORB", "color": "#B000FF", "desc": "Calm explorer — shields against mistakes."},
}

UPGRADES = {
    "hint_power":    {"name": "Hint Beacon",   "lvl": 0, "max": 5, "desc": "Reveal a letter hint before guessing (+1 use/lvl)"},
    "shield_will":   {"name": "Iron Will",     "lvl": 0, "max": 5, "desc": "Chance to not lose energy on a wrong answer (+8%/lvl)"},
    "shard_magnet":  {"name": "Shard Magnet",  "lvl": 0, "max": 5, "desc": "Extra star shards per correct answer (+1/lvl)"},
    "streak_focus":  {"name": "Focus Streak",  "lvl": 0, "max": 5, "desc": "Bonus points for answer streaks (+10%/lvl)"},
    "vital_core":    {"name": "Vital Core",    "lvl": 0, "max": 5, "desc": "Increases max energy (+1 max/lvl)"},
}

WORD_BANK = [
    ("cat", "🐱"), ("dog", "🐶"), ("sun", "☀️"), ("moon", "🌙"), ("star", "⭐"),
    ("tree", "🌳"), ("fish", "🐟"), ("bird", "🐦"), ("ball", "⚽"), ("book", "📚"),
    ("apple", "🍎"), ("cake", "🎂"), ("hat", "🎩"), ("shoe", "👟"), ("bed", "🛏️"),
    ("house", "🏠"), ("car", "🚗"), ("boat", "⛵"), ("flower", "🌸"), ("frog", "🐸"),
    ("duck", "🦆"), ("egg", "🥚"), ("milk", "🥛"), ("rain", "🌧️"), ("snow", "❄️"),
    ("king", "👑"), ("queen", "👸"), ("dragon", "🐉"), ("robot", "🤖"), ("rocket", "🚀"),
]

MONSTERS = [
    ("Grumblin", "👾"), ("Wobble Ghost", "👻"), ("Snaggle Dragon", "🐲"),
    ("Puddle Squid", "🦑"), ("Party Yeti", "☃️"), ("Sir Snorts-a-lot", "🐗"),
    ("Glimmer Bat", "🦇"), ("Fizzle Imp", "😈"),
]

# Boss round question bank: type is grammar / vocab / rhyme / comprehension
BOSS_QUESTIONS = [
    {"type": "grammar", "prompt": "The dog ___ fast.", "options": ["run", "runs", "running"], "answer": 1},
    {"type": "grammar", "prompt": "I ___ two apples.", "options": ["has", "have", "having"], "answer": 1},
    {"type": "grammar", "prompt": "She ___ happy today.", "options": ["is", "are", "am"], "answer": 0},
    {"type": "grammar", "prompt": "We ___ playing outside.", "options": ["is", "am", "are"], "answer": 2},
    {"type": "grammar", "prompt": "The cats ___ on the bed.", "options": ["sleep", "sleeps", "sleeping"], "answer": 0},
    {"type": "grammar", "prompt": "Yesterday, I ___ to the park.", "options": ["go", "went", "going"], "answer": 1},
    {"type": "grammar", "prompt": "There ___ three books on the table.", "options": ["is", "are", "be"], "answer": 1},
    {"type": "grammar", "prompt": "He ___ his homework every day.", "options": ["do", "does", "doing"], "answer": 1},
    {"type": "vocab", "prompt": "Which word means the opposite of 'big'?", "options": ["small", "tall", "fast"], "answer": 0},
    {"type": "vocab", "prompt": "Which word means the opposite of 'happy'?", "options": ["sad", "funny", "loud"], "answer": 0},
    {"type": "vocab", "prompt": "Which word means the same as 'quick'?", "options": ["slow", "fast", "quiet"], "answer": 1},
    {"type": "vocab", "prompt": "Which word means the opposite of 'up'?", "options": ["down", "left", "big"], "answer": 0},
    {"type": "vocab", "prompt": "Which word means 'a baby dog'?", "options": ["kitten", "puppy", "cub"], "answer": 1},
    {"type": "vocab", "prompt": "Which word means the opposite of 'hot'?", "options": ["cold", "wet", "loud"], "answer": 0},
    {"type": "rhyme", "prompt": "Which word rhymes with 'cat'?", "options": ["dog", "hat", "sun"], "answer": 1},
    {"type": "rhyme", "prompt": "Which word rhymes with 'star'?", "options": ["car", "tree", "fish"], "answer": 0},
    {"type": "rhyme", "prompt": "Which word rhymes with 'sun'?", "options": ["moon", "fun", "cat"], "answer": 1},
    {"type": "rhyme", "prompt": "Which word rhymes with 'hop'?", "options": ["top", "dog", "cake"], "answer": 0},
    {"type": "rhyme", "prompt": "Which word rhymes with 'tree'?", "options": ["bee", "car", "hat"], "answer": 0},
    {"type": "comprehension", "passage": "Tom has a red ball. He likes to play with his dog in the park.",
     "prompt": "What color is Tom's ball?", "options": ["red", "blue", "green"], "answer": 0},
    {"type": "comprehension", "passage": "Lily planted a seed. She watered it every day. Soon, a flower grew.",
     "prompt": "What grew from the seed?", "options": ["A tree", "A flower", "A rock"], "answer": 1},
    {"type": "comprehension", "passage": "The sun was hot, so the children went to swim in the lake.",
     "prompt": "Why did the children go swim?", "options": ["They were bored", "The sun was hot", "It was raining"], "answer": 1},
    {"type": "comprehension", "passage": "Ben lost his shoe under the bed. He looked and looked until he found it.",
     "prompt": "Where was Ben's shoe?", "options": ["In the kitchen", "Under the bed", "In the yard"], "answer": 1},
]

STORIES = [
    {
        "title": "The Lost Star",
        "text": "Mia found a tiny star in her backyard. It was cold and could not shine. "
                "She held it gently and gave it a warm blanket. Soon, the star began to glow again.",
        "questions": [
            {"q": "Where did Mia find the star?", "options": ["In her backyard", "At school", "In a book"], "answer": 0},
            {"q": "How did Mia help the star?", "options": ["She threw it away", "She gave it a warm blanket", "She ate it"], "answer": 1},
            {"q": "What happened at the end?", "options": ["The star cried", "The star ran away", "The star began to glow"], "answer": 2},
        ],
    },
    {
        "title": "Gearbot's Big Day",
        "text": "Gearbot loved fixing things. One morning, his spaceship would not start. "
                "He checked every wire until he found a loose one. He fixed it, and the ship zoomed into space.",
        "questions": [
            {"q": "What did Gearbot love to do?", "options": ["Sing", "Fixing things", "Sleeping"], "answer": 1},
            {"q": "What was wrong with the ship?", "options": ["It had no fuel", "A loose wire", "It was too small"], "answer": 1},
            {"q": "What happened after he fixed it?", "options": ["It broke again", "It zoomed into space", "It turned pink"], "answer": 2},
        ],
    },
    {
        "title": "The Shy Fox",
        "text": "A little fox was too shy to play with the other animals. One day, a rabbit invited her to play tag. "
                "The fox smiled, said yes, and had the best day ever.",
        "questions": [
            {"q": "How did the fox feel at first?", "options": ["Shy", "Angry", "Sleepy"], "answer": 0},
            {"q": "Who invited the fox to play?", "options": ["A bird", "A rabbit", "A dog"], "answer": 1},
            {"q": "What game did they play?", "options": ["Hide and seek", "Tag", "Chess"], "answer": 1},
        ],
    },
]

READ_ALOUD_LINES = [
    "The cat sat on the mat.",
    "I can see a big red star.",
    "The dog ran to the park.",
    "We like to sing and dance.",
    "The moon glows at night.",
]

TYPE_LABELS = {
    "grammar": ("📐 GRAMMAR", "#00F0FF"),
    "vocab": ("📖 VOCABULARY", "#50FF50"),
    "rhyme": ("🎵 RHYME TIME", "#FF00C8"),
    "comprehension": ("🧠 COMPREHENSION", "#FF9050"),
}

# ----------------------------------------------------------------------------
# OPTIONAL AI QUESTION GENERATION (Google Gemini API)
# ----------------------------------------------------------------------------
def get_gemini_key():
    if hasattr(st, "secrets"):
        return st.secrets.get("GEMINI_API_KEY", None)
    return None

def generate_ai_boss_round(round_types):
    """Ask Gemini for all boss-round questions in ONE call (fast) instead of one call
    per question (slow, and what caused the earlier stall). Returns a list of dicts in
    the same shape as BOSS_QUESTIONS entries (same order as round_types), or None on
    any failure — callers should fall back to the local question bank in that case."""
    key = get_gemini_key()
    if not key:
        return None
    type_instructions = {
        "grammar": "a fill-in-the-blank grammar question (subject-verb agreement, tense, or plurals) with '___' in the sentence",
        "vocab": "a vocabulary question about a word's opposite, synonym, or simple meaning",
        "rhyme": "a question asking which word rhymes with a given simple word",
        "comprehension": "a 1-2 sentence mini story ('passage') followed by a simple comprehension question about it",
    }
    items_desc = "\n".join(
        f'{i + 1}. type="{t}": {type_instructions.get(t, type_instructions["vocab"])}'
        for i, t in enumerate(round_types)
    )
    prompt = f"""Create {len(round_types)} short quiz questions for a 7-year-old learning to read English, one for each numbered item below:
{items_desc}
Use simple, everyday, age-appropriate words only. Each question needs exactly 3 answer options with only one correct.
Respond with ONLY a raw JSON array (no markdown fences) of {len(round_types)} objects, in the same order as the list above, each matching this shape:
{{"type": "...", "prompt": "...", "passage": "..." (include only for comprehension type, omit otherwise), "options": ["...", "...", "..."], "answer": 0}}
"answer" is the 0-based index of the correct option."""
    try:
        resp = requests.post(
            GEMINI_URL,
            headers={"x-goog-api-key": key, "Content-Type": "application/json"},
            json={"contents": [{"parts": [{"text": prompt}]}]},
            timeout=20,
        )
        resp.raise_for_status()
        data = resp.json()
        text = data["candidates"][0]["content"]["parts"][0]["text"].strip()
        text = text.replace("```json", "").replace("```", "").strip()
        arr = json.loads(text)
        if isinstance(arr, list) and len(arr) == len(round_types):
            for item, t in zip(arr, round_types):
                if not all(k in item for k in ("prompt", "options", "answer")):
                    return None
                item["type"] = t
                item["ai_generated"] = True
            return arr
    except Exception:
        return None
    return None

# ----------------------------------------------------------------------------
# STATE
# ----------------------------------------------------------------------------
def init_state():
    defaults = {
        "screen": "menu",
        "explorer": None,
        "wave": 1,
        "max_energy": 5,
        "energy": 5,
        "shards": 0,
        "score": 0,
        "streak": 0,
        "queue": [],
        "q_index": 0,
        "options": [],
        "feedback": "",
        "story_idx": 0,
        "story_q_idx": 0,
        "monster_name": "",
        "monster_emoji": "",
        "monster_hp": 0,
        "monster_max_hp": 0,
        "zap": False,
        "boss_questions": [],
        "boss_index": 0,
        "boss_correct": 0,
        "boss_choice": None,
        "boss_feedback": "",
        "boss_answered": False,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_state()

def get_upg(key):
    return UPGRADES[key]["lvl"]

def reset_run():
    st.session_state.wave = 1
    st.session_state.max_energy = 5 + get_upg("vital_core")
    st.session_state.energy = st.session_state.max_energy
    st.session_state.shards = 0
    st.session_state.score = 0
    st.session_state.streak = 0

def build_wave():
    n = min(4 + st.session_state.wave, len(WORD_BANK))
    pool = random.sample(WORD_BANK, n)
    st.session_state.queue = pool
    st.session_state.q_index = 0
    st.session_state.feedback = ""
    st.session_state.zap = False
    name, emoji = random.choice(MONSTERS)
    st.session_state.monster_name = name
    st.session_state.monster_emoji = emoji
    st.session_state.monster_hp = n
    st.session_state.monster_max_hp = n
    next_question()

def next_question():
    if st.session_state.q_index >= len(st.session_state.queue):
        build_boss_round()
        st.session_state.screen = "boss"
        return
    word, emoji = st.session_state.queue[st.session_state.q_index]
    wrong = random.sample([w for w in WORD_BANK if w[0] != word], 3)
    opts = wrong + [(word, emoji)]
    random.shuffle(opts)
    st.session_state.options = opts
    st.session_state.current_word = word
    st.session_state.current_emoji = emoji

def answer_word(chosen_word, chosen_emoji):
    correct = chosen_word == st.session_state.current_word
    if correct:
        st.session_state.streak += 1
        bonus = int(st.session_state.streak * (1 + get_upg("streak_focus") * 0.1))
        gained_shards = 1 + get_upg("shard_magnet")
        st.session_state.score += 10 + bonus
        st.session_state.shards += gained_shards
        st.session_state.monster_hp = max(0, st.session_state.monster_hp - 1)
        st.session_state.zap = True
        st.session_state.feedback = f"⚡ ZAP! **{chosen_word}** {chosen_emoji} hits {st.session_state.monster_name}!  (+{gained_shards} shards)"
        st.session_state.q_index += 1
        next_question()
    else:
        shielded = random.random() < (get_upg("shield_will") * 0.08)
        if not shielded:
            st.session_state.energy -= 1
        st.session_state.streak = 0
        st.session_state.zap = False
        note = " (Iron Will protected you!)" if shielded else ""
        st.session_state.feedback = f"💨 {st.session_state.monster_name} dodges! That was **{st.session_state.current_word}**.{note}"
        if st.session_state.energy <= 0:
            st.session_state.screen = "gameover"

def buy_upgrade(key):
    lvl = UPGRADES[key]["lvl"]
    cost = 5 + lvl * 8
    if lvl < UPGRADES[key]["max"] and st.session_state.shards >= cost:
        st.session_state.shards -= cost
        UPGRADES[key]["lvl"] += 1
        if key == "vital_core":
            st.session_state.max_energy += 1
            st.session_state.energy += 1

# ----------------------------------------------------------------------------
# BOSS ROUND (5 randomized questions: grammar / vocab / rhyme / comprehension)
# ----------------------------------------------------------------------------
def build_boss_round():
    types = ["grammar", "vocab", "rhyme", "comprehension"]
    random.shuffle(types)
    extra_type = random.choice(types)
    round_types = types + [extra_type]  # 5 total, one of each + 1 random extra

    questions = None
    if get_gemini_key():
        with st.spinner("🤖 Summoning the Boss Round..."):
            questions = generate_ai_boss_round(round_types)

    if not questions:
        questions = []
        for t in round_types:
            pool = [x for x in BOSS_QUESTIONS if x["type"] == t]
            questions.append(dict(random.choice(pool)))

    random.shuffle(questions)
    st.session_state.boss_questions = questions
    st.session_state.boss_index = 0
    st.session_state.boss_correct = 0
    st.session_state.boss_choice = None
    st.session_state.boss_feedback = ""
    st.session_state.boss_answered = False

def submit_boss_answer(selected_idx):
    q = st.session_state.boss_questions[st.session_state.boss_index]
    st.session_state.boss_answered = True
    st.session_state.boss_choice = selected_idx
    if selected_idx == q["answer"]:
        st.session_state.boss_correct += 1
        gained = 5 + get_upg("shard_magnet")
        st.session_state.score += 15
        st.session_state.shards += gained
        st.session_state.boss_feedback = f"✅ Correct! +15 points, +{gained} shards"
    else:
        correct_text = q["options"][q["answer"]]
        st.session_state.boss_feedback = f"❌ Not quite — the answer was **{correct_text}**"

def boss_next():
    st.session_state.boss_index += 1
    st.session_state.boss_choice = None
    st.session_state.boss_feedback = ""
    st.session_state.boss_answered = False
    if st.session_state.boss_index >= len(st.session_state.boss_questions):
        st.session_state.screen = "shop"

# ----------------------------------------------------------------------------
# SCREENS
# ----------------------------------------------------------------------------
def hud():
    st.markdown(f"""
    <div class="hud-box">
    ⚡ ENERGY: {'❤️' * st.session_state.energy}{'🖤' * (st.session_state.max_energy - st.session_state.energy)}
    &nbsp;&nbsp;|&nbsp;&nbsp; 💎 SHARDS: {st.session_state.shards}
    &nbsp;&nbsp;|&nbsp;&nbsp; 🌊 WAVE: {st.session_state.wave}
    &nbsp;&nbsp;|&nbsp;&nbsp; 🏆 SCORE: {st.session_state.score}
    &nbsp;&nbsp;|&nbsp;&nbsp; 🔥 STREAK: {st.session_state.streak}
    </div>
    """, unsafe_allow_html=True)

def screen_menu():
    st.markdown("<h1 style='text-align:center;'>⭐ STARWORD ⭐</h1>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align:center;color:#ff00c8;'>FIVE EXPLORERS</h3>", unsafe_allow_html=True)
    st.write("")
    st.markdown("Pick your explorer to begin your reading mission:")
    cols = st.columns(len(EXPLORERS))
    for i, (name, cfg) in enumerate(EXPLORERS.items()):
        with cols[i]:
            st.markdown("<div style='text-align:center;font-size:40px;'>🚀</div>", unsafe_allow_html=True)
            st.markdown(f"<div style='text-align:center;color:{cfg['color']};font-weight:800;'>{name}</div>", unsafe_allow_html=True)
            st.caption(cfg["desc"])
            if st.button("Choose", key=f"pick_{name}"):
                st.session_state.explorer = name
                reset_run()
                build_wave()
                st.session_state.screen = "game"
                st.rerun()
    st.divider()
    if st.button("🎙️ Voice Training Chamber (practice reading aloud)"):
        st.session_state.screen = "read_aloud"
        st.rerun()
    if get_gemini_key() is None:
        st.caption("💡 Tip: add a GEMINI_API_KEY in your app's Streamlit secrets to unlock AI-generated boss questions. Works great without it too, using a built-in question bank.")

def screen_game():
    hud()
    hp_pct = int(100 * st.session_state.monster_hp / max(1, st.session_state.monster_max_hp))
    st.markdown(f"""
    <div class="monster-box">
        <div style="font-weight:800; letter-spacing:1px;">⚔️ WAVE GUARDIAN: {st.session_state.monster_name}</div>
        <div class="monster-emoji">{st.session_state.monster_emoji}</div>
        <div class="hp-bar-bg"><div class="hp-bar-fill" style="width:{hp_pct}%;"></div></div>
        <div style="font-size:13px;color:#aaa;">{st.session_state.monster_hp} / {st.session_state.monster_max_hp} HP left</div>
    </div>
    """, unsafe_allow_html=True)
    st.session_state.zap = False

    st.markdown(f"### Read the word to attack — Word {st.session_state.q_index + 1} of {len(st.session_state.queue)}")
    st.markdown(f"<div class='big-word'>{st.session_state.current_word}</div>", unsafe_allow_html=True)

    if get_upg("hint_power") > 0 and st.button("💡 Use Hint"):
        w = st.session_state.current_word
        st.info(f"It starts with **'{w[0]}'** and has {len(w)} letters.")

    st.write("Tap the picture that matches the word:")
    cols = st.columns(4)
    for i, (word, emoji) in enumerate(st.session_state.options):
        with cols[i]:
            if st.button(f"{emoji}", key=f"opt_{i}_{st.session_state.q_index}"):
                answer_word(word, emoji)
                st.rerun()

    if st.session_state.feedback:
        st.markdown(st.session_state.feedback)

def screen_boss():
    hud()
    total = len(st.session_state.boss_questions)
    idx = st.session_state.boss_index
    q = st.session_state.boss_questions[idx]
    label, color = TYPE_LABELS.get(q["type"], ("QUESTION", "#fff"))

    st.markdown(f"<div class='boss-tag' style='background:{color}22;color:{color};border:1px solid {color};'>{label}</div>", unsafe_allow_html=True)
    st.markdown(f"## 🏆 Boss Round — Question {idx + 1} of {total}")

    if q.get("passage"):
        st.markdown(f"<div class='story-box' style='font-size:20px;'>{q['passage']}</div>", unsafe_allow_html=True)

    st.markdown(f"<div class='big-sentence'>{q['prompt']}</div>", unsafe_allow_html=True)

    if not st.session_state.boss_answered:
        cols = st.columns(len(q["options"]))
        for i, opt in enumerate(q["options"]):
            with cols[i]:
                if st.button(opt, key=f"boss_opt_{idx}_{i}"):
                    submit_boss_answer(i)
                    st.rerun()
    else:
        for i, opt in enumerate(q["options"]):
            tag = ""
            if i == q["answer"]:
                tag = " ✅"
            elif i == st.session_state.boss_choice:
                tag = " ❌"
            st.write(f"- {opt}{tag}")
        st.markdown(st.session_state.boss_feedback)
        btn_label = "Next Question ➜" if idx + 1 < total else "See Boss Results ➜"
        if st.button(btn_label):
            boss_next()
            st.rerun()

def screen_shop():
    hud()
    correct = st.session_state.boss_correct
    total = len(st.session_state.boss_questions) if st.session_state.boss_questions else 5
    st.markdown(f"## 🎉 {st.session_state.monster_name} was zapped away! Boss Round: {correct}/{total} correct!")
    st.markdown("### 🛠️ Star Depot — spend your shards!")
    for key, upg in UPGRADES.items():
        cost = 5 + upg["lvl"] * 8
        c1, c2, c3 = st.columns([3, 1, 1])
        with c1:
            st.markdown(f"**{upg['name']}** (Lvl {upg['lvl']}/{upg['max']})")
            st.caption(upg["desc"])
        with c2:
            st.markdown(f"💎 {cost}" if upg["lvl"] < upg["max"] else "MAXED")
        with c3:
            if upg["lvl"] < upg["max"]:
                if st.button("Buy", key=f"buy_{key}"):
                    buy_upgrade(key)
                    st.rerun()
    st.divider()
    if st.session_state.wave % 3 == 0:
        if st.button("📖 Continue to Story Challenge ➜"):
            st.session_state.story_idx = random.randrange(len(STORIES))
            st.session_state.story_q_idx = 0
            st.session_state.screen = "story"
            st.rerun()
    else:
        if st.button("🚀 Launch Next Wave ➜"):
            st.session_state.wave += 1
            build_wave()
            st.session_state.screen = "game"
            st.rerun()

def screen_story():
    hud()
    story = STORIES[st.session_state.story_idx]
    st.markdown(f"## 📖 {story['title']}")
    st.markdown(f"<div class='story-box'>{story['text']}</div>", unsafe_allow_html=True)

    qi = st.session_state.story_q_idx
    if qi < len(story["questions"]):
        q = story["questions"][qi]
        st.markdown(f"**{q['q']}**")
        choice = st.radio("Pick one:", q["options"], key=f"story_q_{qi}", index=None)
        if st.button("Submit Answer"):
            if choice is not None:
                if q["options"].index(choice) == q["answer"]:
                    st.success("✅ Correct! +15 points, +3 shards")
                    st.session_state.score += 15
                    st.session_state.shards += 3
                else:
                    st.warning(f"Not quite — the answer was **{q['options'][q['answer']]}**")
                st.session_state.story_q_idx += 1
                st.rerun()
    else:
        st.success("🎉 Story complete!")
        if st.button("🚀 Launch Next Wave ➜"):
            st.session_state.wave += 1
            build_wave()
            st.session_state.screen = "game"
            st.rerun()

def screen_gameover():
    st.markdown("<h1 style='text-align:center;color:#ff3050;'>MISSION PAUSED</h1>", unsafe_allow_html=True)
    st.markdown(f"<h3 style='text-align:center;'>You reached Wave {st.session_state.wave} with a score of {st.session_state.score}!</h3>", unsafe_allow_html=True)
    st.balloons()
    c1, c2 = st.columns(2)
    with c1:
        if st.button("🔁 Try Again"):
            reset_run()
            build_wave()
            st.session_state.screen = "game"
            st.rerun()
    with c2:
        if st.button("🏠 Back to Menu"):
            st.session_state.screen = "menu"
            st.rerun()

def screen_read_aloud():
    import streamlit.components.v1 as components

    st.markdown("## 🎙️ Voice Training Chamber")
    st.write("Pick a line, then either just record & listen back, or let the AI Listener check your reading!")
    line = st.selectbox("Choose a line to read:", READ_ALOUD_LINES)
    st.markdown(f"<div class='big-word' style='font-size:34px;'>{line}</div>", unsafe_allow_html=True)

    st.markdown("#### 🎧 AI Listening Check (Chrome or Edge browser)")
    st.caption("Tap Start, read the sentence out loud, and it will highlight each word it heard.")
    target_json = json.dumps(line)
    html = """
    <div style="font-family:sans-serif;text-align:center;padding:10px;background:#15151f;border-radius:14px;">
      <button id="startBtn" style="font-size:18px;font-weight:700;padding:12px 24px;border-radius:10px;
        border:2px solid #00f0ff;background:#0a0a0f;color:#00f0ff;cursor:pointer;">🎤 Start Listening</button>
      <div id="status" style="margin-top:14px;color:#aaa;font-size:14px;">Tap the button and read the sentence above.</div>
      <div id="result" style="margin-top:14px;font-size:22px;font-weight:700;"></div>
      <div id="score" style="margin-top:10px;font-size:16px;color:#50ff50;"></div>
    </div>
    <script>
    const target = TARGET_JSON;
    const targetWords = target.toLowerCase().replace(/[^a-z0-9 ]/g, "").split(" ").filter(Boolean);
    const btn = document.getElementById("startBtn");
    const statusEl = document.getElementById("status");
    const resultEl = document.getElementById("result");
    const scoreEl = document.getElementById("score");
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;

    if (!SpeechRecognition) {
      statusEl.innerHTML = "⚠️ Speech recognition isn't supported in this browser. Try Chrome or Edge.";
      btn.disabled = true;
    } else {
      const recognition = new SpeechRecognition();
      recognition.lang = "en-US";
      recognition.interimResults = false;
      recognition.maxAlternatives = 1;

      btn.onclick = function() {
        statusEl.innerHTML = "🔴 Listening... read the sentence now!";
        resultEl.innerHTML = "";
        scoreEl.innerHTML = "";
        try { recognition.start(); } catch (e) {}
      };

      recognition.onresult = function(event) {
        const said = event.results[0][0].transcript;
        const saidWords = said.toLowerCase().replace(/[^a-z0-9 ]/g, "").split(" ").filter(Boolean);
        let matched = 0;
        let highlighted = targetWords.map(function(w) {
          const hit = saidWords.includes(w);
          if (hit) matched++;
          const color = hit ? "#50ff50" : "#ff3050";
          return "<span style='color:" + color + ";margin:0 4px;'>" + w + "</span>";
        }).join("");
        resultEl.innerHTML = highlighted;
        const pct = Math.round((matched / targetWords.length) * 100);
        let msg = "";
        if (pct >= 90) { msg = "🌟 Amazing reading! " + pct + "% matched"; }
        else if (pct >= 60) { msg = "👍 Good try! " + pct + "% matched"; }
        else { msg = "💪 Keep practicing! " + pct + "% matched"; }
        scoreEl.innerHTML = msg;
        statusEl.innerHTML = "Heard: \\"" + said + "\\"";
      };

      recognition.onerror = function(event) {
        statusEl.innerHTML = "⚠️ Couldn't hear that — try again (" + event.error + ")";
      };
    }
    </script>
    """
    html = html.replace("TARGET_JSON", target_json)
    components.html(html, height=230)

    st.divider()
    st.markdown("#### 🎙️ Record & Playback")
    audio = st.audio_input("Or just record yourself reading it, and listen back")
    if audio:
        st.success("Nice reading! Listen back below 👇")
        st.audio(audio)

    st.divider()
    if st.button("🏠 Back to Menu"):
        st.session_state.screen = "menu"
        st.rerun()

# ----------------------------------------------------------------------------
# ROUTER
# ----------------------------------------------------------------------------
screens = {
    "menu": screen_menu,
    "game": screen_game,
    "boss": screen_boss,
    "shop": screen_shop,
    "story": screen_story,
    "gameover": screen_gameover,
    "read_aloud": screen_read_aloud,
}
screens[st.session_state.screen]()
