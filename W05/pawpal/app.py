import streamlit as st
from pawpal_system import (
    Owner, Pet, Task,
    Priority, TaskType,
    Scheduler, to_dict_list,
)

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="wide")

st.title("🐾 PawPal+")

st.markdown(
    """
**PawPal+** is a smart pet care planning assistant. It helps owners create optimized daily schedules 
based on task priorities, preferred times, and availability constraints.

Key features:
- 🎯 **Priority-based scheduling** — HIGH priority tasks always schedule first
- ⏰ **Time-aware planning** — respects preferred times and detects conflicts
- 🔄 **Recurring automation** — daily/weekly tasks clone automatically when marked complete
- ⚠️ **Conflict detection** — warns about overlapping task times before scheduling
"""
)

with st.expander("How it works"):
    st.markdown(
        """
**Smart Scheduling Features:**
- **Priority sorting** — HIGH priority tasks always get scheduled first
- **Time preferences** — respects preferred start times, with HIGH priority winning conflicts
- **Conflict detection** — warns you about overlapping task times before scheduling
- **Recurring automation** — daily/weekly tasks auto-clone when marked complete
- **Filtering & analysis** — view tasks by type, priority, or completion status
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
    st.write(f"**Tasks for {st.session_state.pet.name}:**")
    
    # Display tasks sorted by preferred time (intelligent UI)
    scheduler = Scheduler()
    sorted_tasks = scheduler.get_tasks_sorted_by_time(st.session_state.pet)
    
    # Create enhanced task display with priority indicators
    task_display = []
    for task in sorted_tasks:
        pref_time = f"{task.preferred_time // 60:02d}:{task.preferred_time % 60:02d}" if task.preferred_time else "Flexible"
        task_display.append({
            "Title": task.title,
            "Type": task.task_type.value,
            "Duration": f"{task.duration} min",
            "Priority": task.priority.name,
            "Preferred Time": pref_time,
            "Recurring": "✓ Daily" if (task.is_recurring and task.recurrence == "daily") else 
                        "✓ Weekly" if (task.is_recurring and task.recurrence == "weekly") else "",
        })
    
    # Display as table
    st.dataframe(
        task_display,
        use_container_width=True,
        hide_index=True,
    )
    
    # Check for pre-schedule conflicts
    conflicts = scheduler.detect_conflicts(st.session_state.pet)
    if conflicts:
        st.warning("⚠️ **Time Conflicts Detected!**")
        st.markdown(
            "The following tasks have overlapping preferred times. "
            "The scheduler will adjust times to avoid conflicts."
        )
        
        # Display conflict pairs clearly
        for task_a, task_b in conflicts:
            a_end_min = task_a.preferred_time + task_a.duration
            b_end_min = task_b.preferred_time + task_b.duration
            
            a_time = f"{task_a.preferred_time // 60:02d}:{task_a.preferred_time % 60:02d}–{a_end_min // 60:02d}:{a_end_min % 60:02d}"
            b_time = f"{task_b.preferred_time // 60:02d}:{task_b.preferred_time % 60:02d}–{b_end_min // 60:02d}:{b_end_min % 60:02d}"
            
            st.write(
                f"🔸 **{task_a.title}** ({a_time}) ↔️ **{task_b.title}** ({b_time})"
            )
        
        st.info(
            "💡 **Tip:** Lower priority tasks will be shifted to non-preferred times to accommodate "
            "higher priority tasks at their preferred times."
        )
    
    # Show recurring tasks if any
    recurring = scheduler.get_recurring_tasks(st.session_state.pet)
    if recurring:
        st.success(f"✓ {len(recurring)} recurring task(s) — will auto-clone when marked complete")

else:
    st.info("No tasks yet. Add one above.")

st.divider()

# ---------------------------------------------------------------------------
# Section 3: Analyze & Filter Tasks (Optional)
# ---------------------------------------------------------------------------

st.subheader("Analyze Tasks (Optional)")

if st.session_state.pet:
    scheduler = Scheduler()
    
    # Create tabs for different views
    tab1, tab2, tab3 = st.tabs(["By Priority", "By Type", "By Status"])
    
    with tab1:
        st.write("Tasks ordered by priority (HIGH → LOW):")
        priority_sorted = sorted(
            st.session_state.pet.tasks,
            key=lambda t: t.priority.value,
            reverse=True
        )
        if priority_sorted:
            priority_display = [
                {
                    "Priority": "🔴 HIGH" if t.priority.name == "HIGH" else "🟡 MEDIUM" if t.priority.name == "MEDIUM" else "🟢 LOW",
                    "Task": t.title,
                    "Type": t.task_type.value,
                    "Duration": f"{t.duration} min",
                }
                for t in priority_sorted
            ]
            st.dataframe(priority_display, use_container_width=True, hide_index=True)
        else:
            st.info("No tasks yet.")
    
    with tab2:
        # Filter by type
        st.write("Filter tasks by type:")
        selected_type = st.selectbox(
            "Select task type:",
            [t.value for t in TaskType],
            key="filter_type"
        )
        
        filtered = scheduler.filter_by_type(st.session_state.pet, TaskType(selected_type))
        if filtered:
            type_display = [
                {
                    "Task": t.title,
                    "Duration": f"{t.duration} min",
                    "Priority": t.priority.name,
                    "Recurring": "✓" if t.is_recurring else "",
                }
                for t in filtered
            ]
            st.dataframe(type_display, use_container_width=True, hide_index=True)
            st.success(f"Found {len(filtered)} {selected_type} task(s)")
        else:
            st.info(f"No {selected_type} tasks yet.")
    
    with tab3:
        col_status_a, col_status_b = st.columns(2)
        
        with col_status_a:
            st.write("**Pending Tasks:**")
            pending = scheduler.filter_by_status(st.session_state.pet, completed=False)
            if pending:
                pending_display = [
                    {"Task": t.title, "Priority": t.priority.name, "Duration": f"{t.duration} min"}
                    for t in pending
                ]
                st.dataframe(pending_display, use_container_width=True, hide_index=True)
                st.info(f"{len(pending)} task(s) to do")
            else:
                st.success("All tasks complete! 🎉")
        
        with col_status_b:
            st.write("**Completed Tasks:**")
            completed = scheduler.filter_by_status(st.session_state.pet, completed=True)
            if completed:
                complete_display = [
                    {"Task": t.title, "Priority": t.priority.name}
                    for t in completed
                ]
                st.dataframe(complete_display, use_container_width=True, hide_index=True)
                st.success(f"{len(completed)} task(s) done")
            else:
                st.info("No completed tasks yet.")

st.divider()

# ---------------------------------------------------------------------------
# Section 4: Generate schedule
# ---------------------------------------------------------------------------

st.subheader("Build Schedule")

if st.button("Generate schedule", use_container_width=True):
    if st.session_state.owner is None or st.session_state.pet is None:
        st.error("Set up an owner and pet before generating a schedule.")
    elif not st.session_state.tasks:
        st.warning("Add at least one task before generating a schedule.")
    else:
        scheduler = Scheduler()
        result = scheduler.build_schedule(
            st.session_state.owner,
            st.session_state.pet,
        )
        rows = to_dict_list(result)
        
        # Show summary metrics
        scheduled_count = len(result["scheduled_tasks"])
        unscheduled_count = len(result["unscheduled_tasks"])
        total_duration = sum(t.duration for t in result["scheduled_tasks"])
        available_mins = st.session_state.owner.total_available_minutes()
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Scheduled", f"{scheduled_count}/{len(st.session_state.tasks)}")
        with col2:
            st.metric("Total Duration", f"{total_duration} min")
        with col3:
            st.metric("Available", f"{available_mins} min")
        with col4:
            utilization = min(100, int(total_duration / available_mins * 100)) if available_mins > 0 else 0
            st.metric("Utilization", f"{utilization}%")
        
        st.divider()
        
        if rows:
            st.success("✓ Schedule generated successfully!")
            
            # Display scheduled tasks with enhanced formatting
            st.subheader("Daily Schedule")
            
            # Create an enhanced schedule display
            schedule_display = []
            for task in sorted(result["scheduled_tasks"], key=lambda t: t.scheduled_start or 0):
                start_time = f"{task.scheduled_start // 60:02d}:{task.scheduled_start % 60:02d}"
                end_time = f"{task.scheduled_end // 60:02d}:{task.scheduled_end % 60:02d}"
                
                # Priority color coding
                priority_emoji = "🔴" if task.priority.name == "HIGH" else "🟡" if task.priority.name == "MEDIUM" else "🟢"
                
                schedule_display.append({
                    "Time": f"{start_time} → {end_time}",
                    "Task": task.title,
                    "Type": task.task_type.value,
                    "Duration": f"{task.duration} min",
                    "Priority": f"{priority_emoji} {task.priority.name}",
                })
            
            st.dataframe(
                schedule_display,
                use_container_width=True,
                hide_index=True,
            )
            
            # Explain scheduling logic
            with st.expander("📋 How the schedule was built"):
                st.markdown("""
**Scheduling Algorithm:**
1. **Priority ordering** — HIGH priority tasks reserve their slots first, then MEDIUM, then LOW
2. **Preferred time respect** — tasks try to start at their preferred time, with HIGH priority getting priority
3. **No overlaps** — the scheduler ensures no two tasks occupy the same time slot
4. **Overflow handling** — tasks that don't fit in the available window are marked as unscheduled
5. **Duration boundary** — each task reserves exactly `duration` minutes (e.g., a 30-min walk reserves 9:00–9:30)

**Why tasks might move:**
- A HIGH priority task at 9:00 will push a MEDIUM priority task from 9:00 to the next available slot
- Tasks can only fit if there's a continuous block of time available
- If the day is full, remaining tasks are listed as unscheduled
                """)
        else:
            st.warning("No tasks could be scheduled in the available window.")
        
        # Show unscheduled tasks with reasons
        if result["unscheduled_tasks"]:
            st.warning("⚠️ **Could not fit the following tasks:**")
            
            unscheduled_display = []
            for task in result["unscheduled_tasks"]:
                unscheduled_display.append({
                    "Task": task.title,
                    "Duration": f"{task.duration} min",
                    "Priority": task.priority.name,
                    "Reason": task.unscheduled_reason or "No space available",
                })
            
            st.dataframe(unscheduled_display, use_container_width=True, hide_index=True)
            
            st.info(
                "💡 **Suggestions:**\n"
                "- Extend your availability window (more time in the day)\n"
                "- Split long tasks into shorter ones\n"
                "- Mark less important tasks as lower priority\n"
                "- Remove or defer non-essential tasks"
            )
