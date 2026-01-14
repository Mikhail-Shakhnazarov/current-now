# INTERPRETATION_PIPELINE.md

System document for devOS interpreter. Load before design work.

Purpose: Transform a project vision into executable build loops. The interpreter
pre-interprets everything the executor would need to interpret, then encodes it
as a verification-gated loop graph.

Input: Vision (vague or detailed idea for something to build).
Output: Loop graph (feedback loops the executor can run without interpretation).

---

## Pipeline overview

```
VISION → GOAL SPEC → PROOF TABLE → LOOP GRAPH → [executor runs]
         ────────────────────────────────────
              interpreter's territory
```

The interpreter does not write "how to build." The interpreter writes "what done
looks like" and "what would prove each part works." The build process falls out
of the proof structure.

---

## Stage 0: Triage

Before starting the pipeline, assess fit.

Questions:

- Does this project produce artifacts (files, schemas, observable state)?
- Can "done" be described as a concrete repo shape?
- Are intermediate states meaningful (can verify incrementally)?
- Can I pre-interpret enough, or will the executor drown in friction?

If yes to all: proceed.

If no: this project may need a different approach (exploratory, conversational,
human-driven). Flag this to operator and stop.

Output: GO / NO-GO decision with rationale.

---

## Stage 1: Decompile vision → goal spec

Take the vision and crystallize it into a concrete end-state description.

The goal spec answers: *what does the repo look like when it's done?*

### 1.1 Extract core intent

Ask:

- What is this thing? (one sentence)
- What does it do? (observable behaviors, not internals)
- Who/what consumes it? (human, another system, both)
- What's the simplest form that would be "done"?

Compress the vision into a tight statement of intent. If the vision is vague,
propose a concrete interpretation and mark assumptions explicitly.

### 1.2 Describe the printed repo

Specify the final file structure:

- Directory layout
- Key files and their roles
- What's generated vs. static

This is not architecture—it's inventory. What would `tree` show?

### 1.3 Define artifact contracts

For each artifact that must exist:

- Path (fixed or pattern)
- Schema (fields, types, constraints)
- Stability guarantee (immutable, versioned, ephemeral)

Artifact contracts are the verification surface. If it can't be checked against
a contract, it can't be verified.

### 1.4 List observable behaviors

Behaviors are not features. Behaviors are: *if I do X, I can observe Y.*

Format:

```
BEHAVIOR: [name]
  TRIGGER: [what causes it]
  OBSERVABLE: [what artifact/state changes]
  CONSTRAINT: [invariants that must hold]
```

### 1.5 Compile proof table

The proof table is the skeleton. Every behavior must have a verification path.

Format:

| Behavior | Observable | Check | Failure mode |
|----------|------------|-------|--------------|
| ...      | ...        | ...   | ...          |

Each row is a claim that can be proven or disproven by examining artifacts.

### Stage 1 output: Goal spec document

Contains:

- Intent statement
- Repo structure (printed shape)
- Artifact contracts (schemas, paths)
- Behavior list
- Proof table

This is the target. Everything else derives from it.

---

## Stage 2: Reverse-engineer goal spec → loop graph

Work backward from the goal spec. Ask: *what must exist before each proof can run?*

### 2.1 Derive bindings from proof table

Each proof table row becomes a binding. A binding is an atomic unit of provable
progress.

Format:

```
BINDING: [id]
  INVARIANT: [what should be true]
  OBSERVABLE: [what artifact proves it]
  CHECK: [how to verify the artifact]
  FRICTION_IF: [conditions that block this binding]
```

Bindings are closed loops. The executor works on one binding at a time. Progress
equals bindings proven.

### 2.2 Trace binding dependencies

For each binding, ask:

- What artifacts must exist before this binding can be attempted?
- What other bindings produce those artifacts?

Build the dependency graph. This determines ordering.

Format:

```
BINDING: [id]
  DEPENDS: [list of binding ids that must be proven first]
```

### 2.3 Identify verification primitives

Some bindings require infrastructure to verify (test harness, logging, schemas).
These are "primitives"—bindings that exist to enable verification of other
bindings.

Primitives come first. They are the foundation of the loop graph.

Common primitives:

- Determinism seams (fixed clocks, IDs for reproducibility)
- Schema definitions (so artifacts can be validated)
- Logging infrastructure (so observables are captured)
- Test harness (so checks can run)

### 2.4 Structure as feedback loops

Convert bindings into executable loops.

Format:

```
LOOP: [binding id]
  TARGET: [artifact/state that should exist after loop completes]
  DEPENDS: [loops that must complete first]
  BUILD: [what the executor does—concrete actions]
  VERIFY: [command or check that proves target exists and is correct]
  ON_PASS: [next loops unlocked]
  ON_FAIL: [fix and retry, or emit friction with context]
```

Each loop is self-contained. The executor can run it without interpreting.

### 2.5 Sequence into tiers

Group loops by dependency depth:

- Tier 0: primitives (no dependencies)
- Tier 1: loops that depend only on Tier 0
- Tier 2: loops that depend on Tier 0–1
- ...

Within a tier, loops can run in any order (or parallel, if executor supports).
Across tiers, ordering is strict.

### Stage 2 output: Loop graph document

Contains:

- Binding list (derived from proof table)
- Dependency graph (which bindings require which)
- Loop definitions (build → verify → gate)
- Tier sequence (execution order)

---

## Stage 3: Anticipate friction

The executor will get stuck. The interpreter's job is to minimize unnecessary
friction by pre-resolving decisions.

### 3.1 Identify interpretation points

Scan each loop's BUILD section. Ask:

- Where would the executor need to make a judgment call?
- Where is there ambiguity about what "correct" means?
- Where might the executor invent rather than apply?

### 3.2 Pre-resolve or mark

For each interpretation point:

- If the interpreter can decide now: make the decision, encode it in the loop.
- If the decision requires operator input: mark as expected friction.

Format for pre-resolved:

```
DECISION: [id]
  CONTEXT: [what the ambiguity was]
  RESOLUTION: [what the interpreter decided]
  RATIONALE: [why]
```

Format for expected friction:

```
FRICTION_POINT: [id]
  LOOP: [which loop]
  CONTEXT: [what the executor will encounter]
  SIGNAL: [what the friction message should say]
  RESOLUTION_HINT: [what the operator should consider]
```

### 3.3 Compile friction map

List all pre-resolved decisions and expected friction points. This is the
operator's guide to what might need intervention.

### Stage 3 output: Friction map document

Contains:

- Pre-resolved decisions (with rationale)
- Expected friction points (with resolution hints)

---

## Stage 4: Package projection set

Assemble the outputs into a coherent package for handoff.

### Projection set contents

1. **Goal spec** (Stage 1 output)
   - Intent statement
   - Repo structure
   - Artifact contracts
   - Behavior list
   - Proof table

2. **Loop graph** (Stage 2 output)
   - Binding list
   - Dependency graph
   - Loop definitions
   - Tier sequence

3. **Friction map** (Stage 3 output)
   - Pre-resolved decisions
   - Expected friction points

4. **Execution contract** (metadata)
   - Stop conditions (what halts the executor)
   - Strictness settings (must all checks pass? can some be soft?)
   - Artifact paths (where outputs go)

### Validation checklist

Before handoff, verify:

- [ ] Every behavior in goal spec has a proof table row
- [ ] Every proof table row has a binding
- [ ] Every binding has a loop definition
- [ ] Every loop has a concrete VERIFY step
- [ ] Dependency graph has no cycles
- [ ] Tier 0 contains all primitives (no external dependencies)
- [ ] All interpretation points are either pre-resolved or marked as friction

If any check fails: fix before handoff.

---

## Execution contract (default)

The executor consumes the loop graph under these rules:

```
EXECUTION_CONTRACT:
  STOP_ON: any VERIFY failure after retry
  RETRY_LIMIT: 2 per loop
  FRICTION_EMIT: on interpretation required, on repeated failure, on missing dependency
  ARTIFACT_ROOT: [repo root]/logs/[project]/
  STRICT_ORDER: across tiers yes, within tier no
```

Operator may override these defaults in the projection set.

---

## Pipeline summary

```
┌─────────────────────────────────────────────────────────────────────┐
│ STAGE 0: TRIAGE                                                     │
│   Is this project suitable for verification-gated build?            │
│   Output: GO / NO-GO                                                │
└─────────────────────────────┬───────────────────────────────────────┘
                              │ if GO
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│ STAGE 1: DECOMPILE VISION → GOAL SPEC                               │
│   1.1 Extract core intent                                           │
│   1.2 Describe printed repo                                         │
│   1.3 Define artifact contracts                                     │
│   1.4 List observable behaviors                                     │
│   1.5 Compile proof table                                           │
│   Output: Goal spec document                                        │
└─────────────────────────────┬───────────────────────────────────────┘
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│ STAGE 2: REVERSE-ENGINEER → LOOP GRAPH                              │
│   2.1 Derive bindings from proof table                              │
│   2.2 Trace binding dependencies                                    │
│   2.3 Identify verification primitives                              │
│   2.4 Structure as feedback loops                                   │
│   2.5 Sequence into tiers                                           │
│   Output: Loop graph document                                       │
└─────────────────────────────┬───────────────────────────────────────┘
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│ STAGE 3: ANTICIPATE FRICTION                                        │
│   3.1 Identify interpretation points                                │
│   3.2 Pre-resolve or mark                                           │
│   3.3 Compile friction map                                          │
│   Output: Friction map document                                     │
└─────────────────────────────┬───────────────────────────────────────┘
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│ STAGE 4: PACKAGE PROJECTION SET                                     │
│   Assemble: goal spec + loop graph + friction map + exec contract   │
│   Validate: all behaviors traced to loops, no cycles, primitives    │
│   Output: Projection set (ready for executor handoff)               │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Usage

Load this document before starting design work on a build project.

When operator brings a vision:

1. Run Stage 0 triage.
2. If GO, proceed through Stages 1–4.
3. Present projection set for operator review.
4. On approval, projection set becomes the executor's input.

The interpreter does not hand off until the validation checklist passes.
