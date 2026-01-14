# Atlas TUI (v2) — Textual cockpit + engine inspection (+ optional web glass)

Thin terminal UI layer for Atlas TUI v2. No provider API calls. A long-lived engine child process performs context assembly and request construction over a JSONL protocol. The TUI writes deterministic inspection logs and renders a compact context contract summary.

This build also includes an optional **web “glass” inspector**: a local, read-only web page that continuously shows the latest engine output by reading the same inspection artifacts the TUI writes.

## Install (dev)

```bash
cd atlas-tui
python -m venv .venv
source .venv/bin/activate
pip install -e .
```

## Run

From anywhere inside a git repo:

```bash
atlas-tui
```

By default Atlas TUI launches a bundled dummy engine:

- `python -m atlas_tui.dummy_engine`

To use a real engine:

```bash
ATLAS_ENGINE_CMD="python -m atlas_engine" atlas-tui
# or
atlas-tui --engine-cmd "python -m atlas_engine"
```

## Context prefs (repo-relative)

Press **Ctrl+P** to edit context prefs:
- profile: minimal/repo/project/debug
- budget (chars)
- pinned paths (repo-relative)
- excluded paths (repo-relative)

Prefs are persisted to:
- wrapper: `project_root/logs/atlas-tui/state/ui_state.json`
- no wrapper: `repo_root/.atlas-tui/state/ui_state.json`

Paths sent to the engine (and returned in selection contracts) are **repo-relative everywhere**.

## Logs

On each submit, an inspection log is written to:
- wrapper: `project_root/logs/atlas-tui/assembled/`
- no wrapper: `repo_root/.atlas-tui/logs/assembled/`

Chat transcript logging is optional (Ctrl+L): `.../logs/chat/<session>.jsonl`.

## Web glass inspector (diagnostic addon)

Start TUI + glass server:

```bash
atlas-tui --glass
```

The TUI transcript will display the glass URL, e.g.:

- `http://127.0.0.1:8765/`

The glass page is **read-only**. It polls `/api/latest` and renders the latest assembled log.

### How “latest” works

Each successful submit updates a pointer file:

- wrapper: `project_root/logs/atlas-tui/state/latest.json`
- no wrapper: `repo_root/.atlas-tui/state/latest.json`

This pointer references the last assembled log path. The glass server reads the pointer, loads the referenced JSON log, and displays it.

Security posture: the server binds to `127.0.0.1` by default and has no auth. Do not expose it on a public interface without adding proper controls.

## License

MIT — see LICENSE.
