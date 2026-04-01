import streamlit as st
from pawpal_system import (
    Owner, Pet, Task,
    Priority, TaskType,
    Scheduler, to_dict_list,
)

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")

st.markdown(
    """
Welcome to the PawPal+ starter app.

This file is intentionally thin. It gives you a working Streamlit app so you can start quickly,
but **it does not implement the project logic**. Your job is to design the system and build it.

Use this app as your interactive demo once your backend classes/functions exist.
"""
)

with st.expander("Scenario", expanded=True):
    st.markdown(
        """
**PawPal+** is a pet care planning assistant. It helps a pet owner plan care tasks
for their pet(s) based on constraints like time, priority, and preferences.

You will design and implement the scheduling logic and connect it to this Streamlit UI.
"""
    )

with st.expander("What you need to build", expanded=True):
    st.markdown(
        """
At minimum, your system should:
- Represent pet care tasks (what needs to happen, how long it takes, priority)
- Represent the pet and the owner (basic info and preferences)
- Build a plan/schedule for a day that chooses and orders tasks based on constraints
- Explain the plan (why each task was chosen and when it happens)
"""
    )

st.divider()

# Initialize session state on first load — objects persist across Streamlit reruns.
# Only created once; subsequent reruns skip these blocks and reuse existing objects.
if "owner" not in st.session_state:
    st.session_state.owner = None   # set when the user confirms owner details

if "pet" not in st.session_state:
    st.session_state.pet = None     # set when the user confirms pet details

if "tasks" not in st.session_state:
    st.session_state.tasks = []     # raw task dicts shown in the table

# ---------------------------------------------------------------------------
# Section 1: Owner + Pet setup
# ---------------------------------------------------------------------------

st.subheader("Owner & Pet Setup")

col_o, col_p = st.columns(2)
with col_o:
    owner_name = st.text_input("Owner name", value="Jordan")
    avail_start = st.number_input("Availability start (hour)", min_value=0, max_value=23, value=8)
    avail_end   = st.number_input("Availability end (hour)",   min_value=1, max_value=23, value=22)
with col_p:
    pet_name = st.text_input("Pet name", value="Mochi")
    species  = st.selectbox("Species", ["dog", "cat", "other"])
    age      = st.number_input("Pet age (years)", min_value=0, max_value=30, value=3)

if st.button("Set up Owner & Pet"):
    owner = Owner(
        name=owner_name,
        available_start=avail_start * 60,   # convert hours to minutes since midnight
        available_end=avail_end * 60,
    )
    pet = Pet(name=pet_name, species=species, age=int(age))
    owner.add_pet(pet)                       # Owner.add_pet() registers the pet
    st.session_state.owner = owner
    st.session_state.pet   = pet
    st.session_state.tasks = []              # reset tasks when a new pet is created
    st.success(f"Owner **{owner_name}** and pet **{pet_name}** are ready!")

if st.session_state.owner:
    o = st.session_state.owner
    p = st.session_state.pet
    st.caption(
        f"Active: **{o.name}** — {o.total_available_minutes()} min available  |  "
        f"Pet: **{p.name}** ({p.species}, {p.age} yr)"
    )

st.divider()

# ---------------------------------------------------------------------------
# Section 2: Add tasks
# ---------------------------------------------------------------------------

st.subheader("Add Tasks")

_priority_map = {"High": Priority.HIGH, "Medium": Priority.MEDIUM, "Low": Priority.LOW}
_type_map     = {t.value: t for t in TaskType}

col1, col2, col3 = st.columns(3)
with col1:
    task_title = st.text_input("Task title", value="Morning walk")
    task_type  = st.selectbox("Type", [t.value for t in TaskType])
with col2:
    duration      = st.number_input("Duration (min)", min_value=1, max_value=240, value=20)
    preferred_hour = st.number_input("Preferred start (hour, 0=none)", min_value=0, max_value=23, value=8)
with col3:
    priority    = st.selectbox("Priority", ["High", "Medium", "Low"])
    is_recurring = st.checkbox("Recurring daily")

if st.button("Add task"):
    if st.session_state.pet is None:
        st.error("Set up an owner and pet first.")
    else:
        preferred_time = preferred_hour * 60 if preferred_hour > 0 else None
        task = Task(
            title=task_title,
            duration=int(duration),
            priority=_priority_map[priority],
            task_type=_type_map[task_type],
            preferred_time=preferred_time,
            is_recurring=is_recurring,
        )
        st.session_state.pet.add_task(task)   # Pet.add_task() registers the task
        st.session_state.tasks.append({
            "Title": task_title,
            "Type": task_type,
            "Duration (min)": int(duration),
            "Priority": priority,
            "Preferred": f"{preferred_hour}:00" if preferred_time else "—",
            "Recurring": is_recurring,
        })

if st.session_state.tasks:
    st.write(f"Tasks for **{st.session_state.pet.name}**:")
    st.table(st.session_state.tasks)
else:
    st.info("No tasks yet. Add one above.")

st.divider()

# ---------------------------------------------------------------------------
# Section 3: Generate schedule
# ---------------------------------------------------------------------------

st.subheader("Build Schedule")

if st.button("Generate schedule"):
    if st.session_state.owner is None or st.session_state.pet is None:
        st.error("Set up an owner and pet before generating a schedule.")
    elif not st.session_state.tasks:
        st.warning("Add at least one task before generating a schedule.")
    else:
        result = Scheduler().build_schedule(
            st.session_state.owner,
            st.session_state.pet,
        )
        rows = to_dict_list(result)
        if rows:
            st.success("Schedule generated!")
            st.dataframe(rows, use_container_width=True)
        else:
            st.warning("No tasks could be scheduled in the available window.")

        if result["unscheduled_tasks"]:
            st.warning("Could not fit the following tasks:")
            for task in result["unscheduled_tasks"]:
                st.write(f"- **{task.title}** ({task.duration} min) — {task.unscheduled_reason}")
