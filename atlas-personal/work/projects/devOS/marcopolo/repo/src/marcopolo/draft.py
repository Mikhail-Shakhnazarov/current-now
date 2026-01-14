from __future__ import annotations

import re
from typing import Dict, List, Tuple

from .extract import Span

TOPIC_RULES: List[Tuple[str, List[str]]] = [
    ("OpenCode output formatting", ["opencode", "output", "format", "ugly", "render", "pretty"]),
    ("Subsidiarity and tool boundaries", ["subsidiarity", "boundary", "permission", "write", "kernel", "port"]),
    ("Forking and observability", ["fork", "upstream", "observability", "log", "diagnostic", "telemetry"]),
    ("Model choice and cognition", ["model", "gpt", "claude", "reason", "cognitive", "engagement"]),
    ("Sequential pipelines and scaling", ["sequential", "pipeline", "scale", "turns", "conversation"]),
    ("Output templates and hygiene", ["template", "format", "requirements", "output", "markdown"]),
    ("Work-OS framing", ["work-os", "atlas", "context", "kernel", "doctrine"]),
]

Q_MARKERS = ["?", "unclear", "needs decision", "what determines", "how do", "is there any way"]

def _contains_any(s: str, needles: List[str]) -> bool:
    s = s.lower()
    return any(n in s for n in needles)

def draft_polo_from_marco(spans: List[Span]) -> str:
    buckets: Dict[str, List[Span]] = {title: [] for title, _ in TOPIC_RULES}
    misc: List[Span] = []

    for sp in spans:
        placed = False
        for title, kws in TOPIC_RULES:
            if _contains_any(sp.text, kws):
                buckets[title].append(sp)
                placed = True
                break
        if not placed:
            misc.append(sp)

    out: List[str] = []
    thread_num = 0
    for title, _ in TOPIC_RULES:
        if not buckets[title]:
            continue
        thread_num += 1
        out.append(f"## Thread {thread_num}: {title}")
        out.append("")
        for sp in buckets[title]:
            txt = sp.text.replace("\n", " ").strip()
            out.append(f"SRC: {txt} [trace:{sp.id}]")
            if _contains_any(sp.text, Q_MARKERS):
                out.append(f"OPEN: Clarify decision/question implied by: {sp.id} [trace:{sp.id}]")
            if re.search(r"\b(readme|docs/|src/|\.md|\.py)\b", sp.text.lower()):
                out.append(f"PROP: Consider routing this to an appropriate doc surface. [trace:{sp.id}]")
        out.append("")

    if misc:
        thread_num += 1
        out.append(f"## Thread {thread_num}: Misc")
        out.append("")
        for sp in misc:
            txt = sp.text.replace("\n", " ").strip()
            out.append(f"SRC: {txt} [trace:{sp.id}]")
            if _contains_any(sp.text, Q_MARKERS):
                out.append(f"OPEN: Clarify decision/question implied by: {sp.id} [trace:{sp.id}]")
        out.append("")

    return "\n".join(out).strip() + "\n"
