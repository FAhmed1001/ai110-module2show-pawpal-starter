# pawpal_system.py
# Logic layer for PawPal+ — all backend classes live here

from dataclasses import dataclass, field
from typing import List


@dataclass
class Owner:
    name: str
    available_time: int  # total minutes available per day
    pets: List = field(default_factory=list)

    def add_pet(self, pet):
        """Add a Pet to this owner's list of pets."""
        self.pets.append(pet)

    def get_schedule(self):
        """Return a flat list of all tasks across every pet."""
        all_tasks = []
        for pet in self.pets:
            all_tasks.extend(pet.get_tasks())
        return all_tasks


@dataclass
class Task:
    name: str
    category: str  # e.g. "walk", "feeding", "meds", "grooming"
    duration: int  # minutes
    priority: int  # 1 (low) to 5 (high)
    completed: bool = False

    def mark_complete(self):
        """Mark this task as completed."""
        self.completed = True

    def __str__(self):
        """Return a readable one-line summary of the task."""
        status = "done" if self.completed else "pending"
        return f"[{self.category}] {self.name} — {self.duration} min | priority {self.priority} | {status}"


@dataclass
class Pet:
    name: str
    species: str
    age: int
    owner: Owner
    tasks: List[Task] = field(default_factory=list)

    def add_task(self, task: Task):
        """Add a Task to this pet's task list."""
        self.tasks.append(task)

    def remove_task(self, task: Task):
        """Remove a Task from this pet's task list."""
        self.tasks.remove(task)

    def get_tasks(self) -> List[Task]:
        """Return all tasks assigned to this pet."""
        return self.tasks


def _pet_emoji(species: str) -> str:
    return {"dog": "🐶", "cat": "🐱", "bird": "🐦", "rabbit": "🐰"}.get(species.lower(), "🐾")


class Scheduler:
    def __init__(self, pet: Pet, available_time: int):
        self.pet = pet
        self.available_time = available_time  # minutes
        self.tasks = pet.get_tasks()

    def sort_by_priority(self) -> List[Task]:
        """Return tasks sorted from highest to lowest priority."""
        return sorted(self.tasks, key=lambda t: t.priority, reverse=True)

    def filter_by_time(self) -> List[Task]:
        """Select tasks greedily by priority until the time budget is exhausted."""
        sorted_tasks = self.sort_by_priority()
        selected = []
        time_remaining = self.available_time
        for task in sorted_tasks:
            if task.duration <= time_remaining:
                selected.append(task)
                time_remaining -= task.duration
        return selected

    def generate_plan(self) -> List[Task]:
        """Return the final scheduled task list for the day."""
        return self.filter_by_time()

    def explain_plan(self) -> str:
        """Return a formatted terminal summary of the schedule with skipped tasks noted."""
        plan = self.generate_plan()
        total_time = sum(t.duration for t in plan)
        skipped = [t for t in self.tasks if t not in plan]
        owner = self.pet.owner

        lines = [
            "=" * 45,
            "      PawPal+ — Today's Schedule",
            "=" * 45,
            f"Owner: {owner.name} | Time Budget: {self.available_time} min",
            "",
        ]

        if not plan:
            lines.append("  No tasks could be scheduled within the time budget.")
        else:
            for pet in owner.pets:
                lines.append(f"{_pet_emoji(pet.species)} {pet.name} ({pet.species})")
                for task in pet.get_tasks():
                    in_plan = task in plan
                    icon = "✅" if in_plan else "⏭ "
                    stars = "★" * task.priority + "☆" * (5 - task.priority)
                    note = " ← skipped" if not in_plan else ""
                    lines.append(
                        f"  {icon} [{task.category.upper():10}] "
                        f"{task.name:<22} {task.duration:>3} min  {stars}{note}"
                    )
                lines.append("")

        lines.append("-" * 45)
        lines.append(f"Time used: {total_time} / {self.available_time} min")
        lines.append(f"Tasks scheduled: {len(plan)} | Skipped: {len(skipped)}")
        lines.append("=" * 45)

        return "\n".join(lines)
