# Executor Spec (Maximum Flexibility)

Purpose: Single-run plan optimized for speed and creative problem-solving. The
executor can adapt steps as needed, but must keep basic observability and a
minimal smoke suite.

Scope: Atlas-TUI repo copy (sandbox). No provider calls. Build to debug.

## Execution Rules (Light)
1. Keep changes small, but do not over-specify structure.
2. Add observability where it unlocks the next decision.
3. Use tests as guidance, not a gate for every micro-change.
4. Prefer pragmatic fixes over refactors.

## Minimal Guarantees
- At least one UI event log and one snapshot per session.
- A smoke suite that covers Esc, F1, F2, submit->log.
- Logs are repo-relative (no absolute paths in outputs).

## One-Run Sequence (Flexible)
### Step A: Basic observability
- Add a lightweight event emitter (can be a helper function).
- Add a basic snapshot function (only top-level fields).
- Log both to disk once per session.

### Step B: Core behaviors
- Ensure submit writes logs and updates latest pointer.
- Ensure Esc/F1/F2 behave as expected (no hard-coded UI pixel tests).

### Step C: Engine + web boundaries
- Ensure engine protocol can be exercised via a deterministic stub.
- Ensure Glass serves latest artifacts for inspection (snapshot + assembled log).

### Step D: Context visibility
- Add a short summary of selected_artifacts in UI and logs.

### Step E: Optional modularization
- If code feels messy, split into modules.
- If not, skip and defer to a later pass.

### Step F: Glass (optional)
- Only if time permits: show latest snapshot + event list.

## Testing Policy (Lean)
- Use `unittest`.
- Add a minimal smoke test file:
  - Esc closes modal or opens confirm.
  - F1 opens help.
  - F2 changes focus.
  - Submit produces a log.

## Stop Conditions (Soft)
- If a test fails twice in a row, fix it before moving on.
- If a behavior is confusing, add an observable rather than guess.
