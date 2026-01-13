#!/usr/bin/env python3
"""Render a spec.json (schema-valid) into a readable Markdown summary.

This is a presentation tool to avoid dumping large JSON into chat UIs.

Usage:
  python atlas-personal/desk/tools/render_spec_json.py path/to/SPEC-001.json
  python atlas-personal/desk/tools/render_spec_json.py path/to/SPEC-001.json --out path/to/SPEC-001.md
"""

from __future__ import annotations

import argparse
import json
import pathlib
import sys


def render(spec: dict) -> str:
    spec_id = spec.get("id", "")
    status = spec.get("status", "")
    summary = (spec.get("summary") or "").strip()

    scope = spec.get("scope") or {}
    scope_in = scope.get("in") or []
    scope_out = scope.get("out") or []

    reqs = spec.get("requirements") or {}
    must = reqs.get("must") or []
    should = reqs.get("should") or []
    may = reqs.get("may") or []

    target = spec.get("target") or []
    open_items = spec.get("open") or []
    verification = spec.get("verification") or []

    lines: list[str] = []
    lines.append(f"# {spec_id}")
    if status:
        lines.append(f"\nStatus: {status}")
    if summary:
        lines.append("\n## Summary\n")
        lines.append(summary)

    def bullet_block(title: str, items: list[str]) -> None:
        lines.append(f"\n## {title}\n")
        if not items:
            lines.append("- (none)")
            return
        for item in items:
            lines.append(f"- {item}")

    bullet_block("Scope In", [str(x) for x in scope_in])
    bullet_block("Scope Out", [str(x) for x in scope_out])

    bullet_block("Requirements Must", [str(x) for x in must])
    bullet_block("Requirements Should", [str(x) for x in should])
    bullet_block("Requirements May", [str(x) for x in may])

    bullet_block("Target Files", [str(x) for x in target])

    lines.append("\n## Open Items\n")
    if not open_items:
        lines.append("- (none)")
    else:
        for item in open_items:
            item_id = item.get("id", "")
            desc = (item.get("description") or "").strip()
            closure = (item.get("closure") or "").strip()
            lines.append(f"- {item_id}: {desc}")
            if closure:
                lines.append(f"  Closure: {closure}")

    lines.append("\n## Verification\n")
    if not verification:
        lines.append("- (none)")
    else:
        for v in verification:
            check = (v.get("check") or "").strip()
            expected = (v.get("expected") or "").strip()
            lines.append(f"- Check: {check}")
            lines.append(f"  Expected: {expected}")

    return "\n".join(lines).strip() + "\n"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("spec_json", type=pathlib.Path)
    parser.add_argument("--out", type=pathlib.Path)
    args = parser.parse_args()

    spec = json.loads(args.spec_json.read_text(encoding="utf-8"))
    md = render(spec)

    if args.out:
        args.out.write_text(md, encoding="utf-8", newline="\n")
    else:
        sys.stdout.write(md)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
