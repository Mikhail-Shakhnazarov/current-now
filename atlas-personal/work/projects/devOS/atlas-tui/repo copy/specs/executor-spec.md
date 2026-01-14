# Executor Spec (Printed Repo Build)

Purpose: Provide a single-run, loop-based implementation plan for a small model
executor. This spec emphasizes observability, explicit checks, and zero
assumptions about feature correctness. The executor should complete all steps
in one pass, using a tight build-verify loop (no separate phases required).

Scope: Atlas-TUI repo copy (sandbox). No provider calls. Build to debug.

## Execution Rules
1. Never assume a feature works; verify via checks.
2. Add observability before behavior.
3. Each phase ends with tests and a short status summary.
4. Prefer small, reversible changes.
5. If a check fails, stop and fix before proceeding.

## Single-Run Build Loop (Doable in One Run)
Goal: Build and verify continuously in one pass.

### Loop contract
Each unit of work must include:
1. Add observability (event/snapshot/log).
2. Add or update behavior.
3. Add or update checks.
4. Run tests and record results.

If any check fails, fix and repeat the same unit before continuing.

## One-Run Sequence (ordered tasks)
The executor should follow this order, but keep the loop contract per step.

### Step 1: Contracts + observability
Define UI event types and schema (JSON):
- focus_changed(panel, widget_id)
- key_handled(key, action, screen_stack_depth, result)
- submit_started(request_id, mode, provider, model)
- submit_done(request_id, ok, system_chars)
- log_written(path, bytes)
- glass_pointer_updated(path)

Deliverable:
- `ui_events.py` (or module) with dataclasses and `to_dict()`.

Check:
- Unit test asserts each event serializes to valid JSON.

### Step 2: Debug snapshot
Define a single snapshot schema (JSON):
- focused_panel, focused_widget_id
- screen_stack (list of screen type names)
- selected_path (repo-relative)
- mode/provider/model
- last_request_id, last_log_path
- prefs (context profile, budget, pins, excludes)

Deliverable:
- `ui_snapshot.py` with `capture_snapshot(app)` and `to_json()`.

Check:
- Unit test creates a fake app and validates all fields exist.

### Step 3: Binding schema template
Create a template file to map invariants -> observables -> checks:
- `specs/binding-schema-template.md`

Check:
- Manual review: template includes examples for key handling and logging.

### Step 4: Submit loop events
Add events when submit starts and completes.

Check:
- Smoke test presses Enter (or calls action_submit) and verifies events.

### Step 5: Log + latest pointer
Ensure log writing always emits log_written and glass_pointer_updated.

Check:
- Smoke test asserts log file exists and latest pointer updated.

### Step 6: Key handling events
Emit key_handled with result:
- result=pop (modal closed)
- result=quit_confirm (opened)
- result=help_toggle (help opened/closed)

Check:
- Smoke tests for Esc/F1/F2 assert key_handled events + snapshot changes.

### Step 7: Focus policy
Define focus order and invariants:
- Default focus: composer
- F2 cycles repo -> chat -> project

Check:
- UI smoke test validates focus order via snapshot.

### Step 8: Context visibility
Add UI summary panel for selected_artifacts and exclusions.

Check:
- Submit -> verify summary includes selected_artifacts count.

### Step 9: Log integration
Persist selection summary in assembled logs.

Check:
- Log JSON includes selected_artifacts and ui_state.

### Step 10: Engine protocol roundtrip
Prove the engine boundary is deterministic and testable.

Deliverable:
- Engine protocol dataclasses and a stub/dummy implementation.

Check:
- Unit test runs a protocol roundtrip (no network calls) and asserts stable output.

### Step 11: Web contract (Glass core endpoints)
Make the web inspection surface testable.

Deliverable:
- Stable endpoints that serve latest assembled log and latest UI snapshot.

Check:
- Smoke test starts the server and asserts core endpoints return valid JSON.

### Step 12: Modularization split
Create packages:
- ui/
- engine/
- logging/
- state/
- web/
- assets/

Check:
- Imports updated; tests pass.

### Step 13: Public contracts
Ensure each module exports a small API:
- ui: event emission + snapshot capture
- engine: EngineClient + protocol dataclasses
- logging: write_assembled_log + write_latest_pointer
- state: prefs + snapshot persistence

Check:
- `rg` for cross-module imports; ensure no circular dependencies.

### Step 14: UI event log
Write UI event stream to a log file in `logs/atlas-tui/ui/`.

Check:
- Log file rotates per session; events appended per action.

### Step 15: Glass viewer
Add a Glass tab for UI events and snapshot.

Check:
- Glass renders latest UI snapshot and event list.

## Testing Policy
- Use `unittest` (no new dependencies).
- Keep tests fast (<10s total).
- Tests must assert artifacts (events, logs, snapshots), not UI pixels.

## Stop Conditions (always-on)
- Any failing test stops the process.
- Any missing observable blocks feature development.
- Any new feature requires a binding schema update.
