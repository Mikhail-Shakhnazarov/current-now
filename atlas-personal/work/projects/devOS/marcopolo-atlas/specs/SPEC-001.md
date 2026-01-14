# SPEC-001: Atlas operator CLI for marcopolo pipeline (v1)

> Status: active
> Created: 2026-01-14
> Updated: 2026-01-14
> Target: `work/projects/devOS/marcopolo-atlas/`

---

## Summary

Create an Atlas-specific operator CLI (invoked from repo root) that enforces ASCII admission (overwrite in place) and runs the deterministic marcopolo pipeline to produce canonical typed POLO artifacts and trace evidence for `writeOS/marco-polo`.

The standalone repo at `work/projects/devOS/marcopolo/repo/` remains exportable and unchanged.

---

## Requirements

The operator CLI must:

- Run from the Atlas root.
- Enforce ASCII-only on provided airlock file paths by default and overwrite them in place.
- Be strict by default; permissive behavior must be explicit.
- Produce deterministic artifacts (typed POLO, trace edges, graded verification report) with predictable project-local output paths.
- Produce an admission record (what was overwritten, what artifacts were written, what was not activated).
- Never activate by default (no todos, no multi-surface mutation).

---

## Open

OPEN-001: CLI name and argument contract.

Closure: choose command name and flags (project selection, mode draft/verify, strict/permissive).

OPEN-002: Output placement.

Closure: choose canonical output folder scheme under `work/projects/writeOS/marco-polo/outputs/`.

---

## Verification

- Running the CLI on an example MARCO/POLO pair produces typed artifacts and a report in the chosen output folder.
- Any non-ASCII input fails strict mode and is not admitted.
