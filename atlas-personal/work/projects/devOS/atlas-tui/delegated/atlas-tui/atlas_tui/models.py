from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Any, Dict, List, Literal, Optional

Mode = Literal["interpret", "plan", "execute"]
Provider = Literal["openai", "anthropic"]

@dataclass(frozen=True)
class Workspace:
    repo_root: str
    project_root: Optional[str] = None

@dataclass
class EngineInput:
    workspace: Workspace
    mode: Mode
    provider: Provider
    model: str
    user_message: str
    # ui_state includes context hints. Paths MUST be repo-relative.
    ui_state: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["workspace"] = asdict(self.workspace)
        return d

@dataclass
class AssembledContext:
    mode: Mode
    system: str

@dataclass
class ProviderRequest:
    provider: Provider
    model: str
    system: str
    user: str
    messages: Optional[List[Dict[str, Any]]] = None

@dataclass
class EngineOutput:
    assembled_context: AssembledContext
    provider_request: ProviderRequest
    diagnostics: Optional[Dict[str, Any]] = None

    @staticmethod
    def from_dict(payload: Dict[str, Any]) -> "EngineOutput":
        ac = payload.get("assembled_context") or {}
        pr = payload.get("provider_request") or {}
        return EngineOutput(
            assembled_context=AssembledContext(
                mode=ac.get("mode", "interpret"),
                system=ac.get("system", ""),
            ),
            provider_request=ProviderRequest(
                provider=pr.get("provider", "openai"),
                model=pr.get("model", ""),
                system=pr.get("system", ""),
                user=pr.get("user", ""),
                messages=pr.get("messages"),
            ),
            diagnostics=payload.get("diagnostics"),
        )
