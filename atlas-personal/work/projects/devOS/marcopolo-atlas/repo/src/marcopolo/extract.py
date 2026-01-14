from __future__ import annotations

import json
import re
from dataclasses import dataclass
from typing import List

from .util import normalize_ascii, sha256_hex

@dataclass
class Span:
    id: str
    kind: str
    line_start: int
    line_end: int
    col_start: int
    col_end: int
    text: str
    fingerprint: str

_NUM_RE = re.compile(r"^\s*(\d+)[\.)]\s+")
_BUL_RE = re.compile(r"^\s*[-*+]\s+")

def extract_marco_spans(text: str) -> List[Span]:
    text = normalize_ascii(text)
    lines = text.split("\n")

    spans: List[Span] = []
    cur_lines: List[str] = []
    cur_kind: str | None = None
    cur_start: int | None = None

    def flush(end_i: int) -> None:
        nonlocal cur_lines, cur_kind, cur_start
        if not cur_lines or cur_kind is None or cur_start is None:
            cur_lines, cur_kind, cur_start = [], None, None
            return
        span_text = "\n".join(cur_lines).strip()
        if span_text:
            sid = f"m:{len(spans)+1:04d}"
            spans.append(Span(
                id=sid,
                kind=cur_kind,
                line_start=cur_start+1,
                line_end=end_i+1,
                col_start=0,
                col_end=len(lines[end_i]) if 0 <= end_i < len(lines) else 0,
                text=span_text,
                fingerprint=sha256_hex(span_text),
            ))
        cur_lines, cur_kind, cur_start = [], None, None

    for i, ln in enumerate(lines):
        if ln.strip() == "":
            if cur_lines:
                flush(i-1 if i > 0 else 0)
            continue

        is_num = bool(_NUM_RE.match(ln))
        is_bul = bool(_BUL_RE.match(ln))

        if is_num:
            if cur_lines:
                flush(i-1)
            cur_kind = "numbered_item"
            cur_start = i
            cur_lines = [ln]
            continue

        if is_bul:
            if cur_lines:
                flush(i-1)
            cur_kind = "bullet"
            cur_start = i
            cur_lines = [ln]
            continue

        if not cur_lines:
            cur_kind = "block"
            cur_start = i
            cur_lines = [ln]
        else:
            cur_lines.append(ln)

    if cur_lines:
        flush(len(lines)-1)

    return spans

_THREAD_RE = re.compile(r"^\s*##\s+(.+?)\s*$")
_TYPED_RE = re.compile(r"^\s*(SRC|OPEN|PROP)\s*:\s*(.*)$")

@dataclass
class Unit:
    id: str
    kind: str
    thread_id: str
    text: str
    fingerprint: str

def extract_polo_units(text: str) -> List[Unit]:
    text = normalize_ascii(text)
    lines = text.split("\n")
    units: List[Unit] = []

    thread_id = "T00"
    thread_idx = 0
    counters = {"src": 0, "open": 0, "prop": 0, "thread": 0}

    for ln in lines:
        m = _THREAD_RE.match(ln)
        if m:
            thread_idx += 1
            thread_id = f"T{thread_idx:02d}"
            counters = {"src": 0, "open": 0, "prop": 0, "thread": 0}
            txt = m.group(1).strip()
            counters["thread"] += 1
            uid = f"p:{thread_id}.thread{counters['thread']:02d}"
            units.append(Unit(uid, "thread", thread_id, txt, sha256_hex(txt)))
            continue

        m = _TYPED_RE.match(ln)
        if m:
            tag = m.group(1).lower()
            body = m.group(2).strip()
            counters[tag] += 1
            uid = f"p:{thread_id}.{tag}{counters[tag]:02d}"
            units.append(Unit(uid, tag, thread_id, body, sha256_hex(body)))
            continue

    return units

def write_spans_jsonl(spans: List[Span], path: str) -> None:
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        for sp in spans:
            f.write(json.dumps({
                "id": sp.id,
                "source_range": {
                    "line_start": sp.line_start,
                    "line_end": sp.line_end,
                    "col_start": sp.col_start,
                    "col_end": sp.col_end,
                },
                "kind": sp.kind,
                "text": sp.text,
                "fingerprint": sp.fingerprint,
            }) + "\n")

def write_units_jsonl(units: List[Unit], path: str) -> None:
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        for u in units:
            f.write(json.dumps({
                "id": u.id,
                "kind": u.kind,
                "thread_id": u.thread_id,
                "text": u.text,
                "fingerprint": u.fingerprint,
            }) + "\n")
