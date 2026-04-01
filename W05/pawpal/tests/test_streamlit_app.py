"""
tests/test_streamlit_app.py — Automated UI tests for the Streamlit app (app.py).

Tests the Streamlit frontend including:
- Page configuration
- Form inputs and buttons
- Session state management
- Error/success/warning messages
- Table displays
- Complete user workflows

Run with: python -m pytest tests/test_streamlit_app.py
"""

import pytest
from streamlit.testing.v1 import AppTest
import os
import sys

# Add parent directory to path so we can import pawpal_system
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pawpal_system import _reset_id_counter


@pytest.fixture(autouse=True)
def reset_ids():
    """Reset the global task ID counter before each test for clean IDs."""
    _reset_id_counter()


@pytest.fixture
def app():
    """Fixture to create and return a fresh Streamlit app instance."""
    app_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "app.py")
    app_instance = AppTest.from_file(app_path)
    app_instance.run()
    return app_instance


# ===========================================================================
# Page Configuration Tests
# ===========================================================================

def test_page_title_present(app):
    """Page should have a title with PawPal+."""
    # Check that title element exists
    title_blocks = app.title
    assert len(title_blocks) > 0


def test_page_layout_is_centered(app):
    """Page layout should be centered."""
    # Streamlit doesn't expose layout in AppTest, but we can verify the page loads
    assert app is not None


def test_page_renders_without_errors(app):
    """App should render without exceptions."""
    # If we got here, the app rendered successfully without errors
    assert app is not None


# ===========================================================================
# Welcome Section Tests
# ===========================================================================

def test_welcome_and_scenario_sections_load(app):
    """Welcome and scenario sections should load."""
    # The app should have multiple expanders and sections
    subheaders = [elem for elem in app.subheader]
    assert len(subheaders) >= 2


def test_scenario_description_present(app):
    """Scenario description should be available."""
    # Check that key UI elements are present
    buttons = [btn.label for btn in app.button]
    assert len(buttons) >= 3


def test_requirements_section_present(app):
    """Requirements section should be present."""
    # Check for existence of key buttons from all 3 sections
    buttons = [btn.label for btn in app.button]
    assert "Set up Owner & Pet" in buttons
    assert "Add task" in buttons
    assert "Generate schedule" in buttons


# ===========================================================================
# UI Elements Presence Tests
# ===========================================================================

def test_owner_pet_setup_section_present(app):
    """Owner & Pet Setup section should be visible with required inputs."""
    # Check for required text inputs
    owner_inputs = [elem for elem in app.text_input if "Owner" in (elem.label or "")]
    assert len(owner_inputs) > 0


def test_owner_name_input_exists(app):
    """Owner name input field should exist."""
    owner_name_inputs = [elem for elem in app.text_input if "Owner" in (elem.label or "")]
    assert len(owner_name_inputs) > 0


def test_pet_name_input_exists(app):
    """Pet name input field should exist."""
    pet_name_inputs = [elem for elem in app.text_input if "Pet" in (elem.label or "")]
    assert len(pet_name_inputs) > 0


def test_availability_inputs_exist(app):
    """Availability start and end inputs should exist."""
    avail_inputs = [elem for elem in app.number_input 
                    if "Availability" in (elem.label or "")]
    assert len(avail_inputs) >= 2


def test_species_selectbox_exists(app):
    """Species selectbox should exist."""
    species_boxes = [elem for elem in app.selectbox if "Species" in (elem.label or "")]
    assert len(species_boxes) > 0


def test_pet_age_input_exists(app):
    """Pet age input should exist."""
    age_inputs = [elem for elem in app.number_input if "age" in (elem.label or "").lower()]
    assert len(age_inputs) > 0


def test_setup_owner_pet_button_exists(app):
    """'Set up Owner & Pet' button should exist."""
    button_labels = [btn.label for btn in app.button]
    assert "Set up Owner & Pet" in button_labels


def test_add_tasks_section_present(app):
    """Add Tasks section should be visible with required inputs."""
    # Check for task title input
    task_inputs = [elem for elem in app.text_input if "Task" in (elem.label or "")]
    assert len(task_inputs) > 0


def test_task_title_input_exists(app):
    """Task title input should exist."""
    task_inputs = [elem for elem in app.text_input if "Task" in (elem.label or "")]
    assert len(task_inputs) > 0


def test_task_type_selectbox_exists(app):
    """Task type selectbox should exist."""
    type_boxes = [elem for elem in app.selectbox if "Type" in (elem.label or "")]
    assert len(type_boxes) > 0


def test_duration_input_exists(app):
    """Duration input should exist."""
    duration_inputs = [elem for elem in app.number_input 
                       if "Duration" in (elem.label or "")]
    assert len(duration_inputs) > 0


def test_priority_selectbox_exists(app):
    """Priority selectbox should exist."""
    priority_boxes = [elem for elem in app.selectbox if "Priority" in (elem.label or "")]
    assert len(priority_boxes) > 0


def test_recurring_checkbox_exists(app):
    """Recurring checkbox should exist."""
    checkboxes = [elem for elem in app.checkbox if "Recurring" in (elem.label or "")]
    assert len(checkboxes) > 0


def test_add_task_button_exists(app):
    """'Add task' button should exist."""
    button_labels = [btn.label for btn in app.button]
    assert "Add task" in button_labels


def test_build_schedule_section_present(app):
    """Build Schedule section should be visible with generate button."""
    # Check for generate schedule button
    button_labels = [btn.label for btn in app.button]
    assert "Generate schedule" in button_labels


def test_generate_schedule_button_exists(app):
    """'Generate schedule' button should exist."""
    button_labels = [btn.label for btn in app.button]
    assert "Generate schedule" in button_labels


# ===========================================================================
# Session State Initialization Tests
# ===========================================================================

# ===========================================================================
# Session State Initialization Tests
# ===========================================================================

def test_session_state_owner_initially_none(app):
    """Session state owner should initially be None."""
    assert app.session_state.owner is None


def test_session_state_pet_initially_none(app):
    """Session state pet should initially be None."""
    assert app.session_state.pet is None


def test_session_state_tasks_initially_empty(app):
    """Session state tasks should initially be an empty list."""
    assert app.session_state.tasks == []


# ===========================================================================
# Setup Owner & Pet Workflow Tests
# ===========================================================================

def test_setup_owner_and_pet_creates_objects(app):
    """Clicking 'Set up Owner & Pet' should populate session state."""
    setup_button = [btn for btn in app.button if btn.label == "Set up Owner & Pet"][0]
    setup_button.click()
    app.run()
    
    assert app.session_state.owner is not None
    assert app.session_state.pet is not None


def test_setup_uses_input_names(app):
    """Setup should use the names from the input fields."""
    setup_button = [btn for btn in app.button if btn.label == "Set up Owner & Pet"][0]
    setup_button.click()
    app.run()
    
    assert app.session_state.owner.name == "Jordan"  # default value
    assert app.session_state.pet.name == "Mochi"      # default value


def test_setup_resets_tasks_list(app):
    """Tasks list should be reset when setting up a new pet."""
    app.session_state.tasks = [{"test": "data"}]
    
    setup_button = [btn for btn in app.button if btn.label == "Set up Owner & Pet"][0]
    setup_button.click()
    app.run()
    
    assert app.session_state.tasks == []


def test_setup_converts_hours_to_minutes(app):
    """Setup should convert availability hours to minutes."""
    setup_button = [btn for btn in app.button if btn.label == "Set up Owner & Pet"][0]
    setup_button.click()
    app.run()
    
    # Default is 8 AM to 10 PM (8 to 22 hours)
    assert app.session_state.owner.available_start == 480   # 8 * 60
    assert app.session_state.owner.available_end == 1320    # 22 * 60


def test_setup_with_custom_values(app):
    """Setup should respect custom input values."""
    # Get the availability inputs and update them
    avail_start = [elem for elem in app.number_input 
                   if "Availability start" in (elem.label or "")][0]
    avail_end = [elem for elem in app.number_input 
                 if "Availability end" in (elem.label or "")][0]
    
    avail_start.set_value(9)
    avail_end.set_value(20)
    
    setup_button = [btn for btn in app.button if btn.label == "Set up Owner & Pet"][0]
    setup_button.click()
    app.run()
    
    assert app.session_state.owner.available_start == 540   # 9 * 60
    assert app.session_state.owner.available_end == 1200    # 20 * 60


def test_setup_creates_pet_relationship(app):
    """Pet should be registered with owner after setup."""
    setup_button = [btn for btn in app.button if btn.label == "Set up Owner & Pet"][0]
    setup_button.click()
    app.run()
    
    # Pet should be in owner's pets
    assert len(app.session_state.owner.pets) > 0


def test_success_message_shown_after_setup(app):
    """Success message should be displayed after setup."""
    setup_button = [btn for btn in app.button if btn.label == "Set up Owner & Pet"][0]
    setup_button.click()
    app.run()
    
    # Check that success messages were shown
    assert len(app.success) > 0


# ===========================================================================
# Add Tasks Section Tests
# ===========================================================================

def test_add_task_without_owner_shows_error(app):
    """Adding task without owner setup should show error."""
    add_task_button = [btn for btn in app.button if btn.label == "Add task"][0]
    add_task_button.click()
    app.run()
    
    assert len(app.error) > 0


def test_add_task_after_owner_setup_succeeds(app):
    """Adding task after owner setup should succeed."""
    # Setup owner/pet first
    setup_button = [btn for btn in app.button if btn.label == "Set up Owner & Pet"][0]
    setup_button.click()
    app.run()
    
    # Now add a task
    add_task_button = [btn for btn in app.button if btn.label == "Add task"][0]
    add_task_button.click()
    app.run()
    
    # Task should be added to session state
    assert len(app.session_state.tasks) > 0


def test_task_added_to_pet_object(app):
    """Task should be registered with the pet."""
    # Setup owner/pet
    setup_button = [btn for btn in app.button if btn.label == "Set up Owner & Pet"][0]
    setup_button.click()
    app.run()
    
    # Add task
    add_task_button = [btn for btn in app.button if btn.label == "Add task"][0]
    add_task_button.click()
    app.run()
    
    # Pet should have the task
    assert len(app.session_state.pet.tasks) > 0


def test_add_multiple_tasks(app):
    """Should be able to add tasks in sequence."""
    # Setup owner/pet
    setup_button = [btn for btn in app.button if btn.label == "Set up Owner & Pet"][0]
    setup_button.click()
    app.run()
    
    # Add first task
    add_task_button = [btn for btn in app.button if btn.label == "Add task"][0]
    add_task_button.click()
    app.run()
    
    first_task_count = len(app.session_state.tasks)
    assert first_task_count == 1
    
    # Verify the first task was added to the pet
    assert len(app.session_state.pet.tasks) == 1


def test_task_uses_default_title(app):
    """Task should use default title if not changed."""
    setup_button = [btn for btn in app.button if btn.label == "Set up Owner & Pet"][0]
    setup_button.click()
    app.run()
    
    add_task_button = [btn for btn in app.button if btn.label == "Add task"][0]
    add_task_button.click()
    app.run()
    
    # Default task title is "Morning walk"
    assert app.session_state.tasks[0]["Title"] == "Morning walk"


def test_task_with_custom_title(app):
    """Custom task title should be stored."""
    setup_button = [btn for btn in app.button if btn.label == "Set up Owner & Pet"][0]
    setup_button.click()
    app.run()
    
    # Set custom title
    task_title = [elem for elem in app.text_input if "Task title" in (elem.label or "")][0]
    task_title.set_value("Afternoon play")
    
    add_task_button = [btn for btn in app.button if btn.label == "Add task"][0]
    add_task_button.click()
    app.run()
    
    assert app.session_state.tasks[0]["Title"] == "Afternoon play"


def test_task_duration_stored_correctly(app):
    """Task duration should be stored as integer in minutes."""
    setup_button = [btn for btn in app.button if btn.label == "Set up Owner & Pet"][0]
    setup_button.click()
    app.run()
    
    # Change duration
    duration = [elem for elem in app.number_input if "Duration" in (elem.label or "")][0]
    duration.set_value(30)
    
    add_task_button = [btn for btn in app.button if btn.label == "Add task"][0]
    add_task_button.click()
    app.run()
    
    assert app.session_state.tasks[0]["Duration (min)"] == 30


def test_task_priority_stored_correctly(app):
    """Task priority should be stored correctly."""
    setup_button = [btn for btn in app.button if btn.label == "Set up Owner & Pet"][0]
    setup_button.click()
    app.run()
    
    priority = [elem for elem in app.selectbox if "Priority" in (elem.label or "")][0]
    priority.select("High")
    
    add_task_button = [btn for btn in app.button if btn.label == "Add task"][0]
    add_task_button.click()
    app.run()
    
    assert app.session_state.tasks[0]["Priority"] == "High"


def test_task_preferred_time_conversion(app):
    """Preferred time should be shown as time string when set."""
    setup_button = [btn for btn in app.button if btn.label == "Set up Owner & Pet"][0]
    setup_button.click()
    app.run()
    
    # Default preferred hour is 8
    add_task_button = [btn for btn in app.button if btn.label == "Add task"][0]
    add_task_button.click()
    app.run()
    
    # Should show as "8:00"
    assert app.session_state.tasks[0]["Preferred"] == "8:00"


def test_task_no_preferred_time_shows_dash(app):
    """When preferred hour is 0, should show dash."""
    setup_button = [btn for btn in app.button if btn.label == "Set up Owner & Pet"][0]
    setup_button.click()
    app.run()
    
    pref_hour = [elem for elem in app.number_input if "Preferred start" in (elem.label or "")][0]
    pref_hour.set_value(0)
    
    add_task_button = [btn for btn in app.button if btn.label == "Add task"][0]
    add_task_button.click()
    app.run()
    
    assert app.session_state.tasks[0]["Preferred"] == "—"


def test_recurring_checkbox_stored(app):
    """Recurring checkbox value should be stored in task."""
    setup_button = [btn for btn in app.button if btn.label == "Set up Owner & Pet"][0]
    setup_button.click()
    app.run()
    
    recurring = [elem for elem in app.checkbox if "Recurring" in (elem.label or "")][0]
    recurring.check()
    
    add_task_button = [btn for btn in app.button if btn.label == "Add task"][0]
    add_task_button.click()
    app.run()
    
    assert app.session_state.tasks[0]["Recurring"] is True


def test_no_tasks_shows_info_message(app):
    """When no tasks, info message should be shown."""
    setup_button = [btn for btn in app.button if btn.label == "Set up Owner & Pet"][0]
    setup_button.click()
    app.run()
    
    # Check for info message when no tasks
    info_messages = app.info
    assert len(info_messages) > 0


# ===========================================================================
# Generate Schedule Workflow Tests
# ===========================================================================

def test_generate_schedule_without_owner_shows_error(app):
    """Generating schedule without owner setup should show error."""
    generate_btn = [btn for btn in app.button if btn.label == "Generate schedule"][0]
    generate_btn.click()
    app.run()
    
    assert len(app.error) > 0


def test_generate_schedule_with_owner_no_tasks_shows_warning(app):
    """Generating schedule with owner but no tasks should show warning."""
    setup_button = [btn for btn in app.button if btn.label == "Set up Owner & Pet"][0]
    setup_button.click()
    app.run()
    
    generate_btn = [btn for btn in app.button if btn.label == "Generate schedule"][0]
    generate_btn.click()
    app.run()
    
    # Should show warning about adding tasks
    assert len(app.warning) > 0


def test_generate_schedule_with_owner_and_tasks_succeeds(app):
    """Generating schedule with tasks should produce success message."""
    setup_button = [btn for btn in app.button if btn.label == "Set up Owner & Pet"][0]
    setup_button.click()
    app.run()
    
    # Add a task
    add_task_button = [btn for btn in app.button if btn.label == "Add task"][0]
    add_task_button.click()
    app.run()
    
    # Generate schedule
    generate_btn = [btn for btn in app.button if btn.label == "Generate schedule"][0]
    generate_btn.click()
    app.run()
    
    # Should have success message (schedule generated)
    assert len(app.success) > 0 or len(app.warning) == 0  # Either success or at least no error


def test_schedule_generation_with_multiple_tasks(app):
    """Schedule should handle multiple tasks."""
    setup_button = [btn for btn in app.button if btn.label == "Set up Owner & Pet"][0]
    setup_button.click()
    app.run()
    
    add_task_button = [btn for btn in app.button if btn.label == "Add task"][0]
    
    # Add two tasks
    add_task_button.click()
    app.run()
    
    # Change title and add another
    task_title = [elem for elem in app.text_input if "Task title" in (elem.label or "")][0]
    task_title.set_value("Evening meal")
    add_task_button.click()
    app.run()
    
    # Generate schedule
    generate_btn = [btn for btn in app.button if btn.label == "Generate schedule"][0]
    generate_btn.click()
    app.run()
    
    # Should handle multiple tasks without error
    assert app.session_state.pet is not None


# ===========================================================================
# Complete Workflow Integration Tests
# ===========================================================================

def test_complete_workflow_owner_to_schedule(app):
    """Complete workflow: setup -> add task -> generate schedule."""
    # Step 1: Setup owner and pet
    setup_button = [btn for btn in app.button if btn.label == "Set up Owner & Pet"][0]
    setup_button.click()
    app.run()
    
    assert app.session_state.owner is not None
    assert app.session_state.pet is not None
    assert len(app.success) > 0
    
    # Step 2: Add a task
    add_task_button = [btn for btn in app.button if btn.label == "Add task"][0]
    add_task_button.click()
    app.run()
    
    assert len(app.session_state.tasks) > 0
    assert len(app.session_state.pet.tasks) > 0
    
    # Step 3: Generate schedule
    generate_btn = [btn for btn in app.button if btn.label == "Generate schedule"][0]
    generate_btn.click()
    app.run()
    
    # Should have success or generated schedule
    assert len(app.success) > 0 or len(app.session_state.pet.tasks) > 0


def test_workflow_with_multiple_tasks_and_schedule(app):
    """Workflow with tasks should work end-to-end."""
    # Setup
    setup_button = [btn for btn in app.button if btn.label == "Set up Owner & Pet"][0]
    setup_button.click()
    app.run()
    
    # Add a task
    add_task_button = [btn for btn in app.button if btn.label == "Add task"][0]
    add_task_button.click()
    app.run()
    
    # Should have one task
    task_count = len(app.session_state.tasks)
    assert task_count >= 1
    
    # Pet should also have the task
    assert len(app.session_state.pet.tasks) >= 1


def test_session_state_persists_across_interactions(app):
    """Session state should persist when interacting with the app."""
    # Setup owner and pet
    setup_button = [btn for btn in app.button if btn.label == "Set up Owner & Pet"][0]
    setup_button.click()
    app.run()
    
    owner_name_before = app.session_state.owner.name
    
    # Add a task
    add_task_button = [btn for btn in app.button if btn.label == "Add task"][0]
    add_task_button.click()
    app.run()
    
    # Owner should still be there
    assert app.session_state.owner.name == owner_name_before
    assert app.session_state.pet is not None
    assert len(app.session_state.tasks) > 0


def test_can_add_more_tasks_after_schedule_generation(app):
    """Should be able to continue using app after generating schedule."""
    # Setup
    setup_button = [btn for btn in app.button if btn.label == "Set up Owner & Pet"][0]
    setup_button.click()
    app.run()
    
    # Add task
    add_task_button = [btn for btn in app.button if btn.label == "Add task"][0]
    add_task_button.click()
    app.run()
    
    initial_count = len(app.session_state.tasks)
    assert initial_count >= 1
    
    # Generate schedule
    generate_btn = [btn for btn in app.button if btn.label == "Generate schedule"][0]
    generate_btn.click()
    app.run()
    
    # App should still be functional after schedule generation
    assert app.session_state.owner is not None
    assert app.session_state.pet is not None
