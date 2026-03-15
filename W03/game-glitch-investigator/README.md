# 🎮 Game Glitch Investigator: The Impossible Guesser

## 🚨 The Situation

You asked an AI to build a simple "Number Guessing Game" using Streamlit.
It wrote the code, ran away, and now the game is unplayable. 

- You can't win.
- The hints lie to you.
- The secret number seems to have commitment issues.

## 🛠️ Setup

1. Install dependencies: `pip install -r requirements.txt`
2. Run the broken app: `python -m streamlit run app.py`

## 🕵️‍♂️ Your Mission

1. **Play the game.** Open the "Developer Debug Info" tab in the app to see the secret number. Try to win.
2. **Find the State Bug.** Why does the secret number change every time you click "Submit"? Ask ChatGPT: *"How do I keep a variable from resetting in Streamlit when I click a button?"*
3. **Fix the Logic.** The hints ("Higher/Lower") are wrong. Fix them.
4. **Refactor & Test.** - Move the logic into `logic_utils.py`.
   - Run `pytest` in your terminal.
   - Keep fixing until all tests pass!

## 📝 Document Your Experience

**Game Purpose**
A Streamlit number guessing game where the player guesses a secret number within a limited number of attempts. Difficulty controls the range (Easy: 1–20, Normal: 1–50, Hard: 1–100). Each guess is scored — fewer attempts means a higher score.

**Top 5 Bugs Found**
1. **Secret number reset on every submit** — the secret was re-generated on every rerun instead of being stored persistently.
2. **Backwards hints** — "Too High" told the player to go higher, and "Too Low" told them to go lower — the exact opposite of correct.
3. **Attempts counter off by one** — the counter initialized at 1, so the game showed 1 attempt used before any guess was submitted.
4. **New Game button didn't fully reset** — clicking New Game kept the old history, score, and game status, so the game was broken for subsequent rounds.
5. **Progress bar one step behind** — the bar was rendered before the submit handler ran, so it always reflected the previous attempt count instead of the current one.

**Top 5 Fixes Applied**
1. Moved `secret` into `st.session_state` so it is generated once and persists across reruns.
2. Swapped the hint messages so "Too High" correctly says "Go LOWER!" and "Too Low" says "Go HIGHER!".
3. Changed the attempts initialization from `1` to `0` and moved the increment to only fire after a valid, in-range guess.
4. Updated the New Game handler to reset `history`, `score`, and `status` in addition to `attempts` and `secret`.
5. Replaced the direct `st.progress()` call with an `st.empty()` placeholder filled after the submit handler, matching the same pattern used for the attempts banner.

## 📸 Demo

<img src="tests.png" width="600"/>
<img src="winning.png" width="600"/>

## 🚀 Stretch Features
- [x] Sidebar metrics: Score and Attempts Used as prominent numbers in the sidebar.
- [x] Progress bar: Visual bar below the attempts banner showing how many attempts are used.
- [x] Colored history badges	Each past guess shown as a colored pill — red (Too High), blue (Too Low), green (Win).
- [x] Visual container	Groups the guess section for a cleaner layout boundary.
