# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## Features

- **Greedy schedule generation** — builds a daily plan using a greedy algorithm (O(n log n)): tasks are sorted, then accepted one-by-one until the time budget is exhausted. Fast and intuitive for small task lists; may miss an optimal combination in edge cases (see: 0/1 knapsack).
- **Priority-first sorting** — `generate_plan(sort_by="priority")` ranks tasks 1–5 and selects the highest-priority tasks first, so critical care (meds, feeding) claims the budget before optional tasks do.
- **Shortest-first sorting** — `generate_plan(sort_by="duration")` selects the shortest tasks first, fitting the maximum number of tasks into the available time.
- **Chronological view** — `sort_by_time()` orders all tasks by their assigned start time (`time_slot`), with unscheduled tasks pushed to the end using a `float('inf')` sentinel key.
- **Daily and weekly recurrence** — tasks can be marked `recurrence="daily"` or `"weekly"`. Calling `complete_task()` marks the task done and automatically appends a fresh copy to the correct pet with a `due_date` offset of +1 day or +7 days via `timedelta`.
- **Conflict detection** — `detect_conflicts()` compares every pair of timed tasks using interval-overlap logic (`a.start < b.end and b.start < a.end`) and reports overlaps with human-readable messages, distinguishing same-pet from cross-pet conflicts. The check is wrapped in `try/except` so it degrades gracefully rather than crashing.
- **AND-logic filtering** — `filter_tasks(pet_name=, completed=)` returns tasks matching all supplied criteria; omitting an argument disables that filter.
- **Schedule summary** — `explain_plan()` renders a formatted terminal report showing scheduled vs. skipped tasks, priority stars, time slots, recurrence indicators, and total time used vs. budget.

## Smarter Scheduling

The `Scheduler` class goes beyond a basic priority sort with several additional features:

- **Sort modes** — `generate_plan(sort_by=)` supports `"priority"` (highest first, default) and `"duration"` (shortest first, fits more tasks into the budget).
- **Chronological view** — `sort_by_time()` returns all tasks ordered by their assigned start time, with unscheduled tasks placed at the end.
- **Filtering** — `filter_tasks(pet_name=, completed=)` returns a filtered task list using AND logic; either argument can be omitted to skip that filter.
- **Recurring tasks** — tasks support `recurrence="daily"` or `recurrence="weekly"`. Calling `complete_task()` marks the task done and automatically adds a fresh copy to the pet's list with a `due_date` calculated via `timedelta` (today + 1 day or today + 7 days).
- **Conflict detection** — `detect_conflicts()` compares all tasks that have a `time_slot` assigned and reports any overlapping intervals, labeling each conflict as `[same pet]` or `[cross-pet]`. The check is wrapped in a `try/except` so it returns a warning string rather than crashing if something unexpected occurs.

The scheduler uses a **greedy algorithm** (O(n log n)) which is a deliberate tradeoff: it runs fast and produces intuitive results for small task lists, at the cost of occasionally missing an optimal combination of tasks.

## Testing PawPal+

### Running the tests

```bash
python3 -m pytest
```

### What the tests cover

Tests live in `tests/test_pawpal.py` and are organized around five areas:

- **Task & Pet basics** — marking a task complete, adding/removing tasks from a pet, and verifying `get_tasks()` returns all entries.
- **Owner & schedule** — adding pets to an owner and confirming `get_schedule()` aggregates tasks across all pets.
- **`generate_plan` (happy paths + edge cases)** — verifies the greedy budget constraint (never exceeds `available_time`), both sort modes (`"priority"` and `"duration"`), exact-budget-fit inclusion, zero-budget rejection, and empty-pet/no-pet scenarios.
- **Recurring tasks** — completing a `daily` task produces a new task due tomorrow; completing a `weekly` task produces one due in 7 days; non-recurring tasks return `None`. A multi-pet test confirms the next occurrence is appended to the correct pet.
- **Chronological sorting** — `sort_by_time()` returns timed tasks in ascending slot order, with `time_slot=None` tasks pushed to the end.
- **Conflict detection** — overlapping time windows are flagged; same-pet and cross-pet conflicts are labeled correctly; adjacent (non-overlapping) tasks and untimed tasks do not produce false positives.
- **Filtering** — `filter_tasks()` correctly applies `pet_name`, `completed`, and combined AND filters; an unknown pet name returns an empty list.

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.
