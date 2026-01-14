from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Literal, Optional

from .determinism import Clock, RealClock

UIEventType = Literal[
    "focus_changed",
    "key_handled",
    "submit_started",
    "submit_done",
    "log_written",
    "glass_pointer_updated",
]


@dataclass(frozen=True)
class UIEvent:
    type: UIEventType
    payload: Dict[str, Any]
    session_id: str
    clock: Clock = RealClock()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "schema_version": 1,
            "type": self.type,
            "ts": self.clock.now_iso(),
            "session_id": self.session_id,
            "payload": self.payload,
        }


def focus_changed(session_id: str, panel: str, widget_id: Optional[str], clock: Optional[Clock] = None) -> UIEvent:
    return UIEvent(
        type="focus_changed",
        payload={"panel": panel, "widget_id": widget_id},
        session_id=session_id,
        clock=clock or RealClock(),
    )


def key_handled(
    session_id: str,
    key: str,
    action: str,
    screen_stack_depth: int,
    result: str,
    clock: Optional[Clock] = None,
) -> UIEvent:
    return UIEvent(
        type="key_handled",
        payload={
            "key": key,
            "action": action,
            "screen_stack_depth": int(screen_stack_depth),
            "result": result,
        },
        session_id=session_id,
        clock=clock or RealClock(),
    )


def submit_started(
    session_id: str, request_id: str, mode: str, provider: str, model: str, clock: Optional[Clock] = None
) -> UIEvent:
    return UIEvent(
        type="submit_started",
        payload={"request_id": request_id, "mode": mode, "provider": provider, "model": model},
        session_id=session_id,
        clock=clock or RealClock(),
    )


def submit_done(session_id: str, request_id: str, ok: bool, system_chars: int, clock: Optional[Clock] = None) -> UIEvent:
    return UIEvent(
        type="submit_done",
        payload={"request_id": request_id, "ok": bool(ok), "system_chars": int(system_chars)},
        session_id=session_id,
        clock=clock or RealClock(),
    )


def log_written(session_id: str, path: str, bytes_written: int, clock: Optional[Clock] = None) -> UIEvent:
    return UIEvent(
        type="log_written",
        payload={"path": path, "bytes": int(bytes_written)},
        session_id=session_id,
        clock=clock or RealClock(),
    )


def glass_pointer_updated(session_id: str, path: str, clock: Optional[Clock] = None) -> UIEvent:
    return UIEvent(
        type="glass_pointer_updated",
        payload={"path": path},
        session_id=session_id,
        clock=clock or RealClock(),
    )

