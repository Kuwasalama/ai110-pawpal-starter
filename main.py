"""Temporary testing ground for the PawPal+ logic layer.

Builds an owner with two pets and several tasks, then prints today's
schedule to the terminal so we can verify the scheduler by eye.
"""

from pawpal_system import Owner, Pet, Scheduler, Task


def main() -> None:
    # Owner with limited time so the scheduler has to make real choices.
    owner = Owner(name="Jordan", preferred_times=["07:30"], available_minutes=70)

    # Pet 1: a dog with two tasks.
    biscuit = Pet(name="Biscuit", species="dog", breed="Golden Retriever", age=4)
    biscuit.add_task(Task("Morning walk", duration_minutes=30, priority="high"))
    biscuit.add_task(Task("Feeding", duration_minutes=10, priority="high"))

    # Pet 2: a cat with three tasks.
    mochi = Pet(name="Mochi", species="cat", breed="Tabby", age=2)
    mochi.add_task(Task("Give meds", duration_minutes=5, priority="high"))
    mochi.add_task(Task("Clean litter", duration_minutes=15, priority="medium"))
    mochi.add_task(Task("Playtime", duration_minutes=20, priority="low"))

    owner.add_pet(biscuit)
    owner.add_pet(mochi)

    scheduler = Scheduler(owner)
    plan = scheduler.generate_schedule()

    print(f"Today's schedule for {owner.name}:")
    for entry in plan:
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
