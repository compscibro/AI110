# 🎵 Music Recommender Simulation

## Project Summary

In this project you will build and explain a small music recommender system.

Your goal is to:

- Represent songs and a user "taste profile" as data
- Design a scoring rule that turns that data into recommendations
- Evaluate what your system gets right and wrong
- Reflect on how this mirrors real world AI recommenders

Replace this paragraph with your own summary of what your version does.

---

## How The System Works

Real-world music recommenders like Spotify or YouTube use two main strategies: collaborative filtering (recommending what similar users liked) and content-based filtering (recommending songs with similar audio features). This simulation focuses on content-based filtering, which means it never needs to know what other users listened to — it matches songs directly to a user's stated preferences. Genre is weighted highest because it is the hardest stylistic boundary — a jazz fan given a pop song at the right mood still notices the mismatch immediately. Mood provides secondary intent signal, and energy acts as a continuous tiebreaker between songs that share the same genre and mood. Each song receives a score from 0.0 to 4.0, and the top-k highest-scoring songs are returned as recommendations.

### Song Features Used

| Feature | Type | Role in scoring |
|---|---|---|
| `genre` | categorical | +2.0 pts for exact match |
| `mood` | categorical | +1.0 pts for exact match |
| `energy` | float (0–1) | +0.0–1.0 pts via proximity formula |
| `tempo_bpm` | float | available for future tiebreaking |
| `valence` | float (0–1) | available for future tiebreaking |
| `danceability` | float (0–1) | available for future tiebreaking |
| `acousticness` | float (0–1) | available for future tiebreaking |

### UserProfile Fields

- `favorite_genre` — the genre the user most wants to hear
- `favorite_mood` — the emotional tone the user is seeking (e.g., chill, intense, happy)
- `target_energy` — a float (0–1) representing the desired intensity level
- `likes_acoustic` — boolean flag for future use to further filter by acoustic character

### Finalized Algorithm Recipe

Every song is scored using this formula:

```
score = 0.0
if song.genre == user.genre:   score += 2.0
if song.mood  == user.mood:    score += 1.0
score += 1.0 - abs(song.energy - user.target_energy)
```

**Maximum score: 4.0** (genre + mood + perfect energy match)

Example — user `{genre: "lofi", mood: "focused", target_energy: 0.40}`:

| Song | Genre | Mood | Energy sim | Total |
|---|---|---|---|---|
| Focus Flow (lofi, focused, 0.40) | +2.0 | +1.0 | +1.00 | **4.00** |
| Midnight Coding (lofi, chill, 0.42) | +2.0 | +0.0 | +0.98 | **2.98** |
| Library Rain (lofi, chill, 0.35) | +2.0 | +0.0 | +0.95 | **2.95** |
| Coffee Shop Stories (jazz, relaxed, 0.37) | +0.0 | +0.0 | +0.97 | **0.97** |
| Storm Runner (rock, intense, 0.91) | +0.0 | +0.0 | +0.49 | **0.49** |

### Scoring Pipeline

```
load_songs()      →  18 song dicts from CSV
                          ↓  for each song
score_song()      →  (score 0.0–4.0, reasons list)
                          ↓  collect all 18, sort descending, slice
recommend_songs() →  top-k (song, score, explanation) tuples
```

### Expected Biases

- **Genre over-dominance** — assigning 2.0 points to genre means a wrong-genre song can never outscore a same-genre song even if mood and energy are perfect. A great ambient track will always lose to a mediocre lofi track for a lofi user.
- **Mood blind spots** — exact-match only means "focused" and "chill" are treated as completely unrelated, even though in practice they occupy the same low-intensity listening space.
- **Catalog skew** — lofi has 3 songs, most other genres have 1. A lofi user gets richer recommendations than a country or reggae user by default.
- **Energy is always active** — every song earns at least some energy similarity points, which means high-energy songs like metal (0.97) still score 0.49 against a low-energy user, potentially sneaking into top-k if the catalog is small.

---

## Sample Output

Running `python src/main.py` executes all six profiles — three standard and three adversarial edge cases:

### Standard Profiles

```
Loaded songs: 18

==============================================================
  Profile : High-Energy Pop
  Genre   : pop  |  Mood: happy  |  Energy: 0.85
==============================================================

  #1  Sunrise City — Neon Echo
       Score : 3.97 / 4.00  |  Genre: pop  |  Mood: happy
       • genre match: pop (+2.0)
       • mood match: happy (+1.0)
       • energy similarity: 0.97 (song 0.82 vs target 0.85)

  #2  Gym Hero — Max Pulse
       Score : 2.92 / 4.00  |  Genre: pop  |  Mood: intense
       • genre match: pop (+2.0)
       • energy similarity: 0.92 (song 0.93 vs target 0.85)

  #3  Rooftop Lights — Indigo Parade
       Score : 1.91 / 4.00  |  Genre: indie pop  |  Mood: happy
       • mood match: happy (+1.0)
       • energy similarity: 0.91 (song 0.76 vs target 0.85)

  #4  Storm Runner — Voltline
       Score : 0.94 / 4.00  |  Genre: rock  |  Mood: intense
       • energy similarity: 0.94 (song 0.91 vs target 0.85)

  #5  Night Drive Loop — Neon Echo
       Score : 0.90 / 4.00  |  Genre: synthwave  |  Mood: moody
       • energy similarity: 0.90 (song 0.75 vs target 0.85)

--------------------------------------------------------------

==============================================================
  Profile : Chill Lofi
  Genre   : lofi  |  Mood: chill  |  Energy: 0.38
==============================================================

  #1  Library Rain — Paper Lanterns
       Score : 3.97 / 4.00  |  Genre: lofi  |  Mood: chill
       • genre match: lofi (+2.0)
       • mood match: chill (+1.0)
       • energy similarity: 0.97 (song 0.35 vs target 0.38)

  #2  Midnight Coding — LoRoom
       Score : 3.96 / 4.00  |  Genre: lofi  |  Mood: chill
       • genre match: lofi (+2.0)
       • mood match: chill (+1.0)
       • energy similarity: 0.96 (song 0.42 vs target 0.38)

  #3  Focus Flow — LoRoom
       Score : 2.98 / 4.00  |  Genre: lofi  |  Mood: focused
       • genre match: lofi (+2.0)
       • energy similarity: 0.98 (song 0.40 vs target 0.38)

  #4  Spacewalk Thoughts — Orbit Bloom
       Score : 1.90 / 4.00  |  Genre: ambient  |  Mood: chill
       • mood match: chill (+1.0)
       • energy similarity: 0.90 (song 0.28 vs target 0.38)

  #5  Coffee Shop Stories — Slow Stereo
       Score : 0.99 / 4.00  |  Genre: jazz  |  Mood: relaxed
       • energy similarity: 0.99 (song 0.37 vs target 0.38)

--------------------------------------------------------------

==============================================================
  Profile : Deep Intense Rock
  Genre   : rock  |  Mood: intense  |  Energy: 0.92
==============================================================

  #1  Storm Runner — Voltline
       Score : 3.99 / 4.00  |  Genre: rock  |  Mood: intense
       • genre match: rock (+2.0)
       • mood match: intense (+1.0)
       • energy similarity: 0.99 (song 0.91 vs target 0.92)

  #2  Gym Hero — Max Pulse
       Score : 1.99 / 4.00  |  Genre: pop  |  Mood: intense
       • mood match: intense (+1.0)
       • energy similarity: 0.99 (song 0.93 vs target 0.92)

  #3  Bass Drop Festival — HYPR
       Score : 0.96 / 4.00  |  Genre: edm  |  Mood: energetic
       • energy similarity: 0.96 (song 0.96 vs target 0.92)

  #4  Iron Storm — Vortex Null
       Score : 0.95 / 4.00  |  Genre: metal  |  Mood: angry
       • energy similarity: 0.95 (song 0.97 vs target 0.92)

  #5  Sunrise City — Neon Echo
       Score : 0.90 / 4.00  |  Genre: pop  |  Mood: happy
       • energy similarity: 0.90 (song 0.82 vs target 0.92)

--------------------------------------------------------------
```

### Adversarial / Edge Case Profiles

```
==============================================================
  Profile : Conflicting: sad + high energy
  Genre   : hip-hop  |  Mood: sad  |  Energy: 0.9
==============================================================

  #1  Broken Crown — Verse Zero
       Score : 3.75 / 4.00  |  Genre: hip-hop  |  Mood: sad
       • genre match: hip-hop (+2.0)
       • mood match: sad (+1.0)
       • energy similarity: 0.75 (song 0.65 vs target 0.90)

  #2  Storm Runner — Voltline
       Score : 0.99 / 4.00  |  Genre: rock  |  Mood: intense
       • energy similarity: 0.99 (song 0.91 vs target 0.90)

  #3  Gym Hero — Max Pulse
       Score : 0.97 / 4.00  |  Genre: pop  |  Mood: intense
       • energy similarity: 0.97 (song 0.93 vs target 0.90)

  #4  Bass Drop Festival — HYPR
       Score : 0.94 / 4.00  |  Genre: edm  |  Mood: energetic
       • energy similarity: 0.94 (song 0.96 vs target 0.90)

  #5  Iron Storm — Vortex Null
       Score : 0.93 / 4.00  |  Genre: metal  |  Mood: angry
       • energy similarity: 0.93 (song 0.97 vs target 0.90)

--------------------------------------------------------------

==============================================================
  Profile : Ghost genre (no match)
  Genre   : bossa nova  |  Mood: relaxed  |  Energy: 0.45
==============================================================

  #1  Coffee Shop Stories — Slow Stereo
       Score : 1.92 / 4.00  |  Genre: jazz  |  Mood: relaxed
       • mood match: relaxed (+1.0)
       • energy similarity: 0.92 (song 0.37 vs target 0.45)

  #2  Dusty Road Home — The Hollow Pines
       Score : 1.00 / 4.00  |  Genre: country  |  Mood: nostalgic
       • energy similarity: 1.00 (song 0.45 vs target 0.45)

  #3  Midnight Coding — LoRoom
       Score : 0.97 / 4.00  |  Genre: lofi  |  Mood: chill
       • energy similarity: 0.97 (song 0.42 vs target 0.45)

  #4  Focus Flow — LoRoom
       Score : 0.95 / 4.00  |  Genre: lofi  |  Mood: focused
       • energy similarity: 0.95 (song 0.40 vs target 0.45)

  #5  Library Rain — Paper Lanterns
       Score : 0.90 / 4.00  |  Genre: lofi  |  Mood: chill
       • energy similarity: 0.90 (song 0.35 vs target 0.45)

--------------------------------------------------------------

==============================================================
  Profile : Extreme low energy
  Genre   : ambient  |  Mood: peaceful  |  Energy: 0.01
==============================================================

  #1  Spacewalk Thoughts — Orbit Bloom
       Score : 2.73 / 4.00  |  Genre: ambient  |  Mood: chill
       • genre match: ambient (+2.0)
       • energy similarity: 0.73 (song 0.28 vs target 0.01)

  #2  Morning Sonata — Clara Voss
       Score : 1.81 / 4.00  |  Genre: classical  |  Mood: peaceful
       • mood match: peaceful (+1.0)
       • energy similarity: 0.81 (song 0.20 vs target 0.01)

  #3  Wildflower Lullaby — Fern & Glass
       Score : 0.71 / 4.00  |  Genre: folk  |  Mood: melancholic
       • energy similarity: 0.71 (song 0.30 vs target 0.01)

  #4  Library Rain — Paper Lanterns
       Score : 0.66 / 4.00  |  Genre: lofi  |  Mood: chill
       • energy similarity: 0.66 (song 0.35 vs target 0.01)

  #5  Coffee Shop Stories — Slow Stereo
       Score : 0.64 / 4.00  |  Genre: jazz  |  Mood: relaxed
       • energy similarity: 0.64 (song 0.37 vs target 0.01)

--------------------------------------------------------------
```

---

## Getting Started

### Setup

1. Create a virtual environment (optional but recommended):

   ```bash
   python -m venv .venv
   source .venv/bin/activate      # Mac or Linux
   .venv\Scripts\activate         # Windows

2. Install dependencies

```bash
pip install -r requirements.txt
```

3. Run the app:

```bash
python -m src.main
```

### Running Tests

Run the starter tests with:

```bash
pytest
```

You can add more tests in `tests/test_recommender.py`.

---

## Experiments You Tried

Use this section to document the experiments you ran. For example:

- What happened when you changed the weight on genre from 2.0 to 0.5
- What happened when you added tempo or valence to the score
- How did your system behave for different types of users

---

## Limitations and Risks

Summarize some limitations of your recommender.

Examples:

- It only works on a tiny catalog
- It does not understand lyrics or language
- It might over favor one genre or mood

You will go deeper on this in your model card.

---

## Reflection

Read and complete `model_card.md`:

[**Model Card**](model_card.md)

Write 1 to 2 paragraphs here about what you learned:

- about how recommenders turn data into predictions
- about where bias or unfairness could show up in systems like this


---

## 7. `model_card_template.md`

Combines reflection and model card framing from the Module 3 guidance. :contentReference[oaicite:2]{index=2}  

```markdown
# 🎧 Model Card - Music Recommender Simulation

## 1. Model Name

Give your recommender a name, for example:

> VibeFinder 1.0

---

## 2. Intended Use

- What is this system trying to do
- Who is it for

Example:

> This model suggests 3 to 5 songs from a small catalog based on a user's preferred genre, mood, and energy level. It is for classroom exploration only, not for real users.

---

## 3. How It Works (Short Explanation)

Describe your scoring logic in plain language.

- What features of each song does it consider
- What information about the user does it use
- How does it turn those into a number

Try to avoid code in this section, treat it like an explanation to a non programmer.

---

## 4. Data

Describe your dataset.

- How many songs are in `data/songs.csv`
- Did you add or remove any songs
- What kinds of genres or moods are represented
- Whose taste does this data mostly reflect

---

## 5. Strengths

Where does your recommender work well

You can think about:
- Situations where the top results "felt right"
- Particular user profiles it served well
- Simplicity or transparency benefits

---

## 6. Limitations and Bias

Where does your recommender struggle

Some prompts:
- Does it ignore some genres or moods
- Does it treat all users as if they have the same taste shape
- Is it biased toward high energy or one genre by default
- How could this be unfair if used in a real product

---

## 7. Evaluation

How did you check your system

Examples:
- You tried multiple user profiles and wrote down whether the results matched your expectations
- You compared your simulation to what a real app like Spotify or YouTube tends to recommend
- You wrote tests for your scoring logic

You do not need a numeric metric, but if you used one, explain what it measures.

---

## 8. Future Work

If you had more time, how would you improve this recommender

Examples:

- Add support for multiple users and "group vibe" recommendations
- Balance diversity of songs instead of always picking the closest match
- Use more features, like tempo ranges or lyric themes

---

## 9. Personal Reflection

A few sentences about what you learned:

- What surprised you about how your system behaved
- How did building this change how you think about real music recommenders
- Where do you think human judgment still matters, even if the model seems "smart"

