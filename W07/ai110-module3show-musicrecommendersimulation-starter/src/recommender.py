import csv
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass, field


@dataclass
class Song:
    id: int
    title: str
    artist: str
    genre: str
    mood: str
    energy: float
    tempo_bpm: float
    valence: float
    danceability: float
    acousticness: float
    popularity: int = 50
    release_decade: int = 2020
    instrumentalness: float = 0.5
    speechiness: float = 0.1
    mood_tags: str = ""


@dataclass
class UserProfile:
    favorite_genre: str
    favorite_mood: str
    target_energy: float
    likes_acoustic: bool
    preferred_decade: Optional[int] = None
    target_instrumentalness: float = 0.5
    preferred_mood_tags: List[str] = field(default_factory=list)
    scoring_mode: str = "genre_first"


class Recommender:
    def __init__(self, songs: List[Song]):
        self.songs = songs

    def _song_to_dict(self, song: Song) -> Dict:
        return {
            "id": song.id, "title": song.title, "artist": song.artist,
            "genre": song.genre, "mood": song.mood, "energy": song.energy,
            "tempo_bpm": song.tempo_bpm, "valence": song.valence,
            "danceability": song.danceability, "acousticness": song.acousticness,
            "popularity": song.popularity, "release_decade": song.release_decade,
            "instrumentalness": song.instrumentalness, "speechiness": song.speechiness,
            "mood_tags": song.mood_tags,
        }

    def _profile_to_dict(self, user: UserProfile) -> Dict:
        return {
            "genre": user.favorite_genre, "mood": user.favorite_mood,
            "target_energy": user.target_energy,
            "preferred_decade": user.preferred_decade,
            "preferred_mood_tags": user.preferred_mood_tags,
        }

    def recommend(self, user: UserProfile, k: int = 5) -> List[Song]:
        user_dict = self._profile_to_dict(user)
        scored = []
        for song in self.songs:
            s, _ = score_song(user_dict, self._song_to_dict(song), mode=user.scoring_mode)
            scored.append((song, s))
        scored.sort(key=lambda x: x[1], reverse=True)
        return [s for s, _ in scored[:k]]

    def explain_recommendation(self, user: UserProfile, song: Song) -> str:
        user_dict = self._profile_to_dict(user)
        _, reasons = score_song(user_dict, self._song_to_dict(song), mode=user.scoring_mode)
        return " | ".join(reasons)


def load_songs(csv_path: str) -> List[Dict]:
    """Read a CSV of songs and return a list of dicts with typed numeric fields."""
    songs = []
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            songs.append({
                "id":               int(row["id"]),
                "title":            row["title"],
                "artist":           row["artist"],
                "genre":            row["genre"],
                "mood":             row["mood"],
                "energy":           float(row["energy"]),
                "tempo_bpm":        int(row["tempo_bpm"]),
                "valence":          float(row["valence"]),
                "danceability":     float(row["danceability"]),
                "acousticness":     float(row["acousticness"]),
                "popularity":       int(row["popularity"]),
                "release_decade":   int(row["release_decade"]),
                "instrumentalness": float(row["instrumentalness"]),
                "speechiness":      float(row["speechiness"]),
                "mood_tags":        row["mood_tags"],
            })
    print(f"Loaded songs: {len(songs)}")
    return songs


def score_song(user_prefs: Dict, song: Dict, mode: str = "genre_first") -> Tuple[float, List[str]]:
    """Score one song against user preferences and return a (score, reasons) tuple.

    Modes
    -----
    genre_first   — genre +2.0 | mood +1.0 | energy 0–1.0   (default, max base 4.0)
    mood_first    — mood  +2.0 | genre +1.0 | energy 0–1.0  (max base 4.0)
    energy_focused — genre +0.5 | mood +0.5 | energy 0–3.0  (max base 4.0)

    Bonus features (same across all modes, max +1.0 total)
    -------------------------------------------------------
    popularity bonus   0–0.30  (popularity/100 * 0.30)
    decade match       +0.20 exact | +0.10 adjacent (if preferred_decade set)
    mood tag overlap   +0.25 per matching tag, capped at +0.50
    """
    score = 0.0
    reasons = []

    if mode == "mood_first":
        genre_w, mood_w, energy_scale = 1.0, 2.0, 1.0
    elif mode == "energy_focused":
        genre_w, mood_w, energy_scale = 0.5, 0.5, 3.0
    else:
        genre_w, mood_w, energy_scale = 2.0, 1.0, 1.0

    if song["genre"] == user_prefs["genre"]:
        score += genre_w
        reasons.append(f"genre match: {song['genre']} (+{genre_w:.1f})")

    if song["mood"] == user_prefs["mood"]:
        score += mood_w
        reasons.append(f"mood match: {song['mood']} (+{mood_w:.1f})")

    energy_sim = (1.0 - abs(song["energy"] - user_prefs["target_energy"])) * energy_scale
    score += energy_sim
    reasons.append(
        f"energy: {energy_sim:.2f} (song {song['energy']:.2f} vs target {user_prefs['target_energy']:.2f})"
    )

    pop_bonus = round((song.get("popularity", 50) / 100) * 0.30, 2)
    score += pop_bonus
    reasons.append(f"popularity: +{pop_bonus:.2f} ({song.get('popularity', 50)}/100)")

    preferred_decade = user_prefs.get("preferred_decade")
    if preferred_decade is not None:
        song_decade = song.get("release_decade", 2020)
        if song_decade == preferred_decade:
            score += 0.20
            reasons.append(f"decade match: {song_decade}s (+0.20)")
        elif abs(song_decade - preferred_decade) == 10:
            score += 0.10
            reasons.append(f"adjacent decade: {song_decade}s (+0.10)")

    preferred_tags = user_prefs.get("preferred_mood_tags", [])
    if preferred_tags:
        song_tags = [t.strip() for t in song.get("mood_tags", "").split(",") if t.strip()]
        overlap = [t for t in preferred_tags if t in song_tags]
        tag_bonus = min(len(overlap) * 0.25, 0.50)
        if tag_bonus > 0:
            score += tag_bonus
            reasons.append(f"mood tags {overlap}: +{tag_bonus:.2f}")

    return (score, reasons)


def recommend_songs(
    user_prefs: Dict,
    songs: List[Dict],
    k: int = 5,
    mode: str = "genre_first",
    diversity: bool = True,
) -> List[Tuple[Dict, float, str]]:
    """Score all songs, apply optional diversity penalty, and return top-k results.

    Diversity penalty
    -----------------
    After initial ranking, results are selected greedily. Each candidate is
    penalized −0.50 if its artist already appears in the accepted set and −0.30
    if its genre already appears. This prevents a single artist or genre from
    dominating the top-5 list.
    """
    scored = []
    for song in songs:
        sc, reasons = score_song(user_prefs, song, mode)
        scored.append((song, sc, reasons))

    ranked = sorted(scored, key=lambda x: x[1], reverse=True)

    if not diversity:
        return [(s, sc, " | ".join(r)) for s, sc, r in ranked[:k]]

    results = []
    seen_artists: set = set()
    seen_genres: set = set()
    remaining = list(ranked)

    while len(results) < k and remaining:
        penalized = []
        for song, sc, reasons in remaining:
            penalty, notes = 0.0, []
            if song["artist"] in seen_artists:
                penalty += 0.50
                notes.append("artist repeat −0.50")
            if song["genre"] in seen_genres:
                penalty += 0.30
                notes.append("genre repeat −0.30")
            penalized.append((song, sc - penalty, reasons, notes))

        penalized.sort(key=lambda x: x[1], reverse=True)
        song, adj_score, reasons, notes = penalized[0]

        all_reasons = list(reasons)
        if notes:
            all_reasons.append("diversity: " + ", ".join(notes))

        results.append((song, adj_score, " | ".join(all_reasons)))
        seen_artists.add(song["artist"])
        seen_genres.add(song["genre"])
        remaining = [(s, sc, r) for s, sc, r in remaining if s["id"] != song["id"]]

    return results
