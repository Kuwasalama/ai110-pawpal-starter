"""Basic tests for the PawPal+ logic layer."""

from datetime import date, timedelta

from pawpal_system import Owner, Pet, Scheduler, Task


def test_mark_complete_changes_status():
    """mark_complete() should flip a task from not-done to done."""
    task = Task("Morning walk", duration_minutes=30, priority="high")

    assert task.completed is False  # starts out not done

    task.mark_complete()

    assert task.completed is True  # now marked done


def test_adding_task_increases_pet_task_count():
    """add_task() should grow the pet's task list by one."""
    pet = Pet(name="Biscuit", species="dog")

    assert len(pet.tasks) == 0  # starts with no tasks

    pet.add_task(Task("Feeding", duration_minutes=10, priority="high"))

    assert len(pet.tasks) == 1  # one task after adding


def test_sort_returns_pinned_tasks_in_chronological_order():
    """sort_by_priority() should return pinned-time tasks earliest-first."""
    # Three tasks pinned to specific clock times, added OUT of order on purpose.
    pet = Pet(name="Biscuit", species="dog")
    pet.add_task(Task("Evening walk", duration_minutes=30, time="17:00"))
    pet.add_task(Task("Morning walk", duration_minutes=30, time="08:00"))
    pet.add_task(Task("Midday feed", duration_minutes=15, time="12:00"))

    owner = Owner(name="Sam", available_minutes=180)
    owner.add_pet(pet)
    scheduler = Scheduler(owner)

    ordered_titles = [task.title for task in scheduler.sort_by_priority()]

    # Regardless of insertion order, the clock should drive the order.
    assert ordered_titles == ["Morning walk", "Midday feed", "Evening walk"]


def test_completing_daily_task_creates_task_for_next_day():
    """Completing a daily task should queue a fresh copy due one day later."""
    today = date.today()
    pet = Pet(name="Biscuit", species="dog")
    daily = Task(
        "Morning walk",
        duration_minutes=30,
        priority="high",
        frequency="daily",
        due_date=today,
    )
    pet.add_task(daily)

    next_task = pet.complete_task(daily)

    # The original is done; a brand-new instance exists for tomorrow.
    assert daily.completed is True
    assert next_task is not None
    assert next_task.completed is False
    assert next_task.due_date == today + timedelta(days=1)
    # And it was auto-appended to the pet's list (original + next = 2).
    assert len(pet.tasks) == 2


def test_conflict_detection_flags_duplicate_times():
    """detect_conflicts() should warn when two pinned tasks overlap in time."""
    pet = Pet(name="Biscuit", species="dog")
    # Both pinned to 08:00 for 30 min — a direct overlap.
    pet.add_task(Task("Walk", duration_minutes=30, time="08:00"))
    pet.add_task(Task("Vet call", duration_minutes=30, time="08:00"))

    owner = Owner(name="Sam", available_minutes=120)
    owner.add_pet(pet)
    scheduler = Scheduler(owner)

    warning = scheduler.detect_conflicts()

    # A non-empty string naming both tasks signals the clash was caught.
    assert warning != ""
    assert "Walk" in warning
    assert "Vet call" in warning
