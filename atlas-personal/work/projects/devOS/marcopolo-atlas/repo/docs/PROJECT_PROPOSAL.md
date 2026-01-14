# Marco-Polo Project Proposal (v2)

## Summary

Marco-Polo is a portable reliability tool for MARCO/POLO pairs:

- Verification: given MARCO and POLO, produce graded, explainable evidence of correspondence.
- Preprocessing: given MARCO alone, produce a conservative POLO draft via deterministic transforms.

Reliability is the point. Outputs are ASCII-only (strict by default) and non-activating by default
(staging artifacts only; explicit promotion required to change state elsewhere).

## Problem statement

Operators write MARCO notes fast, multi-threaded, and semi-structured. POLO attempts to stabilize MARCO
into explicit threads, OPEN questions, and non-binding routing proposals so review and re-entry are cheap.

The reliability problem: POLO can drift. It can miss signal, invent commitments, or silently resolve ambiguities.
Binary checks ("looks right") do not scale. A graded, explainable verification layer is required.

## Goals

1) Verification is graded and explainable (coverage, novelty risk, ambiguity, confidence with reasons).
2) Traceability is first-class (trace artifact linking POLO units back to MARCO spans).
3) Preprocessing is conservative (deterministic surface transforms only; no invented commitments).
4) Admission is reliable (ASCII-only airlock; explicit permissive repair only).
5) Activation is throttled (no todos or state mutation by default; explicit operator promotion step).

## Non-goals (v1)

- No UI beyond CLI + plain artifacts.
- No automatic integration into a broader Atlas system.
- No LLM dependency in the core pipeline (LLM suggestions, if added later, remain a separate channel).

## Core design: trace graph as verification primitive

Verification is treated as a trace graph, not document similarity:

- MarcoSpan: item-level unit of MARCO (numbered item, bullet, or block).
- PoloUnit: unit of POLO (thread header, SRC/OPEN/PROP line, etc.).
- Edge: typed link PoloUnit -> MarcoSpan with score and rationale.

This makes verification explainable by construction: every POLO unit is either traced to MARCO or flagged.

## v1 design choices

- Matching: deterministic TF-IDF similarity for recall, with hard thresholds.
- Segmentation: MARCO spans are item-level in v1; resolution can improve later (clause/entity level).
- Confidence policy: parameterized (thresholds/weights/bands exposed; no canonical thresholds in v1).

## Typed POLO protocol

POLO lines are typed:

- SRC: grounded paraphrase/quote of MARCO (expects strong trace support).
- OPEN: decision/question required (expects trace to explicit ambiguity markers).
- PROP: non-binding routing/projection suggestion (allowed but must be labeled and trace-linked).

## Allowed vs forbidden transforms (preprocessing contract)

Allowed (deterministic):
- Segment by surface markers (numbering, bullets, blank lines).
- Label by keyword/regex patterns.
- Cluster by similarity above threshold; otherwise keep separate.
- Extract OPEN items only from explicit markers ("?", "needs decision", "unclear", etc.).
- Emit PROP routing suggestions only as PROP and only when anchored to concrete references.

Forbidden (v1):
- Invent commitments ("we will", deadlines, assignments).
- Resolve ambiguity silently.
- Generate actions or mutate external state by default.
- Present elaboration as SRC (elaboration must be typed PROP).

## Activation throttling

Default: produce only local artifacts. No task creation. No routing execution.
Promotion is a separate explicit step (can be implemented as a promotion record file in v1).

## Deliverables (v1)

- Spec pack for artifact formats, contracts, and scoring.
- Reference CLI implementation (python): airlock, extract, match, verify, draft.
- Example corpus: MARCO/POLO pairs including at least one "drifty POLO" case.
- Golden tests: airlock strictness, segmentation stability, deterministic matching, report computations.

## Milestones

M0: schemas + airlock + config surface.
M1: MARCO item-level segmentation.
M2: POLO unit parser (SRC/OPEN/PROP).
M3: TF-IDF matcher + trace edges + ambiguity detection.
M4: graded verification report generator.
M5: conservative POLO drafter + example corpus + tests.
