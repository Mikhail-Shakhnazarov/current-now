from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .models import Workspace
from .ui.app import AtlasTUIApp


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Atlas TUI (3d_printed)")
    parser.add_argument("--repo-root", type=str, default=".", help="Repository root to browse")
    parser.add_argument("--project-root", type=str, default=".", help="Project root for logs (default: CWD)")
    parser.add_argument("--no-glass", action="store_true", help="Do not start Glass server")
    args = parser.parse_args(argv)

    repo_root = str(Path(args.repo_root).resolve())
    project_root = str(Path(args.project_root).resolve())
    ws = Workspace(repo_root=repo_root, project_root=project_root)

    engine_cmd = [sys.executable, "-m", "atlas_tui.dummy_engine"]
    app = AtlasTUIApp(workspace=ws, engine_cmd=engine_cmd, start_glass=not args.no_glass)
    app.run()


if __name__ == "__main__":
    main()

