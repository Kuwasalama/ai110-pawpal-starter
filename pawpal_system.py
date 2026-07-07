"""PawPal+ logic layer: Owner, Pet, Task, and the Scheduler that plans the day."""

from __future__ import annotations

from dataclasses import dataclass, field


# Maps priority labels to a sortable rank (higher = more important).
PRIORITY_RANK = {"low": 1, "medium": 2, "high": 3}

# If the owner lists no preferred times, start the day here.
DEFAULT_START = "08:00"


def _to_minutes(hhmm: str) -> int:
    """Turn a 'HH:MM' string into minutes since midnight."""
    hours, minutes = hhmm.split(":")
    return int(hours) * 60 + int(minutes)


def _to_hhmm(total_minutes: int) -> str:
    """Turn minutes since midnight back into a 'HH:MM' string."""
    return f"{total_minutes // 60:02d}:{total_minutes % 60:02d}"


@dataclass
class Task:
    """A single pet-care task (walk, feeding, meds, etc.)."""

    title: str
    duration_minutes: int
    priority: str = "medium"
    category: str = ""
    recurring: bool = False
    completed: bool = False

    def mark_complete(self) -> None:
        """Mark this task as done."""
        self.completed = True

    def priority_rank(self) -> int:
        """Return a numeric rank so tasks can be sorted by priority.

        Unknown labels fall back to 0 so a typo can't crash the scheduler.
        """
        return PRIORITY_RANK.get(self.priority, 0)


@dataclass
class Pet:
    """A pet and the care tasks it needs."""

    name: str
    species: str
    breed: str = ""
    age: int = 0
    tasks: list[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Attach a care task to this pet."""
        self.tasks.append(task)


@dataclass
class Owner:
    """The pet owner and their scheduling constraints/preferences."""

    name: str
    preferred_times: list[str] = field(default_factory=list)
    available_minutes: int = 0
    pets: list[Pet] = field(default_factory=list)

    def add_pet(self, pet: Pet) -> None:
        """Register a pet under this owner."""
        self.pets.append(pet)

    def day_start(self) -> int:
        """Minutes-since-midnight the day begins: the earliest preferred time."""
        if not self.preferred_times:
            return _to_minutes(DEFAULT_START)
        return min(_to_minutes(t) for t in self.preferred_times)


class Scheduler:
    """Engine that turns an owner's tasks + constraints into a daily plan."""

    def __init__(self, owner: Owner) -> None:
        """Set up the scheduler for an owner and collect their pets' tasks."""
        self.owner = owner
        # Fix #1: pull the tasks straight off the owner's pets so the planner
        # always works from the real to-do lists, not a hand-passed copy.
        self.tasks = self.collect_tasks()

    def collect_tasks(self) -> list[Task]:
        """Gather every task from every pet the owner has."""
        return [task for pet in self.owner.pets for task in pet.tasks]

    def sort_by_priority(self) -> list[Task]:
        """Return tasks ordered by priority (highest first).

        Ties are broken by longest duration first, per the design decision.
        """
        return sorted(
            self.tasks,
            key=lambda task: (task.priority_rank(), task.duration_minutes),
            reverse=True,
        )

    def fits_in_time(self, task: Task, remaining_minutes: int) -> bool:
        """Return True if the task fits in the time still left in the day.

        Fix #2: the caller passes how many minutes are still free, so the
        planner accounts for tasks already scheduled instead of assuming the
        day is empty every time.
        """
        return task.duration_minutes <= remaining_minutes

    def generate_schedule(self) -> list[dict]:
        """Build the daily plan: an ordered list of scheduled task entries.

        Walks the priority-sorted tasks. A task that fits gets its full time.
        A task that doesn't fully fit is still included at a *shortened*
        length as long as at least half its normal time is free (design
        decision), so nothing meaningful is dropped silently. Anything that
        can't get at least half is recorded on ``self.skipped``.
        """
        clock = self.owner.day_start()
        remaining = self.owner.available_minutes
        plan: list[dict] = []
        self.skipped: list[Task] = []

        for task in self.sort_by_priority():
            if self.fits_in_time(task, remaining):
                used = task.duration_minutes
                shortened = False
                reason = f"{task.priority} priority; fit in the {remaining} min still free"
            elif remaining * 2 >= task.duration_minutes:
                # At least half the task's time is available: give it the
                # leftover minutes rather than skipping it entirely.
                used = remaining
                shortened = True
                reason = (
                    f"{task.priority} priority; shortened to {used} of "
                    f"{task.duration_minutes} min to use the time left"
                )
            else:
                self.skipped.append(task)
                continue

            plan.append(
                {
                    "time": _to_hhmm(clock),
                    "title": task.title,
                    "duration_minutes": used,
                    "full_duration": task.duration_minutes,
                    "priority": task.priority,
                    "shortened": shortened,
                    "reason": reason,
                }
            )
            clock += used
            remaining -= used

        return plan

    def explain(self) -> str:
        """Explain, in plain language, what was scheduled and what was skipped."""
        plan = self.generate_schedule()
        lines = [
            f"Planned {len(plan)} task(s) starting at "
            f"{_to_hhmm(self.owner.day_start())}, "
            f"within {self.owner.available_minutes} available minutes."
        ]
        for entry in plan:
            lines.append(f"  {entry['time']} — {entry['title']} ({entry['reason']})")
        if self.skipped:
            skipped_titles = ", ".join(task.title for task in self.skipped)
            lines.append(
                f"Left off (less than half their time was free): {skipped_titles}."
            )
        return "\n".join(lines)
