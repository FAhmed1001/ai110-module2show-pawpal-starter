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

## Smarter Scheduling

The `Scheduler` class goes beyond a basic priority sort with several additional features:

- **Sort modes** — `generate_plan(sort_by=)` supports `"priority"` (highest first, default) and `"duration"` (shortest first, fits more tasks into the budget).
- **Chronological view** — `sort_by_time()` returns all tasks ordered by their assigned start time, with unscheduled tasks placed at the end.
- **Filtering** — `filter_tasks(pet_name=, completed=)` returns a filtered task list using AND logic; either argument can be omitted to skip that filter.
- **Recurring tasks** — tasks support `recurrence="daily"` or `recurrence="weekly"`. Calling `complete_task()` marks the task done and automatically adds a fresh copy to the pet's list with a `due_date` calculated via `timedelta` (today + 1 day or today + 7 days).
- **Conflict detection** — `detect_conflicts()` compares all tasks that have a `time_slot` assigned and reports any overlapping intervals, labeling each conflict as `[same pet]` or `[cross-pet]`. The check is wrapped in a `try/except` so it returns a warning string rather than crashing if something unexpected occurs.

The scheduler uses a **greedy algorithm** (O(n log n)) which is a deliberate tradeoff: it runs fast and produces intuitive results for small task lists, at the cost of occasionally missing an optimal combination of tasks.

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
