# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## Smarter Scheduling

The scheduler goes beyond a simple list to give the owner a smarter daily plan:

- **Sorting** — tasks are displayed in preferred-time order regardless of the order they were added, and scheduled by priority (HIGH first) so critical tasks like medication always claim their slot first.
- **Filtering** — tasks can be filtered by `TaskType` (e.g. show only FEEDING tasks) or by completion status (pending vs. done).
- **Recurring task automation** — marking a recurring task complete automatically clones it with a `next_due` date (today + 1 day for daily, + 7 days for weekly), so the owner never has to re-enter it.
- **Conflict detection** — the scheduler warns about two kinds of conflicts before and after scheduling:
  - *Pre-schedule*: tasks whose `preferred_time` intervals overlap, flagging slots that will need to shift.
  - *Post-schedule / cross-pet*: scheduled tasks that end up overlapping, including tasks across different pets that require the owner to be in two places at once.

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.
