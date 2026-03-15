from logic_utils import check_guess, parse_guess, get_range_for_difficulty, update_score


# --- check_guess ---

def test_winning_guess():
    result = check_guess(50, 50)
    assert result == "Win"

def test_guess_too_high():
    result = check_guess(60, 50)
    assert result == "Too High"

def test_guess_too_low():
    result = check_guess(40, 50)
    assert result == "Too Low"

def test_check_guess_boundary_low():
    # Guess equals the lowest possible value and is still below secret
    result = check_guess(1, 2)
    assert result == "Too Low"

def test_check_guess_boundary_high():
    # Guess equals the highest possible value and is still above secret
    result = check_guess(100, 99)
    assert result == "Too High"


# --- parse_guess ---

def test_parse_guess_valid_integer():
    ok, value, err = parse_guess("42")
    assert ok is True
    assert value == 42
    assert err is None

def test_parse_guess_valid_float():
    # Floats like "5.0" should be accepted and truncated to int
    ok, value, err = parse_guess("5.0")
    assert ok is True
    assert value == 5
    assert err is None

def test_parse_guess_truncates_decimal():
    # Decimal part is truncated, not rounded
    ok, value, err = parse_guess("7.9")
    assert ok is True
    assert value == 7

def test_parse_guess_empty_string():
    ok, value, err = parse_guess("")
    assert ok is False
    assert value is None
    assert err == "Enter a guess."

def test_parse_guess_none():
    ok, value, err = parse_guess(None)
    assert ok is False
    assert value is None
    assert err == "Enter a guess."

def test_parse_guess_non_numeric():
    ok, value, err = parse_guess("abc")
    assert ok is False
    assert value is None
    assert err == "That is not a number."

def test_parse_guess_negative_number():
    # Negative numbers parse successfully; game logic handles range separately
    ok, value, err = parse_guess("-3")
    assert ok is True
    assert value == -3


# --- get_range_for_difficulty ---

def test_range_easy():
    low, high = get_range_for_difficulty("Easy")
    assert low == 1
    assert high == 20

def test_range_normal():
    low, high = get_range_for_difficulty("Normal")
    assert low == 1
    assert high == 50

def test_range_hard():
    low, high = get_range_for_difficulty("Hard")
    assert low == 1
    assert high == 100

def test_range_unknown_defaults_to_normal():
    # Any unrecognized difficulty falls back to the Normal range
    low, high = get_range_for_difficulty("Unknown")
    assert low == 1
    assert high == 50


# --- update_score ---

def test_score_win_first_attempt():
    # 100 - 10 * 1 = 90
    result = update_score(0, "Win", 1)
    assert result == 90

def test_score_win_fifth_attempt():
    # 100 - 10 * 5 = 50
    result = update_score(0, "Win", 5)
    assert result == 50

def test_score_win_floor():
    # Points floor at 10 when attempt number is high enough
    result = update_score(0, "Win", 10)
    assert result == 10

def test_score_win_accumulates():
    # Score adds to existing points, not reset to zero
    result = update_score(50, "Win", 1)
    assert result == 140

def test_score_too_high_deducts():
    result = update_score(20, "Too High", 1)
    assert result == 15

def test_score_too_low_deducts():
    result = update_score(20, "Too Low", 1)
    assert result == 15

def test_score_unknown_outcome_unchanged():
    # Unrecognized outcome should leave score unchanged
    result = update_score(20, "Unknown", 1)
    assert result == 20


# --- edge cases and rare events ---

def test_check_guess_same_value_at_boundary():
    # Both guess and secret at the lowest possible value
    assert check_guess(1, 1) == "Win"

def test_check_guess_large_numbers():
    result = check_guess(999999, 1)
    assert result == "Too High"

def test_parse_guess_zero():
    # Zero is a valid integer input
    ok, value, err = parse_guess("0")
    assert ok is True
    assert value == 0

def test_parse_guess_whitespace_only():
    # Whitespace alone is not a valid number
    ok, value, err = parse_guess("   ")
    assert ok is False
    assert err == "That is not a number."

def test_parse_guess_special_characters():
    ok, value, err = parse_guess("5!")
    assert ok is False
    assert err == "That is not a number."

def test_parse_guess_just_decimal_point():
    # A lone "." has no integer value
    ok, value, err = parse_guess(".")
    assert ok is False
    assert err == "That is not a number."

def test_parse_guess_negative_float():
    # Negative floats truncate toward zero
    ok, value, err = parse_guess("-5.9")
    assert ok is True
    assert value == -5

def test_range_case_sensitive():
    # Lowercase "easy" is not a recognized difficulty — falls back to default
    low, high = get_range_for_difficulty("easy")
    assert low == 1
    assert high == 50

def test_score_win_exactly_at_floor_boundary():
    # Attempt 9: 100 - 10*9 = 10, exactly at the floor — should not be reduced further
    result = update_score(0, "Win", 9)
    assert result == 10

def test_score_win_beyond_floor():
    # Attempt 11: 100 - 10*11 = -10, clamped to floor of 10
    result = update_score(0, "Win", 11)
    assert result == 10

def test_score_starts_negative():
    # Score can go negative and still accumulate correctly
    result = update_score(-20, "Too Low", 1)
    assert result == -25

def test_score_win_from_negative():
    result = update_score(-30, "Win", 1)
    assert result == 60  # -30 + 90

def test_parse_guess_scientific_notation():
    # "1e5" has no "." so int("1e5") raises ValueError — not a valid guess
    ok, value, err = parse_guess("1e5")
    assert ok is False
    assert err == "That is not a number."

def test_parse_guess_multiple_decimal_points():
    # "5.5.5" is not a valid float
    ok, value, err = parse_guess("5.5.5")
    assert ok is False
    assert err == "That is not a number."

def test_parse_guess_leading_spaces_with_number():
    # Python's int() strips surrounding whitespace, so " 5 " parses successfully
    ok, value, err = parse_guess(" 5 ")
    assert ok is True
    assert value == 5

def test_parse_guess_very_large_number():
    ok, value, err = parse_guess("999999999")
    assert ok is True
    assert value == 999999999

def test_check_guess_win_at_upper_boundary():
    # Secret at the top of Easy range
    assert check_guess(20, 20) == "Win"

def test_check_guess_win_at_lower_boundary():
    # Secret at the bottom of any range
    assert check_guess(1, 1) == "Win"

def test_score_win_attempt_zero():
    # Attempt 0 (hypothetical edge): 100 - 10*0 = 100
    result = update_score(0, "Win", 0)
    assert result == 100

def test_score_accumulates_across_multiple_wrong_guesses():
    # Simulates 3 consecutive Too Low guesses
    score = 0
    score = update_score(score, "Too Low", 1)
    score = update_score(score, "Too Low", 2)
    score = update_score(score, "Too Low", 3)
    assert score == -15


# --- check_guess: exhaustive coverage ---

def test_check_guess_one_below_secret():
    # Guess is exactly one less than the secret
    assert check_guess(4, 5) == "Too Low"

def test_check_guess_one_above_secret():
    # Guess is exactly one more than the secret
    assert check_guess(6, 5) == "Too High"

def test_check_guess_zero_equals_zero():
    assert check_guess(0, 0) == "Win"

def test_check_guess_negative_guess_positive_secret():
    assert check_guess(-1, 5) == "Too Low"

def test_check_guess_large_equal_numbers():
    assert check_guess(999999, 999999) == "Win"


# --- parse_guess: exhaustive coverage ---

def test_parse_guess_leading_plus_sign():
    # Python's int() accepts a leading "+", so "+5" is a valid guess
    ok, value, err = parse_guess("+5")
    assert ok is True
    assert value == 5

def test_parse_guess_just_plus_sign():
    ok, value, err = parse_guess("+")
    assert ok is False
    assert err == "That is not a number."

def test_parse_guess_just_minus_sign():
    ok, value, err = parse_guess("-")
    assert ok is False
    assert err == "That is not a number."

def test_parse_guess_trailing_dot():
    # "1." has "." so uses float path — float("1.") = 1.0 → int 1
    ok, value, err = parse_guess("1.")
    assert ok is True
    assert value == 1

def test_parse_guess_leading_zeros():
    # int("007") = 7 in Python 3 (no octal interpretation for int())
    ok, value, err = parse_guess("007")
    assert ok is True
    assert value == 7

def test_parse_guess_comma_thousands_separator():
    # Commas are not valid in Python int() or float()
    ok, value, err = parse_guess("1,000")
    assert ok is False
    assert err == "That is not a number."

def test_parse_guess_mixed_letters_and_numbers():
    ok, value, err = parse_guess("12abc")
    assert ok is False
    assert err == "That is not a number."

def test_parse_guess_float_scientific_notation():
    # "1.0e5" has "." so uses float path — float("1.0e5") = 100000.0 → int 100000
    ok, value, err = parse_guess("1.0e5")
    assert ok is True
    assert value == 100000


# --- get_range_for_difficulty: exhaustive coverage ---

def test_range_empty_string():
    low, high = get_range_for_difficulty("")
    assert low == 1
    assert high == 50

def test_range_none_input():
    # None does not equal any known difficulty string — falls back to Normal range
    low, high = get_range_for_difficulty(None)
    assert low == 1
    assert high == 50

def test_range_all_caps_easy():
    low, high = get_range_for_difficulty("EASY")
    assert low == 1
    assert high == 50

def test_range_all_caps_hard():
    low, high = get_range_for_difficulty("HARD")
    assert low == 1
    assert high == 50

def test_range_all_caps_normal():
    low, high = get_range_for_difficulty("NORMAL")
    assert low == 1
    assert high == 50

def test_range_lowercase_hard():
    low, high = get_range_for_difficulty("hard")
    assert low == 1
    assert high == 50

def test_range_lowercase_normal():
    low, high = get_range_for_difficulty("normal")
    assert low == 1
    assert high == 50


# --- update_score: all win attempt values 1–8 ---

def test_score_win_second_attempt():
    # 100 - 10 * 2 = 80
    assert update_score(0, "Win", 2) == 80

def test_score_win_third_attempt():
    # 100 - 10 * 3 = 70
    assert update_score(0, "Win", 3) == 70

def test_score_win_fourth_attempt():
    # 100 - 10 * 4 = 60
    assert update_score(0, "Win", 4) == 60

def test_score_win_sixth_attempt():
    # 100 - 10 * 6 = 40
    assert update_score(0, "Win", 6) == 40

def test_score_win_seventh_attempt():
    # 100 - 10 * 7 = 30
    assert update_score(0, "Win", 7) == 30

def test_score_win_eighth_attempt():
    # 100 - 10 * 8 = 20 — last valid attempt before game ends
    assert update_score(0, "Win", 8) == 20

def test_score_too_high_from_zero():
    assert update_score(0, "Too High", 1) == -5

def test_score_too_low_from_zero():
    assert update_score(0, "Too Low", 1) == -5

def test_score_empty_string_outcome():
    # Empty string is not a recognized outcome — score unchanged
    assert update_score(50, "", 1) == 50

def test_score_win_after_wrong_guesses():
    # 3 wrong guesses (-15) then win on attempt 4 (+60) = 45
    score = 0
    score = update_score(score, "Too High", 1)
    score = update_score(score, "Too Low", 2)
    score = update_score(score, "Too High", 3)
    score = update_score(score, "Win", 4)
    assert score == 45

def test_score_mixed_too_high_and_too_low():
    # Alternating Too High and Too Low both deduct 5 each
    score = 0
    score = update_score(score, "Too High", 1)
    score = update_score(score, "Too Low", 2)
    assert score == -10
