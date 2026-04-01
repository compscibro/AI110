"""
main.py — CLI demo script for PawPal+.

Run with: python main.py
"""

from pawpal_system import (
    Owner, Pet, Task,
    Priority, TaskType,
    Scheduler,
)


def format_time(minutes: int) -> str:
    """Convert minutes since midnight to HH:MM AM/PM."""
    h, m = divmod(minutes, 60)
    period = "AM" if h < 12 else "PM"
    h12 = h % 12 or 12
    return f"{h12}:{m:02d} {period}"


def print_schedule(pet_name: str, result: dict):
    """Print a clean, aligned schedule for one pet."""
    scheduled = result["scheduled_tasks"]
    unscheduled = result["unscheduled_tasks"]

    print(f"\n  {pet_name}")
    print(f"  {'─' * 55}")

    if scheduled:
        # Column header
        print(f"  {'TIME':<22}{'TASK':<22}{'TYPE':<14}{'PRI'}")
        print(f"  {'─' * 62}")
        for task in scheduled:
            time_range = f"{format_time(task.scheduled_start)} - {format_time(task.scheduled_end)}"
            shifted = (
                " *" if task.preferred_time is not None
                and task.scheduled_start != task.preferred_time
                else ""
            )
            recur = " ↻" if task.is_recurring else ""
            print(
                f"  {time_range:<22}"
                f"{task.title + recur + shifted:<22}"
                f"{task.task_type.value:<14}"
                f"{task.priority.name}"
            )
    else:
        print("  No tasks scheduled.")

    if unscheduled:
        print(f"\n  Could not schedule:")
        for task in unscheduled:
            print(f"    • {task.title} — {task.unscheduled_reason}")

    print()


# ---------------------------------------------------------------------------
# Set up owner
# ---------------------------------------------------------------------------

owner = Owner(name="Jordan", available_start=480, available_end=1320)  # 8AM–10PM

# ---------------------------------------------------------------------------
# Mochi the dog
# ---------------------------------------------------------------------------

mochi = Pet(name="Mochi", species="dog", age=3)

mochi.add_task(Task(
    title="Morning Walk",
    duration=30,
    priority=Priority.HIGH,
    task_type=TaskType.WALK,
    description="30-minute walk around the block",
    preferred_time=480,
    is_recurring=True,
))
mochi.add_task(Task(
    title="Breakfast",
    duration=10,
    priority=Priority.HIGH,
    task_type=TaskType.FEEDING,
    description="Half cup dry food with water",
    preferred_time=510,
    is_recurring=True,
))
mochi.add_task(Task(
    title="Flea Medication",
    duration=5,
    priority=Priority.MEDIUM,
    task_type=TaskType.MEDICATION,
    description="Apply topical flea treatment",
    preferred_time=600,
))
mochi.add_task(Task(
    title="Afternoon Play",
    duration=20,
    priority=Priority.LOW,
    task_type=TaskType.ENRICHMENT,
    description="Fetch in the backyard",
    preferred_time=780,
))

# ---------------------------------------------------------------------------
# Luna the cat
# ---------------------------------------------------------------------------

luna = Pet(name="Luna", species="cat", age=5)

luna.add_task(Task(
    title="Wet Food Breakfast",
    duration=5,
    priority=Priority.HIGH,
    task_type=TaskType.FEEDING,
    description="One pouch of wet food",
    preferred_time=480,
    is_recurring=True,
))
luna.add_task(Task(
    title="Vet Appointment",
    duration=60,
    priority=Priority.HIGH,
    task_type=TaskType.APPOINTMENT,
    description="Annual checkup at City Pet Clinic",
    preferred_time=660,
))
luna.add_task(Task(
    title="Brushing",
    duration=15,
    priority=Priority.LOW,
    task_type=TaskType.GROOMING,
    description="Brush to reduce shedding",
    preferred_time=900,
))

# ---------------------------------------------------------------------------
# Register pets and run scheduler
# ---------------------------------------------------------------------------

owner.add_pet(mochi)
owner.add_pet(luna)

scheduler = Scheduler()
full = scheduler.build_full_schedule(owner)

# ---------------------------------------------------------------------------
# Print today's schedule
# ---------------------------------------------------------------------------

width = 59
print("\n" + "=" * width)
print(f"  PawPal+  —  Today's Schedule for {owner.name}".center(width))
print(f"  Availability: {format_time(owner.available_start)} – {format_time(owner.available_end)}".center(width))
print("=" * width)

for pet_name, result in full.items():
    print_schedule(pet_name, result)

print("  ↻ = recurring   * = moved from preferred time")
print("=" * width + "\n")
