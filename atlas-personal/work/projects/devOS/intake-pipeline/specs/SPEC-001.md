# SPEC-001: Intake Pipeline Proposal (v1)

> Status: active
> Created: 2026-01-14
> Updated: 2026-01-14
> Target: `work/projects/devOS/intake-pipeline/`

---

## Summary

Define and operationalize a daily intake pipeline that converts semi-structured operator notes (MARCO) into a canonical typed POLO artifact, then propagates POLO deterministically into project-local state with minimal spam.

This project is the devOS handoff surface: it should be readable to a developer friend and specific enough to implement.

---

## Design Goals

Reliability and leverage are the point. The pipeline should produce durable artifacts that are easy to re-enter and easy to audit.

The operating mode is a stable parking lot: the operator works in hyperfocused bursts and switches contexts quickly. The worst failure mode is spammy activation.

---

## Pipeline (Target Shape)

Stage 0: capture

Operator writes MARCO as a markdown file in Obsidian throughout the day. MARCO is semi-structured, not garbage.

MARCO template (v1): `inbox-airlock/operator-obsidian-render/marcopolo-intake/MARCO_TEMPLATE.md`

Stage 1: compile

A small model converts MARCO into typed POLO. The output contract is strict and parseable.

Design note: the intake pipeline is primarily a context-forming process. The capture stage holds signal in semi-structured form. The compile stage performs a light semantic transform into a strict typed POLO interface. The deterministic propagation stage precompiles engineered context (state, admissions, runs). Interpreter work later starts from clean context.

Project mention annotation (v1): `@<project>` in MARCO is treated as a weak mention marker (not a routing command). Hash tags are out of scope for v1.

Stage 2: termination

Operator reads typed POLO and approves it. Approval gates propagation.

Stage 3: propagate (deterministic)

A deterministic tool parses typed POLO and updates exactly one rolling project state file. It also writes run artifacts and an append-only admission record.

Stage 4: verify (optional, late)

A deterministic verifier can generate trace artifacts and a graded report after the fact. This is not required for v1 propagation.

Stage 5: synthesize (optional)

A larger model performs higher-order synthesis using the precompiled artifacts (typed POLO + state + admission logs + optional verification).

---

## Handoff Contract (v1)

Typed POLO is canonical and typed by explicit line prefixes.

Threads are markdown headings starting with `## `.

Typed lines:

- `SRC:` grounded paraphrase or quote of MARCO (no new commitments)
- `OPEN:` explicit question/decision (no silent closure)
- `PROP:` non-binding suggestion (always labeled, never activated by default)

Everything that is not grounded must not be emitted as `SRC`.

---

## Deterministic Propagation (v1)

Propagation is the primary automated step in v1. It must be deterministic and low-spam.

It must:

- Enforce ASCII-only at the airlock by overwriting input files in place.
- Write immutable run artifacts for provenance.
- Update exactly one rolling state file per project.
- Append an admission record (tooling emits system data).
- Never create tasks or mutate multiple surfaces by default.

PROP inclusion in the rolling state is an explicit operator flag.

Canonical intake location (v1):

`inbox-airlock/operator-obsidian-render/marcopolo-intake`

---

## Synergy Notes

The pipeline is a precompilation mechanism for interpreter context. Typed POLO and deterministic propagation reduce ambiguity and reduce token waste by turning raw operator notes into expectation-compatible artifacts.

Two additional system leverage ideas connect directly to this project: a RAG-ready context pack per repo/project (portable summaries and key artifacts), and explicit two-step sequential processing with a clear handoff point (plan/interpret -> agentic/execute) optimized for safe parallelization.

## References

- writeOS design and constraints: `work/projects/writeOS/marco-polo/specs/SPEC-001.md`
- deterministic propagation prototype: `desk/tools/marcopolo_atlas.py`
- deterministic verifier reference: `work/projects/devOS/marcopolo/repo/`
- Atlas glue fork: `work/projects/devOS/marcopolo-atlas/specs/SPEC-001.md`

---

## Acceptance Criteria

A v1 implementation is acceptable if:

- An operator can run a single root-invoked command that takes MARCO and typed POLO from the intake folder and produces a run folder plus a rolling state file.
- The tool is strict about ASCII by default and fails fast on unrepairable input.
- The tool is non-activating by default and does not create todos.
- The system remains re-enterable: the latest state is visible in one file, and provenance exists via run artifacts and admissions.

---

## Open

OPEN-001: Decide the minimal MARCO discipline/template.

Closure: keep it lightweight and iterate from real usage.

OPEN-002: Decide the model split.

Closure: confirm small model for MARCO->POLO, big model for synthesis.

OPEN-003: Decide where the implementation lives.

Closure: keep `desk/tools/` as prototype; migrate later into a standalone `repo/` under this project.

OPEN-004: Alias policy for project mentions.

Closure: define whether `@intake_pipeline`-style aliases are accepted and how aliases resolve to canonical project paths.

OPEN-005: Pair ledger and retention policy.

Closure: define the canonical ledger artifact for MARCO/POLO pairs (pointer-based, no copies) and when entries are created.

OPEN-006: Resolution tracking for MARCO items.

Closure: define whether resolution state is tracked in rolling POLO-derived state (preferred) vs tracked directly in MARCO.

---

## Verification

- Project wrapper exists with `now.md`, `specs/`, `logs/`, `.atlas/version`.
