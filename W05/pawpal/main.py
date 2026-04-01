"""
main.py — CLI demo script for PawPal+.

Demonstrates sorting, filtering, conflict detection, recurring tasks,
task completion, and overflow handling.

Run with: python main.py
"""

from pawpal_system import (
    Owner, Pet, Task,
    Priority, TaskType,
    Scheduler,
)

W = 62  # column width for section headers


def fmt(minutes: int) -> str:
    """Convert minutes since midnight to HH:MM AM/PM."""
    h, m = divmod(minutes, 60)
    period = "AM" if h < 12 else "PM"
    return f"{h % 12 or 12}:{m:02d} {period}"


def header(title: str):
    print(f"\n{'─' * W}")
    print(f"  {title}")
    print(f"{'─' * W}")


# ---------------------------------------------------------------------------
# Owner setup
# ---------------------------------------------------------------------------

owner = Owner(name="Jordan", available_start=480, available_end=1320)  # 8AM–10PM

# ---------------------------------------------------------------------------
# Mochi the dog — tasks added OUT OF ORDER intentionally
# ---------------------------------------------------------------------------

mochi = Pet(name="Mochi", species="dog", age=3)

# Added out of time order: afternoon task first, then morning tasks
mochi.add_task(Task(
    title="Afternoon Play",
    duration=20,
    priority=Priority.LOW,
    task_type=TaskType.ENRICHMENT,
    preferred_time=780,          # 1:00 PM  ← added first but happens last
    is_recurring=True,
    recurrence="daily",
))
mochi.add_task(Task(
    title="Flea Medication",
    duration=5,
    priority=Priority.MEDIUM,
    task_type=TaskType.MEDICATION,
    preferred_time=510,          # 8:30 AM  ← same slot as Breakfast (conflict!)
))
mochi.add_task(Task(
    title="Breakfast",
    duration=10,
    priority=Priority.HIGH,
    task_type=TaskType.FEEDING,
    preferred_time=510,          # 8:30 AM  ← same preferred_time as Medication
    is_recurring=True,
    recurrence="daily",
))
mochi.add_task(Task(
    title="Morning Walk",
    duration=30,
    priority=Priority.HIGH,
    task_type=TaskType.WALK,
    preferred_time=480,          # 8:00 AM
    is_recurring=True,
    recurrence="daily",
))
mochi.add_task(Task(
    title="Full Grooming Session",
    duration=900,                # 15 hours — intentionally too long to fit
    priority=Priority.LOW,
    task_type=TaskType.GROOMING,
    preferred_time=600,
))

# ---------------------------------------------------------------------------
# Luna the cat
# ---------------------------------------------------------------------------

luna = Pet(name="Luna", species="cat", age=5)

luna.add_task(Task(
    title="Vet Appointment",
    duration=60,
    priority=Priority.HIGH,
    task_type=TaskType.APPOINTMENT,
    preferred_time=660,          # 11:00 AM
))
luna.add_task(Task(
    title="Wet Food Breakfast",
    duration=5,
    priority=Priority.HIGH,
    task_type=TaskType.FEEDING,
    preferred_time=480,          # 8:00 AM
    is_recurring=True,
    recurrence="daily",
))
luna.add_task(Task(
    title="Brushing",
    duration=15,
    priority=Priority.LOW,
    task_type=TaskType.GROOMING,
    preferred_time=900,          # 3:00 PM
))

owner.add_pet(mochi)
owner.add_pet(luna)

scheduler = Scheduler()

# ---------------------------------------------------------------------------
# 1. Sort by time (pre-schedule) — shows tasks in time order regardless of
#    the order they were added
# ---------------------------------------------------------------------------

header("1. Tasks sorted by preferred time (pre-schedule)")
for pet in owner.pets:
    print(f"\n  {pet.name}:")
    for t in scheduler.get_tasks_sorted_by_time(pet):
        pref = fmt(t.preferred_time) if t.preferred_time else "no preference"
        print(f"    {pref:<14}  [{t.priority.name:<6}]  {t.title}")

# ---------------------------------------------------------------------------
# 2. Detect conflicts — preferred_time intervals that overlap before scheduling
# ---------------------------------------------------------------------------

header("2. Pre-schedule conflict detection")
for pet in owner.pets:
    conflicts = scheduler.detect_conflicts(pet)
    if conflicts:
        print(f"\n  {pet.name} — {len(conflicts)} conflict(s) detected:")
        for a, b in conflicts:
            print(f"    ⚠  '{a.title}' ({fmt(a.preferred_time)}) overlaps "
                  f"'{b.title}' ({fmt(b.preferred_time)})")
    else:
        print(f"\n  {pet.name} — no conflicts")

# ---------------------------------------------------------------------------
# 3. Filter by type — show only FEEDING tasks
# ---------------------------------------------------------------------------

header("3. Filter by type: FEEDING tasks only")
for pet in owner.pets:
    feeding = scheduler.filter_by_type(pet, TaskType.FEEDING)
    if feeding:
        print(f"\n  {pet.name}:")
        for t in feeding:
            print(f"    • {t.title}")

# ---------------------------------------------------------------------------
# 4. Recurring tasks
# ---------------------------------------------------------------------------

header("4. Recurring tasks")
for pet in owner.pets:
    recurring = scheduler.get_recurring_tasks(pet)
    print(f"\n  {pet.name}: {len(recurring)} recurring task(s)")
    for t in recurring:
        print(f"    ↻  {t.title}")

# ---------------------------------------------------------------------------
# 5. Build and display full schedule
# ---------------------------------------------------------------------------

header("5. Generated schedule")
full = scheduler.build_full_schedule(owner)

for pet_name, result in full.items():
    print(f"\n  {pet_name}")
    print(f"  {'TIME':<22}{'TASK':<24}{'PRI'}")
    print(f"  {'─' * 50}")
    for t in result["scheduled_tasks"]:
        shifted = " *" if t.preferred_time and t.scheduled_start != t.preferred_time else ""
        recur   = " ↻" if t.is_recurring else ""
        time_r  = f"{fmt(t.scheduled_start)} - {fmt(t.scheduled_end)}"
        print(f"  {time_r:<22}{t.title + recur + shifted:<24}{t.priority.name}")

    if result["unscheduled_tasks"]:
        print(f"\n  Could not schedule:")
        for t in result["unscheduled_tasks"]:
            print(f"    ✗  {t.title} ({t.duration} min) — {t.unscheduled_reason}")

# ---------------------------------------------------------------------------
# 6. Mark a task complete, then filter for pending tasks
# ---------------------------------------------------------------------------

header("6. Post-schedule conflict check (per pet)")
any_conflicts = False
for pet_name, result in full.items():
    warnings = scheduler.detect_schedule_conflicts(result)
    if warnings:
        any_conflicts = True
        for w in warnings:
            print(f"  [{pet_name}] {w}")
    else:
        print(f"  [{pet_name}] No post-schedule conflicts — greedy algorithm held.")

header("7. Cross-pet conflict detection")
cross = scheduler.detect_cross_pet_conflicts(full)
if cross:
    print()
    for w in cross:
        print(f"  {w}")
    print(f"\n  Note: owner cannot be in two places at once.")
else:
    print("  No cross-pet conflicts detected.")

header("8. Task completion + recurring auto-clone")

from datetime import date  # noqa: E402

walk_task = next(t for t in mochi.tasks if t.title == "Morning Walk")
task_count_before = len(mochi.tasks)

scheduler.mark_task_completed(owner, walk_task.id)

print(f"\n  Marked '{walk_task.title}' as completed (recurrence: {walk_task.recurrence!r}).")
print(f"  Tasks before: {task_count_before}  →  after: {len(mochi.tasks)}")

cloned = mochi.tasks[-1]  # new occurrence appended last
print(f"\n  Auto-cloned next occurrence:")
print(f"    Title    : {cloned.title}")
print(f"    Next due : {cloned.next_due}  (today + 1 day via timedelta)")
print(f"    Completed: {cloned.is_completed}")

print()
for pet in owner.pets:
    pending = scheduler.filter_by_status(pet, completed=False)
    done    = scheduler.filter_by_status(pet, completed=True)
    print(f"  {pet.name} — {len(pending)} pending, {len(done)} completed:")
    for t in pending:
        due = f"  [due {t.next_due}]" if t.next_due else ""
        print(f"    ○  {t.title}{due}")
    for t in done:
        print(f"    ✓  {t.title}")

print(f"\n{'═' * W}")
print("  ↻ = recurring   * = moved from preferred time   ✗ = unscheduled")
print(f"{'═' * W}\n")
