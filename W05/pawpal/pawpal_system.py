"""
pawpal_system.py — PawPal+ backend logic layer.

All times are in minutes since midnight (e.g. 480 = 8:00 AM, 1320 = 10:00 PM).
"""

from dataclasses import dataclass, field
from datetime import date, timedelta
from enum import Enum
from itertools import count


# ---------------------------------------------------------------------------
# Enumerations
# ---------------------------------------------------------------------------

class Priority(Enum):
    HIGH = 3
    MEDIUM = 2
    LOW = 1


class TaskType(Enum):
    FEEDING = "feeding"
    WALK = "walk"
    MEDICATION = "medication"
    APPOINTMENT = "appointment"
    ENRICHMENT = "enrichment"
    GROOMING = "grooming"


# ---------------------------------------------------------------------------
# Task
# ---------------------------------------------------------------------------

_id_counter = count(start=1)


def _reset_id_counter():
    """Reset the global task ID counter. Intended for use in tests only."""
    global _id_counter
    _id_counter = count(start=1)


@dataclass
class Task:
    """A single pet care task."""

    title: str
    duration: int                      # minutes
    priority: Priority
    task_type: TaskType
    description: str = ""              # optional longer description of the activity
    preferred_time: int | None = None  # minutes since midnight, or None
    is_recurring: bool = False
    recurrence: str = ""       # "daily", "weekly", or "" for non-recurring

    # Set automatically — not passed by the caller
    next_due: date | None = field(default=None)
    id: int = field(default_factory=lambda: next(_id_counter))
    is_completed: bool = field(default=False)
    scheduled_start: int | None = field(default=None)
    scheduled_end: int | None = field(default=None)
    unscheduled_reason: str | None = field(default=None)

    def __post_init__(self):
        """Validate duration is positive, preferred_time is within a valid day, and recurrence is a known value."""
        if self.duration <= 0:
            raise ValueError(
                f"Task '{self.title}': duration must be positive, got {self.duration}"
            )
        if self.preferred_time is not None and not (0 <= self.preferred_time <= 1439):
            raise ValueError(
                f"Task '{self.title}': preferred_time must be 0–1439, got {self.preferred_time}"
            )
        if self.recurrence not in ("", "daily", "weekly"):
            raise ValueError(
                f"Task '{self.title}': recurrence must be '', 'daily', or 'weekly', got '{self.recurrence}'"
            )

    def __str__(self):
        """Return a human-readable summary of the task for CLI debugging."""
        status = "done" if self.is_completed else "pending"
        time_info = (
            _minutes_to_time(self.scheduled_start)
            if self.scheduled_start is not None
            else "unscheduled"
        )
        return f"[{self.priority.name}] {self.title} ({self.duration} min) — {time_info} [{status}]"

    def mark_completed(self):
        """Mark this task as completed."""
        self.is_completed = True

    def clone_for_next_occurrence(self) -> "Task":
        """Return a fresh, unscheduled copy of this task due on the next occurrence date.

        Uses timedelta to compute next_due: today + 1 day for daily, + 7 days for weekly.
        """
        delta = timedelta(days=1) if self.recurrence == "daily" else timedelta(weeks=1)
        return Task(
            title=self.title,
            duration=self.duration,
            priority=self.priority,
            task_type=self.task_type,
            description=self.description,
            preferred_time=self.preferred_time,
            is_recurring=self.is_recurring,
            recurrence=self.recurrence,
            next_due=date.today() + delta,
        )

    def overlaps_with(self, other: "Task") -> bool:
        """Return True if this task's scheduled interval overlaps with other's.

        Uses stored scheduled_end to avoid recalculation.
        Returns False if either task has not been scheduled yet.
        """
        if (
            self.scheduled_start is None
            or self.scheduled_end is None
            or other.scheduled_start is None
            or other.scheduled_end is None
        ):
            return False
        return self.scheduled_start < other.scheduled_end and other.scheduled_start < self.scheduled_end


# ---------------------------------------------------------------------------
# Pet
# ---------------------------------------------------------------------------

@dataclass
class Pet:
    """A pet and its list of care tasks."""

    name: str
    species: str
    age: int
    tasks: list[Task] = field(default_factory=list)

    def add_task(self, task: Task):
        """Add a task to this pet's task list."""
        self.tasks.append(task)

    def remove_task(self, task_id: int):
        """Remove a task by its unique id."""
        self.tasks = [t for t in self.tasks if t.id != task_id]

    def get_tasks_by_priority(self) -> list[Task]:
        """Return tasks sorted highest priority first."""
        return sorted(self.tasks, key=lambda t: t.priority.value, reverse=True)


# ---------------------------------------------------------------------------
# Owner
# ---------------------------------------------------------------------------

@dataclass
class Owner:
    """A pet owner with a daily availability window."""

    name: str
    available_start: int = 480   # 8:00 AM
    available_end: int = 1320    # 10:00 PM
    pets: list[Pet] = field(default_factory=list)

    def __post_init__(self):
        """Validate that the availability window is within a real day and start is before end."""
        for val, label in [
            (self.available_start, "available_start"),
            (self.available_end, "available_end"),
        ]:
            if not (0 <= val <= 1439):
                raise ValueError(
                    f"Owner '{self.name}': {label} must be 0–1439, got {val}"
                )
        if self.available_start >= self.available_end:
            raise ValueError(
                f"Owner '{self.name}': available_start must be before available_end"
            )

    def add_pet(self, pet: Pet):
        """Add a pet to this owner's list."""
        self.pets.append(pet)

    def total_available_minutes(self) -> int:
        """Return the total number of minutes in the owner's availability window."""
        return self.available_end - self.available_start

    def get_all_tasks(self) -> list[Task]:
        """Return a flat list of all tasks across every pet."""
        return [task for pet in self.pets for task in pet.tasks]


# ---------------------------------------------------------------------------
# Scheduler
# ---------------------------------------------------------------------------

class Scheduler:
    """Stateless scheduling service.

    Uses a greedy interval algorithm: tasks are sorted by priority (highest
    first), then by preferred_time, then by duration (shorter first to fit
    more tasks). Each task is placed at the earliest available slot at or
    after its preferred_time within the owner's availability window.
    """

    def build_schedule(self, owner: Owner, pet: Pet) -> dict:
        """Build a daily schedule for one pet.

        Resets scheduled_start/end on all tasks before scheduling to avoid
        stale results from a previous run.

        Returns:
            {
                "scheduled_tasks":   list[Task],  tasks with scheduled_start/end set
                "unscheduled_tasks": list[Task],  tasks that did not fit, with reason set
            }
        """
        # Clear stale scheduling data from any previous run
        for task in pet.tasks:
            task.scheduled_start = None
            task.scheduled_end = None
            task.unscheduled_reason = None

        # Sort key: priority DESC, preferred_time ASC (None last), duration ASC
        sorted_tasks = sorted(
            pet.tasks,
            key=lambda t: (
                -t.priority.value,
                t.preferred_time if t.preferred_time is not None else float("inf"),
                t.duration,
            ),
        )

        # Each Task is mutated in place (scheduled_start/end set here).
        # Do not share Task objects across multiple pets — a second call would overwrite them.
        occupied: list[tuple[int, int]] = []  # (start, end) of placed tasks, kept sorted
        scheduled: list[Task] = []
        unscheduled: list[Task] = []

        for task in sorted_tasks:
            search_from = (
                task.preferred_time
                if task.preferred_time is not None
                else owner.available_start
            )

            # Preferred time is entirely outside the owner's window
            if search_from >= owner.available_end:
                task.unscheduled_reason = "outside availability window"
                unscheduled.append(task)
                continue

            start = self._find_slot(
                occupied, search_from, task.duration, owner.available_end
            )
            if start is None:
                task.unscheduled_reason = "no available slot"
                unscheduled.append(task)
            else:
                task.scheduled_start = start
                task.scheduled_end = start + task.duration
                occupied.append((start, task.scheduled_end))
                occupied.sort()  # keep sorted so _find_slot scans in order
                scheduled.append(task)

        scheduled.sort(key=lambda t: t.scheduled_start)

        return {"scheduled_tasks": scheduled, "unscheduled_tasks": unscheduled}

    def get_tasks_sorted_by_time(self, pet: Pet) -> list[Task]:
        """Return all tasks sorted by preferred_time ascending; tasks with no preference sort last."""
        return sorted(
            pet.tasks,
            key=lambda t: t.preferred_time if t.preferred_time is not None else float("inf"),
        )

    def filter_by_type(self, pet: Pet, task_type: TaskType) -> list[Task]:
        """Return tasks matching a specific TaskType."""
        return [t for t in pet.tasks if t.task_type == task_type]

    def filter_by_status(self, pet: Pet, completed: bool = False) -> list[Task]:
        """Return tasks filtered by completion status."""
        return [t for t in pet.tasks if t.is_completed == completed]

    def get_recurring_tasks(self, pet: Pet) -> list[Task]:
        """Return all tasks marked as recurring."""
        return [t for t in pet.tasks if t.is_recurring]

    def detect_conflicts(self, pet: Pet) -> list[tuple]:
        """Return pairs of tasks whose preferred_time intervals overlap before scheduling.

        Useful for warning the user upfront about tasks that will need to be shifted.
        Only compares tasks that have a preferred_time set.
        """
        timed = [t for t in pet.tasks if t.preferred_time is not None]
        conflicts = []
        for i, a in enumerate(timed):
            for b in timed[i + 1:]:
                a_end = a.preferred_time + a.duration
                b_end = b.preferred_time + b.duration
                if a.preferred_time < b_end and b.preferred_time < a_end:
                    conflicts.append((a, b))
        return conflicts

    def detect_schedule_conflicts(self, result: dict) -> list[str]:
        """Post-schedule sanity check: return warnings for any overlapping scheduled tasks.

        The greedy algorithm guarantees no overlaps within one pet's schedule,
        but this makes that guarantee explicit and testable.
        """
        warnings = []
        scheduled = result["scheduled_tasks"]
        for i, a in enumerate(scheduled):
            for b in scheduled[i + 1:]:
                if a.overlaps_with(b):
                    warnings.append(
                        f"⚠ Conflict: '{a.title}' ({_minutes_to_time(a.scheduled_start)}–"
                        f"{_minutes_to_time(a.scheduled_end)}) overlaps "
                        f"'{b.title}' ({_minutes_to_time(b.scheduled_start)}–"
                        f"{_minutes_to_time(b.scheduled_end)})"
                    )
        return warnings

    def detect_cross_pet_conflicts(self, full_result: dict) -> list[str]:
        """Warn when scheduled tasks across different pets overlap in the final schedule.

        Useful when the owner must be present for both tasks simultaneously —
        e.g. walking one pet while feeding another at the same time.
        """
        warnings = []
        pet_names = list(full_result.keys())
        for i, pet_a in enumerate(pet_names):
            for pet_b in pet_names[i + 1:]:
                for a in full_result[pet_a]["scheduled_tasks"]:
                    for b in full_result[pet_b]["scheduled_tasks"]:
                        if a.overlaps_with(b):
                            warnings.append(
                                f"⚠ Cross-pet: [{pet_a}] '{a.title}' "
                                f"({_minutes_to_time(a.scheduled_start)}–{_minutes_to_time(a.scheduled_end)}) "
                                f"overlaps [{pet_b}] '{b.title}' "
                                f"({_minutes_to_time(b.scheduled_start)}–{_minutes_to_time(b.scheduled_end)})"
                            )
        return warnings

    def build_full_schedule(self, owner: Owner) -> dict:
        """Build a daily schedule for every pet the owner has.

        Returns a dict keyed by pet name, each value being the result of build_schedule.
        """
        return {pet.name: self.build_schedule(owner, pet) for pet in owner.pets}

    def get_pending_tasks(self, pet: Pet) -> list[Task]:
        """Return all incomplete tasks for a pet, sorted by priority."""
        return [t for t in pet.get_tasks_by_priority() if not t.is_completed]

    def mark_task_completed(self, owner: Owner, task_id: int) -> bool:
        """Find a task by ID across all of the owner's pets and mark it complete.

        If the task is recurring, automatically adds a new instance to the same
        pet using clone_for_next_occurrence() with next_due computed via timedelta.

        Returns True if the task was found and marked, False if not found.
        """
        for pet in owner.pets:
            for task in pet.tasks:
                if task.id == task_id:
                    task.mark_completed()
                    if task.is_recurring and task.recurrence:
                        pet.add_task(task.clone_for_next_occurrence())
                    return True
        return False

    def _find_slot(
        self,
        occupied: list[tuple[int, int]],
        search_from: int,
        duration: int,
        available_end: int,
    ) -> int | None:
        """Find the earliest start >= search_from where duration minutes fit.

        Steps forward past conflicting intervals until a free gap is found
        or the availability window is exhausted.
        """
        # Nothing placed yet — the window start is always free
        if not occupied:
            return search_from if search_from + duration <= available_end else None

        # O(n²) over occupied intervals — acceptable for a small daily task list
        candidate = search_from
        while candidate + duration <= available_end:
            conflicts = [
                end for (start, end) in occupied
                if start < candidate + duration and end > candidate
            ]
            if not conflicts:
                return candidate
            # Jump past the furthest conflicting interval to avoid redundant checks
            candidate = max(conflicts)
        return None


# ---------------------------------------------------------------------------
# Display helpers
# ---------------------------------------------------------------------------

def _minutes_to_time(minutes: int) -> str:
    """Convert minutes since midnight to a readable 12-hour string."""
    h, m = divmod(minutes, 60)
    period = "AM" if h < 12 else "PM"
    h12 = h % 12 or 12
    return f"{h12}:{m:02d} {period}"


def display_schedule(result: dict) -> str:
    """Return a formatted CLI string for a build_schedule result."""
    lines = ["=== PawPal+ Daily Schedule ===\n"]

    for task in result["scheduled_tasks"]:
        start = _minutes_to_time(task.scheduled_start)
        end = _minutes_to_time(task.scheduled_end)
        recur = " (recurring)" if task.is_recurring else ""
        # Note when the task was placed later than the owner requested
        shifted = (
            f" (moved from {_minutes_to_time(task.preferred_time)})"
            if task.preferred_time is not None and task.scheduled_start != task.preferred_time
            else ""
        )
        lines.append(
            f"  {start} - {end}  [{task.task_type.value.upper()}] {task.title}{recur}{shifted}"
        )

    if not result["scheduled_tasks"]:
        lines.append("  No tasks scheduled.")

    if result["unscheduled_tasks"]:
        lines.append("\n--- Could not fit in availability window ---")
        for task in result["unscheduled_tasks"]:
            lines.append(
                f"  {task.title} ({task.duration} min) — {task.unscheduled_reason}"
            )

    return "\n".join(lines)


def to_dict_list(result: dict) -> list[dict]:
    """Convert scheduled tasks to a list of dicts for Streamlit display."""
    rows = [
        {
            "Time": f"{_minutes_to_time(t.scheduled_start)} – {_minutes_to_time(t.scheduled_end)}",
            "Task": t.title,
            "Type": t.task_type.value,
            "Duration (min)": t.duration,
            "Priority": t.priority.name,
            "Recurring": t.is_recurring,
            "Completed": t.is_completed,
        }
        for t in result["scheduled_tasks"]
    ]
    return rows
