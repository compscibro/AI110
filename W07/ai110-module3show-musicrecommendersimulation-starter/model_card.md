# Model Card: Music Recommender Simulation

---

## 1. Model Name

**VibeFinder 1.0**

---

## 2. Goal / Task

VibeFinder suggests songs from a small catalog that match a user's current listening mood. Given three inputs — a preferred genre, a preferred mood, and a target energy level — it scores every song in the catalog and returns the top 5 best matches. It does not learn from listening history. It does not adapt over time. It simply asks: "how close is this song to what the user described?"

---

## 3. Data Used

- **Catalog size:** 18 songs (10 original starter songs + 8 added manually)
- **Features per song:** genre, mood, energy (0.0–1.0), tempo, valence, danceability, acousticness
- **Genres covered:** lofi, pop, rock, ambient, jazz, synthwave, indie pop, hip-hop, r&b, classical, edm, country, metal, folk, reggae
- **Moods covered:** chill, happy, intense, relaxed, focused, moody, sad, romantic, peaceful, energetic, nostalgic, angry, melancholic, uplifting
- **Key limit:** 13 of 15 genres appear only once. The catalog heavily favors lofi (3 songs) and to a lesser degree pop (2 songs). Most genres have no backup — if a song is unavailable, the user gets nothing from that genre.
- **What is missing:** lyrics, language, release era, instrumental vs. vocal flag, user listening history

---

## 4. Algorithm Summary

Every song gets a score between 0.0 and 4.0. The score is built from three checks:

1. **Genre match (+2.0 points):** If the song's genre matches the user's preferred genre exactly, add 2 points. Otherwise add nothing. Genre is weighted the highest because it is the hardest stylistic boundary — a jazz fan given a pop song at the right mood still notices the mismatch immediately.

2. **Mood match (+1.0 point):** If the song's mood label matches the user's preferred mood exactly, add 1 point. Otherwise add nothing.

3. **Energy proximity (+0.0 to +1.0 points):** Subtract the gap between the song's energy and the user's target energy from 1.0. A perfect energy match adds 1.0. A song that is 0.5 away adds 0.5. This is the only continuous signal — it rewards being close, not just being high or low.

The three components are added together. Songs are sorted from highest to lowest score, and the top 5 are returned with a written explanation of why each scored the way it did.

---

## 5. Observed Behavior and Biases

**Lofi users get a better experience than everyone else.**
Lofi is the only genre with three songs in the catalog. A lofi user gets meaningful ranked variety at the top of their results. A metal user, a reggae user, or a country user gets one genre match and then a list of energetically convenient but stylistically unrelated songs filling the remaining spots. The system applies the same rules to everyone but produces unequal results based on how the catalog was built.

**Gym Hero keeps appearing for happy pop users.**
"Gym Hero" is a pop song with an intense mood, not a happy one. It still ranks #2 for pop/happy users because genre is worth +2.0 and mood is only worth +1.0. With only two pop songs in the catalog, a mood mismatch is not enough to push it out of the top 5. A user who wants cheerful pop music will see an aggressive gym track near the top of every recommendation, with no explanation of why it doesn't match their mood.

**Missing genres silently fall back without warning.**
When a user asks for a genre that does not exist in the catalog (tested with "bossa nova"), the genre check never fires for any song. The system returns results based on mood and energy alone and does not tell the user that no genre match was found. The output looks exactly like a successful recommendation.

**Mood matching is all-or-nothing.**
"Focused" and "chill" describe the same low-intensity listening context but score identically to "focused" and "metal" — zero partial credit. Related moods get no benefit from closeness.

---

## 6. Evaluation Process

Six user profiles were tested:

| Profile | Genre | Mood | Energy |
|---|---|---|---|
| High-Energy Pop | pop | happy | 0.85 |
| Chill Lofi | lofi | chill | 0.38 |
| Deep Intense Rock | rock | intense | 0.92 |
| Conflicting: sad + high energy | hip-hop | sad | 0.90 |
| Ghost genre (no catalog match) | bossa nova | relaxed | 0.45 |
| Extreme low energy | ambient | peaceful | 0.01 |

For each profile, the top 5 results were reviewed and compared against intuition. The main questions asked were: does the #1 result feel correct? Does anything in slots 2–5 feel wrong? Is there a song missing that should be there?

One logic experiment was also run: genre weight was halved to +1.0 and energy weight was doubled to 0–2.0, keeping the maximum score at 4.0. Standard profiles barely changed. The extreme low energy profile flipped its #1 and #2 results, confirming that energy only becomes the dominant signal when its weight is large enough to overcome a genre match.

The biggest finding was that the system's quality scales directly with catalog depth per genre. Profiles that matched well-represented genres got useful ranked results; profiles that matched underrepresented genres got one real match followed by noise.

---

## 7. Intended Use and Non-Intended Use

**Intended use:**
This system is for classroom exploration only. It demonstrates how content-based filtering works — how a program can turn song attributes and user preferences into a number, and how ranking that number produces something that looks like a recommendation.

**Not intended for:**
- Real users making real music decisions
- Discovering new music outside a tiny pre-built catalog
- Any context where catalog bias or mood mismatches could cause harm
- Replacing streaming service recommendations, which use millions of songs, real listening data, and collaborative filtering across many users

---

## 8. Ideas for Improvement

1. **Add partial mood credit.** Build a mood similarity table that gives 0.5 points for related moods (e.g., "focused" ↔ "chill", "intense" ↔ "angry"). This would make the mood check a gradient rather than a binary switch and reduce the all-or-nothing problem.

2. **Warn the user when no genre match exists.** Before returning results, check whether any song in the catalog matches the requested genre. If none do, print a message like "No [genre] songs found — showing closest matches by mood and energy instead." This turns a silent failure into an honest one.

3. **Balance the catalog before scoring.** Weight each genre match by how rare that genre is in the catalog. A rock match should be worth slightly more than a lofi match since lofi has three songs and rock has one — otherwise the system accidentally rewards having a large genre presence.

---

## 9. Personal Reflection

The biggest learning moment in this project was seeing the difference between a system that *works* and a system that *works fairly*. VibeFinder produces correct output for every input — no crashes, no bugs, reasonable scores. But running it against six different user types revealed that "correct" does not mean "equally useful." A lofi user and a reggae user both get a ranked list of five songs, but only one of them is getting genuine recommendations. The system does not know the difference, and neither would a user looking at the output without understanding how it was built.

AI tools helped most during the design phase — thinking through weight tradeoffs, identifying edge cases before running the code, and structuring the algorithm recipe in a way that was easy to implement cleanly. The moments that required the most double-checking were the ones involving data claims. When analyzing bias, it was easy to say "lofi is over-represented" without actually counting. Running the catalog distribution check confirmed it, and the numbers (lofi: 3, everything else: 1) were more specific and honest than a general impression would have been.

What surprised me most was how much a three-rule scoring function could *feel* like a real recommender. Running the Chill Lofi profile and seeing Library Rain, Midnight Coding, and Focus Flow stack up at the top — all genuinely mellow, low-energy songs — produced a result that felt intuitively right even though the logic behind it was just addition. The "feeling" comes from the catalog design and feature labeling as much as from the algorithm itself. A well-labeled dataset makes even simple math look smart.

If this project continued, the first extension would be expanding the catalog to at least five songs per genre so that every user type gets meaningful ranked variety, not just one real match followed by fallbacks. The second would be adding an `instrumentalness` feature so that a user asking for focus music would stop getting vocal-heavy tracks just because they happen to match on energy.
