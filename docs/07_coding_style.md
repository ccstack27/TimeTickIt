# Coding Style Guide

This document defines the **coding style and development guidelines** for the
TimeTickIt project.

The purpose of this guide is to ensure that code remains **clear, predictable,
maintainable, and aligned with documented system behavior**, especially when
developed with AI assistance.

This guide is **strongly recommended**, but not dogmatic.

---

## Core Principles

All code written for TimeTickIt must prioritize:

- clarity over cleverness
- explicit behavior over implicit assumptions
- predictability over convenience
- readability for humans and AI tools

If code behavior is not obvious from reading it, the code must be simplified.

---

## Architectural Boundaries

Code must respect the following boundaries:

- **System core**:
  - owns session lifecycle logic
  - owns inactivity tracking and enforcement
  - owns time calculations
- **UI layer**:
  - reflects system state
  - triggers explicit user actions
  - must not contain business logic
- **Output layer**:
  - generates files
  - performs encryption
  - must not modify session data

Logic must never “leak” across these boundaries.

---

## Function Design

Functions should be:

- small and focused
- named after what they **do**, not how they work
- explicit about side effects

Prefer:
- multiple small functions  
over:
- one large, multi-purpose function

A function should ideally do **one thing** and do it clearly.

---

## Time Handling

Direct access to system time is allowed.

### Rules

- Capture system time **explicitly** at meaningful moments:
  - session start
  - session end
  - inactivity threshold reached
- Do not repeatedly query the system clock during calculations.
- Do not use `sleep()` or time delays to control logic.
- Separate:
  - time used for **logic**
  - time used for **display**

Time handling must remain deterministic and testable.

---

## Constants and Fixed Values

Fixed values must be:

- declared explicitly
- named clearly
- documented inline

Examples include:
- maximum inactivity time (5 minutes)
- encryption password (`adminv1`)

Inline constants are preferred over centralized configuration files unless
a value becomes genuinely configurable.

Avoid unexplained “magic numbers”.

---

## Error Handling Philosophy

Error handling depends on **context and layer**.

### Rules

- Invalid **user actions**:
  - must not raise exceptions
  - must fail safely or be ignored
- Invalid **system states** or programmer errors:
  - must raise clear exceptions
- Output generation failures:
  - must fail clearly and explicitly
- UI misuse:
  - must be prevented through disabled controls, not error messages

The system must never auto-correct user behavior or guess intent.

---

## Side Effects and Data Safety

- Functions that modify data must do so explicitly.
- Read-only operations must not mutate state.
- Output generation must never reset, clear, or alter session data.

If a function has side effects, they must be obvious from its name and documentation.

---

## Readability and Formatting

- Follow standard Python formatting conventions.
- Use descriptive variable and function names.
- Avoid excessive nesting.
- Prefer early returns to deeply nested conditionals.

Code should be readable without additional explanation.

---

## Comments and Documentation

Comments should explain **why**, not **what**.

Use comments to:
- clarify intent
- document rules
- explain non-obvious decisions

Avoid comments that merely restate the code.

---

## AI Collaboration Guidelines

TimeTickIt is designed to be developed with AI assistance.

Code should be written to be:

- easy for AI tools to read
- safe for AI tools to modify
- resistant to over-abstraction

This means:
- avoid overly generic utilities
- prefer explicit logic over clever reuse
- allow small, intentional duplication when it improves clarity

If AI-generated code obscures intent, it must be refactored.

---

## Testing Alignment

All code must be written with testing in mind.

- Logic must be testable without UI involvement.
- Time-dependent behavior must be verifiable.
- Changes to system core must not break existing tests.

If code cannot be tested, its design must be reconsidered.

---

## Guiding Principle

> **Readable, explicit code is a feature.**

If a choice must be made between elegance and clarity, clarity wins.
