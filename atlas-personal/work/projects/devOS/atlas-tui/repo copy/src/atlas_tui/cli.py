from __future__ import annotations

import argparse
import asyncio
import os
import shlex
import sys
from pathlib import Path

from .workspace import discover_workspace
from .ui.app import AtlasTUIApp

DEFAULT_ENGINE_CMD = [sys.executable, "-m", "atlas_tui.dummy_engine"]

def _parse_engine_cmd(s: str) -> list[str]:
    # Shell-like split (portable enough for a CLI option). Prefer passing a full string.
    return shlex.split(s)

def main() -> None:
    parser = argparse.ArgumentParser(
        prog="atlas-tui",
        description="Atlas TUI v2 (Textual) - thin cockpit + context inspection logs.",
    )
    parser.add_argument("--engine-cmd", type=str, default=None, help="Engine command (string). Overrides ATLAS_ENGINE_CMD.")
    parser.add_argument("--preview-chars", type=int, default=800, help="Preview length for system strings in UI/logs.")
    parser.add_argument("--timeout", type=float, default=60.0, help="Engine request timeout (seconds).")
    parser.add_argument("--glass", action="store_true", help="Start local web 'glass' inspector (read-only).")
    parser.add_argument("--glass-host", type=str, default="127.0.0.1", help="Glass host bind (default: 127.0.0.1).")
    parser.add_argument("--glass-port", type=int, default=8765, help="Glass port (default: 8765).")
    args = parser.parse_args()

    if not sys.stdin.isatty() or not sys.stdout.isatty():
        print("atlas-tui: interactive terminal required (no TTY detected).", file=sys.stderr)
        raise SystemExit(2)

    try:
        workspace = discover_workspace(Path.cwd())
    except Exception as e:
        print(f"atlas-tui: workspace discovery failed: {e}", file=sys.stderr)
        raise SystemExit(2)

    engine_cmd_override = args.engine_cmd or os.environ.get("ATLAS_ENGINE_CMD")
    if engine_cmd_override:
        engine_cmd_str = engine_cmd_override
        engine_cmd = _parse_engine_cmd(engine_cmd_str)
    else:
        engine_cmd = list(DEFAULT_ENGINE_CMD)
        engine_cmd_str = " ".join(engine_cmd)

    glass_url = None
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


if __name__ == "__main__":
    main()
