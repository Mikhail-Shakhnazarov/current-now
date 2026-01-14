# Marco-Polo Challenge (Portable, v2)

This is a portable systems design and creative coding/writing challenge.
It is intentionally independent of any specific repository layout or tool UI.
This artifact is a v2 deliverable; v1 focuses on internal system design and tooling boundaries.

## Problem

You are given two documents.

The first, MARCO, is an operator note: high-throughput, semi-structured, and potentially multi-threaded. It may contain numbered items, bullet points, file references, and interwoven themes (requirements, proposals, questions, constraints). It is written in the operator's natural voice.

The second, POLO, is a derived breakdown that attempts to stabilize MARCO into explicit threads/themes, OPEN questions, and suggested routing to system surfaces. It is a structured reading intended to make review and re-entry cheap.

The operator approves POLO if it preserves MARCO well enough to be treated as a stable representation.

## Design Task

Design a two-way tooling layer that helps an operator work with MARCO/POLO pairs.

One direction is verification: given MARCO and POLO, produce graded, explainable evidence of correspondence rather than a binary match/no-match.

The other direction is preprocessing: given MARCO alone, produce a first-pass POLO draft using deterministic, surface-feature-driven transforms (structure extraction, labeling, conservative clustering) without inventing requirements.

## Constraints

Reliability is the point. This tooling is system plumbing.

Any text admitted to the system must be ASCII-only. Enforcement is strict by default; permissive behavior must be explicit.

Avoid spammy activation. Routing proposals must be non-binding. The tooling must not generate todos or mutate many surfaces by default.

## Acceptance Criteria (Formal)

A proposed solution is acceptable if it defines artifacts and checks such that:

1) Verification is graded and explainable.

It must produce a confidence output with reasons, including at minimum coverage evidence and novelty risk. The operator must be able to see why the tool believes the mapping is acceptable or risky.

2) Traceability is first-class.

It must define a trace artifact linking MARCO spans (or item ids) to POLO sections/threads. It must be possible to audit POLO back to MARCO.

3) Preprocessing is conservative.

It must define what transforms are allowed in v1 (restructure and surface) and what is forbidden (invent commitments, silently close ambiguities).

4) Admission is reliable.

It must define an airlock/admission step that enforces ASCII-only and fails fast on non-repairable input.

5) Activation is throttled.

It must define a default behavior that does not flood projects with todos. Any promotion from a routing proposal into an active task requires explicit operator termination.

## Notes

This challenge is meant to be shareable with other system engineers and developers. It is a problem statement and acceptance criteria, not a complete implementation spec.
