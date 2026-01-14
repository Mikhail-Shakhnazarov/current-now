# Spec Pack v0 (Marco-Polo)

This document defines portable, ASCII-only artifact formats and checks for Marco-Polo.

## 1) Admission / airlock

Default behavior: fail on any non-ASCII input. Emit airlock_report.json.

Optional permissive behavior: --repair-common-punct, using a fixed mapping table for a small allowlist:
- curly quotes -> straight quotes
- apostrophe variants -> '
- en/em dash -> --
- nbsp -> space

Any other non-ASCII character remains a hard fail.

## 2) Units

### 2.1 MarcoSpan (marco_spans.jsonl)
Each line is a JSON object:
- id: m:0007
- source_range: {line_start, line_end, col_start, col_end}
- kind: numbered_item | bullet | block
- text: normalized ASCII text
- fingerprint: sha256(text)

Segmentation rule (v1): item-level spans
- start a new span on numbered item markers (e.g., 1., 2))
- start a new span on bullet markers (-, *, +)
- otherwise use blank-line blocks

### 2.2 PoloUnit (polo_units.jsonl)
- id: p:T03.src02
- kind: thread | src | open | prop
- thread_id: T03
- text: normalized ASCII text
- fingerprint: sha256(text)

POLO typing protocol (v1): lines beginning with SRC:, OPEN:, PROP: are units.

## 3) Trace edges (trace_edges.jsonl)

Each line:
- polo_id
- marco_id
- rel: supports | mentions | proposes | unanswered
- score: float in [0, 1]
- features: small numeric object (e.g., tfidf_cosine, anchor_hits)
- rationale: short ASCII string naming the strongest anchors

Rel assignment rule:
- kind=src -> rel=supports
- kind=open -> rel=unanswered
- kind=prop -> rel=proposes
- kind=thread -> rel=mentions (optional; may be omitted)

No-link default: if no candidate exceeds match_min, do not emit an edge. The unit becomes unsupported.

Ambiguity: if top-2 candidate scores differ by <= ambiguity_epsilon, mark ambiguity in the report.

## 4) Verification report (verify_report.md)

Must include:
- Coverage evidence:
  - % of MarcoSpans referenced by any edge (score >= match_min)
  - list of unreferenced MarcoSpans (ids + short excerpts)
- Novelty risk:
  - list of unsupported PoloUnits (ids + text)
  - separate accounting for PROP ratio (proposal inflation)
- Ambiguity warnings:
  - PoloUnits with near-tied candidates (show both candidates)
- Confidence:
  - numeric confidence in [0,1] plus label
  - explicit reasons derived from metrics

Confidence policy is parameterized:
- thresholds: match_min, ambiguity_epsilon
- weights: w_coverage, w_novelty, w_ambiguity, w_prop_ratio
- bands: label ranges for low/med/high

## 5) Conservative drafting (MARCO -> POLO draft)

Drafting is deterministic and conservative:
- create threads by conservative keyword-tag clustering
- emit SRC lines per MarcoSpan with trace tags
- emit OPEN lines only from explicit question/ambiguity markers
- emit PROP lines only as non-binding suggestions, trace-linked to triggering spans

Forbidden: invent commitments; resolve ambiguity; produce tasks by default.
