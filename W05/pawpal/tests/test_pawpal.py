"""
tests/test_pawpal.py — Automated tests for PawPal+ core logic.

Run with: python -m pytest
"""

import pytest
from datetime import date, timedelta
from pawpal_system import Owner, Pet, Task, Priority, TaskType, Scheduler, _reset_id_counter, to_dict_list


@pytest.fixture(autouse=True)
def reset_ids():
    """Reset the global task ID counter before each test for clean IDs."""
    _reset_id_counter()


def make_task(title="Test Task", duration=30, priority=Priority.MEDIUM, task_type=TaskType.WALK):
    """Helper to create a Task with sensible defaults."""
    return Task(title=title, duration=duration, priority=priority, task_type=task_type)


def make_owner():
    """Helper to create a standard Owner (8 AM – 10 PM)."""
    return Owner(name="Jordan", available_start=480, available_end=1320)


def make_pet(name="Mochi"):
    """Helper to create a Pet with sensible defaults."""
    return Pet(name=name, species="dog", age=3)


# ===========================================================================
# Task — Validation (__post_init__)
# ===========================================================================

def test_mark_completed_changes_status():
    """Calling mark_completed() should set is_completed to True."""
    task = make_task()
    assert task.is_completed is False
    task.mark_completed()
    assert task.is_completed is True


def test_task_duration_zero_raises():
    with pytest.raises(ValueError, match="duration must be positive"):
        Task(title="Bad", duration=0, priority=Priority.HIGH, task_type=TaskType.WALK)


def test_task_negative_duration_raises():
    with pytest.raises(ValueError, match="duration must be positive"):
        Task(title="Bad", duration=-10, priority=Priority.HIGH, task_type=TaskType.WALK)


def test_task_preferred_time_below_zero_raises():
    with pytest.raises(ValueError, match="preferred_time must be 0"):
        Task(title="Bad", duration=10, priority=Priority.HIGH,
             task_type=TaskType.WALK, preferred_time=-1)


def test_task_preferred_time_above_1439_raises():
    with pytest.raises(ValueError, match="preferred_time must be 0"):
        Task(title="Bad", duration=10, priority=Priority.HIGH,
             task_type=TaskType.WALK, preferred_time=1440)


def test_task_invalid_recurrence_raises():
    with pytest.raises(ValueError, match="recurrence must be"):
        Task(title="Bad", duration=10, priority=Priority.HIGH,
             task_type=TaskType.WALK, recurrence="monthly")


def test_task_preferred_time_boundary_zero_is_valid():
    t = Task(title="Midnight", duration=10, priority=Priority.HIGH,
             task_type=TaskType.WALK, preferred_time=0)
    assert t.preferred_time == 0


def test_task_preferred_time_boundary_1439_is_valid():
    t = Task(title="Late", duration=1, priority=Priority.HIGH,
             task_type=TaskType.WALK, preferred_time=1439)
    assert t.preferred_time == 1439


# ===========================================================================
# Task — overlaps_with
# ===========================================================================

def test_overlaps_with_returns_false_when_unscheduled():
    """overlaps_with must return False if either task has no scheduled interval."""
    a = make_task("A")
    b = make_task("B")
    assert a.overlaps_with(b) is False


def test_overlaps_with_detects_true_overlap():
    """[480, 510) vs [500, 530) — intervals cross in the middle."""
    a = make_task("A")
    b = make_task("B")
    a.scheduled_start, a.scheduled_end = 480, 510
    b.scheduled_start, b.scheduled_end = 500, 530
    assert a.overlaps_with(b) is True


def test_overlaps_with_adjacent_tasks_do_not_overlap():
    """[480, 510) vs [510, 540) — touching at the boundary is not an overlap."""
    a = make_task("A")
    b = make_task("B")
    a.scheduled_start, a.scheduled_end = 480, 510
    b.scheduled_start, b.scheduled_end = 510, 540
    assert a.overlaps_with(b) is False


def test_overlaps_with_contained_task_returns_true():
    """[480, 540) fully contains [490, 500) — must be detected as overlap."""
    a = make_task("A")
    b = make_task("B")
    a.scheduled_start, a.scheduled_end = 480, 540
    b.scheduled_start, b.scheduled_end = 490, 500
    assert a.overlaps_with(b) is True


# ===========================================================================
# Task — clone_for_next_occurrence
# ===========================================================================

def test_clone_weekly_sets_next_due_to_next_week():
    t = Task(title="Bath", duration=60, priority=Priority.LOW,
             task_type=TaskType.GROOMING, is_recurring=True, recurrence="weekly")
    clone = t.clone_for_next_occurrence()
    assert clone.next_due == date.today() + timedelta(weeks=1)


def test_clone_preserves_all_fields():
    t = Task(title="Walk", duration=30, priority=Priority.HIGH,
             task_type=TaskType.WALK, preferred_time=480,
             is_recurring=True, recurrence="daily")
    clone = t.clone_for_next_occurrence()
    assert clone.title == t.title
    assert clone.duration == t.duration
    assert clone.priority == t.priority
    assert clone.task_type == t.task_type
    assert clone.preferred_time == t.preferred_time
    assert clone.is_recurring is True
    assert clone.recurrence == t.recurrence


def test_clone_starts_unscheduled_and_incomplete():
    """Clone must have all scheduling fields reset regardless of the original's state."""
    t = Task(title="Walk", duration=30, priority=Priority.HIGH,
             task_type=TaskType.WALK, is_recurring=True, recurrence="daily")
    t.scheduled_start, t.scheduled_end = 480, 510
    clone = t.clone_for_next_occurrence()
    assert clone.is_completed is False
    assert clone.scheduled_start is None
    assert clone.scheduled_end is None


def test_clone_gets_unique_id():
    t = Task(title="Walk", duration=30, priority=Priority.HIGH,
             task_type=TaskType.WALK, is_recurring=True, recurrence="daily")
    clone = t.clone_for_next_occurrence()
    assert clone.id != t.id


# ===========================================================================
# Pet
# ===========================================================================

def test_add_task_increases_pet_task_count():
    """Adding a task to a Pet should increase its task count by one."""
    pet = make_pet()
    assert len(pet.tasks) == 0
    pet.add_task(make_task("Morning Walk"))
    assert len(pet.tasks) == 1
    pet.add_task(make_task("Breakfast"))
    assert len(pet.tasks) == 2


def test_remove_task_removes_correct_task():
    pet = make_pet()
    t1 = make_task("Walk")
    t2 = make_task("Breakfast")
    pet.add_task(t1)
    pet.add_task(t2)
    pet.remove_task(t1.id)
    assert len(pet.tasks) == 1
    assert pet.tasks[0].title == "Breakfast"


def test_remove_task_nonexistent_id_is_no_op():
    pet = make_pet()
    pet.add_task(make_task("Walk"))
    pet.remove_task(9999)
    assert len(pet.tasks) == 1


def test_get_tasks_by_priority_high_before_low():
    pet = make_pet()
    pet.add_task(Task(title="Grooming", duration=15, priority=Priority.LOW,
                      task_type=TaskType.GROOMING))
    pet.add_task(Task(title="Meds", duration=5, priority=Priority.HIGH,
                      task_type=TaskType.MEDICATION))
    pet.add_task(Task(title="Play", duration=20, priority=Priority.MEDIUM,
                      task_type=TaskType.ENRICHMENT))
    values = [t.priority.value for t in pet.get_tasks_by_priority()]
    assert values == sorted(values, reverse=True)


# ===========================================================================
# Owner — Validation
# ===========================================================================

def test_owner_start_after_end_raises():
    with pytest.raises(ValueError, match="available_start must be before available_end"):
        Owner(name="Jordan", available_start=900, available_end=480)


def test_owner_start_equals_end_raises():
    with pytest.raises(ValueError, match="available_start must be before available_end"):
        Owner(name="Jordan", available_start=480, available_end=480)


def test_owner_start_out_of_range_raises():
    with pytest.raises(ValueError, match="available_start"):
        Owner(name="Jordan", available_start=1500, available_end=1320)


def test_total_available_minutes_correct():
    owner = Owner(name="Jordan", available_start=480, available_end=1320)
    assert owner.total_available_minutes() == 840


def test_get_all_tasks_flat_across_pets():
    owner = make_owner()
    pet1 = make_pet("Mochi")
    pet2 = make_pet("Luna")
    pet1.add_task(make_task("Walk"))
    pet2.add_task(make_task("Brush"))
    pet2.add_task(make_task("Feed"))
    owner.add_pet(pet1)
    owner.add_pet(pet2)
    assert len(owner.get_all_tasks()) == 3


# ===========================================================================
# Scheduler — Sorting
# ===========================================================================

def test_get_tasks_sorted_by_time_returns_chronological_order():
    """get_tasks_sorted_by_time should return tasks in ascending preferred_time order."""
    pet = make_pet("Luna")
    pet.add_task(Task(title="Evening Meal",  duration=10, priority=Priority.HIGH,
                      task_type=TaskType.FEEDING,  preferred_time=1080))
    pet.add_task(Task(title="Morning Brush", duration=15, priority=Priority.LOW,
                      task_type=TaskType.GROOMING, preferred_time=540))
    pet.add_task(Task(title="Breakfast",     duration=10, priority=Priority.HIGH,
                      task_type=TaskType.FEEDING,  preferred_time=480))
    times = [t.preferred_time for t in Scheduler().get_tasks_sorted_by_time(pet)]
    assert times == sorted(times)


def test_tasks_without_preferred_time_sort_last():
    """Tasks with preferred_time=None must appear after all timed tasks."""
    pet = make_pet()
    pet.add_task(Task(title="Anytime Play", duration=20, priority=Priority.LOW,
                      task_type=TaskType.ENRICHMENT))  # no preferred_time
    pet.add_task(Task(title="Breakfast", duration=10, priority=Priority.HIGH,
                      task_type=TaskType.FEEDING, preferred_time=480))
    sorted_tasks = Scheduler().get_tasks_sorted_by_time(pet)
    assert sorted_tasks[-1].preferred_time is None


# ===========================================================================
# Scheduler — Filtering
# ===========================================================================

def test_filter_by_type_returns_only_matching():
    pet = make_pet()
    pet.add_task(Task(title="Walk",   duration=30, priority=Priority.HIGH,
                      task_type=TaskType.WALK))
    pet.add_task(Task(title="Feed1",  duration=10, priority=Priority.HIGH,
                      task_type=TaskType.FEEDING))
    pet.add_task(Task(title="Feed2",  duration=10, priority=Priority.HIGH,
                      task_type=TaskType.FEEDING))
    result = Scheduler().filter_by_type(pet, TaskType.FEEDING)
    assert len(result) == 2
    assert all(t.task_type == TaskType.FEEDING for t in result)


def test_filter_by_type_returns_empty_when_no_match():
    pet = make_pet()
    pet.add_task(Task(title="Walk", duration=30, priority=Priority.HIGH,
                      task_type=TaskType.WALK))
    assert Scheduler().filter_by_type(pet, TaskType.MEDICATION) == []


def test_filter_by_status_pending():
    pet = make_pet()
    t1 = make_task("Walk")
    t2 = make_task("Feed")
    t1.mark_completed()
    pet.add_task(t1)
    pet.add_task(t2)
    pending = Scheduler().filter_by_status(pet, completed=False)
    assert len(pending) == 1
    assert pending[0].title == "Feed"


def test_filter_by_status_completed():
    pet = make_pet()
    t1 = make_task("Walk")
    t2 = make_task("Feed")
    t1.mark_completed()
    pet.add_task(t1)
    pet.add_task(t2)
    done = Scheduler().filter_by_status(pet, completed=True)
    assert len(done) == 1
    assert done[0].title == "Walk"


def test_get_recurring_tasks_excludes_non_recurring():
    pet = make_pet()
    pet.add_task(Task(title="Daily Walk", duration=30, priority=Priority.HIGH,
                      task_type=TaskType.WALK, is_recurring=True, recurrence="daily"))
    pet.add_task(Task(title="Vet Visit", duration=60, priority=Priority.HIGH,
                      task_type=TaskType.APPOINTMENT))
    result = Scheduler().get_recurring_tasks(pet)
    assert len(result) == 1
    assert result[0].title == "Daily Walk"


# ===========================================================================
# Scheduler — Conflict detection
# ===========================================================================

def test_detect_conflicts_flags_overlapping_preferred_times():
    """detect_conflicts should return one pair when two tasks share overlapping preferred times."""
    pet = make_pet()
    pet.add_task(Task(title="Breakfast",       duration=10, priority=Priority.HIGH,
                      task_type=TaskType.FEEDING,    preferred_time=510))
    pet.add_task(Task(title="Flea Medication", duration=5,  priority=Priority.MEDIUM,
                      task_type=TaskType.MEDICATION, preferred_time=510))
    conflicts = Scheduler().detect_conflicts(pet)
    assert len(conflicts) == 1
    titles = {t.title for pair in conflicts for t in pair}
    assert "Breakfast" in titles and "Flea Medication" in titles


def test_detect_conflicts_returns_empty_when_no_overlap():
    """Adjacent preferred_time intervals (back-to-back) must not be flagged."""
    pet = make_pet()
    pet.add_task(Task(title="Walk", duration=30, priority=Priority.HIGH,
                      task_type=TaskType.WALK,    preferred_time=480))   # 8:00–8:30
    pet.add_task(Task(title="Feed", duration=10, priority=Priority.HIGH,
                      task_type=TaskType.FEEDING, preferred_time=510))   # 8:30–8:40
    assert Scheduler().detect_conflicts(pet) == []


def test_detect_conflicts_ignores_tasks_without_preferred_time():
    pet = make_pet()
    pet.add_task(Task(title="Walk", duration=30, priority=Priority.HIGH,
                      task_type=TaskType.WALK, preferred_time=480))
    pet.add_task(Task(title="Play", duration=20, priority=Priority.LOW,
                      task_type=TaskType.ENRICHMENT))  # no preferred_time
    assert Scheduler().detect_conflicts(pet) == []


def test_detect_schedule_conflicts_empty_after_greedy_schedule():
    """The greedy algorithm must produce zero post-schedule conflicts."""
    owner = make_owner()
    pet = make_pet()
    for title, pref in [("Walk", 480), ("Feed", 510), ("Play", 600)]:
        pet.add_task(Task(title=title, duration=20, priority=Priority.MEDIUM,
                          task_type=TaskType.WALK, preferred_time=pref))
    result = Scheduler().build_schedule(owner, pet)
    assert Scheduler().detect_schedule_conflicts(result) == []


def test_detect_cross_pet_conflicts_finds_overlap():
    owner = make_owner()
    pet1 = make_pet("Mochi")
    pet2 = make_pet("Luna")
    pet1.add_task(Task(title="Walk",      duration=30, priority=Priority.HIGH,
                       task_type=TaskType.WALK,    preferred_time=480))
    pet2.add_task(Task(title="Breakfast", duration=10, priority=Priority.HIGH,
                       task_type=TaskType.FEEDING, preferred_time=480))
    owner.add_pet(pet1)
    owner.add_pet(pet2)
    full = Scheduler().build_full_schedule(owner)
    assert len(Scheduler().detect_cross_pet_conflicts(full)) >= 1


# ===========================================================================
# Scheduler — build_schedule edge cases
# ===========================================================================

def test_build_schedule_empty_pet_returns_empty_lists():
    owner = make_owner()
    pet = make_pet()
    result = Scheduler().build_schedule(owner, pet)
    assert result["scheduled_tasks"] == []
    assert result["unscheduled_tasks"] == []


def test_build_schedule_task_outside_window_is_unscheduled():
    owner = Owner(name="Jordan", available_start=480, available_end=600)  # 8 AM – 10 AM
    pet = make_pet()
    pet.add_task(Task(title="Evening Walk", duration=30, priority=Priority.HIGH,
                      task_type=TaskType.WALK, preferred_time=1200))  # 8 PM — outside window
    result = Scheduler().build_schedule(owner, pet)
    assert len(result["unscheduled_tasks"]) == 1
    assert result["unscheduled_tasks"][0].unscheduled_reason == "outside availability window"


def test_build_schedule_no_preferred_time_uses_window_start():
    """A task with no preferred_time should be placed at available_start."""
    owner = make_owner()
    pet = make_pet()
    pet.add_task(Task(title="Play", duration=20, priority=Priority.MEDIUM,
                      task_type=TaskType.ENRICHMENT))  # preferred_time=None
    result = Scheduler().build_schedule(owner, pet)
    assert len(result["scheduled_tasks"]) == 1
    assert result["scheduled_tasks"][0].scheduled_start == 480


def test_build_schedule_no_overlap_guarantee():
    """Five tasks all wanting the same slot must be placed without any overlap."""
    owner = make_owner()
    pet = make_pet()
    for i in range(5):
        pet.add_task(Task(title=f"Task {i}", duration=20, priority=Priority.MEDIUM,
                          task_type=TaskType.WALK, preferred_time=480))
    scheduled = Scheduler().build_schedule(owner, pet)["scheduled_tasks"]
    for i, a in enumerate(scheduled):
        for b in scheduled[i + 1:]:
            assert not a.overlaps_with(b), f"'{a.title}' overlaps '{b.title}'"


def test_build_schedule_stale_data_cleared_on_rerun():
    """Running build_schedule twice must produce the same result, not accumulate state."""
    owner = make_owner()
    pet = make_pet()
    pet.add_task(Task(title="Walk", duration=30, priority=Priority.HIGH,
                      task_type=TaskType.WALK, preferred_time=480))
    scheduler = Scheduler()
    r1 = scheduler.build_schedule(owner, pet)
    r2 = scheduler.build_schedule(owner, pet)
    assert r1["scheduled_tasks"][0].scheduled_start == r2["scheduled_tasks"][0].scheduled_start


def test_task_too_long_to_fit_goes_to_unscheduled():
    """A task whose duration exceeds the entire availability window must be unscheduled."""
    owner = make_owner()  # 840-minute window
    pet = make_pet()
    pet.add_task(Task(title="Full Grooming", duration=900, priority=Priority.LOW,
                      task_type=TaskType.GROOMING, preferred_time=600))
    result = Scheduler().build_schedule(owner, pet)
    assert len(result["scheduled_tasks"]) == 0
    assert len(result["unscheduled_tasks"]) == 1
    assert result["unscheduled_tasks"][0].unscheduled_reason is not None


def test_high_priority_task_scheduled_before_low_priority():
    """HIGH priority task must receive an earlier scheduled_start than a LOW priority task
    when both share the same preferred_time."""
    owner = make_owner()
    pet = make_pet("Luna")
    pet.add_task(Task(title="Grooming",  duration=15, priority=Priority.LOW,
                      task_type=TaskType.GROOMING, preferred_time=480))
    pet.add_task(Task(title="Breakfast", duration=10, priority=Priority.HIGH,
                      task_type=TaskType.FEEDING,  preferred_time=480))
    scheduled = Scheduler().build_schedule(owner, pet)["scheduled_tasks"]
    high = next(t for t in scheduled if t.priority == Priority.HIGH)
    low  = next(t for t in scheduled if t.priority == Priority.LOW)
    assert high.scheduled_start <= low.scheduled_start


# ===========================================================================
# Scheduler — Recurrence
# ===========================================================================

def test_mark_recurring_task_completed_clones_next_occurrence():
    """Completing a daily recurring task should add a new task due tomorrow."""
    owner = make_owner()
    pet = make_pet()
    task = Task(title="Morning Walk", duration=30, priority=Priority.HIGH,
                task_type=TaskType.WALK, preferred_time=480,
                is_recurring=True, recurrence="daily")
    pet.add_task(task)
    owner.add_pet(pet)
    count_before = len(pet.tasks)
    Scheduler().mark_task_completed(owner, task.id)
    assert len(pet.tasks) == count_before + 1
    cloned = pet.tasks[-1]
    assert cloned.is_completed is False
    assert cloned.next_due == date.today() + timedelta(days=1)
    assert cloned.title == task.title


def test_mark_weekly_recurring_task_clones_next_week():
    owner = make_owner()
    pet = make_pet()
    task = Task(title="Bath", duration=60, priority=Priority.LOW,
                task_type=TaskType.GROOMING, is_recurring=True, recurrence="weekly")
    pet.add_task(task)
    owner.add_pet(pet)
    Scheduler().mark_task_completed(owner, task.id)
    cloned = pet.tasks[-1]
    assert cloned.next_due == date.today() + timedelta(weeks=1)


def test_mark_task_completed_non_recurring_does_not_clone():
    owner = make_owner()
    pet = make_pet()
    task = make_task("Vet Visit")
    pet.add_task(task)
    owner.add_pet(pet)
    count_before = len(pet.tasks)
    Scheduler().mark_task_completed(owner, task.id)
    assert len(pet.tasks) == count_before
    assert task.is_completed is True


def test_mark_task_completed_returns_false_when_not_found():
    owner = make_owner()
    owner.add_pet(make_pet())
    assert Scheduler().mark_task_completed(owner, 9999) is False


# ===========================================================================
# Scheduler — get_pending_tasks
# ===========================================================================

def test_get_pending_tasks_excludes_completed():
    pet = make_pet()
    t1 = make_task("Walk")
    t2 = make_task("Feed")
    t1.mark_completed()
    pet.add_task(t1)
    pet.add_task(t2)
    pending = Scheduler().get_pending_tasks(pet)
    assert len(pending) == 1
    assert pending[0].title == "Feed"


# ===========================================================================
# Rare events & additional edge cases
# ===========================================================================

# ---------------------------------------------------------------------------
# Boundary: preferred_time exactly at available_end → unscheduled
# ---------------------------------------------------------------------------

def test_preferred_time_at_window_end_is_unscheduled():
    """preferred_time == available_end means search_from >= available_end — no slot possible."""
    owner = Owner(name="Jordan", available_start=480, available_end=600)
    pet = make_pet()
    pet.add_task(Task(title="Late Task", duration=10, priority=Priority.HIGH,
                      task_type=TaskType.WALK, preferred_time=600))  # exactly at end
    result = Scheduler().build_schedule(owner, pet)
    assert len(result["unscheduled_tasks"]) == 1
    assert result["unscheduled_tasks"][0].unscheduled_reason == "outside availability window"


# ---------------------------------------------------------------------------
# Boundary: task fills the remaining window exactly → scheduled
# ---------------------------------------------------------------------------

def test_task_fills_remaining_window_exactly_is_scheduled():
    """A task whose duration equals available_end - preferred_time must just fit."""
    owner = Owner(name="Jordan", available_start=480, available_end=600)  # 120-min window
    pet = make_pet()
    pet.add_task(Task(title="Exact Fit", duration=120, priority=Priority.HIGH,
                      task_type=TaskType.WALK, preferred_time=480))
    result = Scheduler().build_schedule(owner, pet)
    assert len(result["scheduled_tasks"]) == 1
    assert result["scheduled_tasks"][0].scheduled_end == 600


# ---------------------------------------------------------------------------
# Boundary: task one minute too long → unscheduled
# ---------------------------------------------------------------------------

def test_task_one_minute_over_window_is_unscheduled():
    """duration = window_size + 1 must fail to fit."""
    owner = Owner(name="Jordan", available_start=480, available_end=600)  # 120-min window
    pet = make_pet()
    pet.add_task(Task(title="Too Long", duration=121, priority=Priority.HIGH,
                      task_type=TaskType.WALK, preferred_time=480))
    result = Scheduler().build_schedule(owner, pet)
    assert len(result["unscheduled_tasks"]) == 1


# ---------------------------------------------------------------------------
# preferred_time before available_start → placed before window (documented behaviour)
# ---------------------------------------------------------------------------

def test_preferred_time_before_available_start_places_task_early():
    """The scheduler does not clamp preferred_time upward to available_start.
    A task with preferred_time < available_start is placed at preferred_time.
    This test documents the actual behaviour so any future change is explicit."""
    owner = Owner(name="Jordan", available_start=480, available_end=1320)
    pet = make_pet()
    pet.add_task(Task(title="Early Bird", duration=30, priority=Priority.HIGH,
                      task_type=TaskType.WALK, preferred_time=300))  # 5:00 AM < 8:00 AM
    result = Scheduler().build_schedule(owner, pet)
    assert len(result["scheduled_tasks"]) == 1
    assert result["scheduled_tasks"][0].scheduled_start == 300


# ---------------------------------------------------------------------------
# Tiebreaker: same priority, same preferred_time → shorter task goes first
# ---------------------------------------------------------------------------

def test_shorter_task_scheduled_first_when_priority_and_time_tied():
    """Duration is the third sort key — shorter task gets the earlier slot."""
    owner = make_owner()
    pet = make_pet()
    pet.add_task(Task(title="Long",  duration=60, priority=Priority.MEDIUM,
                      task_type=TaskType.GROOMING, preferred_time=480))
    pet.add_task(Task(title="Short", duration=10, priority=Priority.MEDIUM,
                      task_type=TaskType.FEEDING,  preferred_time=480))
    scheduled = Scheduler().build_schedule(owner, pet)["scheduled_tasks"]
    short = next(t for t in scheduled if t.title == "Short")
    long  = next(t for t in scheduled if t.title == "Long")
    assert short.scheduled_start < long.scheduled_start


# ---------------------------------------------------------------------------
# overlaps_with is symmetric
# ---------------------------------------------------------------------------

def test_overlaps_with_is_symmetric():
    """a.overlaps_with(b) must equal b.overlaps_with(a)."""
    a = make_task("A")
    b = make_task("B")
    a.scheduled_start, a.scheduled_end = 480, 510
    b.scheduled_start, b.scheduled_end = 500, 530
    assert a.overlaps_with(b) == b.overlaps_with(a)


def test_overlaps_with_same_interval_is_true():
    """Two tasks at the identical interval must overlap."""
    a = make_task("A")
    b = make_task("B")
    a.scheduled_start, a.scheduled_end = 480, 510
    b.scheduled_start, b.scheduled_end = 480, 510
    assert a.overlaps_with(b) is True


# ---------------------------------------------------------------------------
# detect_conflicts with 3 mutually overlapping tasks → 3 pairs
# ---------------------------------------------------------------------------

def test_detect_conflicts_returns_all_pairs_for_three_overlapping_tasks():
    """Three tasks all at the same preferred_time must yield C(3,2)=3 conflict pairs."""
    pet = make_pet()
    for title in ("Walk", "Feed", "Meds"):
        pet.add_task(Task(title=title, duration=30, priority=Priority.HIGH,
                          task_type=TaskType.WALK, preferred_time=480))
    assert len(Scheduler().detect_conflicts(pet)) == 3


def test_detect_conflicts_single_task_returns_empty():
    """A single timed task cannot conflict with itself."""
    pet = make_pet()
    pet.add_task(Task(title="Walk", duration=30, priority=Priority.HIGH,
                      task_type=TaskType.WALK, preferred_time=480))
    assert Scheduler().detect_conflicts(pet) == []


# ---------------------------------------------------------------------------
# is_recurring=True but recurrence="" → no clone on completion
# ---------------------------------------------------------------------------

def test_recurring_flag_without_recurrence_string_does_not_clone():
    """is_recurring=True with recurrence='' must not auto-clone (empty string is falsy)."""
    owner = make_owner()
    pet = make_pet()
    task = Task(title="Odd Task", duration=10, priority=Priority.LOW,
                task_type=TaskType.ENRICHMENT, is_recurring=True, recurrence="")
    pet.add_task(task)
    owner.add_pet(pet)
    count_before = len(pet.tasks)
    Scheduler().mark_task_completed(owner, task.id)
    assert len(pet.tasks) == count_before  # no clone appended


# ---------------------------------------------------------------------------
# mark_task_completed finds task in a later pet, returns True
# ---------------------------------------------------------------------------

def test_mark_task_completed_finds_task_in_second_pet():
    """mark_task_completed must search all pets, not just the first."""
    owner = make_owner()
    pet1 = make_pet("Mochi")
    pet2 = make_pet("Luna")
    task = make_task("Luna Walk")
    pet2.add_task(task)
    owner.add_pet(pet1)
    owner.add_pet(pet2)
    result = Scheduler().mark_task_completed(owner, task.id)
    assert result is True
    assert task.is_completed is True


def test_mark_task_completed_returns_true_when_found():
    owner = make_owner()
    pet = make_pet()
    task = make_task()
    pet.add_task(task)
    owner.add_pet(pet)
    assert Scheduler().mark_task_completed(owner, task.id) is True


# ---------------------------------------------------------------------------
# get_pending_tasks edge cases
# ---------------------------------------------------------------------------

def test_get_pending_tasks_returns_empty_when_all_completed():
    pet = make_pet()
    for title in ("Walk", "Feed", "Meds"):
        t = make_task(title)
        t.mark_completed()
        pet.add_task(t)
    assert Scheduler().get_pending_tasks(pet) == []


def test_get_pending_tasks_sorted_by_priority():
    """Pending tasks must be returned HIGH → MEDIUM → LOW."""
    pet = make_pet()
    pet.add_task(Task(title="Low",  duration=10, priority=Priority.LOW,
                      task_type=TaskType.ENRICHMENT))
    pet.add_task(Task(title="High", duration=10, priority=Priority.HIGH,
                      task_type=TaskType.MEDICATION))
    pet.add_task(Task(title="Med",  duration=10, priority=Priority.MEDIUM,
                      task_type=TaskType.FEEDING))
    values = [t.priority.value for t in Scheduler().get_pending_tasks(pet)]
    assert values == sorted(values, reverse=True)


# ---------------------------------------------------------------------------
# Methods are robust on empty inputs
# ---------------------------------------------------------------------------

def test_build_full_schedule_with_no_pets_returns_empty_dict():
    owner = make_owner()  # no pets added
    assert Scheduler().build_full_schedule(owner) == {}


def test_get_all_tasks_with_no_pets_returns_empty_list():
    owner = make_owner()
    assert owner.get_all_tasks() == []


def test_get_tasks_sorted_by_time_on_empty_pet_returns_empty():
    assert Scheduler().get_tasks_sorted_by_time(make_pet()) == []


def test_filter_by_type_on_empty_pet_returns_empty():
    assert Scheduler().filter_by_type(make_pet(), TaskType.WALK) == []


def test_filter_by_status_on_empty_pet_returns_empty():
    assert Scheduler().filter_by_status(make_pet(), completed=False) == []


def test_get_recurring_tasks_on_empty_pet_returns_empty():
    assert Scheduler().get_recurring_tasks(make_pet()) == []


def test_detect_conflicts_on_empty_pet_returns_empty():
    assert Scheduler().detect_conflicts(make_pet()) == []


def test_detect_schedule_conflicts_on_empty_result_returns_empty():
    assert Scheduler().detect_schedule_conflicts({"scheduled_tasks": [], "unscheduled_tasks": []}) == []


def test_detect_cross_pet_conflicts_single_pet_returns_empty():
    """Only one pet in the schedule → no cross-pet pairs to compare."""
    owner = make_owner()
    pet = make_pet()
    pet.add_task(Task(title="Walk", duration=30, priority=Priority.HIGH,
                      task_type=TaskType.WALK, preferred_time=480))
    owner.add_pet(pet)
    full = Scheduler().build_full_schedule(owner)
    assert Scheduler().detect_cross_pet_conflicts(full) == []


# ---------------------------------------------------------------------------
# remove_task with duplicate-titled tasks — removes by id, not title
# ---------------------------------------------------------------------------

def test_remove_task_by_id_with_duplicate_titles():
    """When two tasks share a title, remove_task must remove only the one with the given id."""
    pet = make_pet()
    t1 = Task(title="Walk", duration=30, priority=Priority.HIGH, task_type=TaskType.WALK)
    t2 = Task(title="Walk", duration=30, priority=Priority.HIGH, task_type=TaskType.WALK)
    pet.add_task(t1)
    pet.add_task(t2)
    pet.remove_task(t1.id)
    assert len(pet.tasks) == 1
    assert pet.tasks[0].id == t2.id


# ---------------------------------------------------------------------------
# build_schedule output is sorted by scheduled_start
# ---------------------------------------------------------------------------

def test_build_schedule_output_sorted_by_start_time():
    """scheduled_tasks must be in ascending scheduled_start order regardless of input order."""
    owner = make_owner()
    pet = make_pet()
    # Added in reverse time order
    pet.add_task(Task(title="C", duration=10, priority=Priority.MEDIUM,
                      task_type=TaskType.WALK, preferred_time=600))
    pet.add_task(Task(title="B", duration=10, priority=Priority.MEDIUM,
                      task_type=TaskType.WALK, preferred_time=540))
    pet.add_task(Task(title="A", duration=10, priority=Priority.MEDIUM,
                      task_type=TaskType.WALK, preferred_time=480))
    scheduled = Scheduler().build_schedule(owner, pet)["scheduled_tasks"]
    starts = [t.scheduled_start for t in scheduled]
    assert starts == sorted(starts)


# ---------------------------------------------------------------------------
# Multiple tasks pack exactly into the window → all scheduled, none unscheduled
# ---------------------------------------------------------------------------

def test_tasks_packing_exactly_into_window_all_scheduled():
    """Three 40-minute tasks in a 120-minute window must all fit with nothing left over."""
    owner = Owner(name="Jordan", available_start=480, available_end=600)  # 120 min
    pet = make_pet()
    for i, pref in enumerate([480, 520, 560]):
        pet.add_task(Task(title=f"Task {i}", duration=40, priority=Priority.MEDIUM,
                          task_type=TaskType.WALK, preferred_time=pref))
    result = Scheduler().build_schedule(owner, pet)
    assert len(result["scheduled_tasks"]) == 3
    assert len(result["unscheduled_tasks"]) == 0


# ===========================================================================
# Input validation — Task (additional)
# ===========================================================================

def test_task_duration_one_is_valid():
    """Minimum positive duration must be accepted without error."""
    t = Task(title="Quick Check", duration=1, priority=Priority.LOW, task_type=TaskType.MEDICATION)
    assert t.duration == 1


def test_task_with_no_preferred_time_is_valid():
    """preferred_time=None (the default) must never raise."""
    t = Task(title="Anytime Play", duration=20, priority=Priority.LOW,
             task_type=TaskType.ENRICHMENT, preferred_time=None)
    assert t.preferred_time is None


def test_task_recurrence_daily_is_valid():
    t = Task(title="Walk", duration=30, priority=Priority.HIGH,
             task_type=TaskType.WALK, recurrence="daily")
    assert t.recurrence == "daily"


def test_task_recurrence_weekly_is_valid():
    t = Task(title="Bath", duration=60, priority=Priority.LOW,
             task_type=TaskType.GROOMING, recurrence="weekly")
    assert t.recurrence == "weekly"


def test_task_recurrence_empty_string_is_valid():
    """Empty string is the default non-recurring value and must be accepted."""
    t = Task(title="Vet", duration=60, priority=Priority.HIGH,
             task_type=TaskType.APPOINTMENT, recurrence="")
    assert t.recurrence == ""


def test_task_empty_title_is_accepted():
    """Task does not validate the title field — empty string must not raise."""
    t = Task(title="", duration=10, priority=Priority.LOW, task_type=TaskType.ENRICHMENT)
    assert t.title == ""


def test_task_description_field_stored_correctly():
    t = Task(title="Walk", duration=30, priority=Priority.HIGH,
             task_type=TaskType.WALK, description="Leash walk around the block")
    assert t.description == "Leash walk around the block"


def test_task_id_auto_increments():
    """Each new Task must receive a strictly higher id than the previous one."""
    t1 = make_task("A")
    t2 = make_task("B")
    t3 = make_task("C")
    assert t1.id < t2.id < t3.id


def test_task_default_fields_on_creation():
    """Verify every auto-set field starts at the correct default."""
    t = make_task()
    assert t.is_completed is False
    assert t.scheduled_start is None
    assert t.scheduled_end is None
    assert t.unscheduled_reason is None
    assert t.next_due is None
    assert t.is_recurring is False
    assert t.recurrence == ""
    assert t.description == ""


# ===========================================================================
# Input validation — Owner (additional)
# ===========================================================================

def test_owner_available_end_above_1439_raises():
    with pytest.raises(ValueError, match="available_end"):
        Owner(name="Jordan", available_start=480, available_end=1440)


def test_owner_available_start_zero_is_valid():
    """available_start=0 (midnight) is within the 0–1439 range."""
    owner = Owner(name="Jordan", available_start=0, available_end=480)
    assert owner.available_start == 0


def test_owner_available_end_1439_is_valid():
    """available_end=1439 (11:59 PM) is the maximum valid value."""
    owner = Owner(name="Jordan", available_start=0, available_end=1439)
    assert owner.available_end == 1439


def test_owner_one_minute_window_is_valid():
    """A one-minute availability window (start=1438, end=1439) must be accepted."""
    owner = Owner(name="Jordan", available_start=1438, available_end=1439)
    assert owner.total_available_minutes() == 1


# ===========================================================================
# Output validation — build_schedule
# ===========================================================================

def test_scheduled_tasks_have_start_and_end_set():
    """Every task in scheduled_tasks must have non-None scheduled_start and scheduled_end."""
    owner = make_owner()
    pet = make_pet()
    for i in range(3):
        pet.add_task(Task(title=f"Task {i}", duration=20, priority=Priority.MEDIUM,
                          task_type=TaskType.WALK, preferred_time=480 + i * 30))
    result = Scheduler().build_schedule(owner, pet)
    for t in result["scheduled_tasks"]:
        assert t.scheduled_start is not None, f"'{t.title}' missing scheduled_start"
        assert t.scheduled_end is not None,   f"'{t.title}' missing scheduled_end"


def test_scheduled_end_equals_start_plus_duration():
    """scheduled_end must always equal scheduled_start + duration exactly."""
    owner = make_owner()
    pet = make_pet()
    pet.add_task(Task(title="Walk", duration=45, priority=Priority.HIGH,
                      task_type=TaskType.WALK, preferred_time=480))
    result = Scheduler().build_schedule(owner, pet)
    t = result["scheduled_tasks"][0]
    assert t.scheduled_end == t.scheduled_start + t.duration


def test_scheduled_tasks_never_exceed_available_end():
    """No scheduled task may end after the owner's available_end."""
    owner = make_owner()
    pet = make_pet()
    for i in range(10):
        pet.add_task(Task(title=f"Task {i}", duration=30, priority=Priority.MEDIUM,
                          task_type=TaskType.WALK, preferred_time=480 + i * 30))
    result = Scheduler().build_schedule(owner, pet)
    for t in result["scheduled_tasks"]:
        assert t.scheduled_end <= owner.available_end, \
            f"'{t.title}' ends at {t.scheduled_end}, past window end {owner.available_end}"


def test_unscheduled_tasks_have_no_scheduled_times():
    """Tasks that could not be placed must have scheduled_start and scheduled_end as None."""
    owner = make_owner()
    pet = make_pet()
    pet.add_task(Task(title="Too Long", duration=900, priority=Priority.LOW,
                      task_type=TaskType.GROOMING, preferred_time=480))
    result = Scheduler().build_schedule(owner, pet)
    t = result["unscheduled_tasks"][0]
    assert t.scheduled_start is None
    assert t.scheduled_end is None


def test_unscheduled_tasks_always_have_a_reason():
    """Every task in unscheduled_tasks must have unscheduled_reason set to a non-empty string."""
    owner = Owner(name="Jordan", available_start=480, available_end=600)
    pet = make_pet()
    pet.add_task(Task(title="Overflow",    duration=200, priority=Priority.LOW,
                      task_type=TaskType.GROOMING, preferred_time=480))
    pet.add_task(Task(title="OutOfWindow", duration=10,  priority=Priority.HIGH,
                      task_type=TaskType.WALK, preferred_time=700))  # past 10 AM end
    result = Scheduler().build_schedule(owner, pet)
    for t in result["unscheduled_tasks"]:
        assert t.unscheduled_reason, f"'{t.title}' has no unscheduled_reason"


def test_scheduled_tasks_have_no_unscheduled_reason():
    """Tasks that were successfully placed must have unscheduled_reason as None."""
    owner = make_owner()
    pet = make_pet()
    pet.add_task(Task(title="Walk", duration=30, priority=Priority.HIGH,
                      task_type=TaskType.WALK, preferred_time=480))
    result = Scheduler().build_schedule(owner, pet)
    assert result["scheduled_tasks"][0].unscheduled_reason is None


def test_scheduled_start_at_or_after_preferred_time():
    """A scheduled task must never start before its preferred_time."""
    owner = make_owner()
    pet = make_pet()
    pet.add_task(Task(title="Walk", duration=30, priority=Priority.HIGH,
                      task_type=TaskType.WALK, preferred_time=600))
    t = Scheduler().build_schedule(owner, pet)["scheduled_tasks"][0]
    assert t.scheduled_start >= 600


# ===========================================================================
# Output validation — detect_conflicts
# ===========================================================================

def test_detect_conflicts_pairs_contain_exactly_two_tasks():
    """Each conflict entry must be a 2-tuple of Task objects."""
    pet = make_pet()
    pet.add_task(Task(title="A", duration=30, priority=Priority.HIGH,
                      task_type=TaskType.WALK, preferred_time=480))
    pet.add_task(Task(title="B", duration=30, priority=Priority.HIGH,
                      task_type=TaskType.FEEDING, preferred_time=480))
    for pair in Scheduler().detect_conflicts(pet):
        assert len(pair) == 2
        assert isinstance(pair[0], Task)
        assert isinstance(pair[1], Task)


def test_detect_conflicts_tasks_belong_to_pet():
    """Tasks inside conflict pairs must be the same objects that are in the pet's task list."""
    pet = make_pet()
    t1 = Task(title="A", duration=30, priority=Priority.HIGH,
               task_type=TaskType.WALK, preferred_time=480)
    t2 = Task(title="B", duration=30, priority=Priority.HIGH,
               task_type=TaskType.FEEDING, preferred_time=480)
    pet.add_task(t1)
    pet.add_task(t2)
    for a, b in Scheduler().detect_conflicts(pet):
        assert a in pet.tasks
        assert b in pet.tasks


# ===========================================================================
# Output validation — clone_for_next_occurrence
# ===========================================================================

def test_clone_has_no_unscheduled_reason():
    t = Task(title="Walk", duration=30, priority=Priority.HIGH,
             task_type=TaskType.WALK, is_recurring=True, recurrence="daily")
    assert t.clone_for_next_occurrence().unscheduled_reason is None


def test_clone_next_due_is_not_none():
    t = Task(title="Walk", duration=30, priority=Priority.HIGH,
             task_type=TaskType.WALK, is_recurring=True, recurrence="daily")
    assert t.clone_for_next_occurrence().next_due is not None


# ===========================================================================
# Output validation — Task.__str__
# ===========================================================================

def test_task_str_scheduled_contains_time():
    t = Task(title="Walk", duration=30, priority=Priority.HIGH, task_type=TaskType.WALK)
    t.scheduled_start, t.scheduled_end = 480, 510
    assert "8:00" in str(t)


def test_task_str_unscheduled_contains_unscheduled():
    t = make_task()
    assert "unscheduled" in str(t)


def test_task_str_completed_contains_done():
    t = make_task()
    t.mark_completed()
    assert "done" in str(t)


def test_task_str_pending_contains_pending():
    t = make_task()
    assert "pending" in str(t)


# ===========================================================================
# Output validation — to_dict_list
# ===========================================================================

_EXPECTED_KEYS = {"Time", "Task", "Type", "Duration (min)", "Priority", "Recurring", "Completed"}


def test_to_dict_list_contains_expected_keys():
    """Every row returned by to_dict_list must have all seven expected keys."""
    owner = make_owner()
    pet = make_pet()
    pet.add_task(Task(title="Walk", duration=30, priority=Priority.HIGH,
                      task_type=TaskType.WALK, preferred_time=480))
    result = Scheduler().build_schedule(owner, pet)
    rows = to_dict_list(result)
    assert len(rows) == 1
    assert set(rows[0].keys()) == _EXPECTED_KEYS


def test_to_dict_list_values_match_task_fields():
    """Row values must accurately reflect the corresponding Task's data."""
    owner = make_owner()
    pet = make_pet()
    pet.add_task(Task(title="Morning Walk", duration=30, priority=Priority.HIGH,
                      task_type=TaskType.WALK, preferred_time=480,
                      is_recurring=True, recurrence="daily"))
    result = Scheduler().build_schedule(owner, pet)
    row = to_dict_list(result)[0]
    assert row["Task"] == "Morning Walk"
    assert row["Duration (min)"] == 30
    assert row["Priority"] == "HIGH"
    assert row["Type"] == "walk"
    assert row["Recurring"] is True
    assert row["Completed"] is False


def test_to_dict_list_empty_when_no_scheduled_tasks():
    owner = make_owner()
    pet = make_pet()
    pet.add_task(Task(title="Too Long", duration=900, priority=Priority.LOW,
                      task_type=TaskType.GROOMING, preferred_time=480))
    result = Scheduler().build_schedule(owner, pet)
    assert to_dict_list(result) == []
