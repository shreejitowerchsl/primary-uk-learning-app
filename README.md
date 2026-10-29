# Year 4/5 Learning Adventure 🎓

An interactive Streamlit learning app for a UK Year 4/5 pupil, covering:

- **Multiplication** — 2×1, 2×2, 3×2, 3×3, and Year 4 word problems
- **Division** — short division ("bus stop" method) with quotient & remainder
- **Powers** — squares, cubes, and 4th powers
- **Word Problems** — Multiplication, Division, and two-step Mixed problems,
  each with Beginner / Intermediate / Advanced levels
- **Learn the Abacus** — Beginner → Intermediate → Advanced soroban lessons
  (Direct addition, Small Friends / 5-complement, Big Friends / 10-complement)
- **English Vocabulary** — 🌐 brand-new words from the internet (by topic and
  Year level) in flashcard and quiz modes, plus a **🔍 Search a Word** section that
  shows meanings, example sentences, similar/opposite words, pronunciation audio
  and sentence starters
- **Spelling Practice** — Year 4 and Year 5 levels: 🌐 a brand-new word each
  question (definition, sentence clue and British pronunciation audio) or the
  built-in UK word lists

Every question, answer, and worked solution is stored in `st.session_state`,
so switching tabs, changing a dropdown, or clicking "Check Answer" never
loses your current progress.

## Project structure

```
year4_learning_app/
├── app.py                      # Main entry point — run this file
├── requirements.txt
├── README.md
└── modules/
    ├── __init__.py
    ├── state.py                 # All session_state defaults, in one place
    ├── helpers.py                # Shared feedback + maths explanation helpers
    ├── web_words.py              # Internet word services (dictionary + topic words)
    ├── abacus_engine.py          # Abacus drawing + bead-move simulator
    ├── multiplication_tab.py
    ├── division_tab.py
    ├── powers_tab.py
    ├── word_problems_tab.py
    ├── abacus_tab.py
    ├── vocabulary_tab.py
    └── spelling_tab.py
```

## How the internet word feature works

The app uses two free public services. **Neither needs an API key or account.**

| Service | Used for |
|---|---|
| [Free Dictionary API](https://dictionaryapi.dev) | meanings, example sentences, phonetics, pronunciation audio |
| [Datamuse](https://www.datamuse.com/api/) | finding words related to a topic, and how common they are |

- Each new word is chosen from a topic (adventure, animals, space...) and filtered
  by length and how common it is, so **Year 4** gets friendlier words and
  **Year 5** gets trickier ones.
- Nothing is fetched until the pupil clicks a button, and results are cached for
  a while so repeat look-ups are instant.
- **If the internet or a service is unavailable, the app automatically falls back
  to the built-in word lists** and tells the pupil — it never crashes.
- Streamlit Community Cloud allows outbound internet access by default, so
  nothing extra is needed when deploying.

Things worth knowing:
- The dictionary data comes from Wiktionary, so a few definitions can be a bit
  technical or have no example sentence. The app skips obsolete/offensive-labelled
  definitions and a small blocklist of unsuitable words, but this is a basic filter —
  an adult should still supervise open word searches.
- The free services can rate-limit heavy use; if that happens the app simply
  uses the built-in lists for that question.

## Running locally

1. Make sure you have Python 3.9+ installed.
2. Install the one dependency:
   ```bash
   pip install -r requirements.txt
   ```
3. From inside the `year4_learning_app` folder, run:
   ```bash
   streamlit run app.py
   ```
4. Streamlit will open the app in your browser automatically (usually at
   `http://localhost:8501`).

## Deploying to Streamlit Community Cloud (free)

Streamlit Community Cloud deploys directly from a GitHub repository, so the
steps are:

### 1. Put the project on GitHub

1. Create a new (public or private) repository on [github.com](https://github.com),
   e.g. `year4-learning-app`.
2. Upload this whole `year4_learning_app` folder to the repository — either
   by dragging the files into GitHub's web uploader, or via the command line:
   ```bash
   cd year4_learning_app
   git init
   git add .
   git commit -m "Initial commit"
   git branch -M main
   git remote add origin https://github.com/<your-username>/year4-learning-app.git
   git push -u origin main
   ```
   Make sure `app.py`, `requirements.txt`, and the whole `modules/` folder
   (including `modules/__init__.py`) all end up in the repo root — the file
   layout on GitHub must match the structure above exactly, since `app.py`
   imports from `modules.*`.

### 2. Deploy on Streamlit Community Cloud

1. Go to **[share.streamlit.io](https://share.streamlit.io)** and sign in
   with your GitHub account (create a free account if you don't have one).
2. Click **"New app"**.
3. Choose:
   - **Repository:** `<your-username>/year4-learning-app`
   - **Branch:** `main`
   - **Main file path:** `app.py`
4. Click **"Deploy"**.

Streamlit Cloud will automatically detect `requirements.txt`, install
Streamlit, and launch the app. The first deploy usually takes 1–2 minutes.
You'll be given a public URL like:

```
https://<your-username>-year4-learning-app-app-xxxxxx.streamlit.app
```

Share that link with anyone — no installation needed on their end, it runs
in any web browser (including on phones and tablets).

### 3. Updating the app later

Any time you push a new commit to the `main` branch on GitHub, Streamlit
Community Cloud automatically redeploys the app with your changes within
a minute or two — no extra steps needed.

### Notes & troubleshooting

- **"ModuleNotFoundError: No module named 'modules'"** — this means the
  folder structure wasn't preserved when uploading to GitHub. Double-check
  that `modules/` (with all its `.py` files) sits in the same directory as
  `app.py`, at the repository root.
- **App looks fine locally but fails to deploy** — check the "Manage app"
  logs on Streamlit Cloud (bottom-right of the app page); the most common
  cause is a missing entry in `requirements.txt`, though this project only
  needs `streamlit` itself.
- Streamlit Community Cloud's free tier is intended for public, non-commercial
  apps and may sleep after inactivity — the next visitor's request wakes it
  back up automatically after a short delay.
