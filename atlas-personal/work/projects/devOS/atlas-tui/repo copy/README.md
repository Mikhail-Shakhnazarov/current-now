# atlas-tui

Atlas TUI is a chat-first terminal cockpit for working inside a single repository, while delegating prompt construction to an Atlas-style context assembly engine.

In v2, `atlas-tui` is UI-first. The app launches a Textual cockpit and starts an engine subprocess. The engine assembles the concrete provider request payload (including a full `system` prompt built from bundled Atlas templates), and the app writes inspection logs so the assembled context can be reviewed without relying on model behavior. Provider API calls are intentionally out of scope for this phase.

The operator-facing UI keeps three facets visible: chat (input and transcript), repo state (tree + basic health), and project state (Atlas wrapper artifacts when present). The repository being managed is the one the app is launched from; there is no multi-project switching in v2.

Bundled Atlas documents (kernel, protocols, projections, schemas) are shipped as package assets under `src/atlas_tui/assets/atlas/` and are used by the default engine implementation.

## Run (v2)

From anywhere inside a git repo (or inside an Atlas wrapper repo):

```bash
atlas-tui
```

By default, the UI starts a bundled local engine subprocess:

```bash
python -m atlas_tui.dummy_engine
```

A different engine command can be supplied:

```bash
ATLAS_ENGINE_CMD="python -m atlas_engine" atlas-tui
# or
atlas-tui --engine-cmd "python -m atlas_engine"
```

On each submit, an inspection log is written to:

- If wrapper exists: `<project_root>/logs/atlas-tui/assembled/`
- Else: `<repo_root>/.atlas-tui/logs/assembled/`

## Keys (v2)

- Submit: `Enter` (Shift+Enter inserts newline)
- Help overlay: `F1`
- Cycle focus (repo > chat > project): `F2`
- Quit: button in the top bar (with confirmation)
- Force quit: `Ctrl+C` (no confirmation)
- Quit (with confirmation): `Esc` when no modal is open

Other actions are available via the top-bar buttons (Refresh, Chat Log, Details, Prefs, Restart, Quit).

## Context prefs (v2)

Context prefs are UI-owned hints sent to the engine in `EngineInput.ui_state`:

- profile: minimal/repo/project/debug
- budget (chars)
- pinned paths (repo-relative)
- excluded paths (repo-relative)

Prefs persist to:

- If wrapper exists: `<project_root>/logs/atlas-tui/state/ui_state.json`
- Else: `<repo_root>/.atlas-tui/state/ui_state.json`

## Glass (optional local web inspector)

Start the TUI plus a read-only local web inspector:

```bash
atlas-tui --glass
```

The inspector reads the `latest.json` pointer and renders the last assembled log:

- If wrapper exists: `<project_root>/logs/atlas-tui/state/latest.json`
- Else: `<repo_root>/.atlas-tui/state/latest.json`

## License

Code and packaged templates (including bundled Atlas docs under `src/atlas_tui/assets/atlas/`) are MIT licensed. Project writings are CC BY 4.0. See `LICENSE`, `LICENSE-CC-BY-4.0.txt`, and `NOTICE.txt`.
