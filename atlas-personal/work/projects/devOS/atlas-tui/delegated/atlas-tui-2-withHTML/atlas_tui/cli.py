from __future__ import annotations

import argparse
import os
import shlex
from pathlib import Path
from typing import Optional

from .workspace import discover_workspace
from .ui.app import AtlasTUIApp

DEFAULT_ENGINE_CMD = "python -m atlas_tui.dummy_engine"

def _parse_engine_cmd(s: str) -> list[str]:
    return shlex.split(s)

def main() -> None:
    parser = argparse.ArgumentParser(
        prog="atlas-tui",
        description="Atlas TUI v2 (Textual) — thin cockpit + context inspection logs (+ optional local web glass).",
    )
    parser.add_argument("--engine-cmd", type=str, default=None, help="Engine command (string). Overrides ATLAS_ENGINE_CMD.")
    parser.add_argument("--preview-chars", type=int, default=800, help="Preview length for system strings in UI/logs.")
    parser.add_argument("--timeout", type=float, default=60.0, help="Engine request timeout (seconds).")

    # Web glass (read-only inspector)
    parser.add_argument("--glass", action="store_true", help="Start local web 'glass' inspector (read-only).")
    parser.add_argument("--glass-host", type=str, default="127.0.0.1", help="Glass host bind (default: 127.0.0.1).")
    parser.add_argument("--glass-port", type=int, default=8765, help="Glass port (default: 8765).")

    args = parser.parse_args()

    workspace = discover_workspace(Path.cwd())

    engine_cmd_str = args.engine_cmd or os.environ.get("ATLAS_ENGINE_CMD") or DEFAULT_ENGINE_CMD
    engine_cmd = _parse_engine_cmd(engine_cmd_str)

    glass_url: Optional[str] = None
    if args.glass:
        from .web.server import start_glass_server
        srv = start_glass_server(workspace=workspace, host=args.glass_host, port=args.glass_port)
        glass_url = srv.url

    app = AtlasTUIApp(
        workspace=workspace,
        engine_cmd=engine_cmd,
        engine_cmd_str=engine_cmd_str,
        preview_chars=args.preview_chars,
        engine_timeout_s=args.timeout,
        glass_url=glass_url,
    )
    app.run()
