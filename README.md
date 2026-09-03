# STARWORD: Five Explorers

A reading game for kids, rebuilt from your original pygame "Neon Katana" — same
five-explorer / wave / shop structure, but "combat" is replaced with word-reading
challenges, and there's a story-comprehension mode and a read-aloud practice room.

## Run it locally
```bash
pip install -r requirements.txt
streamlit run app.py
```
It'll open at http://localhost:8501

## Put it on Streamlit Community Cloud (free)
1. Create a GitHub repo and push `app.py` + `requirements.txt` to it.
2. Go to https://share.streamlit.io, sign in with GitHub.
3. Click "New app", pick your repo/branch, set the main file to `app.py`.
4. Click Deploy — you'll get a shareable link in a minute or two.

## What maps to what from your original game
| Original (Neon Katana)        | This version                          |
|--------------------------------|----------------------------------------|
| 5 classes (BEAST, GOD, ...)    | 5 explorers (COMET CAT, STAR GUARDIAN...) |
| Enemies / combat               | Words to match to pictures            |
| HP                              | Energy (hearts)                       |
| Nanoshard cells                 | Star shards                           |
| Shop / upgrade tree             | Star Depot (hint power, iron will, etc.) |
| Wave clear                      | Wave clear → shop → (every 3rd wave) story challenge |
| —                                | New: Voice Training Chamber (record & play back reading aloud) |

## Customizing for your kid
- Add/remove words + emoji in `WORD_BANK` in `app.py`.
- Add more stories (with their own questions) in `STORIES`.
- Add more sentences to read aloud in `READ_ALOUD_LINES`.
- Add more boss-round questions (grammar/vocab/rhyme/comprehension) in `BOSS_QUESTIONS`.
- Rename explorers/colors in `EXPLORERS`.

## New: Boss Round after every wave
After clearing a wave's words, your kid faces a 5-question "Boss Round" mixing
grammar, vocabulary, rhymes, and reading comprehension — randomized every time.
It works out of the box using a built-in question bank, no setup needed.

## New: AI Listening Check (optional, needs an API key)
In the Voice Training Chamber, there's now a live "AI Listening Check" that
uses your browser's built-in speech recognition (Chrome or Edge) to hear your
kid read a sentence and highlight each word it caught — no API key needed for
this part, it's all in the browser.

If you also want the Boss Round questions to be freshly AI-generated (instead
of pulled from the built-in bank) every single time, add your own Google
Gemini API key:
1. Get a free key at https://aistudio.google.com/apikey
2. In Streamlit Community Cloud, open your app → Settings → Secrets, and add:
