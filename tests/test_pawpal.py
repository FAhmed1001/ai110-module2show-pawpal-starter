import pytest
from datetime import date, timedelta
from pawpal_system import Owner, Pet, Task, Scheduler


# --- Fixtures ---

@pytest.fixture
def owner():
    return Owner(name="Fahim", available_time=60)

@pytest.fixture
def pet(owner):
    p = Pet(name="Biscuit", species="dog", age=3, owner=owner)
    owner.add_pet(p)
    return p

@pytest.fixture
def tasks():
    return [
        Task(name="Morning Walk",  category="walk",    duration=30, priority=5),
        Task(name="Breakfast",     category="feeding", duration=10, priority=4),
        Task(name="Flea Medicine", category="meds",    duration=5,  priority=5),
        Task(name="Bath Time",     category="grooming",duration=40, priority=2),
    ]


# --- Task tests ---

def test_task_mark_complete():
    task = Task(name="Walk", category="walk", duration=20, priority=3)
    task.mark_complete()
    assert task.completed is True

def test_task_str_contains_name():
    task = Task(name="Walk", category="walk", duration=20, priority=3)
    assert "Walk" in str(task)


# --- Pet tests ---

def test_pet_add_task(pet, tasks):
    pet.add_task(tasks[0])
    assert tasks[0] in pet.get_tasks()

def test_pet_remove_task(pet, tasks):
    pet.add_task(tasks[0])
    pet.remove_task(tasks[0])
    assert tasks[0] not in pet.get_tasks()

def test_pet_get_tasks_returns_all(pet, tasks):
    for task in tasks:
        pet.add_task(task)
    assert len(pet.get_tasks()) == len(tasks)


# --- Owner tests ---

def test_owner_add_pet(owner, pet):
    assert pet in owner.pets

def test_owner_get_schedule_returns_all_tasks(owner, pet, tasks):
    for task in tasks:
        pet.add_task(task)
    assert len(owner.get_schedule()) == len(tasks)


# --- Scheduler: generate_plan happy paths ---

def test_generate_plan_respects_time_budget(owner, pet, tasks):
    for task in tasks:
        pet.add_task(task)
    scheduler = Scheduler(owner=owner, available_time=60)
    plan = scheduler.generate_plan()
    assert sum(t.duration for t in plan) <= 60

def test_generate_plan_exact_budget_fit(owner, pet):
    # Task duration equals budget exactly — should be included (uses <=)
    task = Task(name="Walk", category="walk", duration=60, priority=3)
    pet.add_task(task)
    scheduler = Scheduler(owner=owner, available_time=60)
    assert task in scheduler.generate_plan()

def test_generate_plan_sort_by_priority(owner, pet):
    low  = Task(name="Bath", category="grooming", duration=20, priority=1)
    high = Task(name="Meds", category="meds",     duration=20, priority=5)
    pet.add_task(low)
    pet.add_task(high)
    scheduler = Scheduler(owner=owner, available_time=20)
    plan = scheduler.generate_plan(sort_by="priority")
    assert high in plan
    assert low not in plan

def test_generate_plan_sort_by_duration(owner, pet):
    # Budget=25: shortest-first should fit 10+5=15 min; longest (20) skipped
    short = Task(name="Snack",    category="feeding", duration=10, priority=1)
    med   = Task(name="Meds",     category="meds",    duration=5,  priority=1)
    long_ = Task(name="Big Walk", category="walk",    duration=20, priority=5)
    pet.add_task(short)
    pet.add_task(med)
    pet.add_task(long_)
    scheduler = Scheduler(owner=owner, available_time=25)
    plan = scheduler.generate_plan(sort_by="duration")
    assert short in plan
    assert med in plan
    assert long_ not in plan

def test_generate_plan_task_exceeds_budget_skipped(owner, pet):
    pet.add_task(Task(name="Long Walk", category="walk", duration=120, priority=5))
    scheduler = Scheduler(owner=owner, available_time=60)
    assert scheduler.generate_plan() == []


# --- Scheduler: generate_plan edge cases ---

def test_generate_plan_owner_no_pets(owner):
    scheduler = Scheduler(owner=owner, available_time=60)
    assert scheduler.generate_plan() == []

def test_generate_plan_pet_no_tasks(owner):
    empty_pet = Pet(name="Biscuit", species="dog", age=3, owner=owner)
    owner.add_pet(empty_pet)
    scheduler = Scheduler(owner=owner, available_time=60)
    assert scheduler.generate_plan() == []

def test_generate_plan_zero_budget(owner, pet, tasks):
    for task in tasks:
        pet.add_task(task)
    scheduler = Scheduler(owner=owner, available_time=0)
    assert scheduler.generate_plan() == []


# --- Scheduler: complete_task ---

def test_complete_task_marks_done(owner, pet):
    task = Task(name="Walk", category="walk", duration=30, priority=3)
    pet.add_task(task)
    scheduler = Scheduler(owner=owner, available_time=60)
    scheduler.complete_task(task)
    assert task.completed is True

def test_complete_task_daily_recurrence(owner, pet):
    task = Task(name="Meds", category="meds", duration=5, priority=5, recurrence="daily")
    pet.add_task(task)
    scheduler = Scheduler(owner=owner, available_time=60)
    next_task = scheduler.complete_task(task)
    assert next_task is not None
    assert next_task.due_date == date.today() + timedelta(days=1)
    assert next_task.completed is False

def test_complete_task_weekly_recurrence(owner, pet):
    task = Task(name="Bath", category="grooming", duration=40, priority=2, recurrence="weekly")
    pet.add_task(task)
    scheduler = Scheduler(owner=owner, available_time=60)
    next_task = scheduler.complete_task(task)
    assert next_task is not None
    assert next_task.due_date == date.today() + timedelta(weeks=1)

def test_complete_task_no_recurrence_returns_none(owner, pet):
    task = Task(name="Walk", category="walk", duration=30, priority=3)
    pet.add_task(task)
    scheduler = Scheduler(owner=owner, available_time=60)
    assert scheduler.complete_task(task) is None

def test_complete_task_adds_to_correct_pet(owner):
    # Two pets — recurring task belongs to pet2; next occurrence must go to pet2
    pet1 = Pet(name="Biscuit", species="dog", age=3, owner=owner)
    pet2 = Pet(name="Mochi",   species="cat", age=2, owner=owner)
    owner.add_pet(pet1)
    owner.add_pet(pet2)
    task = Task(name="Meds", category="meds", duration=5, priority=5, recurrence="daily")
    pet2.add_task(task)
    scheduler = Scheduler(owner=owner, available_time=60)
    scheduler.complete_task(task)
    assert any(t.name == "Meds" and not t.completed for t in pet2.get_tasks())
    assert all(t.completed or t.name != "Meds" for t in pet1.get_tasks())


# --- Scheduler: sort_by_time ---

def test_sort_by_time_chronological_order(owner, pet):
    # Add tasks out of order; sort_by_time must return them earliest-slot first
    lunch  = Task(name="Lunch",   category="feeding", duration=10, priority=3, time_slot=720)  # 12:00
    walk   = Task(name="Walk",    category="walk",    duration=30, priority=5, time_slot=480)  # 08:00
    dinner = Task(name="Dinner",  category="feeding", duration=10, priority=4, time_slot=1080) # 18:00
    pet.add_task(lunch)
    pet.add_task(walk)
    pet.add_task(dinner)
    scheduler = Scheduler(owner=owner, available_time=120)
    ordered = scheduler.sort_by_time()
    slots = [t.time_slot for t in ordered]
    assert slots == sorted(slots)

def test_sort_by_time_untimed_tasks_last(owner, pet):
    # Tasks without time_slot must appear after all timed tasks
    timed   = Task(name="Walk",  category="walk",    duration=30, priority=5, time_slot=480)
    untimed = Task(name="Meds",  category="meds",    duration=5,  priority=5)
    pet.add_task(untimed)
    pet.add_task(timed)
    scheduler = Scheduler(owner=owner, available_time=60)
    ordered = scheduler.sort_by_time()
    assert ordered[0] is timed
    assert ordered[-1] is untimed


# --- Scheduler: detect_conflicts ---

def test_detect_conflicts_no_overlap(owner, pet):
    pet.add_task(Task(name="Walk",      category="walk",    duration=30, priority=5, time_slot=480))
    pet.add_task(Task(name="Breakfast", category="feeding", duration=10, priority=4, time_slot=510))
    scheduler = Scheduler(owner=owner, available_time=120)
    assert scheduler.detect_conflicts() == []

def test_detect_conflicts_adjacent_not_a_conflict(owner, pet):
    # Walk ends at 510 (480+30), Breakfast starts at 510 — should NOT conflict
    pet.add_task(Task(name="Walk",      category="walk",    duration=30, priority=5, time_slot=480))
    pet.add_task(Task(name="Breakfast", category="feeding", duration=10, priority=4, time_slot=510))
    scheduler = Scheduler(owner=owner, available_time=120)
    assert scheduler.detect_conflicts() == []

def test_detect_conflicts_same_time_slot(owner, pet):
    pet.add_task(Task(name="Walk", category="walk",    duration=30, priority=5, time_slot=480))
    pet.add_task(Task(name="Meds", category="meds",    duration=5,  priority=5, time_slot=480))
    scheduler = Scheduler(owner=owner, available_time=120)
    conflicts = scheduler.detect_conflicts()
    assert len(conflicts) == 1
    assert "same pet" in conflicts[0]

def test_detect_conflicts_overlap_same_pet(owner, pet):
    pet.add_task(Task(name="Walk",      category="walk",    duration=30, priority=5, time_slot=480))
    pet.add_task(Task(name="Breakfast", category="feeding", duration=20, priority=4, time_slot=500))
    scheduler = Scheduler(owner=owner, available_time=120)
    conflicts = scheduler.detect_conflicts()
    assert len(conflicts) == 1
    assert "same pet: Biscuit" in conflicts[0]

def test_detect_conflicts_cross_pet(owner):
    pet1 = Pet(name="Biscuit", species="dog", age=3, owner=owner)
    pet2 = Pet(name="Mochi",   species="cat", age=2, owner=owner)
    owner.add_pet(pet1)
    owner.add_pet(pet2)
    pet1.add_task(Task(name="Walk", category="walk",    duration=30, priority=5, time_slot=480))
    pet2.add_task(Task(name="Meds", category="meds",    duration=10, priority=5, time_slot=490))
    scheduler = Scheduler(owner=owner, available_time=120)
    conflicts = scheduler.detect_conflicts()
    assert len(conflicts) == 1
    assert "cross-pet" in conflicts[0]

def test_detect_conflicts_no_time_slot_ignored(owner, pet):
    # Tasks without time_slot should not trigger conflict detection
    pet.add_task(Task(name="Walk", category="walk",    duration=30, priority=5))
    pet.add_task(Task(name="Meds", category="meds",    duration=5,  priority=5))
    scheduler = Scheduler(owner=owner, available_time=60)
    assert scheduler.detect_conflicts() == []


# --- Scheduler: filter_tasks ---

def test_filter_by_pet_name(owner):
    pet1 = Pet(name="Biscuit", species="dog", age=3, owner=owner)
    pet2 = Pet(name="Mochi",   species="cat", age=2, owner=owner)
    owner.add_pet(pet1)
    owner.add_pet(pet2)
    t1 = Task(name="Walk", category="walk",    duration=30, priority=5)
    t2 = Task(name="Meds", category="meds",    duration=5,  priority=5)
    pet1.add_task(t1)
    pet2.add_task(t2)
    scheduler = Scheduler(owner=owner, available_time=60)
    result = scheduler.filter_tasks(pet_name="Biscuit")
    assert t1 in result
    assert t2 not in result

def test_filter_by_completed_false(owner, pet):
    done    = Task(name="Walk", category="walk",    duration=30, priority=5, completed=True)
    pending = Task(name="Meds", category="meds",    duration=5,  priority=5)
    pet.add_task(done)
    pet.add_task(pending)
    scheduler = Scheduler(owner=owner, available_time=60)
    result = scheduler.filter_tasks(completed=False)
    assert pending in result
    assert done not in result

def test_filter_by_pet_and_completed(owner):
    pet1 = Pet(name="Biscuit", species="dog", age=3, owner=owner)
    pet2 = Pet(name="Mochi",   species="cat", age=2, owner=owner)
    owner.add_pet(pet1)
    owner.add_pet(pet2)
    t1 = Task(name="Walk", category="walk", duration=30, priority=5, completed=True)
    t2 = Task(name="Meds", category="meds", duration=5,  priority=5)
    t3 = Task(name="Bath", category="grooming", duration=20, priority=2, completed=True)
    pet1.add_task(t1)
    pet1.add_task(t2)
    pet2.add_task(t3)
    scheduler = Scheduler(owner=owner, available_time=120)
    result = scheduler.filter_tasks(pet_name="Biscuit", completed=True)
    assert t1 in result
    assert t2 not in result
    assert t3 not in result

def test_filter_unknown_pet_returns_empty(owner, pet):
    pet.add_task(Task(name="Walk", category="walk", duration=30, priority=5))
    scheduler = Scheduler(owner=owner, available_time=60)
    assert scheduler.filter_tasks(pet_name="Ghost") == []


# --- Scheduler: explain_plan ---

def test_explain_plan_contains_owner_name(owner, pet, tasks):
    for task in tasks:
        pet.add_task(task)
    scheduler = Scheduler(owner=owner, available_time=60)
    assert "Fahim" in scheduler.explain_plan()

def test_explain_plan_no_tasks_message(owner):
    empty_pet = Pet(name="Biscuit", species="dog", age=3, owner=owner)
    owner.add_pet(empty_pet)
    scheduler = Scheduler(owner=owner, available_time=60)
    assert "No tasks" in scheduler.explain_plan()
