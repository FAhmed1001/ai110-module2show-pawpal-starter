from pawpal_system import Owner, Pet, Task, Scheduler

# --- Setup ---
owner = Owner(name="Fahim", available_time=90)

dog = Pet(name="Biscuit", species="Dog", age=3, owner=owner)
cat = Pet(name="Mochi", species="Cat", age=5, owner=owner)

owner.add_pet(dog)
owner.add_pet(cat)

# --- Tasks added intentionally out of time-slot order ---
dog.add_task(Task(name="Flea Medicine",   category="meds",    duration=5,  priority=5, recurrence=None,    time_slot=9*60))
dog.add_task(Task(name="Morning Walk",    category="walk",    duration=30, priority=5, recurrence="daily", time_slot=8*60))
dog.add_task(Task(name="Breakfast",       category="feeding", duration=10, priority=4, recurrence="daily", time_slot=8*60))    # same-pet conflict: 08:00 = Morning Walk

cat.add_task(Task(name="Playtime",         category="enrichment", duration=20, priority=2, recurrence=None))
cat.add_task(Task(name="Wet Food Feeding", category="feeding",    duration=10, priority=4, recurrence="daily",  time_slot=8*60+30))
cat.add_task(Task(name="Litter Box Clean", category="grooming",   duration=10, priority=3, recurrence="weekly", time_slot=9*60))  # cross-pet conflict: 09:00 = Flea Medicine

scheduler = Scheduler(owner=owner, available_time=owner.available_time)

# --- Sort by time_slot ---
print("=== sort_by_time() ===")
for t in scheduler.sort_by_time():
    print(" ", t)

# --- Filter by pet ---
print("\n=== filter_tasks(pet_name='Biscuit') ===")
for t in scheduler.filter_tasks(pet_name="Biscuit"):
    print(" ", t)

# --- Filter by status ---
print("\n=== filter_tasks(completed=False) ===")
for t in scheduler.filter_tasks(completed=False):
    print(" ", t)

# --- Complete a daily task and verify next occurrence is created ---
walk = dog.tasks[1]  # Morning Walk (daily)
print(f"\n=== complete_task('{walk.name}') ===")
next_task = scheduler.complete_task(walk)
print(f"  Marked complete: {walk}")
print(f"  Next occurrence: {next_task}")
print(f"  Due date: {next_task.due_date}")

print("\n=== Biscuit's tasks after completion ===")
for t in scheduler.filter_tasks(pet_name="Biscuit"):
    print(" ", t)

# --- Complete a weekly task and verify next occurrence is created ---
litter = cat.tasks[2]  # Litter Box Clean (weekly)
print(f"\n=== complete_task('{litter.name}') ===")
next_task = scheduler.complete_task(litter)
print(f"  Marked complete: {litter}")
print(f"  Next occurrence: {next_task}")
print(f"  Due date: {next_task.due_date}")

print("\n=== Mochi's tasks after completion ===")
for t in scheduler.filter_tasks(pet_name="Mochi"):
    print(" ", t)

# --- Conflict detection ---
print("\n=== detect_conflicts() ===")
conflicts = scheduler.detect_conflicts()
if conflicts:
    for c in conflicts:
        print(" ⚠", c)
else:
    print("  No conflicts detected.")
