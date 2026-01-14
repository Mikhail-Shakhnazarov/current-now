# Atlas-TUI End-Result Spec (Printed Repo)

Purpose: Describe the target repo shape and behavior for the final Atlas-TUI
build. This is a normal product spec (not the executor loop).

Scope: TUI + dummy engine + inspection logs + Glass. No provider calls.

## Product Goals
- Reliable TUI cockpit for repo context assembly inspection.
- Deterministic logs and UI observability for debugging.
- Minimal dependencies and predictable behavior across terminals.

## Non-Goals
- No live provider API calls.
- No auto-modifying the repo.
- No multi-project switching.

## Repo Structure (Target)
- src/atlas_tui/
  - ui/ (screens, widgets, focus policy)
  - engine/ (client, protocol, dummy engine)
  - logging/ (assembled logs, chat logs, latest pointer)
  - state/ (prefs, snapshot persistence)
  - web/ (glass server, static assets)
  - assets/ (atlas docs, test fixtures)
- specs/
  - binding-schema-template.md
  - end-result-spec.md
  - executor-spec.md
- tests/ (unittest smoke suite)
- README.md, LICENSE, NOTICE.txt, pyproject.toml

## Core Behaviors
### UI
- Three panels: repo (left), chat (center), project/inspection (right).
- Top bar: Help, Refresh, Chat Log, Details, Prefs, Restart, Quit.
- Focus policy: default to composer; F2 cycles repo -> chat -> project.
- Key bindings:
  - Enter: submit
  - Shift+Enter: newline
  - F1: Help
  - F2: Focus cycle
  - Esc: close modal; if none, open quit confirm
  - Ctrl+C: force quit (no confirmation)
- Repo tree updates selected_path label (repo-relative).
- Project panel shows now.md preview + recent specs/logs (if wrapper exists).
- Inspection panel shows last assembly summary.

### Engine
- Dummy engine assembles system prompt from bundled Atlas assets.
- Engine protocol: JSONL stdin/stdout with submit/result.
- No external calls.

### Logging
- Assembled logs written on each submit.
- Latest pointer updated after each submit.
- Chat log optional, toggled in UI.
- UI event stream and snapshot logs (for observability).

### Glass
- Optional local web inspector.
- Serves latest log, selected artifacts, and UI snapshot.

## Observability Contract
### UI Events (JSON)
- focus_changed(panel, widget_id)
- key_handled(key, action, screen_stack_depth, result)
- submit_started(request_id, mode, provider, model)
- submit_done(request_id, ok, system_chars)
- log_written(path, bytes)
- glass_pointer_updated(path)

### Snapshot (JSON)
- focused_panel, focused_widget_id
- screen_stack (list of screen type names)
- selected_path (repo-relative)
- mode/provider/model
- last_request_id, last_log_path
- prefs (context profile, budget, pins, excludes)

## Testing
- Use `unittest` only.
- Smoke tests cover:
  - Esc/F1/F2 behavior
  - submit -> log + latest pointer
  - snapshot fields present
  - engine protocol roundtrip (stubbed)
- Tests assert logs/events/snapshots, not UI pixels.

## Acceptance Criteria
- TUI launches without traceback in stable terminals.
- All smoke tests pass in <10s.
- Logs and snapshots are deterministic and repo-relative.
- Glass renders latest assembled log and UI snapshot.
