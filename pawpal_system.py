# pawpal_system.py
# Logic layer for PawPal+ — all backend classes live here

from dataclasses import dataclass, field, replace
from datetime import date, timedelta
from typing import List, Optional


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
    recurrence: Optional[str] = None  # None, "daily", or "weekly"
    time_slot: Optional[int] = None  # minutes from midnight, e.g. 480 = 08:00
    due_date: Optional[date] = None

    def mark_complete(self):
        """Mark this task as completed."""
        self.completed = True

    def next_occurrence(self) -> Optional["Task"]:
        """Return a fresh copy of this task for its next occurrence, or None if not recurring."""
        if self.recurrence is None:
            return None
        if self.recurrence == "daily":
            next_due = date.today() + timedelta(days=1)
        else:  # "weekly"
            next_due = date.today() + timedelta(weeks=1)
        return replace(self, completed=False, due_date=next_due)

    def __str__(self):
        """Return a readable one-line summary of the task."""
        status = "done" if self.completed else "pending"
        recur = f" ↺{self.recurrence}" if self.recurrence else ""
        slot = f" @{self.time_slot // 60:02d}:{self.time_slot % 60:02d}" if self.time_slot is not None else ""
        due = f" due {self.due_date}" if self.due_date else ""
        return f"[{self.category}] {self.name}{recur}{slot}{due} — {self.duration} min | priority {self.priority} | {status}"


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
    def __init__(self, owner: Owner, available_time: int):
        self.owner = owner
        self.available_time = available_time  # minutes
        self.tasks = owner.get_schedule()

    def generate_plan(self, sort_by: str = "priority") -> List[Task]:
        """Return tasks greedily selected within the available time budget.

        Uses a greedy algorithm: tasks are sorted, then accepted one-by-one until
        the time budget is exhausted. This runs in O(n log n) and works well for
        small task lists, but may miss an optimal combination (see: 0/1 knapsack).

        Args:
            sort_by: Ordering strategy before selection.
                'priority' — highest priority first (default).
                'duration' — shortest tasks first (fits more tasks in budget).

        Returns:
            Ordered list of Task objects that fit within available_time.
        """
        if sort_by == "duration":
            sorted_tasks = sorted(self.tasks, key=lambda t: t.duration)
        else:
            sorted_tasks = sorted(self.tasks, key=lambda t: t.priority, reverse=True)
        selected = []
        time_remaining = self.available_time
        for task in sorted_tasks:
            if task.duration <= time_remaining:
                selected.append(task)
                time_remaining -= task.duration
        return selected

    def sort_by_time(self) -> List[Task]:
        """Return all tasks sorted chronologically by their assigned time_slot.

        Tasks with no time_slot (None) are pushed to the end of the list using
        float('inf') as a sort key, so they don't interfere with timed tasks.

        Returns:
            List of Task objects ordered by time_slot ascending, untimed tasks last.
        """
        return sorted(
            self.tasks,
            key=lambda t: t.time_slot if t.time_slot is not None else float('inf')
        )

    def complete_task(self, task: Task) -> Optional[Task]:
        """Mark a task complete and, if recurring, add the next occurrence to its pet.

        Returns the newly created Task, or None for non-recurring tasks.
        """
        task.mark_complete()
        next_task = task.next_occurrence()
        if next_task is not None:
            for pet in self.owner.pets:
                if task in pet.get_tasks():
                    pet.add_task(next_task)
                    break
            self.tasks = self.owner.get_schedule()
        return next_task

    def filter_tasks(self, pet_name: Optional[str] = None, completed: Optional[bool] = None) -> List[Task]:
        """Return a filtered subset of tasks based on pet name and/or completion status.

        Filters are applied with AND logic — both conditions must match if both are given.
        Passing None for either argument disables that filter (returns all values for that field).

        Args:
            pet_name: If provided, only return tasks belonging to the named pet.
            completed: If True, return only completed tasks. If False, only pending.
                       If None, return tasks regardless of status.

        Returns:
            List of matching Task objects in their original insertion order.
        """
        task_to_pet = {id(t): pet for pet in self.owner.pets for t in pet.get_tasks()}
        result = []
        for task in self.tasks:
            if pet_name is not None and task_to_pet.get(id(task)) is not None:
                if task_to_pet[id(task)].name != pet_name:
                    continue
            if completed is not None and task.completed != completed:
                continue
            result.append(task)
        return result

    def _conflict_message(self, a: Task, b: Task, task_to_pet: dict) -> str:
        """Format a human-readable description of a time-slot overlap between two tasks.

        Determines whether the conflict is within the same pet or across different pets,
        and includes the time ranges of both tasks for easy debugging.

        Args:
            a: The first overlapping Task.
            b: The second overlapping Task.
            task_to_pet: Mapping of id(task) → Pet, used to resolve ownership.

        Returns:
            A string like: 'Walk' (08:00–08:30) overlaps 'Breakfast' (08:15–08:25) [same pet: Biscuit]
        """
        def fmt(m: int) -> str:
            return f"{m // 60:02d}:{m % 60:02d}"

        pet_a = task_to_pet.get(id(a))
        pet_b = task_to_pet.get(id(b))
        context = (f"same pet: {pet_a.name}" if pet_a is pet_b
                   else f"cross-pet: {pet_a.name if pet_a else '?'} vs {pet_b.name if pet_b else '?'}")
        return (f"'{a.name}' ({fmt(a.time_slot)}–{fmt(a.time_slot + a.duration)}) "
                f"overlaps '{b.name}' ({fmt(b.time_slot)}–{fmt(b.time_slot + b.duration)}) [{context}]")

    def detect_conflicts(self) -> List[str]:
        """Return descriptions of time-slot overlaps, noting same-pet vs cross-pet conflicts.

        Returns a single warning string if the check itself fails, so callers never crash.
        """
        try:
            task_to_pet = {id(t): pet for pet in self.owner.pets for t in pet.get_tasks()}
            timed = [t for t in self.tasks if t.time_slot is not None]

            conflicts = []
            for i, a in enumerate(timed):
                for b in timed[i + 1:]:
                    a_end = a.time_slot + a.duration
                    b_end = b.time_slot + b.duration
                    if a.time_slot < b_end and b.time_slot < a_end:
                        conflicts.append(self._conflict_message(a, b, task_to_pet))
            return conflicts
        except Exception as e:
            return [f"⚠ Conflict check could not complete: {e}"]

    def explain_plan(self, sort_by: str = "priority") -> str:
        """Return a formatted terminal summary of the schedule with skipped tasks noted."""
        plan = self.generate_plan(sort_by=sort_by)
        total_time = sum(t.duration for t in plan)
        skipped = [t for t in self.tasks if t not in plan]
        owner = self.owner

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
                    icon = "✅" if task.completed else ("📋" if in_plan else "⏭ ")
                    stars = "★" * task.priority + "☆" * (5 - task.priority)
                    note = " ← skipped" if not in_plan else ""
                    recur = f" ↺{task.recurrence}" if task.recurrence else "  "
                    slot = f" @{task.time_slot // 60:02d}:{task.time_slot % 60:02d}" if task.time_slot is not None else ""
                    due = f" due {task.due_date}" if task.due_date else ""
                    lines.append(
                        f"  {icon} [{task.category.upper():10}] "
                        f"{task.name:<22}{recur} {task.duration:>3} min  {stars}{slot}{due}{note}"
                    )
                lines.append("")

        lines.append("-" * 45)
        lines.append(f"Time used: {total_time} / {self.available_time} min")
        lines.append(f"Tasks scheduled: {len(plan)} | Skipped: {len(skipped)}")
        lines.append("=" * 45)

        return "\n".join(lines)
