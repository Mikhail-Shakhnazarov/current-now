# SPEC-001: Marco-Polo Mapping Evaluation (Open Design)

> Status: active
> Created: 2026-01-13
> Updated: 2026-01-14 (v1 propagation + intake path locked)
> Note: v1 assumes ASCII hygiene enforced at intake; interpreter must still flag violations if encountered.
> Target: `work/projects/writeOS/marco-polo/`
> Supersedes: N/A
> Superseded by: N/A

---

## Summary

Define the design space for mechanically easing operator approval of a derived breakdown (`polo.md`) from a semi-structured operator note (`marco.md`). The project focuses on (1) graded verification (non-binary confidence that the documents map) and (2) deterministic pre-processing to restructure marco-style input into a first-pass polo-style breakdown, using surface features (Obsidian-style structure) without automating authority: operator termination remains the only closure.

---

## Problem Definition: The Marco-Polo Challenge (High-Leverage, High-Reliability)

This project treats operator input assimilation as a systems-engineering problem rather than a writing exercise. We start from a proven pair of artifacts: `marco.md`, a raw operator note written in the operator's natural voice, and `polo.md`, a derived structured breakdown that the operator approved as faithful enough to use. The creative challenge is not to generate nicer prose. The creative challenge is to build a two-way tooling layer that makes the relationship between these documents legible, leverageable, and safe to operationalize under parallel project pressure.

In this framing, marco is high-bandwidth signal with implicit structure. It is messy by design: multiple themes, proposals, questions, constraints, and meta-intent can be interwoven because that is how the operator thinks at speed. Polo is a stabilization artifact: it externalizes structure into explicit threads, surfaces, and OPEN items so the system can park complexity, preserve re-entry, and reduce drift. Polo is not "more true" than marco; it is a structured reading whose authority comes only from operator termination. The system's job is to reduce the cost of that termination event by making evidence visible and review cheap, without pretending to automate judgment.

The twist, and the point of leverage, is that we want the system to be composable and self-amplifying. We leverage everything and we build everything to be leveraged. That means every stage of the pipeline should produce artifacts that can serve downstream operations: trace maps that support audit and re-entry, graded verification reports that support safe parking, deterministic pre-processing that supports throughput without spam, and project inbox drops that support immediate routing without interpretation. The artifacts are not just outputs; they are interfaces. A good interface makes future automation easier without requiring it now.

Tooling is also a source of system data. Reliable plumbing should emit durable, structured traces of what it did (what arrived, what was normalized, what artifacts were written, what was explicitly not activated). When those traces are stable and well-formatted, they become a memex-like substrate for later retrieval and synthesis.

This project now has an implementation candidate in `work/projects/devOS/marcopolo/`. The system is moving toward typed POLO (SRC/OPEN/PROP) as the deterministic interface for preprocessing and verification. Human-facing POLO views remain possible, but the pipeline treats MARCO and POLO as typed artifacts and uses trace-first evidence to justify the mapping.

Atlas-specific glue work is tracked in `work/projects/devOS/marcopolo-atlas/`. The goal is to keep `work/projects/devOS/marcopolo/repo/` exportable as a standalone repository while `work/projects/devOS/marcopolo-atlas/repo/` evolves operator CLI wrappers and Atlas path conventions.

Reliability is the non-negotiable constraint. This tooling is plumbing for the Work-OS. It must be very reliable and high quality, because it will sit at the intake boundary where ambiguity and volume are highest, and because the worst failure mode is spammy activation that drowns the operator. Reliability here does not mean binary certainty that two documents "match." Reliability means predictable behavior, explicit uncertainty, conservative defaults, and verifiable outputs. The tool must degrade gracefully on messy input, make its assumptions visible, and never silently promote structure into action.

The core design question is therefore two-way. Given marco and polo, how do we produce graded, explainable evidence that the mapping is acceptable (coverage, novelty risk, provenance/traceability) without claiming total semantic equivalence? And given marco alone, how do we deterministically restructure it into a first-pass polo-style breakdown using surface features and lightweight discipline, while avoiding invention and avoiding automatic activation? In v1, deep long-range semantic linking is explicitly out of scope; the system should instead provide local structure, explicit OPENs, and an operator-controlled direct-throughput channel that routes raw blocks into `drafts/inbox/` for later synthesis.

Because this is system engineering, we set the standards. The success criteria are not aesthetic; they are operational: faster termination with less cognitive load, better re-entry after context switches, less drift under iteration, and minimal spam. If this layer is solid, higher-level synthesis can be layered on later. If this layer is sloppy, everything above it becomes theater.

---

## Inputs

- `drafts/marco.md` (authoritative operator note)
- `drafts/polo.md` (derived breakdown that operator approved)
- Future operator notes (marco-style) captured in Obsidian and exported into this project
- MARCO template: `inbox-airlock/operator-obsidian-render/marcopolo-intake/MARCO_TEMPLATE.md`

---

## Scope

**In:**

- Define what it means for `polo.md` to map well to `marco.md`.
- Define graded verification outputs (confidence plus reasons).
- Define deterministic pre-processing outputs (first-pass polo drafts derived from marco).
- Define evaluation artifacts (trace map, coverage report, novelty report) that make approval faster.
- Define what can be delegated to deterministic tooling (subsidiarity) vs what must remain semantic judgment.
- Define how this workflow fits the "slow communication" principle (durable artifacts + short chat summaries).

**Out:**

- Building the full tooling layer (implementation is later).
- Optimizing OpenCode UI rendering itself.
- Forcing operator writing into a rigid schema; the template must stay natural (see Open).
- Declaring binary "match/no-match" equivalence; verification is graded.
- Producing a new `polo.md` rewrite of the existing pair; the pair is treated as input evidence.

---

## Requirements

### MUST

1. Produce a clear rubric for evaluating `marco.md` -> `polo.md`.
2. Define a traceability model: how to represent links from source items to target sections.
3. Define what constitutes unacceptable drift (invention, omission, silent closure of ambiguity).
4. Define a graded verification output (non-binary confidence plus reasons) suitable for operator review.
5. Define a deterministic pre-processing output that can restructure marco-style notes into a first-pass polo-style breakdown using surface features only.
6. Define a direct-throughput mechanism: operator may tag a target project and have the raw block copied into `work/projects/<project>/drafts/inbox/` as a timestamped markdown file.
7. Define an airlock admission step (operator CLI tooling) that enforces ASCII-only at intake by default, overwriting airlock files in place.
8. Define POLO propagation as the primary deterministic step (v1): parse typed POLO and update exactly one rolling project state file.
9. Specify interpreter behavior when invariants are violated: if the interpreter encounters non-ASCII or malformed formatting in inputs, it must flag this as friction rather than silently proceeding.
10. Capture key forks in the design space as OPEN items (see Open section).

### SHOULD

1. Define a stable vocabulary for the mapping relationship (coverage, fidelity, decomposition quality, routing correctness, OPEN discipline).
2. Define a minimal operator-facing summary format (short, scannable) that references artifacts by file path.
3. Define a lightweight marco template and marco discipline that improve tooling quality without becoming unnatural or burdensome.
4. Define where artifacts would live in the project (`schemas/`, `outputs/`, `logs/`) when implemented.

### MAY

1. Propose a second-order tokenization taxonomy (operator moves) suitable for later automation.
2. Propose quantitative success metrics (time-to-approve reduction, fewer missed items).
3. (v2) Produce a third sibling artifact: a portable problem statement with formal acceptance criteria.

---

## Design Space (Edges)

- Authority boundary: operator approval is the closure event; tools may only surface evidence.
- Delegation boundary: deterministic tooling can parse/index/render/check, but cannot decide semantic equivalence.
- Relationship boundary (v1): deterministic processing is local and surface-based; do not attempt long-range semantic linking across distant tokens.
- Output medium boundary: chat UIs are poor for large structures; durable file artifacts are preferred.
- Balance boundary: marco discipline must improve extraction quality while remaining natural and low-friction for the operator.
- Activation boundary: default behavior must avoid spam; routing proposals are non-binding and do not generate todos without operator promotion.
- Admission boundary (v1): ASCII-only is a hard substrate invariant; it is enforced at the airlock by operator tooling, but interpreters must still detect and flag violations when they appear.
- Propagation boundary (v1): POLO is canonical and typed; propagation is deterministic and updates exactly one rolling state file (PROP inclusion is an explicit flag).
- Portability boundary (v2): produce a third sibling artifact that abstracts the problem into a portable challenge statement with formal acceptance criteria.

---

## Open

| ID | Description | Closure |
|----|-------------|---------|
| OPEN-001 | Should mapping be strictly lossless (every sentence accounted for) or semantically lossless (ideas preserved, some phrasing may drop)? | Operator chooses lossless vs semantic-lossless as the baseline criterion. |
| OPEN-002 | When `polo.md` introduces structure (thread names, routing to projects), is that purely presentational labeling or an interpretive assertion that must be tagged as inference? | Operator chooses labeling-only vs assertion-requiring-inference-tag. |
| OPEN-003 | What counts as "novel" content in `polo.md` (new terms vs new commitments), and how should novelty be surfaced (flag-only vs disallow)? | Operator defines novelty policy and severity levels. |
| OPEN-004 | What is the minimal artifact set to support approval (trace only vs trace+coverage+novelty)? | Operator selects minimum viable evaluation artifacts. |
| OPEN-005 | What is the marco template and marco discipline that improve tooling quality while staying natural (not rigid or bureaucratic)? | Operator defines the minimum structure that remains comfortable to write. |
| OPEN-006 | What should the graded verification look like (one score with sub-scores vs labeled bands), and what evidence should it cite? | Operator chooses the verification presentation contract. |
| OPEN-007 | What should deterministic pre-processing be allowed to do (restructure-only vs limited paraphrase), and what is explicitly forbidden? | Operator defines the safe transform boundary. |
| OPEN-008 | What is the v1 direct-throughput syntax for tagging a target project in a marco note, and what is the filename convention for dropped inbox files? | Operator defines the minimal routing header and naming scheme. |
| OPEN-009 | What is the v1 airlock CLI contract (command name, strict default, permissive flag behavior), and what directory is treated as the canonical airlock? | Canonical intake dir is `inbox-airlock/operator-obsidian-render/marcopolo-intake` for v1. |
| OPEN-010 | What is the v2 portable challenge artifact format and location (file name, sections, acceptance criteria), and how should it stay independent of local system context? | Operator defines the shareable problem statement contract. |

---

## Verification

1. An operator can review the mapping with a trace artifact and determine: coverage, any invented commitments, and OPEN items requiring closure.
2. The spec clearly separates: deterministic checks vs semantic judgment.
3. The workflow description is compatible with "slow communication" (durable artifacts, short summaries).

---

## Lifecycle

| Date | Status | Note |
|------|--------|------|
| 2026-01-13 | active | Define design space, deliverables, and OPEN questions |
