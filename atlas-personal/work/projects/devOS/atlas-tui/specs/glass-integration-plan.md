# Glass Integration Plan (and delegated assimilation)

Status: draft
Date: 2026-01-14
Owner: devOS/atlas-tui

## Goal

Integrate the structural improvements from the delegated builds into the stable exportable repo at `work/projects/devOS/atlas-tui/repo/`, without importing the delegated code wholesale.

Primary target: optional "glass" (read-only local web inspector) plus UI-owned context prefs and repo-relative path semantics, keeping the current stable Textual cockpit and engine boundary intact.

## Inputs

- Delegated v1: `work/projects/devOS/atlas-tui/delegated/atlas-tui-1/`
  - Adds UI context prefs persisted to a state dir
  - Sends repo-relative `selected_path` and prefs in `ui_state`
- Delegated v2: `work/projects/devOS/atlas-tui/delegated/atlas-tui-2-withHTML/`
  - Adds optional web "glass" server and `latest.json` pointer
  - Enriches dummy engine diagnostics (`selected_artifacts` objects, budgets)
- Stable repo: `work/projects/devOS/atlas-tui/repo/`
  - Stable Textual cockpit + JSONL engine subprocess
  - Packaged Atlas docs under `src/atlas_tui/assets/atlas/`

## Constraints

- No provider API calls and no automated repo writes (v2 posture).
- State writes must remain scoped:
  - Wrapper: `project_root/logs/atlas-tui/state/`
  - No wrapper: `repo_root/.atlas-tui/state/`
- Keep ASCII-only committed artifacts.
- Keep current stable build behavior as the default; additions must be opt-in or non-breaking.

## Phase 0: Input reliability and keybinding contract

Problem: some terminals do not reliably distinguish Ctrl+Enter from Enter.

Deliverables:

- Define a stable "submit" chord that works cross-terminal:
  - Preferred: Ctrl+Enter when available
  - Fallback: Ctrl+S (or another non-conflicting chord) for submit
- Ensure keybindings are consistent across:
  - In-app help overlay
  - `repo/README.md`
  - Any UI copy shown in the composer placeholder

Acceptance:

- Submit is possible in all supported terminals.
- Help text and actual behavior match.

## Phase 1: UI-owned context prefs + state persistence (delegated v1)

Integrate:

- `UIContextPrefs` model and persistence helpers (load/save) similar to:
  - `delegated/atlas-tui-1/atlas_tui/state_store.py`
- UI modal to edit prefs (Ctrl+P / F6):
  - profile: minimal/repo/project/debug
  - budget_chars
  - pinned_paths (repo-relative)
  - excluded_paths (repo-relative)

Changes (stable repo target):

- Add `src/atlas_tui/state_store.py` (or similar) for prefs persistence.
- Add `ContextPrefsScreen` to `src/atlas_tui/ui/widgets.py`.
- Wire bindings in `src/atlas_tui/ui/app.py`:
  - Load prefs on startup
  - Send prefs in `EngineInput.ui_state`
  - Save prefs on modal submit

Acceptance:

- Ctrl+P opens prefs editor.
- Prefs persist to the correct state dir (wrapper vs no wrapper).
- `ui_state` contains repo-relative pinned/excluded paths and budget/profile values.

## Phase 2: Repo-relative path semantics (delegated v1)

Integrate:

- Convert `selected_path` to repo-relative before sending to engine.
- Keep any paths stored in UI prefs repo-relative.

Changes:

- Add a `to_repo_rel(repo_root, abs_path)` helper in `src/atlas_tui/ui/app.py`.
- Ensure the DirectoryTree selection is normalized to repo-relative.

Acceptance:

- `ui_state.selected_path` is repo-relative in inspection logs.
- No absolute paths appear in selection hints or contracts (except repo_root/project_root fields).

## Phase 3: "Latest" pointer file (delegated v2 pre-req for glass)

Integrate:

- Pointer file update on each successful submit:
  - `latest.json` contains `last_log_path`, `request_id`, timestamp
  - Similar to `delegated/atlas-tui-2-withHTML/atlas_tui/state_store.py`

Changes:

- Add `latest_pointer_path(...)` and `write_latest_pointer(...)` to state store module.
- Update `src/atlas_tui/log_writer.py` to write `latest.json` after writing assembled log.

Acceptance:

- After a submit, `latest.json` exists in the state dir and points to the last assembled log.

## Phase 4: Glass server (delegated v2)

Integrate:

- Optional local web server that reads `latest.json` and renders the referenced assembled log.
- Static HTML page with polling of `/api/latest`.

Changes:

- Add `src/atlas_tui/web/server.py` and `src/atlas_tui/web/static/index.html`.
- Add CLI flags:
  - `--glass`, `--glass-host`, `--glass-port`
- When enabled, display the glass URL in the transcript and/or status bar.

Acceptance:

- `atlas-tui --glass` serves `http://127.0.0.1:<port>/`.
- The page updates on each submit and shows key fields (mode/provider/model, system preview, selected artifacts, raw JSON).

## Phase 5: Diagnostics compatibility and incremental enrichment

Current stable dummy engine returns `diagnostics.selected_artifacts` as strings; delegated engines return structured objects.

Integrate:

- Make `InspectionPanel` tolerant of both shapes.
- Optionally add a second dummy engine module that implements delegated selection-policy behavior (repo-relative hints, budgets, artifact objects) while keeping the current bundled-Atlas dummy engine as default.

Acceptance:

- Inspection panel renders without exceptions for either diagnostics shape.
- Selection delta can be computed when structured artifacts are present.

## Verification checklist

- Launch from:
  - inside a wrapper (`work/projects/devOS/atlas-tui/`)
  - inside a non-wrapper git repo
- Submit works with at least one guaranteed chord in each terminal.
- Logs write to:
  - wrapper: `<project_root>/logs/atlas-tui/assembled/`
  - no wrapper: `<repo_root>/.atlas-tui/logs/assembled/`
- State writes to:
  - wrapper: `<project_root>/logs/atlas-tui/state/`
  - no wrapper: `<repo_root>/.atlas-tui/state/`
- `latest.json` updates on submit (Phase 3+).
- Glass server remains read-only and binds to loopback by default.

