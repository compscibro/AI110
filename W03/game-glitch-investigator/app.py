import random
import streamlit as st
from logic_utils import get_range_for_difficulty, parse_guess, check_guess, update_score

st.set_page_config(page_title="Glitchy Guesser", page_icon="🎮")

st.title("🎮 Game Glitch Investigator")
st.caption("An AI-generated guessing game. Something was off. All bugs were solved and some new features were implemented by AI Engineer: Mohammed Abdur Rahman.")

st.sidebar.header("Settings")

difficulty = st.sidebar.selectbox(
    "Difficulty",
    ["Easy", "Normal", "Hard"],
    index=0,
)

attempt_limit_map = {
    "Easy": 8,
    "Normal": 8,
    "Hard": 8,
}
attempt_limit = attempt_limit_map[difficulty]

low, high = get_range_for_difficulty(difficulty)

st.sidebar.caption(f"Range: {low} to {high}")
st.sidebar.caption(f"Attempts allowed: {attempt_limit}")
# Placeholders filled after submit so they reflect the post-submission values
score_display = st.sidebar.empty()
attempts_display_sidebar = st.sidebar.empty()

if "secret" not in st.session_state:
    st.session_state.secret = random.randint(low, high)

if "attempts" not in st.session_state:
    st.session_state.attempts = 0

if "score" not in st.session_state:
    st.session_state.score = 0

if "status" not in st.session_state:
    st.session_state.status = "playing"

if "history" not in st.session_state:
    st.session_state.history = []

if "difficulty" not in st.session_state:
    st.session_state.difficulty = difficulty

# Reset all game state when the player switches difficulty
if st.session_state.difficulty != difficulty:
    st.session_state.difficulty = difficulty
    st.session_state.secret = random.randint(low, high)
    st.session_state.attempts = 0
    st.session_state.score = 0
    st.session_state.status = "playing"
    st.session_state.history = []
    st.session_state.show_new_game_msg = True
    st.rerun()

if st.session_state.get("show_new_game_msg"):
    st.session_state.show_new_game_msg = False
    st.success("New game started.")

with st.container():
    st.subheader("Make a guess")

    # Filled immediately so it's never empty; overwritten by submit handler after incrementing
    attempts_display = st.empty()
    attempts_display.info(
        f"Guess a number between {low} and {high}. "
        f"Attempts left: {attempt_limit - st.session_state.attempts}"
    )

    # Placeholder filled after submit so it reflects the post-submission attempt count
    progress_bar = st.empty()
    progress_bar.progress(min(st.session_state.attempts / attempt_limit, 1.0))

    with st.form("guess_form"):
        raw_guess = st.text_input(
            "Enter your guess:",
            key=f"guess_input_{difficulty}"
        )
        submit = st.form_submit_button("Submit Guess 🚀", disabled=st.session_state.status != "playing")

    col1, col2 = st.columns(2)
    with col1:
        new_game = st.button("New Game 🔁")
    with col2:
        show_hint = st.checkbox("Show hint", value=True)

if new_game:
    st.session_state.attempts = 0
    st.session_state.secret = random.randint(low, high)
    st.session_state.history = []
    st.session_state.score = 0
    st.session_state.status = "playing"
    st.session_state.show_new_game_msg = True
    st.rerun()

if st.session_state.status != "playing":
    if st.session_state.status == "won":
        st.success("You already won. Start a new game to play again.")
    else:
        st.error("Game over. Start a new game to try again.")
    st.stop()

if submit:
    ok, guess_int, err = parse_guess(raw_guess)

    if not ok:
        # Invalid input — do not count as an attempt
        attempts_display.info(
            f"Guess a number between {low} and {high}. "
            f"Attempts left: {attempt_limit - st.session_state.attempts}"
        )
        st.error(err)
    elif guess_int < low or guess_int > high:
        # Out-of-range input — remind user and do not count as an attempt
        attempts_display.info(
            f"Guess a number between {low} and {high}. "
            f"Attempts left: {attempt_limit - st.session_state.attempts}"
        )
        st.error(f"Please enter a number between {low} and {high}.")
    else:
        st.session_state.attempts += 1
        st.session_state.history.append(guess_int)
        attempts_display.info(
            f"Guess a number between {low} and {high}. "
            f"Attempts left: {attempt_limit - st.session_state.attempts}"
        )

        outcome = check_guess(guess_int, st.session_state.secret)
        hint_messages = {"Win": "🎉 Correct!", "Too High": "📉 Go LOWER!", "Too Low": "📈 Go HIGHER!"}

        if show_hint:
            st.warning(hint_messages[outcome])

        st.session_state.score = update_score(
            current_score=st.session_state.score,
            outcome=outcome,
            attempt_number=st.session_state.attempts,
        )

        if outcome == "Win":
            st.balloons()
            st.session_state.status = "won"
            st.success(
                f"You won! The secret was {st.session_state.secret}. "
                f"Final score: {st.session_state.score}"
            )
        else:
            if st.session_state.attempts >= attempt_limit:
                st.session_state.status = "lost"
                st.error(
                    f"Out of attempts! "
                    f"The secret was {st.session_state.secret}. "
                    f"Score: {st.session_state.score}"
                )
score_display.metric("Score", st.session_state.score)
attempts_display_sidebar.metric("Attempts Used", st.session_state.attempts)
progress_bar.progress(min(st.session_state.attempts / attempt_limit, 1.0))

# Colored badges for each past guess — red: too high, blue: too low, green: win
if st.session_state.history:
    st.markdown("**Guess History:**")
    badge_parts = []
    for g in st.session_state.history:
        outcome = check_guess(g, st.session_state.secret)
        if outcome == "Win":
            color = "green"
        elif outcome == "Too High":
            color = "#e53935"
        else:
            color = "#1a73e8"
        badge_parts.append(
            f'<span style="background-color:{color};color:white;'
            f'padding:3px 10px;border-radius:12px;margin:2px;display:inline-block">{g}</span>'
        )
    st.markdown(" ".join(badge_parts), unsafe_allow_html=True)

with st.expander("Developer Debug Info"):
    st.write("Secret:", st.session_state.secret)
    st.write("Attempts:", st.session_state.attempts)
    st.write("Score:", st.session_state.score)
    st.write("Difficulty:", difficulty)
    st.write("History:", st.session_state.history)

st.divider()
st.caption("Built by an AI that claims this code is production-ready. Implemented, tested, and validated by the AI Engineer, which made this code production-ready.")
