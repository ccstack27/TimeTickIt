# About TimeTickIt

## Purpose of This Document

This document provides high-level context for the **TimeTickIt** software project.  
It is intended to be read by:

- the project maintainer,
- future contributors, and
- AI assistants (such as PyCharm Junie AI) used to compose or reason about the codebase.

This file is **not** a technical specification, a user guide, or an implementation manual.  
Its role is to establish shared understanding, boundaries, and intent before any system behavior is discussed in detail.

Formal rules, definitions, and logic are intentionally documented in later files.

---

## What TimeTickIt Is

TimeTickIt is a **personal, offline time-tracking application designed for employees**, particularly those working remotely or independently.

The software allows a user to:
- manually start and stop work sessions,
- record time spent on tasks,
- view accumulated working time, and
- generate structured output files (such as invoices and administrative records).

TimeTickIt is implemented in **Python** and uses **Tkinter** for its graphical user interface.

TimeTickIt is **user-operated**. All tracking actions are explicitly initiated by the user.  
There is no automatic monitoring or background surveillance.

---

## What TimeTickIt Is Not

To avoid ambiguity, TimeTickIt is explicitly **not**:

- a monitoring or surveillance tool  
- a keystroke, screenshot, or activity capture system  
- a background process that records time without user intent  
- a cloud-based or network-dependent application  
- an employer-controlled system or dashboard  

The software does not attempt to enforce productivity, validate honesty, or police behavior.  
Its responsibility is **accurate recording**, not judgment.

---

## Offline-Only Design Constraint

TimeTickIt is designed to operate **entirely offline by design**.

This means:
- no internet connection is required,
- no data is transmitted externally,
- no background synchronization exists, and
- all records are stored locally on the user’s machine.

This constraint is intentional and foundational.  
It should be treated as a **hard boundary**, not an optional optimization.

---

## Relationship to Employers

Employers do **not** interact directly with the application.

The employer’s involvement is limited to **receiving generated output files**, such as:
- invoices, and
- administrative session records.

These files are created by the user and shared externally at the user’s discretion.  
There is no live access, remote visibility, or employer-side control built into the system.

---

## Trust and Integrity Model

TimeTickIt follows a **hybrid trust model**:

- The user is trusted to start and stop sessions honestly.
- The system records session data accurately and consistently.
- Administrative records exist to support verification or review if needed.

Integrity is supported through **transparent logging**, not technical coercion.

---

## Scope Stability

This document describes **current, intentional behavior only**.

- No future features are implied.
- No roadmap is suggested.
- Absence of a feature should be interpreted as **out of scope**, not “not yet implemented”.

All future changes must be explicitly documented elsewhere.

---

## Terminology Note

Some terms used in this document (for example: *session*, *accumulated time*, or *output files*) are **formally defined** in:

**02_definition_of_terms.md**

When in doubt, formal definitions take precedence over informal wording.

---

## Guiding Principle

TimeTickIt aims to be:

- simple,
- transparent,
- respectful of user autonomy, and
- predictable in behavior.

Clarity is valued over cleverness.  
Explicit design decisions are preferred over inferred behavior.
