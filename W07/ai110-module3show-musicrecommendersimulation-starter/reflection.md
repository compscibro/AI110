# Reflection: Profile Comparisons and What They Reveal

---

## High-Energy Pop vs. Deep Intense Rock

Both profiles ask for high-energy music — pop at 0.85 and rock at 0.92 — but the results are almost completely different. The pop profile gets Sunrise City and Gym Hero at the top because genre is worth +2.0 points and there are two pop songs in the catalog. The rock profile gets Storm Runner and then falls off a cliff: the only rock song in the catalog scores 3.99, and everything else below it is just "energetically close" songs with no genre or mood connection.

This comparison reveals that the system works best when the catalog has multiple songs in the requested genre. A pop user gets real variety at the top; a rock user gets one genuine match followed by filler. The system is not equally useful for all genres — it just looks like it is because the score format is the same for everyone.

---

## Chill Lofi vs. Ghost Genre (Bossa Nova)

These two profiles both ask for low-energy, laid-back music — lofi at 0.38 and bossa nova at 0.45 — but the outcomes are completely different in quality. The lofi user gets three strong matches (Library Rain, Midnight Coding, Focus Flow) scoring between 2.96 and 3.97. The bossa nova user gets no genre matches at all because bossa nova does not exist in the catalog, so the top result is Coffee Shop Stories (jazz) at 1.92 — less than half the lofi user's top score.

This shows a hidden unfairness: users whose taste is well-represented in the catalog get a genuinely personalized list, while users whose taste is absent get a generic low-energy fallback. Both users see a ranked list of five songs and neither sees any warning. If this were a real app, the bossa nova user might think the system understands them when it is actually just finding the least-wrong option.

---

## Deep Intense Rock vs. Conflicting: Sad + High Energy

Both profiles want high-energy music (rock at 0.92, hip-hop at 0.90), but the mood signals are opposite — "intense" vs. "sad." The rock profile gets results that all feel tonally consistent: Storm Runner, Gym Hero, Bass Drop Festival, Iron Storm. Every song in the top 5 sounds like something you would hear in an action movie.

The sad + high energy profile is more interesting. Broken Crown (hip-hop, sad) wins at #1 because it matches both genre and mood. But slots 2–5 are Storm Runner, Gym Hero, Bass Drop Festival, and Iron Storm — exactly the same energetic songs as the rock profile, none of which are sad in any way. The system correctly identifies one good match and then has nothing else to offer. This is the "filter bubble" problem in practice: Broken Crown is the only sad song in the catalog with high energy, so once you move past it, the recommendations stop reflecting your mood entirely.

---

## Extreme Low Energy vs. Chill Lofi

These two profiles both ask for calm, quiet music — but the extreme low energy profile (0.01 target, ambient genre) exposes something the chill lofi profile hides. A lofi user asking for energy 0.38 gets songs that genuinely cluster around that value: Library Rain at 0.35, Midnight Coding at 0.42, Focus Flow at 0.40. The recommendations feel right because the catalog was built around that energy range.

An ambient user asking for near-silence (0.01) gets Spacewalk Thoughts at 0.28 as its best match — still 28 times the target energy. Every song in the catalog is too loud for this user, but the system shows them a ranked list anyway as if it found good matches. The scores look lower (2.73 vs. 3.97) but the format gives no signal that the results are poor in absolute terms. A real system would flag "no close matches found" rather than silently recommending the least-bad options.

---

## What the Weight Shift Experiment Taught Me

When genre weight was halved and energy weight was doubled, most standard profiles barely changed. The top song stayed the same in all six profiles. But the extreme low energy profile flipped its #1 and #2 results — Morning Sonata (classical, peaceful) overtook Spacewalk Thoughts (ambient, chill) because the heavier energy penalty punished ambient's 0.28 energy more than the genre bonus could compensate for.

This tells me that for typical users, the ranking order is driven mostly by genre — energy is just a tiebreaker. The weights only start to matter when someone's preferences are extreme or unusual. That is probably the wrong behavior for a music app: unusual listeners are exactly the ones who need the most help, not the ones the system is least equipped to serve.
