from __future__ import annotations

import json
import threading
from dataclasses import dataclass
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from importlib import resources
from pathlib import Path
from typing import Any, Dict, List, Optional
from urllib.parse import parse_qs, urlparse

from ..models import Workspace
from ..state_store import latest_pointer_path, resolve_latest_log_path
from ..ui_observability import events_log_path, latest_snapshot_path


def _index_html() -> str:
    return resources.files(__package__).joinpath("static/index.html").read_text(encoding="utf-8")


def _load_json(path: Path) -> Optional[Dict[str, Any]]:
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None


def _load_latest_assembled(workspace: Workspace) -> Dict[str, Any]:
    ptr = latest_pointer_path(workspace)
    meta = _load_json(ptr)
    if not meta:
        return {"status": "none"}
    lp = meta.get("last_log_path")
    if not lp:
        return {"status": "none"}
    log_path = resolve_latest_log_path(workspace, str(lp))
    data = _load_json(log_path)
    if not data:
        return {"status": "none"}
    return {"status": "ok", "data": data, "meta": meta}


def _load_latest_snapshot(workspace: Workspace) -> Dict[str, Any]:
    p = latest_snapshot_path(workspace)
    data = _load_json(p)
    if not data:
        return {"status": "none"}
    return {"status": "ok", "data": data}


def _events_tail(workspace: Workspace, n: int) -> Dict[str, Any]:
    p = events_log_path(workspace)
    if not p.exists():
        return {"status": "none", "events": []}
    try:
        lines = p.read_text(encoding="utf-8").splitlines()
        tail = lines[-n:] if n > 0 else []
        events: List[Dict[str, Any]] = []
        for ln in tail:
            try:
                events.append(json.loads(ln))
            except Exception:
                continue
        return {"status": "ok", "events": events}
    except Exception:
        return {"status": "error", "events": []}


class _Handler(BaseHTTPRequestHandler):
    workspace: Workspace = None  # type: ignore[assignment]
    index_html: str = ""

    def _send_json(self, obj: Dict[str, Any], status: int = 200) -> None:
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
            self._send_json(_load_latest_assembled(self.workspace))
            return
        if parsed.path == "/api/ui/latest_snapshot":
            self._send_json(_load_latest_snapshot(self.workspace))
            return
        if parsed.path == "/api/ui/events_tail":
            qs = parse_qs(parsed.query or "")
            try:
                n = int((qs.get("n") or ["50"])[0])
            except Exception:
                n = 50
            self._send_json(_events_tail(self.workspace, max(0, min(n, 500))))
            return
        self._send_json({"status": "not_found"}, status=404)

    def log_message(self, format: str, *args) -> None:  # noqa: A003
        return


@dataclass
class GlassServer:
    httpd: ThreadingHTTPServer
    thread: threading.Thread
    url: str

    def stop(self) -> None:
        try:
            self.httpd.shutdown()
        except Exception:
            pass
        try:
            self.httpd.server_close()
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
