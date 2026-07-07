"""Basic tests for the PawPal+ logic layer."""

from pawpal_system import Pet, Task


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
