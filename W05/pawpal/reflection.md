# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

The design uses four classes and two enumerations. `Task` holds the details of a single care activity (duration, priority, type, preferred time) and handles overlap checks via `overlaps_with()`. `Pet` owns a list of tasks and manages adding, removing, and sorting them. `Owner` stores the owner's name and daily availability window and owns a list of pets. `Scheduler` is a stateless service — `build_schedule(owner, pet)` applies a greedy interval algorithm and returns scheduled and unscheduled tasks. `Priority` and `TaskType` are enums that enforce type-safe values across the system.

**b. Design changes**

Several refinements were made after reviewing the initial skeleton:

- **Dropped a `Schedule` class** in favour of `Scheduler.build_schedule()` returning a plain dict. A dedicated class added no real behavior for this scope and would have been an extra layer to maintain.
- **Added `id`, `is_completed`, `scheduled_end`, and `unscheduled_reason` to `Task`** after review. `id` makes `remove_task` safe when titles collide; `scheduled_end` avoids recalculating it in `overlaps_with` and display helpers; `unscheduled_reason` gives the UI a clear explanation of why a task was dropped.
- **Added `_reset_id_counter()`** as a module-level utility so tests can reset the global ID counter between runs without producing fragile assertions tied to specific IDs.
- **Updated `display_schedule`** to append a `(moved from X:XX)` note when a task is placed later than its preferred time, making the scheduler's decisions transparent to the user.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
