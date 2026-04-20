"""
Command line runner for the Music Recommender Simulation.
Demonstrates three scoring modes and diversity penalty.
"""

import textwrap
from tabulate import tabulate
from recommender import load_songs, recommend_songs

PROFILES = {
    # --- Standard profiles ---
    "High-Energy Pop":   {"genre": "pop",       "mood": "happy",   "target_energy": 0.85},
    "Chill Lofi":        {"genre": "lofi",      "mood": "chill",   "target_energy": 0.38},
    "Deep Intense Rock": {"genre": "rock",      "mood": "intense", "target_energy": 0.92},
    # --- Edge case / adversarial profiles ---
    "Conflicting: sad + high energy": {"genre": "hip-hop",   "mood": "sad",     "target_energy": 0.90},
    "Ghost genre (no match)":         {"genre": "bossa nova","mood": "relaxed", "target_energy": 0.45},
    "Extreme low energy":             {"genre": "ambient",   "mood": "peaceful","target_energy": 0.01},
}

SCORING_MODES = ["genre_first", "mood_first", "energy_focused"]


def _wrap(text: str, width: int = 42) -> str:
    """Wrap a pipe-delimited reasons string for display in a table cell."""
    lines = text.split(" | ")
    wrapped = []
    for line in lines:
        wrapped.append(textwrap.fill(f"• {line}", width=width))
    return "\n".join(wrapped)


def print_recommendations(
    profile_name: str,
    user_prefs: dict,
    recommendations: list,
    mode: str = "genre_first",
) -> None:
    print(f"\n{'='*72}")
    print(f"  Profile : {profile_name}")
    print(f"  Mode    : {mode}")
    print(f"  Genre   : {user_prefs['genre']}  |  Mood: {user_prefs['mood']}  |  Energy: {user_prefs['target_energy']}")
    print(f"{'='*72}")

    rows = []
    for rank, (song, score, explanation) in enumerate(recommendations, start=1):
        rows.append([
            f"#{rank}",
            song["title"],
            song["artist"],
            song["genre"],
            song["mood"],
            f"{score:.2f}",
            _wrap(explanation),
        ])

    print(tabulate(
        rows,
        headers=["#", "Title", "Artist", "Genre", "Mood", "Score", "Why"],
        tablefmt="rounded_outline",
        maxcolwidths=[3, 22, 16, 11, 10, 6, 44],
    ))


def run_mode_comparison(songs: list, profile_name: str, user_prefs: dict) -> None:
    """Run one profile in all three scoring modes and print side-by-side summaries."""
    print(f"\n{'*'*72}")
    print(f"  MODE COMPARISON — {profile_name}")
    print(f"{'*'*72}")
    for mode in SCORING_MODES:
        recs = recommend_songs(user_prefs, songs, k=5, mode=mode, diversity=True)
        print_recommendations(profile_name, user_prefs, recs, mode=mode)


def main() -> None:
    songs = load_songs("data/songs.csv")

    print("\n" + "#" * 72)
    print("  SECTION 1 — All profiles  |  mode: genre_first  |  diversity: ON")
    print("#" * 72)
    for profile_name, user_prefs in PROFILES.items():
        recs = recommend_songs(user_prefs, songs, k=5, mode="genre_first", diversity=True)
        print_recommendations(profile_name, user_prefs, recs, mode="genre_first")

    print("\n" + "#" * 72)
    print("  SECTION 2 — Mode comparison on 'High-Energy Pop'")
    print("#" * 72)
    run_mode_comparison(songs, "High-Energy Pop", PROFILES["High-Energy Pop"])


if __name__ == "__main__":
    main()
