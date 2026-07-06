"""PawPal+ logic layer.

Skeleton classes generated from diagrams/uml.mmd.
No scheduling logic yet — just structure (attributes + method stubs).
"""

from __future__ import annotations

from dataclasses import dataclass, field


# Maps priority labels to a sortable rank (higher = more important).
PRIORITY_RANK = {"low": 1, "medium": 2, "high": 3}


@dataclass
class Task:
    """A single pet-care task (walk, feeding, meds, etc.)."""

    title: str
    duration_minutes: int
    priority: str = "medium"
    category: str = ""
    recurring: bool = False

    def priority_rank(self) -> int:
        """Return a numeric rank so tasks can be sorted by priority."""
        raise NotImplementedError


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
        raise NotImplementedError


@dataclass
class Owner:
    """The pet owner and their scheduling constraints/preferences."""

    name: str
    preferred_times: list[str] = field(default_factory=list)
    available_minutes: int = 0
    pets: list[Pet] = field(default_factory=list)

    def add_pet(self, pet: Pet) -> None:
        """Register a pet under this owner."""
        raise NotImplementedError


class Scheduler:
    """Engine that turns an owner's tasks + constraints into a daily plan."""

    def __init__(self, owner: Owner, tasks: list[Task]) -> None:
        self.owner = owner
        self.tasks = tasks

    def sort_by_priority(self) -> list[Task]:
        """Return tasks ordered by priority (highest first)."""
        raise NotImplementedError

    def fits_in_time(self, task: Task) -> bool:
        """Return True if the task fits in the owner's remaining time."""
        raise NotImplementedError

    def generate_schedule(self) -> list[dict]:
        """Build the daily plan: an ordered list of scheduled task entries."""
        raise NotImplementedError

    def explain(self) -> str:
        """Explain why the schedule chose and ordered tasks as it did."""
        raise NotImplementedError
