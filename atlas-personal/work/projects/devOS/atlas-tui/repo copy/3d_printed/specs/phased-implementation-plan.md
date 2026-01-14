# Phased Implementation Plan (3d_printed)

Root: `work/projects/devOS/atlas-tui/repo copy/3d_printed`

Sources of truth:
- `work/projects/devOS/atlas-tui/repo copy/specs/executor-spec-deterministic.md`
- `work/projects/devOS/atlas-tui/repo copy/specs/end-result-spec.md`

Intent:
- Build a solid Textual TUI + local web inspector + dummy engine.
- Make correctness provable via deterministic artifacts and fast `unittest` smoke checks.
- No provider calls. No network beyond optional local `127.0.0.1` for Glass tests.

Non-goals:
- Pixel-perfect UI assertions.

## Fixed Artifact Contract (Required)

All paths are relative to the `3d_printed/` root.

- UI events log: `logs/atlas-tui/ui/events.jsonl`
- UI snapshot: `logs/atlas-tui/ui/latest_snapshot.json`
- Assembled log: `logs/atlas-tui/assembled/<request_id>.json`
- Latest pointer: `logs/atlas-tui/state/latest.json`

Constraints:
- Artifacts must be parseable JSON/JSONL and stable-schema v1.
- Tests assert artifacts, not terminal rendering.
- Paths stored inside JSON must be repo-relative when representing repo files.

## Schema v1 (Pinned)

### UI event record v1
Shape:
- `schema_version`: `1`
- `type`: string enum:
  - `focus_changed`
  - `key_handled`
  - `submit_started`
  - `submit_done`
  - `log_written`
  - `glass_pointer_updated`
- `ts`: ISO-8601 string (local time with offset is acceptable)
- `session_id`: stable per app run
- `payload`: object (event-specific)

Payload minimums:
- `focus_changed`: `{ "panel": <string>, "widget_id": <string|null> }`
- `key_handled`: `{ "key": <string>, "action": <string>, "screen_stack_depth": <int>, "result": <string> }`
- `submit_started`: `{ "request_id": <string>, "mode": <string>, "provider": <string>, "model": <string> }`
- `submit_done`: `{ "request_id": <string>, "ok": <bool>, "system_chars": <int> }`
- `log_written`: `{ "path": <string>, "bytes": <int> }`
- `glass_pointer_updated`: `{ "path": <string> }`

### UI snapshot record v1
Shape:
- `schema_version`: `1`
- `ts`: ISO-8601 string
- `session_id`: stable per app run
- `focused_panel`: enum string: `repo|chat|project`
- `focused_widget_id`: string|null
- `screen_stack`: list of screen type names (strings)
- `selected_path`: repo-relative string|null
- `mode`: string
- `provider`: string
- `model`: string
- `last_request_id`: string|null
- `last_log_path`: string|null
- `prefs`: object:
  - `context_profile`: string
  - `budget_chars`: int
  - `pinned_paths`: list[string]
  - `excluded_paths`: list[string]

## Phases (Strict Order)

Each phase follows: observability -> behavior -> tests -> record results.
Stop condition: any failing test blocks the next phase.

### Phase 0 - Bootstrap the `3d_printed` project root

Goal: a standalone, runnable project skeleton with tests discovered by `unittest`.

Deliverables:
- `pyproject.toml` (match baseline deps: `textual`, `rich`; no new deps)
- `src/atlas_tui/__init__.py`
- `src/atlas_tui/cli.py` (entry: run TUI; optional flags for repo/project roots)
- `tests/` package with a trivial sanity test to prove discovery
- `specs/` containing copies or references:
  - `end-result-spec.md`
  - `executor-spec-deterministic.md`
  - `phased-implementation-plan.md` (this file)

Checks:
- `python -m unittest discover -s tests -v` passes

Notes:
- Run and test commands assume CWD is `3d_printed/` to avoid import collisions with the parent project.

### Phase 1 - Determinism primitives (IDs, time, paths)

Goal: stable seams for tests; production defaults remain convenient.

Deliverables:
- `src/atlas_tui/determinism.py`:
  - `Clock` interface (`now_iso()`), default real clock
  - `IdProvider` interface (`new_session_id()`, `new_request_id()`), default UUID-based
  - `PathPolicy` helpers (repo-relative normalization)

Checks:
- Unit tests that inject fixed clock + ids and assert stable outputs

### Phase 2 - UI events and snapshot objects (schema v1)

Goal: in-memory objects that always serialize to schema v1.

Deliverables:
- `src/atlas_tui/ui_events.py`:
  - dataclasses for each event type + `to_dict()` with `schema_version=1`
- `src/atlas_tui/ui_snapshot.py`:
  - snapshot dataclass + `capture_snapshot(app)` + `to_dict()` with `schema_version=1`

Checks:
- Unit tests: each event serializes to JSON; snapshot includes all required keys and `schema_version=1`

### Phase 3 - UI event logging + snapshot logging (fixed paths)

Goal: stable on-disk artifacts for tests to assert.

Deliverables:
- `src/atlas_tui/ui_observability.py` (or similar):
  - `append_ui_event(workspace, event)` -> appends JSONL to `logs/atlas-tui/ui/events.jsonl`
  - `write_latest_snapshot(workspace, snapshot)` -> writes JSON to `logs/atlas-tui/ui/latest_snapshot.json`
- Ensure directories are created as needed.

Checks:
- Unit tests:
  - append event then read back and parse JSON
  - write snapshot then read back and validate required keys

### Phase 4 - Submit loop signals + assembled log + latest pointer

Goal: the smallest end-to-end loop is visible and testable.

Deliverables:
- `src/atlas_tui/state_store.py`:
  - `write_latest_pointer(..., log_path, request_id)` writes `logs/atlas-tui/state/latest.json`
- `src/atlas_tui/log_writer.py`:
  - `write_assembled_log(..., request_id, engine_input, engine_output)` writes exactly:
    - `logs/atlas-tui/assembled/<request_id>.json`
  - emits `log_written` and `glass_pointer_updated` UI events via the observability layer
- Submit events:
  - `submit_started` before calling engine
  - `submit_done` after engine result (with `ok` and `system_chars`)

Checks (smoke-level):
- A headless test that runs the log writer on fixed inputs and asserts:
  - assembled log exists at the required path
  - latest pointer updated
  - UI events appended containing `log_written` and `glass_pointer_updated`

### Phase 5 - Engine protocol roundtrip (deterministic stub)

Goal: engine boundary is real (JSONL) and testable without network.

Deliverables:
- `src/atlas_tui/models.py`:
  - `EngineInput` and `EngineOutput` with `to_dict()` / `from_dict()`
- `src/atlas_tui/engine_client.py`:
  - subprocess JSONL client (`submit` request, `result` response)
- `src/atlas_tui/dummy_engine.py`:
  - JSONL stdin/stdout server returning deterministic `EngineOutput` from `EngineInput`
  - emits stable `selected_artifacts` for context visibility tests

Checks:
- Smoke test: spawn dummy engine, submit fixed input, assert stable JSON output and `selected_artifacts` shape

### Phase 6 - TUI skeleton (3 panels) + key handling + focus policy

Goal: UI exists only to drive artifacts; tests assert artifacts and state transitions.

Deliverables:
- `src/atlas_tui/ui/app.py` (Textual `App`):
  - panels: repo, chat, project/inspection
  - key bindings: `Enter`, `Shift+Enter`, `F1`, `F2`, `Esc`, `Ctrl+C`
  - focus policy: default composer; `F2` cycles `repo -> chat -> project`
  - submit action:
    - emits submit events
    - calls engine client
    - writes assembled log + latest pointer
    - writes latest snapshot after each meaningful action
    - appends UI events for each meaningful action

Checks (smoke-level, `textual` test harness):
- Esc:
  - closes top modal if any; otherwise opens quit confirm
  - asserts `key_handled` event + snapshot.screen_stack change
- F1:
  - toggles help overlay
  - asserts `key_handled` event + snapshot.screen_stack change
- F2:
  - cycles focus
  - asserts `focused_panel` changes in `latest_snapshot.json`
- Submit:
  - asserts submit events order in `events.jsonl`
  - asserts assembled log + latest pointer updated

### Phase 7 - Context visibility (UI + logs)

Goal: selection summary is visible and persisted.

Deliverables:
- UI summary in project/inspection panel:
  - selected_artifacts count
  - pins/excludes (from prefs) summary
- Assembled log includes:
  - `selected_artifacts`
  - `ui_state` (snapshot-compatible subset)

Checks:
- Smoke test: after submit, assembled log contains selection summary and `ui_state`

### Phase 8 - Glass endpoints (deterministic)

Goal: local inspection surface returns stable JSON from artifacts.

Deliverables:
- `src/atlas_tui/web/server.py`:
  - `/api/latest` -> latest assembled log + pointer meta
  - `/api/ui/latest_snapshot` -> latest snapshot JSON
  - `/api/ui/events_tail?n=<int>` -> last N JSONL events (parsed)
- Static page is optional for the first pass; endpoints are required.

Checks (smoke-level):
- Start server on port `0` (ephemeral), GET each endpoint, parse JSON, assert required keys
- Server stops cleanly in test teardown

### Phase 9 - Modularization split + public contracts

Goal: align to the end-result module layout without breaking tests.

Deliverables:
- Move code into:
  - `src/atlas_tui/ui/`
  - `src/atlas_tui/engine/`
  - `src/atlas_tui/logging/`
  - `src/atlas_tui/state/`
  - `src/atlas_tui/web/`
  - `src/atlas_tui/assets/`
- Re-export stable public APIs from package roots to keep imports simple.

Checks:
- All tests still pass
- No circular imports (verify with `rg` and module graph sanity)

### Phase 10 - Glass UI view (manual)

Goal: render latest snapshot and event list for human inspection.

Deliverables:
- `src/atlas_tui/web/static/index.html` (simple page)
  - fetches `/api/latest` and `/api/ui/latest_snapshot`
  - displays events tail

Checks:
- Manual: run server, open `/`, confirm page loads and shows latest artifacts

## Proof Table (Executable Targets)

Behavior -> Observable -> Check
- Esc closes modal -> `key_handled(result=pop)` + snapshot `screen_stack` -> smoke test reads artifacts
- Esc opens quit confirm -> `key_handled(result=quit_confirm)` -> smoke test reads artifacts
- F1 help -> `key_handled(result=help_toggle)` -> smoke test reads artifacts
- F2 focus -> snapshot `focused_panel` -> smoke test reads `latest_snapshot.json`
- Submit -> `submit_started` then `submit_done` -> smoke test reads `events.jsonl`
- Log -> assembled log + `state/latest.json` -> smoke test reads filesystem

## Acceptance Criteria (End Spec)

- TUI launches without traceback in stable terminals.
- Smoke suite passes in <10s.
- Logs and snapshots are deterministic and repo-relative.
- Glass returns latest assembled log and latest UI snapshot via stable endpoints.
