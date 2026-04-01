# Testing Guidelines

## Framework
- All automated tests must use **pytest**.

## When to Test
- Tests must be executed **after every code change**.
- No change should be considered complete until **all tests pass**.

## What to Test
- Core game mechanics
- Score calculations
- Game state transitions
- Edge cases and invalid inputs

## How to Test
- Write pytest test cases for functions and modules.
- Verify expected outputs for known inputs.
- Test both normal gameplay and failure scenarios.
- Ensure tests are deterministic and repeatable.

## Organization
- Write game logic tests in `test/test_game_logic.py`.
- Name test functions using `test_<behavior>` format.

## Execution
- After any modification, run:

```bash
pytest
```

- The codebase must **pass all existing tests before changes are accepted**.

## Goal
Tests ensure the system behaves correctly and prevent previously fixed bugs from returning.