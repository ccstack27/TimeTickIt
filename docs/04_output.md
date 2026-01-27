# Output Files

This document defines how TimeTickIt generates **output files** from recorded session data.

Output files are **read-only artifacts** created explicitly at the USER’s request.
They summarize completed work sessions and are intended for external sharing or
internal verification.

Output generation does **not** modify session data or system state.

---

## General Output Rules

The following rules apply to all outputs:

- Only **completed sessions** are included.
- **Active sessions are always excluded**.
- Output scope is defined by the USER at generation time (for example, a date range).
- All totals and summaries are **derived values**, calculated at generation time.
- Output generation does not start, stop, or alter sessions.

---

## Billable Time Rule

> **All time within a completed session is billable, including periods of user inactivity.**

This applies equally to:
- sessions ended by the USER, and
- sessions automatically ended by the system due to maximum inactivity.

Idle or inactive time **outside** an active session is never included.

---

## Output Package (ZIP)

TimeTickIt always generates outputs as a **single ZIP package**.

### Characteristics

- The ZIP file contains exactly **two PDF documents**:
  1. an invoice, and
  2. an administrative record.
- The ZIP file groups related outputs to prevent partial or accidental disclosure.
- The USER chooses the save location for the ZIP file.
- The application does not transmit, upload, or email files.

### Example Structure

TimeTickIt_Output_<date>.zip
├─ invoice.pdf
└─ administrative_record.pdf

---

## Invoice

An **INVOICE** is an employer-facing output file.

### Purpose

- Provide a clear summary of completed work sessions.
- Present total billable time derived from recorded sessions.

### Characteristics

- Includes completed sessions within the selected scope.
- Displays SESSION START TIME, SESSION END TIME, and SESSION TIME.
- Includes accumulated session time totals.
- **Does not expose user inactivity details**.
- Treats user-ended and inactivity-ended sessions identically.
- Is generated in **PDF format** and is **not encrypted**.

Invoices are generated and shared by the USER at their discretion.
They do not provide employers with access to the application.

---

## Administrative Record

An **ADMINISTRATIVE RECORD** is an internal verification output.

### Purpose

- Provide authoritative session data for review or dispute resolution.
- Explain system-driven session termination when applicable.

### Characteristics

- Includes all completed sessions within the selected scope.
- Displays SESSION START TIME, SESSION END TIME, and SESSION TIME.
- Includes accumulated session time totals.
- Includes **user inactivity duration** when inactivity occurred.
- Includes the **session end reason** for sessions automatically ended due to inactivity.
- Is generated in **PDF format** and is **encrypted**.

---

## Administrative Record Encryption

The administrative record PDF is protected using **password-based encryption**.

### Encryption Rules

- The administrative record is encrypted with the password: "adminv1"
- The purpose of encryption is **access control**, not high-security cryptography.
- The invoice PDF is **not encrypted**.
- Encryption applies to the administrative record PDF itself, not solely to the ZIP file.

The encryption password is intentionally fixed and documented to ensure predictable access
for authorized reviewers.

---

## Auto-Ended Sessions

When a session is automatically ended due to reaching the maximum inactivity time:

- The session is included as a completed session.
- The entire session duration, including inactivity time, is billable.
- The invoice displays the session as a normal completed session.
- The administrative record explicitly includes:
- inactivity duration, and
- the auto-end reason.

---

## Separation of Concerns

This document does not define:
- how sessions are tracked,
- how inactivity is detected,
- how the user interface behaves.

Those concerns are defined in:
- `03_system_core.md`
- `05_ui.md`

---

## Guiding Principle

Output files exist to **accurately and transparently reflect recorded session data**.

Visibility is intentionally controlled:
- invoices prioritize clarity and billing,
- administrative records prioritize verification and accountability.
