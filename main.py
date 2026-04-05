from pawpal_system import Owner, Pet, Task, Scheduler

# --- Setup ---
owner = Owner(name="Fahim", available_time=90)

dog = Pet(name="Biscuit", species="Dog", age=3, owner=owner)
cat = Pet(name="Mochi", species="Cat", age=5, owner=owner)

owner.add_pet(dog)
owner.add_pet(cat)

# --- Tasks for Biscuit (Dog) ---
dog.add_task(Task(name="Morning Walk",    category="walk",    duration=30, priority=5))
dog.add_task(Task(name="Breakfast",       category="feeding", duration=10, priority=4))
dog.add_task(Task(name="Flea Medicine",   category="meds",    duration=5,  priority=5))

# --- Tasks for Mochi (Cat) ---
cat.add_task(Task(name="Wet Food Feeding", category="feeding",    duration=10, priority=4))
cat.add_task(Task(name="Litter Box Clean", category="grooming",   duration=10, priority=3))
cat.add_task(Task(name="Playtime",         category="enrichment", duration=20, priority=2))

# --- Schedule ---
scheduler = Scheduler(pet=dog, available_time=owner.available_time)
scheduler.tasks = owner.get_schedule()  # pull tasks from all pets

print(scheduler.explain_plan())