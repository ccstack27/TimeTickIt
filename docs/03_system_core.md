# System Core

This document defines the **core behavioral logic** of the TimeTickIt system.

It describes what the system does, the rules it must follow, and how it reacts to
user actions and inactivity. This document intentionally avoids UI details and
implementation-specific code.

---

## System Responsibility

The TimeTickIt system is responsible for:

- managing the lifecycle of time-tracking sessions,
- recording authoritative timestamps,
- tracking user inactivity during an active session,
- enforcing inactivity limits,
- maintaining valid system state, and
- preparing reliable data for output generation.

The system does not infer intent, automate work detection, or correct user behavior
beyond the rules explicitly defined here.

---

## System State Model

At any given time, the system exists in exactly one of the following states:

### IDLE
- No active session exists.
- The system is not tracking time.

### ACTIVE
- Exactly one active session exists.
- The system is tracking elapsed time for that session.
- User inactivity may be measured while in this state.

No other states are permitted.

---

## State Invariants

The following rules must always hold:

- At most **one active session** may exist at any time.
- A session cannot be started while another session is active.
- A completed session is **immutable**.
- All recorded times are derived from the system clock.
- User inactivity is evaluated **only while a session is active**.

Violation of these invariants is not allowed.

---

## Session Lifecycle

### Starting a Session

When the USER initiates a start action:

- the system must be in the **IDLE** state,
- the system records the SESSION START TIME,
- the inactivity timer is initialized to zero,
- the system transitions to the **ACTIVE** state.

If a start action is issued while the system is already ACTIVE, the action is rejected
and no state change occurs.

---

### Stopping a Session (User-Initiated)

When the USER initiates a stop action:

- if the system is in the **ACTIVE** state:
  - the system records the SESSION END TIME,
  - the session becomes complete and immutable,
  - the system transitions to the **IDLE** state.

- if the system is in the **IDLE** state:
  - the action is silently ignored,
  - no session is created,
  - no error is raised.

---

## User Inactivity Tracking

### Definition

User inactivity is defined as a continuous period during which **no mouse or keyboard
input** is detected globally (anywhere on the screen).

User inactivity:
- is measured only while the system is in the **ACTIVE** state,
- is tracked using an inactivity timer,
- does not pause or suspend the session.

---

### Inactivity Timer Behavior

- The inactivity timer increments continuously while no input is detected.
- **Any mouse or keyboard input resets the inactivity timer to zero.**
- Inactivity outside an active session is not tracked.

---

## Maximum Inactivity Rule

The system enforces a **maximum inactivity duration of 5 minutes**.

When user inactivity reaches 5 continuous minutes while a session is ACTIVE:

- the system automatically ends the session,
- the SESSION END TIME is set at the moment the inactivity limit is reached,
- the session is marked as completed and immutable,
- the inactivity duration is recorded in the **ADMINISTRATIVE RECORD**,
- the system transitions to the **IDLE** state.

The USER must explicitly start a new session to continue working.

---

## Session Duration Calculation

- SESSION TIME includes **all elapsed time** between SESSION START TIME and SESSION END TIME.
- This includes periods of user inactivity within the session.
- SESSION TIME is calculated only after the session has ended.
- SESSION TIME is not updated continuously while the session is active.

---

## Accumulated Session Time Calculation

ACCUMULATED SESSION TIME is:

- never stored as persistent state,
- calculated only during output generation,
- derived from completed sessions within a defined scope.

Inactivity time within sessions is included in accumulated totals.

---

## Application Interruption Handling

If the application terminates while the system is in the **ACTIVE** state:

- the active session is automatically ended,
- the SESSION END TIME is set to the last known system time,
- the session is treated as complete and immutable.

No retroactive correction is performed.

---

## Error Handling Philosophy

The system follows a **fail-safe and non-intrusive** approach:

- invalid actions do not modify system state,
- no automatic correction or guessing is performed,
- data integrity takes priority over convenience.

---

## Separation of Concerns

This document intentionally excludes:

- user interface behavior,
- visual prompts or warnings,
- output formatting and layout,
- file storage structure.

Those concerns are defined in their respective documents.

---

## Guiding Principle

The system core exists to **record time deterministically based on explicit user actions
and defined inactivity rules**.

All behavior must remain predictable, transparent, and free from hidden automation.
