from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional

from .determinism import Clock, RealClock
from .state_store import UIContextPrefs


@dataclass
class UISnapshot:
    focused_panel: str
    focused_widget_id: Optional[str]
    screen_stack: List[str]
    selected_path: Optional[str]
    mode: str
    provider: str
    model: str
    last_request_id: Optional[str]
    last_log_path: Optional[str]
    prefs: UIContextPrefs
    session_id: str
    clock: Clock = field(default_factory=RealClock)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "schema_version": 1,
            "ts": self.clock.now_iso(),
            "session_id": self.session_id,
            "focused_panel": self.focused_panel,
            "focused_widget_id": self.focused_widget_id,
            "screen_stack": list(self.screen_stack),
            "selected_path": self.selected_path,
            "mode": self.mode,
            "provider": self.provider,
            "model": self.model,
            "last_request_id": self.last_request_id,
            "last_log_path": self.last_log_path,
            "prefs": asdict(self.prefs),
        }


def capture_snapshot(
    *,
    focused_panel: str,
    focused_widget_id: Optional[str],
    screen_stack: List[str],
    selected_path: Optional[str],
    mode: str,
    provider: str,
    model: str,
    last_request_id: Optional[str],
    last_log_path: Optional[str],
    prefs: UIContextPrefs,
    session_id: str,
    clock: Optional[Clock] = None,
) -> UISnapshot:
    return UISnapshot(
        focused_panel=focused_panel,
        focused_widget_id=focused_widget_id,
        screen_stack=list(screen_stack),
        selected_path=selected_path,
        mode=mode,
        provider=provider,
        model=model,
        last_request_id=last_request_id,
        last_log_path=last_log_path,
        prefs=prefs,
        session_id=session_id,
        clock=clock or RealClock(),
    )

