# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.

## 🖥️ Sample Output

Here "Give meds" was pinned to 09:00, so it leads the day and the rest fall in
behind it by priority; "Playtime" is shortened to use up the last of the time.

```
Today's schedule for Jordan:
  09:00 — Give meds (5 min) [priority: high]
  09:05 — Morning walk (30 min) [priority: high]
  09:35 — Feeding (10 min) [priority: high]
  09:45 — Clean litter (15 min) [priority: medium]
  10:00 — Playtime (10 of 20 min, shortened) [priority: low]

Planned 5 task(s) starting at 07:30, within 70 available minutes.
  09:00 — Give meds (high priority; owner set it for 09:00)
  09:05 — Morning walk (high priority; fit in the 65 min still free)
  09:35 — Feeding (high priority; fit in the 35 min still free)
  09:45 — Clean litter (medium priority; fit in the 25 min still free)
  10:00 — Playtime (low priority; shortened to 10 of 20 min to use the time left)
```


## 🧪 Testing PawPal+

Run the tests from the project folder with:

```bash
python -m pytest tests/test_pawpal.py -v
```

The tests check the main things the scheduler is supposed to do. First they
make sure the basics work, like marking a task done and adding a task to a pet.
Then they check the trickier stuff: that sorting puts tasks in the right time
order, that finishing a daily task makes a new task for the next day, and that
the scheduler notices when two tasks are booked for the same time.

Here is what it looks like when all the tests pass:

```
============================= test session starts =============================
platform win32 -- Python 3.14.6, pytest-9.1.1, pluggy-1.6.0 -- C:\Users\kuwam\AppData\Local\Python\pythoncore-3.14-64\python.exe
cachedir: .pytest_cache
rootdir: c:\Users\kuwam\Documents\ai110-module2show-pawpal-starter
plugins: anyio-4.14.0
collecting ... collected 5 items

tests/test_pawpal.py::test_mark_complete_changes_status PASSED           [ 20%]
tests/test_pawpal.py::test_adding_task_increases_pet_task_count PASSED   [ 40%]
tests/test_pawpal.py::test_sort_returns_pinned_tasks_in_chronological_order PASSED [ 60%]
tests/test_pawpal.py::test_completing_daily_task_creates_task_for_next_day PASSED [ 80%]
tests/test_pawpal.py::test_conflict_detection_flags_duplicate_times PASSED [100%]

============================== 5 passed in 0.54s ==============================
```

**Confidence level: ⭐⭐⭐⭐⭐ (5/5)**

All 5 tests pass, and they cover the most important scheduling behaviors
(sorting, recurring tasks, and conflict detection), so I feel really good about
how reliable the system is.

## 📐 Smarter Scheduling

Beyond a basic to-do list, PawPal+ makes several scheduling decisions on the
owner's behalf. Each feature below names the method that implements it.

| Feature | Method(s) | Notes |
|---------|-----------|-------|
| Task sorting | `Scheduler.sort_by_priority()`, `Task.priority_rank()` | Highest priority first; ties broken by longest duration. |
| Owner-pinned / important tasks | `Scheduler.sort_by_priority()`, `Scheduler.generate_schedule()` | A task given a set `time` (or flagged as important) jumps to the front and is placed at that time, even if it's shorter than tasks that would normally go first. |
| Fitting tasks to available time | `Scheduler.generate_schedule()`, `Scheduler.fits_in_time()` | Tracks remaining minutes as it plans; a task that doesn't fully fit is *shortened* if at least half its time is free, otherwise left off (and reported, never hidden). |
| Filtering | `Scheduler.filter_tasks()` | Narrow tasks by completion status and/or pet name; both filters optional. |
| Conflict detection | `Scheduler.detect_conflicts()` | Flags overlapping owner-pinned times (same pet or different pets) and returns a warning message. Advisory only — it never changes the plan. |
| Recurring tasks | `Task.next_occurrence()`, `Task.mark_complete()`, `Pet.complete_task()` | Completing a daily/weekly task auto-creates the next instance with its due date advanced via `timedelta`. |
| Time validation | `is_valid_time()` | Checks that owner-entered times are real 24-hour `HH:MM` values before they reach the scheduler. |
| Plain-language plan | `Scheduler.explain()` | Explains what was scheduled, when, why, and what got left off. |

### How the sorting works

`sort_by_priority()` builds one sort key per task: owner-pinned tasks sort to
the front (earliest set time first), and everything else follows the priority
rank, with longer tasks breaking ties. So a specific-time or important task
always leads, and the rest fall into "most important, then longest" order.

## 📸 Demo Walkthrough

Describe your app in numbered steps so a reader can follow along without watching a video:

1. <!-- Describe this step -->
2. <!-- Describe this step -->
3. <!-- Describe this step -->
4. <!-- Describe this step -->
5. <!-- Add more steps as needed -->

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or link to a demo video here -->
