import streamlit as st
from pawpal_system import Owner, Pet, Task, Scheduler

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")
st.title("🐾 PawPal+")

# --- Owner Setup ---
st.subheader("Owner Info")
owner_name = st.text_input("Your name", value="Fahim")
available_time = st.number_input("Time available today (minutes)", min_value=10, max_value=480, value=90)

if st.button("Save Owner"):
    st.session_state.owner = Owner(name=owner_name, available_time=int(available_time))
    st.success(f"Owner '{owner_name}' saved with {available_time} min available.")

st.divider()

# --- Add a Pet ---
st.subheader("Add a Pet")
pet_name = st.text_input("Pet name", value="Biscuit")
species = st.selectbox("Species", ["Dog", "Cat", "Bird", "Rabbit", "Other"])
age = st.number_input("Age (years)", min_value=0, max_value=30, value=3)

if st.button("Add Pet"):
    if "owner" not in st.session_state:
        st.warning("Please save an owner first.")
    else:
        pet = Pet(name=pet_name, species=species, age=int(age), owner=st.session_state.owner)
        st.session_state.owner.add_pet(pet)
        st.success(f"{pet_name} the {species} added!")

if "owner" in st.session_state and st.session_state.owner.pets:
    st.markdown("**Current pets:**")
    for pet in st.session_state.owner.pets:
        st.markdown(f"- {pet.name} ({pet.species}, age {pet.age})")

st.divider()

# --- Add a Task ---
st.subheader("Add a Task")

TIME_SLOT_OPTIONS = {"(none)": None} | {
    f"{h:02d}:00": h * 60 for h in range(6, 21)
}

if "owner" in st.session_state and st.session_state.owner.pets:
    pet_names = [p.name for p in st.session_state.owner.pets]
    selected_pet_name = st.selectbox("Assign to pet", pet_names)

    col1, col2, col3 = st.columns(3)
    with col1:
        task_name = st.text_input("Task name", value="Morning Walk")
    with col2:
        category = st.selectbox("Category", ["walk", "feeding", "meds", "grooming", "enrichment"])
    with col3:
        duration = st.number_input("Duration (min)", min_value=1, max_value=240, value=20)

    col4, col5, col6 = st.columns(3)
    with col4:
        priority = st.slider("Priority", min_value=1, max_value=5, value=3)
    with col5:
        recurrence = st.selectbox("Recurrence", ["none", "daily", "weekly"])
        recurrence = None if recurrence == "none" else recurrence
    with col6:
        slot_label = st.selectbox("Start time", list(TIME_SLOT_OPTIONS.keys()))
    time_slot = TIME_SLOT_OPTIONS[slot_label]

    if st.button("Add Task"):
        selected_pet = next(p for p in st.session_state.owner.pets if p.name == selected_pet_name)
        task = Task(
            name=task_name,
            category=category,
            duration=int(duration),
            priority=priority,
            recurrence=recurrence,
            time_slot=time_slot,
        )
        selected_pet.add_task(task)
        st.success(f"Task '{task_name}' added to {selected_pet_name}.")

    # --- Task Display with Filters ---
    if any(pet.get_tasks() for pet in st.session_state.owner.pets):
        st.markdown("**Tasks**")
        col_f1, col_f2 = st.columns(2)
        with col_f1:
            filter_pet = st.selectbox("Filter by pet", ["All"] + pet_names, key="filter_pet")
        with col_f2:
            filter_status = st.selectbox("Filter by status", ["All", "Pending", "Done"], key="filter_status")

        scheduler_preview = Scheduler(owner=st.session_state.owner, available_time=st.session_state.owner.available_time)
        completed_filter = None if filter_status == "All" else (filter_status == "Done")
        pet_filter = None if filter_pet == "All" else filter_pet
        filtered = scheduler_preview.filter_tasks(pet_name=pet_filter, completed=completed_filter)

        for pet in st.session_state.owner.pets:
            pet_tasks = [t for t in filtered if t in pet.get_tasks()]
            if pet_tasks:
                st.markdown(f"**{pet.name}'s tasks:**")
                for i, t in enumerate(pet_tasks):
                    checked = st.checkbox(str(t), value=t.completed, key=f"{pet.name}_{i}")
                    if checked and not t.completed:
                        scheduler_preview.complete_task(t)
else:
    st.info("Add an owner and at least one pet to start adding tasks.")

st.divider()

# --- Generate Schedule ---
st.subheader("Generate Schedule")

sort_by = st.selectbox("Sort tasks by", ["priority", "duration"])

if st.button("Generate Schedule"):
    if "owner" not in st.session_state:
        st.warning("Please save an owner first.")
    elif not st.session_state.owner.pets:
        st.warning("Add at least one pet before generating a schedule.")
    elif not st.session_state.owner.get_schedule():
        st.warning("Add at least one task before generating a schedule.")
    else:
        owner = st.session_state.owner
        scheduler = Scheduler(owner=owner, available_time=owner.available_time)

        conflicts = scheduler.detect_conflicts()
        if conflicts:
            st.warning("**Scheduling conflicts detected:**")
            for c in conflicts:
                st.markdown(f"- ⚠️ {c}")

        st.text(scheduler.explain_plan(sort_by=sort_by))
