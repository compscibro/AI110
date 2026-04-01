"""
tests/test_pawpal.py — Automated tests for PawPal+ core logic.

Run with: python -m pytest
"""

import pytest
from pawpal_system import Owner, Pet, Task, Priority, TaskType, Scheduler, _reset_id_counter


@pytest.fixture(autouse=True)
def reset_ids():
    """Reset the global task ID counter before each test for clean IDs."""
    _reset_id_counter()


def make_task(title="Test Task", duration=30, priority=Priority.MEDIUM, task_type=TaskType.WALK):
    """Helper to create a Task with sensible defaults."""
    return Task(title=title, duration=duration, priority=priority, task_type=task_type)


# ---------------------------------------------------------------------------
# Test 1: Task completion
# ---------------------------------------------------------------------------

def test_mark_completed_changes_status():
    """Calling mark_completed() should set is_completed to True."""
    task = make_task()
    assert task.is_completed is False
    task.mark_completed()
    assert task.is_completed is True


# ---------------------------------------------------------------------------
# Test 2: Task addition
# ---------------------------------------------------------------------------

def test_add_task_increases_pet_task_count():
    """Adding a task to a Pet should increase its task count by one."""
    pet = Pet(name="Mochi", species="dog", age=3)
    assert len(pet.tasks) == 0

    pet.add_task(make_task("Morning Walk"))
    assert len(pet.tasks) == 1

    pet.add_task(make_task("Breakfast"))
    assert len(pet.tasks) == 2
