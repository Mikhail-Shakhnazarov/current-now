# Now: intake-pipeline

## Current State

This project defines the end-to-end intake pipeline as a devOS deliverable.

The pipeline is emerging from existing work:

- MARCO template (Obsidian): `inbox-airlock/operator-obsidian-render/marcopolo-intake/MARCO_TEMPLATE.md`
- Conceptual design and constraints: `work/projects/writeOS/marco-polo/specs/SPEC-001.md`
- Deterministic propagation prototype: `desk/tools/marcopolo_atlas.py`
- Deterministic verification/drafting reference: `work/projects/devOS/marcopolo/repo/` and `work/projects/devOS/marcopolo-atlas/repo/`

## Intent

Operationalize the daily intake workflow:

MARCO (Obsidian note) -> small model emits typed POLO -> operator reads/approves -> deterministic propagation -> optional late verification -> big model synthesis.

## Next

1. Read `specs/SPEC-001.md` (project proposal).
2. Capture the synergy notes (RAG context packs; sequential plan/execute handoff and parallelization).
3. Define the v1 handoff contract (typed POLO rules + propagation outputs).
4. Define the devOS implementation work split: what stays in `desk/tools/` vs what becomes a standalone repo under `repo/`.
