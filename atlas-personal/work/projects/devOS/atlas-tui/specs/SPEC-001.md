# SPEC-001: Atlas TUI (stub)

> Status: active
> Created: 2026-01-14
> Updated: 2026-01-14
> Target: `work/projects/devOS/atlas-tui/`

---

## Summary

Define a client-facing Atlas TUI as an exportable devOS project.

Primary value is re-entry: fast project switching, state inspection, and deterministic triggers for tooling workflows.

---

## Scope

In scope (v1):

- Browse projects and open the relevant `now.md`/spec artifacts.
- Show current state (latest admissions, latest state files, recent runs).
- Invoke deterministic commands (repo hygiene, propagation, future airlock tooling).

Out of scope (v1):

- Deep writeOS authoring and transformation features.
- Automatic activation and task scheduling.

---

## Open

OPEN-001: Stack decision.

Closure: choose implementation stack (Python textual vs Rust ratatui vs other).

OPEN-002: v1 feature set.

Closure: define the minimal TUI screens and actions.

---

## Verification

- Project wrapper exists with `now.md`, `specs/`, `logs/`, `.atlas/version`, and `repo/`.
