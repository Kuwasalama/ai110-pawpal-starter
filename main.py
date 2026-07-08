"""Temporary testing ground for the PawPal+ logic layer.

Builds an owner with two pets and several tasks added deliberately out of
order, then prints the sorted plan and a few filtered views to the terminal
so we can verify the sorting and filtering methods by eye.
"""

from datetime import date

from pawpal_system import Owner, Pet, Scheduler, Task


def main() -> None:
    # Owner with limited time so the scheduler has to make real choices.
    owner = Owner(name="Jordan", preferred_times=["07:30"], available_minutes=70)

    # Pet 1: a dog. Tasks added out of priority/duration order on purpose.
    biscuit = Pet(name="Biscuit", species="dog", breed="Golden Retriever", age=4)
    biscuit.add_task(Task("Feeding", duration_minutes=10, priority="high"))
    biscuit.add_task(Task("Morning walk", duration_minutes=30, priority="high"))

    # Pet 2: a cat. A low-priority task is added first, and a short
    # high-priority task is pinned to a specific time to prove it jumps ahead.
    mochi = Pet(name="Mochi", species="cat", breed="Tabby", age=2)
    mochi.add_task(Task("Playtime", duration_minutes=20, priority="low"))
    mochi.add_task(Task("Clean litter", duration_minutes=15, priority="medium"))
    mochi.add_task(Task("Give meds", duration_minutes=5, priority="high", time="09:00"))
    # Deliberate conflict: a different pet's task pinned to the same 09:00 slot.
    biscuit.add_task(
        Task("Vet call", duration_minutes=15, priority="high", time="09:00")
    )

    owner.add_pet(biscuit)
    owner.add_pet(mochi)

    # A recurring task: a daily walk due today. Completing it should auto-queue
    # tomorrow's instance on the same pet.
    daily_walk = Task(
        "Evening walk",
        duration_minutes=25,
        priority="medium",
        frequency="daily",
        due_date=date(2026, 7, 8),
    )
    biscuit.add_task(daily_walk)

    # Mark a couple of tasks done so the completion filter has something to show.
    biscuit.tasks[0].mark_complete()  # Feeding
    mochi.tasks[1].mark_complete()    # Clean litter

    # Complete the recurring task through the pet so the next occurrence is
    # created and appended automatically.
    print("Recurring task demo:")
    print(f"  Before: Biscuit has {len(biscuit.tasks)} tasks; "
          f"'{daily_walk.title}' due {daily_walk.due_date} ({daily_walk.frequency}).")
    next_walk = biscuit.complete_task(daily_walk)
    print(f"  Completed '{daily_walk.title}' — completed={daily_walk.completed}.")
    print(f"  After: Biscuit has {len(biscuit.tasks)} tasks; "
          f"next '{next_walk.title}' auto-created for {next_walk.due_date}.\n")

    scheduler = Scheduler(owner)

    # --- Conflict detection: warn on overlapping pinned times ---
    warning = scheduler.detect_conflicts()
    print(warning if warning else "No schedule conflicts.")
    print()

    # --- Sorting: the order the day is planned in ---
    print("Planning order (sort_by_priority):")
    for task in scheduler.sort_by_priority():
        pin = f" @{task.time}" if task.time else ""
        print(f"  {task.title}{pin} — {task.priority}, {task.duration_minutes} min")

    # --- Filtering: completion status and pet name ---
    print("\nNot yet done (filter_tasks completed=False):")
    for task in scheduler.filter_tasks(completed=False):
        print(f"  {task.title}")

    print("\nAlready done (filter_tasks completed=True):")
    for task in scheduler.filter_tasks(completed=True):
        print(f"  {task.title}")

    print("\nMochi's tasks (filter_tasks pet_name='Mochi'):")
    for task in scheduler.filter_tasks(pet_name="Mochi"):
        print(f"  {task.title}")

    print("\nMochi's unfinished tasks (both filters):")
    for task in scheduler.filter_tasks(completed=False, pet_name="Mochi"):
        print(f"  {task.title}")

    # --- The actual schedule ---
    print("\nToday's schedule for", owner.name + ":")
    for entry in scheduler.generate_schedule():
        if entry["shortened"]:
            length = f"{entry['duration_minutes']} of {entry['full_duration']} min, shortened"
        else:
            length = f"{entry['duration_minutes']} min"
        print(
            f"  {entry['time']} — {entry['title']} "
            f"({length}) [priority: {entry['priority']}]"
        )

    print()
    print(scheduler.explain())


if __name__ == "__main__":
    main()
