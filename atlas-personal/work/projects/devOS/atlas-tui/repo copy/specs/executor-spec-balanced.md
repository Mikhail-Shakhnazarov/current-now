# Executor Spec (Balanced)

Purpose: Single-run, loop-based plan that balances determinism with flexibility.
The executor should finish in one pass, but can reorder minor tasks if checks
remain satisfied.

Scope: Atlas-TUI repo copy (sandbox). No provider calls. Build to debug.

## Execution Rules
1. Observability before behavior, always.
2. Each step ends with a test or a verification checklist.
3. If a check fails, fix before continuing.
4. Avoid large refactors; prefer small, staged moves.

## Required Artifacts
- UI events log (JSONL)
- UI snapshot (JSON)
- Assembled log + latest pointer
- Smoke test suite (unittest)

## One-Run Loop
Each step follows: add observable -> implement -> test -> record.

## Ordered Steps (Recommended)
### Step 1: Event + snapshot schemas
- Define event and snapshot shapes (with version field).
- Add helper functions for serialize/write.
Check:
- Unit tests assert schema fields and JSON parse.

### Step 2: Submit loop observability
- Emit submit_started/submit_done.
- Emit log_written/glass_pointer_updated.
Check:
- Smoke test submit writes log and latest pointer.

### Step 3: Key handling + focus
- Emit key_handled with result.
- Enforce focus cycle.
Check:
- Smoke tests for Esc/F1/F2 and focus order via snapshot.

### Step 4: Context visibility
- Show selected_artifacts + pins/excludes.
- Persist in logs.
Check:
- Assembled log includes selection summary.

### Step 5: Engine + web boundaries
- Prove engine protocol roundtrip via deterministic stub.
- Prove Glass endpoints return valid JSON for latest artifacts.
Check:
- Smoke tests cover engine roundtrip and core web endpoints.

### Step 6: Modularization (light)
- Split into ui/, engine/, logging/, state/, web/, assets/ if safe.
Check:
- Tests pass; no circular imports.

### Step 7: Glass UI view (nice-to-have)
- Render latest snapshot + event list.
Check:
- Manual verification.

## Proof Table (Compact)
Behavior -> Observable -> Check
- Esc modal close -> key_handled(pop) + screen_stack-- -> smoke test
- Esc opens confirm -> key_handled(quit_confirm) -> smoke test
- F1 help -> key_handled(help_toggle) -> smoke test
- F2 focus -> snapshot.focused_panel -> smoke test
- Submit -> submit_started/done -> smoke test
- Log update -> log_written/latest.json -> smoke test

## Testing Policy
- `unittest` only.
- Total runtime <10s.
- Tests assert artifacts, not UI pixels.

## Stop Conditions
- Any failing check blocks next step.
- Missing observable blocks feature work.
