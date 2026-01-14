# SPEC-001: Assimilate marcopolo repo into Atlas (v1)

> Status: active
> Created: 2026-01-14
> Updated: 2026-01-14
> Target: `work/projects/devOS/marcopolo/`

---

## Summary

Wrap the imported `marcopolo` implementation as a first-class Atlas devOS project and align it with the `writeOS/marco-polo` design direction. Preserve the repo's strengths (trace-first verification, typed POLO, deterministic drafting, strict ASCII admission, non-activation by default) while making the integration explicit and low-spam.

---

## Context

This project is an implementation candidate for the workflow specified in `work/projects/writeOS/marco-polo/specs/SPEC-001.md`.
It introduces a typed POLO protocol (SRC/OPEN/PROP) and a trace graph artifact family.

---

## Scope

In scope (v1):

- Make the imported repo portable inside Atlas: stable wrapper structure, clear intent, clear next steps.
- Document assimilation deltas (where Atlas conventions differ from the imported repo defaults).
- Move the system toward typed POLO as the deterministic interface for tooling outputs.

Out of scope (v1):

- Rewriting the entire codebase to match Atlas conventions.
- Deep semantic linking beyond deterministic matching.
- Any automatic activation (task creation, project mutation) by default.

---

## Requirements

Must:

- Maintain strict ASCII-only behavior by default in all tooling.
- Keep outputs non-activating by default (stage artifacts only).
- Keep `repo/` exportable as a normal standalone repository.
- Ensure `repo/` has formal standalone docs (README, license/authorship, how to run tests).
- Define where generated artifacts should live under the Atlas wrapper (project-local outputs/logs).
- Define how typed POLO artifacts relate to human-facing POLO views.

Should:

- Align licensing metadata with the parent Atlas repository conventions.
- Keep the CLI UX minimal (one command per action) and deterministic.

---

## Open

OPEN-001: Airlock behavior delta.

The imported CLI writes `airlock_report.json` but does not overwrite input files.
Atlas v1 wants overwrite-in-place at the airlock.

Closure: decide whether to implement overwrite-in-place as a thin wrapper CLI around the existing tool, or modify the tool's airlock command.

OPEN-002: Output placement.

The imported CLI defaults to `out/`.
Atlas wants predictable project-local artifact locations.

Closure: choose output directories under `work/projects/devOS/marcopolo/` (for example `outputs/` and/or `logs/`).

OPEN-003: Typed POLO adoption.

Closure: decide whether typed POLO is the canonical internal representation, with an optional human rendering, or whether typed POLO remains internal to the tool.

---

## Verification

- `repo/` contains a working Python package layout (`pyproject.toml`, `src/`, `tests/`).
- Wrapper contains `now.md`, `specs/`, `logs/`, `.atlas/version`.
- Hygiene passes (`python atlas-personal/desk/tools/repo_hygiene.py --check`).
