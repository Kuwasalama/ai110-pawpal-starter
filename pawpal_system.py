"""PawPal+ logic layer: Owner, Pet, Task, and the Scheduler that plans the day."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, timedelta

# How far ahead the next occurrence of a recurring task lands. timedelta does
# the calendar math for us: adding it to a date rolls months/years correctly.
FREQUENCY_INTERVALS = {
    "daily": timedelta(days=1),
    "weekly": timedelta(weeks=1),
}


# Maps priority labels to a sortable rank (higher = more important).
PRIORITY_RANK = {"low": 1, "medium": 2, "high": 3}

# If the owner lists no preferred times, start the day here.
DEFAULT_START = "08:00"


def is_valid_time(hhmm: str) -> bool:
    """Return True if ``hhmm`` is a real 24-hour 'HH:MM' string.

    Used to validate owner-entered times before they reach the scheduler,
    which assumes well-formed times.
    """
    parts = hhmm.split(":")
    if len(parts) != 2:
        return False
    hours, minutes = parts
    if not (hours.isdigit() and minutes.isdigit()):
        return False
    return 0 <= int(hours) <= 23 and 0 <= int(minutes) <= 59


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
    # Optional fixed time the owner wants this task at, as "HH:MM".
    # Empty means "no set time" — the scheduler places it by priority as before.
    time: str = ""
    # How often this task repeats: "once" (default), "daily", or "weekly".
    frequency: str = "once"
    # The day this task is due. None means "not date-tracked".
    due_date: date | None = None
    category: str = ""
    completed: bool = False

    def next_occurrence(self) -> Task | None:
        """Build the next instance of a recurring task, or None if it's one-off.

        The new task is a fresh, not-completed copy with its due date pushed
        forward by one interval. We add a ``timedelta`` to the due date so the
        calendar math (month/year rollovers, leap days) is handled correctly;
        if the task had no due date, we count from today.
        """
        interval = FREQUENCY_INTERVALS.get(self.frequency)
        if interval is None:
            return None
        base = self.due_date or date.today()
        return Task(
            title=self.title,
            duration_minutes=self.duration_minutes,
            priority=self.priority,
            time=self.time,
            frequency=self.frequency,
            due_date=base + interval,
            category=self.category,
        )

    def mark_complete(self) -> Task | None:
        """Mark this task done and return its next occurrence if it recurs.

        This is where completion meets frequency: finishing a daily or weekly
        task hands back the next instance so the caller can queue it. A one-off
        task returns None. Marking done never mutates anything but this task.
        """
        self.completed = True
        return self.next_occurrence()

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

    def complete_task(self, task: Task) -> Task | None:
        """Mark one of this pet's tasks done, auto-queuing its next occurrence.

        If the task recurs (daily/weekly), the next instance is created and
        appended to this pet's list right away, and also returned. One-off
        tasks are simply marked done and return None.
        """
        next_task = task.mark_complete()
        if next_task is not None:
            self.tasks.append(next_task)
        return next_task


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

    def filter_tasks(
        self, completed: bool | None = None, pet_name: str | None = None
    ) -> list[Task]:
        """Return tasks narrowed by completion status and/or pet name.

        Both filters are optional. ``completed=True`` keeps only done tasks,
        ``completed=False`` only not-done ones, and ``None`` keeps either.
        ``pet_name`` limits results to that pet; ``None`` spans all pets.
        We walk ``owner.pets`` directly (not the flattened ``self.tasks``) so
        we still know which pet each task belongs to.
        """
        results: list[Task] = []
        for pet in self.owner.pets:
            if pet_name is not None and pet.name != pet_name:
                continue
            for task in pet.tasks:
                if completed is not None and task.completed != completed:
                    continue
                results.append(task)
        return results

    def sort_by_priority(self) -> list[Task]:
        """Return tasks in the order the day should be planned.

        A task the owner pinned to a specific time comes first, earliest time
        first, so those get placed before anything flexible. Everything without
        a set time then follows the original rule: highest priority first, ties
        broken by longest duration.

        The lambda builds one sort key per task. ``0 if task.time else 1`` sends
        pinned tasks to the front; ``_to_minutes(task.time)`` orders them by the
        clock. For flexible tasks we negate priority and duration so that a plain
        ascending sort still puts the highest/longest first.
        """
        return sorted(
            self.tasks,
            key=lambda task: (
                0 if task.time else 1,
                _to_minutes(task.time) if task.time else 0,
                -task.priority_rank(),
                -task.duration_minutes,
            ),
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
            # If the owner pinned a time, jump the clock forward to it so the
            # task lands when they asked. We never move the clock backwards.
            if task.time:
                clock = max(clock, _to_minutes(task.time))

            if self.fits_in_time(task, remaining):
                used = task.duration_minutes
                shortened = False
                if task.time:
                    reason = f"{task.priority} priority; owner set it for {task.time}"
                else:
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

    def detect_conflicts(self) -> str:
        """Return a warning if any owner-pinned tasks overlap in time.

        Lightweight strategy: only tasks with an explicit ``time`` can conflict
        (untimed tasks are placed sequentially and never overlap). Each pinned
        task is treated as the interval ``[start, start + duration)``. Two of
        them clash when ``a_start < b_end and b_start < a_end``. We check every
        pair — the task count is tiny — and note whether the clash is on the
        same pet or across pets. Returns an empty string when there's no
        conflict; this only *warns*, it never changes the plan.
        """
        timed = [
            (pet.name, task)
            for pet in self.owner.pets
            for task in pet.tasks
            if task.time
        ]

        messages: list[str] = []
        for i in range(len(timed)):
            for j in range(i + 1, len(timed)):
                pet_a, a = timed[i]
                pet_b, b = timed[j]
                a_start = _to_minutes(a.time)
                a_end = a_start + a.duration_minutes
                b_start = _to_minutes(b.time)
                b_end = b_start + b.duration_minutes
                if a_start < b_end and b_start < a_end:
                    whose = "same pet" if pet_a == pet_b else "different pets"
                    messages.append(
                        f"'{a.title}' ({pet_a}, {a.time}–{_to_hhmm(a_end)}) overlaps "
                        f"'{b.title}' ({pet_b}, {b.time}–{_to_hhmm(b_end)}) [{whose}]"
                    )

        if not messages:
            return ""
        return "⚠ Schedule conflict detected:\n" + "\n".join(
            "  - " + m for m in messages
        )

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
