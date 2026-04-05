import pytest
from pawpal_system import Owner, Pet, Task, Scheduler


# --- Fixtures ---

@pytest.fixture
def owner():
    return Owner(name="Fahim", available_time=60)

@pytest.fixture
def pet(owner):
    p = Pet(name="Biscuit", species="Dog", age=3, owner=owner)
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


# --- Scheduler tests ---

def test_scheduler_respects_time_budget(pet, tasks):
    for task in tasks:
        pet.add_task(task)
    scheduler = Scheduler(pet=pet, available_time=60)
    scheduler.tasks = pet.owner.get_schedule()
    plan = scheduler.generate_plan()
    total = sum(t.duration for t in plan)
    assert total <= 60

def test_scheduler_prioritizes_high_priority_tasks(pet):
    low  = Task(name="Bath",      category="grooming", duration=20, priority=1)
    high = Task(name="Meds",      category="meds",     duration=20, priority=5)
    pet.add_task(low)
    pet.add_task(high)
    scheduler = Scheduler(pet=pet, available_time=20)
    scheduler.tasks = pet.owner.get_schedule()
    plan = scheduler.generate_plan()
    assert high in plan
    assert low not in plan

def test_scheduler_skips_tasks_that_dont_fit(pet):
    pet.add_task(Task(name="Long Walk", category="walk", duration=120, priority=5))
    scheduler = Scheduler(pet=pet, available_time=60)
    scheduler.tasks = pet.owner.get_schedule()
    plan = scheduler.generate_plan()
    assert len(plan) == 0

def test_scheduler_explain_plan_contains_owner_name(pet, tasks):
    for task in tasks:
        pet.add_task(task)
    scheduler = Scheduler(pet=pet, available_time=60)
    scheduler.tasks = pet.owner.get_schedule()
    output = scheduler.explain_plan()
    assert "Fahim" in output
