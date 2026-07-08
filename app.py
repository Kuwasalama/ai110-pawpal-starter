import streamlit as st
from pawpal_system import Owner, Pet, Task, Scheduler, is_valid_time

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")

st.markdown(
    """
PawPal+ helps a pet owner plan the day's care tasks across their pets,
based on how much time is available, task priority, and preferences.
"""
)

with st.expander("Scenario", expanded=False):
    st.markdown(
        """
**PawPal+** is a pet care planning assistant. It helps a pet owner plan care tasks
for their pet(s) based on constraints like time, priority, and preferences.
"""
    )

st.divider()

# --- Owner + constraints ---
st.subheader("Owner")
owner_name = st.text_input("Owner name", value="Jordan")
available_minutes = st.number_input(
    "Time available today (minutes)", min_value=0, max_value=600, value=90
)
start_time = st.text_input("Preferred start time (HH:MM)", value="08:00")

st.divider()

# --- Pets (persisted across reruns in session_state) ---
st.subheader("Pets")

if "pets" not in st.session_state:
    st.session_state.pets = []

# The "add a new pet" form. On submit, Streamlit reruns the whole script;
# because the pet is stored in session_state it survives that rerun.
with st.form("add_pet_form", clear_on_submit=True):
    new_pet_name = st.text_input("Pet name", value="Mochi")
    new_species = st.selectbox("Species", ["dog", "cat", "other"])
    if st.form_submit_button("Add pet"):
        # Bridge: build a Pet object and register it on the owner-to-be.
        st.session_state.pets.append(Pet(name=new_pet_name, species=new_species))

if st.session_state.pets:
    st.write("Current pets:")
    st.table(
        [
            {"name": p.name, "species": p.species, "tasks": len(p.tasks)}
            for p in st.session_state.pets
        ]
    )
else:
    st.info("No pets yet. Add one above.")

st.divider()

# --- Tasks (each task belongs to a chosen pet) ---
st.subheader("Tasks")

if not st.session_state.pets:
    st.info("Add a pet first, then you can give it tasks.")
else:
    pet_names = [p.name for p in st.session_state.pets]
    with st.form("add_task_form", clear_on_submit=True):
        which_pet = st.selectbox("Which pet?", pet_names)
        task_title = st.text_input("Task title", value="Morning walk")
        duration = st.number_input(
            "Duration (minutes)", min_value=1, max_value=240, value=20
        )
        priority = st.selectbox("Priority", ["low", "medium", "high"], index=2)
        set_time = st.text_input(
            "Set time (HH:MM, optional)",
            value="",
            help="Pin this task to a specific time. Leave blank to let priority decide.",
        )
        if st.form_submit_button("Add task"):
            cleaned_time = set_time.strip()
            if cleaned_time and not is_valid_time(cleaned_time):
                # Bad time: don't add the task, tell the owner what's expected.
                st.error(
                    f"'{cleaned_time}' isn't a valid time. "
                    "Use 24-hour HH:MM, like 09:00 or 17:30 — or leave it blank."
                )
            else:
                # Attach the new Task to the pet the user picked.
                target = st.session_state.pets[pet_names.index(which_pet)]
                target.add_task(
                    Task(
                        title=task_title,
                        duration_minutes=int(duration),
                        priority=priority,
                        time=cleaned_time,
                    )
                )

    # Show each pet's tasks.
    for p in st.session_state.pets:
        if p.tasks:
            st.write(f"**{p.name}**'s tasks:")
            st.table(
                [
                    {
                        "title": t.title,
                        "duration_minutes": t.duration_minutes,
                        "priority": t.priority,
                        "set_time": t.time or "—",
                    }
                    for t in p.tasks
                ]
            )

st.divider()

# --- Build the schedule from everything above ---
st.subheader("Build Schedule")

if st.button("Generate schedule"):
    # Bridge: build the owner from the inputs, attach every pet, then plan.
    owner = Owner(
        name=owner_name,
        preferred_times=[start_time],
        available_minutes=int(available_minutes),
    )
    for pet in st.session_state.pets:
        owner.add_pet(pet)

    scheduler = Scheduler(owner)

    # Warn about overlapping pinned times before showing the plan. This only
    # flags the clash; the schedule is still built.
    conflict_warning = scheduler.detect_conflicts()
    if conflict_warning:
        st.warning(conflict_warning)

    plan = scheduler.generate_schedule()

    if not plan:
        st.warning("Nothing could be scheduled. Add tasks or increase the available time.")
    else:
        st.success(f"Planned {len(plan)} task(s) for {owner.name}.")
        st.table(
            [
                {
                    "time": entry["time"],
                    "task": entry["title"],
                    "minutes": entry["duration_minutes"],
                    "priority": entry["priority"],
                    "shortened": entry["shortened"],
                }
                for entry in plan
            ]
        )
        st.subheader("Why this plan?")
        st.text(scheduler.explain())
