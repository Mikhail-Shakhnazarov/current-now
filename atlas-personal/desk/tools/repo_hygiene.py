#!/usr/bin/env python3
"""Repo hygiene for atlas-personal.

Goals:
- Enforce ASCII-only artifacts across the repository.
- Normalize common typographic Unicode to ASCII.
- Repair common mojibake (UTF-8 bytes interpreted as cp1252), then normalize.
- Normalize all human-facing years to 2026.
- Flag malformed brace-named paths (e.g., literal "{a,b}") that indicate broken scaffolding.

Usage:
  python atlas-personal/desk/tools/repo_hygiene.py --check
  python atlas-personal/desk/tools/repo_hygiene.py --fix

Exit codes:
- 0: success
- 1: hygiene violations
- 2: unexpected error
"""

from __future__ import annotations

import argparse
import pathlib
import re
import sys
from dataclasses import dataclass


ROOT = pathlib.Path(__file__).resolve().parents[2]  # atlas-personal/
SELF = pathlib.Path(__file__).resolve()

CANONICAL_AUTHOR = "Mikhail Shakhnazarov"
CANONICAL_YEAR = "2026"

TEXT_FILE_NAMES = {"LICENSE", "NOTICE.txt", "LICENSE-CC-BY-4.0.txt"}
TEXT_EXTS = {".md", ".txt", ".py", ".json"}


def u(codepoint_hex: str) -> str:
    return chr(int(codepoint_hex, 16))


UNICODE_TO_ASCII = {
    u("00E2"): "",  # mojibake stray prefix
    u("00A0"): " ",  # NBSP
    u("2014"): "--",  # em dash
    u("2013"): "-",  # en dash
    u("2018"): "'",
    u("2019"): "'",
    u("201C"): '"',
    u("201D"): '"',
    u("2026"): "...",
    u("2192"): "->",
    u("2122"): "(TM)",
    u("2020"): "(dagger)",
    u("2030"): "per mille",
    u("00A6"): "|",  # broken bar
    u("2260"): "!=",  # not equal
}

# Box drawing sequences used in tree diagrams.
BOX_TO_ASCII_SEQS = [
    (u("251C") + u("2500") + u("2500"), "|--"),
    (u("2514") + u("2500") + u("2500"), "`--"),
    (u("2502"), "|"),
    (u("2500"), "-"),
]

# Common mojibake markers expressed via codepoints.
# If present, attempt a cp1252->utf-8 repair pass.
MOJIBAKE_MARKERS = (
    u("00E2") + u("20AC"),  # cp1252 mojibake prefix
    u("00C3"),  # another common mojibake prefix
)

# Common 3-character mojibake sequences that may include undefined cp1252 bytes.
MOJIBAKE_SEQ_REPLACEMENTS = [
    (u("00E2") + u("20AC") + u("0153"), '"'),
    (u("00E2") + u("20AC") + u("009D"), '"'),
    (u("00E2") + u("20AC") + u("2122"), "'"),
    (u("00E2") + u("20AC") + u("2014"), "--"),
    (u("00E2") + u("20AC") + u("2013"), "-"),
    # If the prefix appears standalone, drop it.
    (u("00E2") + u("20AC"), ""),
]


@dataclass(frozen=True)
class Violation:
    path: pathlib.Path
    message: str


def iter_candidate_files(root: pathlib.Path) -> list[pathlib.Path]:
    files: list[pathlib.Path] = []
    for p in root.rglob("*"):
        if not p.is_file():
            continue
        if p.name in TEXT_FILE_NAMES:
            files.append(p)
            continue
        if p.suffix.lower() in TEXT_EXTS:
            files.append(p)
    return files


def iter_malformed_paths(root: pathlib.Path) -> list[pathlib.Path]:
    bad: list[pathlib.Path] = []
    for p in root.rglob("*"):
        parts = p.parts
        if any(("{" in part) or ("}" in part) for part in parts):
            bad.append(p)
    return bad


def maybe_repair_mojibake(text: str) -> str:
    if not any(marker in text for marker in MOJIBAKE_MARKERS):
        return text
    try:
        return text.encode("cp1252", errors="strict").decode("utf-8", errors="strict")
    except Exception:
        return text


def normalize_text(text: str) -> str:
    text = maybe_repair_mojibake(text)

    for old, new in MOJIBAKE_SEQ_REPLACEMENTS:
        text = text.replace(old, new)

    for old, new in BOX_TO_ASCII_SEQS:
        text = text.replace(old, new)

    for old, new in UNICODE_TO_ASCII.items():
        text = text.replace(old, new)

    return text


# Normalize human-facing years 2020-2025 to 2026.
YEAR_RE = re.compile(r"\b202[0-5]\b")


def normalize_years_for_path(path: pathlib.Path, text: str) -> str:
    # Only apply year normalization to human-facing text artifacts.
    if path.name == "LICENSE":
        return YEAR_RE.sub(CANONICAL_YEAR, text)
    if path.suffix.lower() in {".md", ".txt"}:
        return YEAR_RE.sub(CANONICAL_YEAR, text)
    return text


def normalize_license_author(text: str) -> str:
    return re.sub(
        r"^Copyright \(c\) \d{4}.*$",
        f"Copyright (c) {CANONICAL_YEAR} {CANONICAL_AUTHOR}",
        text,
        flags=re.MULTILINE,
    )


def is_ascii(text: str) -> bool:
    try:
        text.encode("ascii")
        return True
    except UnicodeEncodeError:
        return False


def read_text_file(path: pathlib.Path) -> str:
    return path.read_text(encoding="utf-8")


def write_text_file(path: pathlib.Path, content: str) -> None:
    path.write_text(content, encoding="utf-8", newline="\n")


def check_or_fix(*, fix: bool) -> int:
    violations: list[Violation] = []

    for p in iter_malformed_paths(ROOT):
        violations.append(Violation(p, "malformed path contains '{' or '}'"))

    for path in iter_candidate_files(ROOT):
        try:
            original = read_text_file(path)
        except Exception as exc:
            violations.append(Violation(path, f"unreadable: {exc}"))
            continue

        normalized = normalize_text(original)
        normalized = normalize_years_for_path(path, normalized)

        if path.name == "LICENSE":
            normalized = normalize_license_author(normalized)

        # Do not self-modify on --fix.
        if fix and path.resolve() == SELF:
            normalized = original

        if fix and normalized != original:
            try:
                write_text_file(path, normalized)
            except Exception as exc:
                violations.append(Violation(path, f"failed to write: {exc}"))
                continue

        final_text = normalized if fix else original

        if path.suffix.lower() in {".md", ".txt"} or path.name in TEXT_FILE_NAMES:
            if YEAR_RE.search(final_text):
                violations.append(Violation(path, "contains year outside 2026"))

        if not is_ascii(final_text):
            violations.append(Violation(path, "contains non-ASCII characters"))

    if violations:
        for v in violations:
            sys.stdout.buffer.write((str(v.path) + ": " + v.message + "\n").encode("utf-8", "backslashreplace"))
        return 1

    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--check", action="store_true", help="fail on hygiene violations")
    mode.add_argument("--fix", action="store_true", help="rewrite files to satisfy hygiene")
    args = parser.parse_args()

    try:
        return check_or_fix(fix=bool(args.fix))
    except Exception as exc:
        sys.stdout.buffer.write(("unexpected error: " + str(exc) + "\n").encode("utf-8", "backslashreplace"))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
