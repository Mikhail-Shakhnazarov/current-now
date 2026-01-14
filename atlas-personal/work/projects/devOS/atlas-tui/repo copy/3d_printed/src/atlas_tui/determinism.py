from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Protocol
import uuid


class Clock(Protocol):
    def now_iso(self) -> str: ...


class IdProvider(Protocol):
    def new_session_id(self) -> str: ...
    def new_request_id(self) -> str: ...


@dataclass(frozen=True)
class RealClock:
    def now_iso(self) -> str:
        return datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")


@dataclass(frozen=True)
class UuidIds:
    session_prefix_len: int = 10
    request_prefix_len: int = 10

    def new_session_id(self) -> str:
        return uuid.uuid4().hex[: self.session_prefix_len]

    def new_request_id(self) -> str:
        return uuid.uuid4().hex[: self.request_prefix_len]


@dataclass(frozen=True)
class FixedClock:
    iso: str

    def now_iso(self) -> str:
        return self.iso


@dataclass(frozen=True)
class FixedIds:
    session_id: str = "session"
    request_id: str = "request"

    def new_session_id(self) -> str:
        return self.session_id

    def new_request_id(self) -> str:
        return self.request_id

