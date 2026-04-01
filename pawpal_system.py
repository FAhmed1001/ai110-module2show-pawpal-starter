# pawpal_system.py
# Logic layer for PawPal+ — all backend classes live here


class Owner:
    def __init__(self, name, available_time):
        self.name = name
        self.available_time = available_time  # total minutes available per day
        self.pets = []

    def add_pet(self, pet):
        pass

    def get_schedule(self):
        pass


class Pet:
    def __init__(self, name, species, age, owner):
        self.name = name
        self.species = species
        self.age = age
        self.owner = owner
        self.tasks = []

    def add_task(self, task):
        pass

    def remove_task(self, task):
        pass

    def get_tasks(self):
        pass


class Task:
    def __init__(self, name, category, duration, priority):
        self.name = name
        self.category = category  # e.g. "walk", "feeding", "meds", "grooming"
        self.duration = duration  # minutes
        self.priority = priority  # 1 (low) to 5 (high)
        self.completed = False

    def mark_complete(self):
        pass

    def __str__(self):
        pass


class Scheduler:
    def __init__(self, pet, available_time):
        self.pet = pet
        self.available_time = available_time  # minutes
        self.tasks = pet.get_tasks()

    def generate_plan(self):
        pass

    def filter_by_time(self):
        pass

    def sort_by_priority(self):
        pass

    def explain_plan(self):
        pass
