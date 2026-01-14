# Now: marcopolo

## Current State

A Python implementation repo was imported into this devOS wrapper.

- Client repo: `repo/`
- Upstream docs: `repo/docs/`
- Schemas: `repo/schemas/`

This repo matches the direction of the writeOS pilot `writeOS/marco-polo/`.
The system is moving toward typed POLO (SRC/OPEN/PROP) as the deterministic interface.

## Intent

Assimilate the imported implementation into Atlas conventions without losing its strengths:
trace-first verification, conservative deterministic drafting, strict ASCII admission, and non-activation by default.

## Next

1. Read `specs/SPEC-001.md` (assimilation plan).
2. Treat typed POLO (SRC/OPEN/PROP) as the deterministic interface; keep optional human renderings.
3. Define the v1 airlock CLI contract (overwrite in place; strict default; permissive flag explicit).
4. Verify standalone demo behavior (tests + CLI runs).
