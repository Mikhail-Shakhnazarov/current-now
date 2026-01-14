# SPEC-001: Compaction Pattern (stub)

> Status: active
> Created: 2026-01-14
> Updated: 2026-01-14
> Target: `work/projects/devOS/compaction/`

---

## Summary

Define the compaction pattern as a reusable interface for Atlas pipelines.
Compaction is treated as a deterministic context engineering primitive.

---

## Definitions

Compaction is a transformation that takes high-dimensional durable state (notes, files, history) and produces a bounded, constrained representation that is suitable for reliable downstream processing.

A compaction instance typically includes an explicit handoff point (typed artifact) followed by deterministic propagation.

---

## Links

- MARCO/POLO pipeline: `work/projects/writeOS/marco-polo/specs/SPEC-001.md`
- Intake pipeline: `work/projects/devOS/intake-pipeline/specs/SPEC-001.md`

---

## Open

OPEN-001: Decide the minimum compaction interface shape.

Closure: define the required fields for (input, constraints, output, verification).

OPEN-002: Decide whether compaction is devOS tooling, writeOS documentation, or both.

Closure: define artifact ownership across `devOS/compaction` and writeOS projects.

---

## Verification

- Project wrapper exists with `now.md`, `specs/`, `logs/`, `.atlas/version`.
