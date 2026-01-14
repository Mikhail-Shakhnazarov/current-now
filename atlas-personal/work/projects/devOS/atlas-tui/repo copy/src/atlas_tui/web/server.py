from __future__ import annotations

import json
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from importlib import resources
from pathlib import Path
from typing import Optional
from urllib.parse import urlparse

from ..models import Workspace
from ..state_store import latest_pointer_path


def _load_latest(workspace: Workspace) -> Optional[dict]:
    ptr = latest_pointer_path(workspace.repo_root, workspace.project_root)
    if not ptr.exists():
        return None
    try:
        meta = json.loads(ptr.read_text(encoding="utf-8"))
        lp = meta.get("last_log_path")
        if not lp:
            return None
        log_path = Path(lp)
        if not log_path.exists():
            return None
        data = json.loads(log_path.read_text(encoding="utf-8"))
        data["_log_path"] = str(log_path)
        data["_latest_meta"] = meta
        return data
    except Exception:
        return None


def _index_html() -> str:
    return resources.files(__package__).joinpath("static/index.html").read_text(encoding="utf-8")


class _Handler(BaseHTTPRequestHandler):
    workspace: Workspace = None  # type: ignore[assignment]
    index_html: str = ""

    def _send_json(self, obj: dict, status: int = 200) -> None:
        b = json.dumps(obj, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(b)))
        self.end_headers()
        self.wfile.write(b)

    def _send_html(self, html: str, status: int = 200) -> None:
        b = html.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(b)))
        self.end_headers()
        self.wfile.write(b)

    def do_GET(self) -> None:  # noqa: N802
        parsed = urlparse(self.path)
        if parsed.path in {"/", "/index.html"}:
            self._send_html(self.index_html)
            return
        if parsed.path == "/api/latest":
            data = _load_latest(self.workspace)
            if not data:
                self._send_json({"status": "none"})
                return
            self._send_json({"status": "ok", "data": data})
            return
        self._send_json({"status": "not_found"}, status=404)

    def log_message(self, format: str, *args) -> None:  # noqa: A003
        return


class GlassServer:
    def __init__(self, httpd: ThreadingHTTPServer, thread: threading.Thread, url: str) -> None:
        self.httpd = httpd
        self.thread = thread
        self.url = url

    def stop(self) -> None:
        try:
            self.httpd.shutdown()
        except Exception:
            pass


def start_glass_server(workspace: Workspace, host: str = "127.0.0.1", port: int = 8765) -> GlassServer:
    handler = _Handler
    handler.workspace = workspace
    handler.index_html = _index_html()

    httpd = ThreadingHTTPServer((host, port), handler)
    actual_port = int(httpd.server_address[1])
    url = f"http://{host}:{actual_port}/"

    t = threading.Thread(target=httpd.serve_forever, name="atlas-glass", daemon=True)
    t.start()
    return GlassServer(httpd=httpd, thread=t, url=url)

