"""
Command line runner for the Music Recommender Simulation.
"""

from recommender import load_songs, recommend_songs

PROFILES = {
    "pop/happy":      {"genre": "pop",   "mood": "happy",   "target_energy": 0.80},
    "lofi/focused":   {"genre": "lofi",  "mood": "focused", "target_energy": 0.40},
    "edm/energetic":  {"genre": "edm",   "mood": "energetic","target_energy": 0.95},
}


def print_recommendations(profile_name: str, user_prefs: dict, recommendations: list) -> None:
    width = 60
    print("\n" + "=" * width)
    print(f"  Profile : {profile_name}")
    print(f"  Genre   : {user_prefs['genre']}")
    print(f"  Mood    : {user_prefs['mood']}")
    print(f"  Energy  : {user_prefs['target_energy']}")
    print("=" * width)

    for rank, (song, score, explanation) in enumerate(recommendations, start=1):
        print(f"\n  #{rank}  {song['title']} — {song['artist']}")
        print(f"       Score : {score:.2f} / 4.00")
        print(f"       Genre : {song['genre']}  |  Mood: {song['mood']}  |  Energy: {song['energy']}")
        for reason in explanation.split(" | "):
            print(f"       • {reason}")

    print("\n" + "-" * width)


def main() -> None:
    songs = load_songs("data/songs.csv")

    active_profile = "pop/happy"
    user_prefs = PROFILES[active_profile]

    recommendations = recommend_songs(user_prefs, songs, k=5)
    print_recommendations(active_profile, user_prefs, recommendations)


if __name__ == "__main__":
    main()
