# Testing Strategy

This document defines the **testing approach** for the TimeTickIt project.

Testing exists to ensure that the system behaves **predictably, deterministically,
and in alignment with documented rules**. The goal is correctness and confidence,
not exhaustive automation.

---

## Testing Philosophy

TimeTickIt follows a **pragmatic testing philosophy**:

- Prefer correctness over complexity.
- Test behavior, not implementation details.
- Validate system core rules before UI polish.
- Use automation where it adds confidence; use manual testing where it adds clarity.

Testing must never redefine system behavior.  
Documentation and system core rules always take precedence.

---

## Testing Scope

Testing is divided into the following layers:

1. **System Core Testing** (highest priority)
2. **Output Generation Testing**
3. **UI Behavior Verification**

---

## System Core Testing

System core tests validate the **authoritative behavior** defined in `03_system_core.md`.

### Required Test Cases

- **Session Lifecycle**
  - Start session transitions system from IDLE to ACTIVE.
  - Stop session transitions system from ACTIVE to IDLE.
  - Starting a session while ACTIVE is rejected.
  - Stopping a session while IDLE has no effect.

- **Single Active Session Invariant**
  - At most one active session exists at any time.
  - Overlapping sessions are not permitted.

- **Inactivity Handling**
  - User inactivity is detected only during an ACTIVE session.
  - Any mouse or keyboard input resets the inactivity timer.
  - A session is automatically ended after **5 minutes of continuous inactivity**.
  - The auto-ended session includes the full inactivity duration in SESSION TIME.

- **Time Calculation**
  - SESSION TIME is calculated only after session completion.
  - SESSION TIME includes all elapsed time, including inactivity.
  - Time calculations use seconds as the base unit.

- **Application Interruption**
  - If the app closes during an ACTIVE session, the session is ended automatically
    at the last known system time.

---

## Output Generation Testing

Output tests validate behavior defined in `04_output.md`.

### Required Test Cases

- **Read-Only Behavior**
  - Generating outputs does not modify session data.
  - Generating outputs does not reset or clear sessions.

- **Scope-Based Totals**
  - Accumulated Session Time is calculated only from sessions included in the
    selected output scope.
  - Different output generations may produce different totals based on scope.

- **ZIP Package Structure**
  - Output generation always produces a ZIP file.
  - The ZIP contains exactly:
    - `invoice.pdf`
    - `administrative_record.pdf`

- **Invoice Rules**
  - Invoice includes only completed sessions.
  - Invoice excludes inactivity details.
  - Invoice is generated in PDF format and is not encrypted.

- **Administrative Record Rules**
  - Administrative record includes inactivity duration when applicable.
  - Administrative record includes auto-end reason when sessions end due to inactivity.
  - Administrative record is generated in PDF format and is encrypted.

- **Encryption Validation**
  - Administrative record PDF requires password `adminv1` to open.
  - Invoice PDF opens without a password.

---

## UI Behavior Verification

UI testing focuses on **verification**, not enforcement.

### Manual Verification Checklist

- UI correctly reflects system state (IDLE / ACTIVE).
- Start and Stop controls are enabled or disabled based on system state.
- Inactivity countdown appears only when inactivity occurs.
- Inactivity countdown resets on mouse or keyboard input.
- Auto-ended sessions display a neutral, temporary notification.
- Avatar cycles through built-in images and persists across restarts.
- Generate Output button prompts for save location and produces a ZIP file.
- UI does not send emails or transmit files.

UI tests must confirm that the UI **does not perform system logic**.

---

## Time Control in Tests

Where possible:
- Time should be **simulated or mocked** for automated tests.
- Real-time delays should be avoided to keep tests fast and deterministic.

Manual testing may use real-time observation when validating UI behavior.

---

## Regression Testing Rule

> **Any change to the system core must not break existing tests.**

When behavior changes intentionally:
- documentation must be updated first,
- tests must be updated second,
- code changes must follow.

Regression tests exist to protect:
- session integrity,
- billing correctness,
- inactivity enforcement,
- output consistency.

---

## Non-Goals of Testing

Testing does **not** aim to:
- validate third-party libraries,
- measure performance benchmarks,
- enforce UI aesthetics,
- provide security guarantees beyond documented behavior.

---

## Guiding Principle

Testing exists to ensure that **what is documented is what the system does**.

If a behavior cannot be tested, it must be questioned.
