# Executor Spec (Ultra-Deterministic)

Purpose: Single-run, zero-ambiguity plan for a small executor model. Every
behavior must be proven by a specific artifact with a stable schema. The goal
is determinism over speed.

Scope: Atlas-TUI repo copy (sandbox). No provider calls. Build to debug.

## Execution Rules (Strict)
1. No feature without an observable and a test.
2. No ambiguous checks; each check must assert a concrete artifact.
3. JSON schemas must be versioned and immutable per run.
4. Stop immediately on any failing test.
5. Do not refactor unless a step explicitly calls for it.

## Required Artifacts (Fixed)
- UI events log: `logs/atlas-tui/ui/events.jsonl`
- UI snapshot: `logs/atlas-tui/ui/latest_snapshot.json`
- Assembled log: `logs/atlas-tui/assembled/<request_id>.json`
- Latest pointer: `logs/atlas-tui/state/latest.json`

## Schemas (Versioned)
- UI event schema v1
  - type, ts, session_id, payload
- UI snapshot schema v1
  - focused_panel, focused_widget_id, screen_stack, selected_path
  - mode, provider, model
  - last_request_id, last_log_path
  - prefs {context_profile, budget_chars, pinned_paths, excluded_paths}
- Assembled log schema v1 (existing shape, pinned in spec)

## One-Run Sequence (Strict order)
Each step must include: observability -> behavior -> test -> record result.

### Step 1: Event system
Deliverable:
- `ui_events.py` with dataclasses + `to_dict()`
Check:
- Unit test: each event serializes to JSON and includes schema_version=1.

### Step 2: Snapshot system
Deliverable:
- `ui_snapshot.py` with `capture_snapshot(app)` + `to_json()`
Check:
- Unit test: snapshot includes all fields and schema_version=1.

### Step 3: Event logging
Deliverable:
- Append events to `logs/atlas-tui/ui/events.jsonl`
Check:
- Unit test: write event, read back, parse JSON.

### Step 4: Snapshot logging
Deliverable:
- Write latest snapshot to `logs/atlas-tui/ui/latest_snapshot.json`
Check:
- Unit test: file exists; JSON parses; required keys present.

### Step 5: Submit loop signals
Deliverable:
- Emit submit_started/submit_done
Check:
- Smoke test: action_submit emits both events in order.

### Step 6: Log pointer signals
Deliverable:
- Emit log_written + glass_pointer_updated
Check:
- Smoke test: assembled log exists and latest.json updated.

### Step 7: Key handling signals
Deliverable:
- Emit key_handled on Esc/F1/F2 with result
Check:
- Smoke test: each key yields expected result and snapshot change.

### Step 8: Focus policy
Deliverable:
- Enforce focus order via F2
Check:
- Smoke test: snapshot.focused_panel cycles repo->chat->project.

### Step 9: Context visibility
Deliverable:
- UI summary panel shows selected_artifacts + pins/excludes
Check:
- Smoke test: after submit, summary shows selected count.

### Step 10: Engine protocol roundtrip
Deliverable:
- Engine protocol dataclasses and deterministic stub implementation.
Check:
- Smoke test: protocol roundtrip produces stable JSON output.

### Step 11: Glass endpoints (deterministic)
Deliverable:
- Stable endpoints serving latest assembled log and latest UI snapshot.
Check:
- Smoke test: start server, GET endpoints, parse JSON, assert required keys.

### Step 12: Modularization split
Deliverable:
- ui/ engine/ logging/ state/ web/ assets/ packages
Check:
- Imports updated; all tests pass.

### Step 13: Glass UI view
Deliverable:
- Glass shows latest UI snapshot + event list
Check:
- Manual verification: page renders without errors.

## Proof Table (Non-Negotiable)
Behavior -> Observable -> Check -> Failure mode
- Esc closes modal -> key_handled(pop) + screen_stack-- -> smoke test -> modal not dismissed
- Esc opens quit confirm -> key_handled(quit_confirm) -> smoke test -> binding shadowed
- F1 help -> key_handled(help_toggle) -> smoke test -> overlay not mounted
- F2 focus -> snapshot.focused_panel -> smoke test -> focus trap
- Submit -> submit_started/done -> smoke test -> engine path broken
- Log -> log_written/latest.json -> smoke test -> log path mismatch

## Stop Conditions (Always On)
- Missing observable = block progress.
- Failing test = fix before continue.
- Schema drift without version bump = failure.
