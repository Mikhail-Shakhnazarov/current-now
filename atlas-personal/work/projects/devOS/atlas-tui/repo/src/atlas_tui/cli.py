from __future__ import annotations

import argparse
import os
import shlex
from pathlib import Path

from .workspace import discover_workspace
from .ui.app import AtlasTUIApp

DEFAULT_ENGINE_CMD = "python -m atlas_tui.dummy_engine"

def _parse_engine_cmd(s: str) -> list[str]:
    # Shell-like split (portable enough for a CLI option). Prefer passing a full string.
    return shlex.split(s)

def main() -> None:
    parser = argparse.ArgumentParser(prog="atlas-tui", description="Atlas TUI v2 (Textual) — thin cockpit + context inspection logs.")
    parser.add_argument("--engine-cmd", type=str, default=None, help="Engine command (string). Overrides ATLAS_ENGINE_CMD.")
    parser.add_argument("--preview-chars", type=int, default=800, help="Preview length for system strings in UI/logs.")
    parser.add_argument("--timeout", type=float, default=60.0, help="Engine request timeout (seconds).")
    args = parser.parse_args()

    workspace = discover_workspace(Path.cwd())

    engine_cmd_str = args.engine_cmd or os.environ.get("ATLAS_ENGINE_CMD") or DEFAULT_ENGINE_CMD
    engine_cmd = _parse_engine_cmd(engine_cmd_str)

    app = AtlasTUIApp(
        workspace=workspace,
        engine_cmd=engine_cmd,
        engine_cmd_str=engine_cmd_str,
        preview_chars=args.preview_chars,
        engine_timeout_s=args.timeout,
    )
    app.run()
