#!/usr/bin/env python3
"""Atlas wrapper tooling for the Marco-Polo pipeline.

This tool is invoked from the Atlas repository root. It does not use an LLM.
It is intended to propagate an operator-approved, typed POLO into deterministic
project artifacts with minimal spam.

v1 design choices:
- Late trace only: no trace tags required in POLO; optional verification can run later.
- Exactly one rolling state file per project (defaults to outputs/state.md).
- PROP propagation is optional (flag).

Typed POLO protocol (recognized):
- Thread headings: lines starting with '## '
- Typed lines: 'SRC:', 'OPEN:', 'PROP:'

Usage example:
  python atlas-personal/desk/tools/marcopolo_atlas.py propagate \
    --project writeOS/marco-polo \
    --marco marco.md \
    --polo polo.md \
    --include-prop
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import sys
from dataclasses import asdict
from datetime import datetime
from pathlib import Path


ATLAS_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_INTAKE = ATLAS_ROOT / "inbox-airlock" / "operator-obsidian-render" / "marcopolo-intake"


def _utc_stamp() -> str:
    return datetime.utcnow().strftime("%Y%m%d_%H%M%S")


def _load_marcopolo_extract_module() -> object:
    """Import extract helpers from the in-house fork.

    We import directly from the copied repo source tree to avoid requiring an
    editable install.
    """

    src_dir = ATLAS_ROOT / "work" / "projects" / "devOS" / "marcopolo-atlas" / "repo" / "src"
    if not src_dir.exists():
        raise RuntimeError(f"missing marcopolo-atlas src directory: {src_dir}")

    sys.path.insert(0, str(src_dir))
    try:
        import marcopolo.extract as extract  # type: ignore
    finally:
        # Keep sys.path clean for callers.
        try:
            sys.path.remove(str(src_dir))
        except ValueError:
            pass

    return extract


def _load_marcopolo_util_module() -> object:
    src_dir = ATLAS_ROOT / "work" / "projects" / "devOS" / "marcopolo-atlas" / "repo" / "src"
    if not src_dir.exists():
        raise RuntimeError(f"missing marcopolo-atlas src directory: {src_dir}")

    sys.path.insert(0, str(src_dir))
    try:
        import marcopolo.util as util  # type: ignore
    finally:
        try:
            sys.path.remove(str(src_dir))
        except ValueError:
            pass

    return util


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8", newline="\n")


def _airlock_overwrite_in_place(path: Path, *, repair_common_punct: bool) -> dict:
    util = _load_marcopolo_util_module()

    raw = _read_text(path)
    fixed, rep = util.airlock_text(raw, repair_common_punct=repair_common_punct)
    if fixed is None:
        raise ValueError(f"airlock failed for {path}: {rep}")

    # Normalize line endings deterministically.
    fixed = util.normalize_ascii(fixed)
    _write_text(path, fixed)

    return rep


def _resolve_project_dir(project: str) -> Path:
    # Accept both "writeOS/marco-polo" and "work/projects/writeOS/marco-polo".
    p = Path(project)
    if p.is_absolute():
        return p

    if project.startswith("work/"):
        return ATLAS_ROOT / project

    return ATLAS_ROOT / "work" / "projects" / project


def _render_state_md(
    *,
    project_rel: str,
    run_rel: str,
    threads: list[tuple[str, str]],
    open_by_thread: dict[str, list[str]],
    prop_by_thread: dict[str, list[str]],
    include_prop: bool,
) -> str:
    lines: list[str] = []
    lines.append("# Marco-Polo State")
    lines.append("")
    lines.append(f"Project: {project_rel}")
    lines.append(f"Last run: {run_rel}")
    lines.append("")

    lines.append("## OPEN")
    lines.append("")
    any_open = False
    for thread_id, title in threads:
        items = open_by_thread.get(thread_id, [])
        if not items:
            continue
        any_open = True
        lines.append(f"### {title}")
        lines.append("")
        for item in items:
            lines.append(f"- {item}")
        lines.append("")
    if not any_open:
        lines.append("(none)")
        lines.append("")

    if include_prop:
        lines.append("## PROP")
        lines.append("")
        any_prop = False
        for thread_id, title in threads:
            items = prop_by_thread.get(thread_id, [])
            if not items:
                continue
            any_prop = True
            lines.append(f"### {title}")
            lines.append("")
            for item in items:
                lines.append(f"- {item}")
            lines.append("")
        if not any_prop:
            lines.append("(none)")
            lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def cmd_propagate(args: argparse.Namespace) -> int:
    intake_dir = Path(args.intake)
    project_dir = _resolve_project_dir(args.project)

    if not intake_dir.exists():
        raise SystemExit(f"missing intake dir: {intake_dir}")
    if not project_dir.exists():
        raise SystemExit(f"missing project dir: {project_dir}")

    marco_path = (intake_dir / args.marco).resolve()
    polo_path = (intake_dir / args.polo).resolve()

    if not marco_path.exists():
        raise SystemExit(f"missing marco file: {marco_path}")
    if not polo_path.exists():
        raise SystemExit(f"missing polo file: {polo_path}")

    # Airlock: overwrite in place to guarantee ASCII-only substrate.
    airlock_reports: dict[str, dict] = {}
    for p in (marco_path, polo_path):
        airlock_reports[str(p)] = _airlock_overwrite_in_place(
            p, repair_common_punct=bool(args.repair_common_punct)
        )

    # Create run folder under the writeOS project.
    stamp = _utc_stamp()
    outputs_dir = project_dir / "outputs"
    runs_dir = outputs_dir / "runs" / stamp
    runs_dir.mkdir(parents=True, exist_ok=True)

    # Copy inputs into the run folder for provenance.
    shutil.copy2(marco_path, runs_dir / "marco.md")
    shutil.copy2(polo_path, runs_dir / "polo_typed.md")

    # Parse typed POLO deterministically.
    extract = _load_marcopolo_extract_module()
    polo_text = _read_text(runs_dir / "polo_typed.md")
    units = extract.extract_polo_units(polo_text)

    if not units:
        raise SystemExit("no typed POLO units found (expected SRC/OPEN/PROP lines)")

    # Write units JSONL (portable evidence).
    units_path = runs_dir / "polo_units.jsonl"
    with units_path.open("w", encoding="utf-8", newline="\n") as f:
        for u in units:
            f.write(json.dumps({
                "id": u.id,
                "kind": u.kind,
                "thread_id": u.thread_id,
                "text": u.text,
                "fingerprint": u.fingerprint,
            }) + "\n")

    # Build thread titles and OPEN/PROP lists.
    thread_titles: dict[str, str] = {}
    threads_order: list[str] = []
    open_by_thread: dict[str, list[str]] = {}
    prop_by_thread: dict[str, list[str]] = {}

    for u in units:
        if u.kind == "thread":
            thread_titles[u.thread_id] = u.text
            if u.thread_id not in threads_order:
                threads_order.append(u.thread_id)
            continue

        if u.kind == "open":
            open_by_thread.setdefault(u.thread_id, []).append(u.text)
        elif u.kind == "prop":
            prop_by_thread.setdefault(u.thread_id, []).append(u.text)

    threads: list[tuple[str, str]] = []
    for tid in threads_order:
        threads.append((tid, thread_titles.get(tid, tid)))

    # Write propagation report.
    report_lines: list[str] = []
    report_lines.append("# Propagation report")
    report_lines.append("")
    report_lines.append(f"Run: {stamp}")
    report_lines.append(f"Intake: {intake_dir}")
    report_lines.append("")
    report_lines.append(f"Typed units: {len(units)}")
    report_lines.append(f"OPEN units: {sum(len(v) for v in open_by_thread.values())}")
    report_lines.append(f"PROP units: {sum(len(v) for v in prop_by_thread.values())}")
    report_lines.append(f"State includes PROP: {bool(args.include_prop)}")
    report_lines.append("")
    report_lines.append("## Airlock")
    report_lines.append("")
    report_lines.append(json.dumps(airlock_reports, indent=2))
    report_lines.append("")
    _write_text(runs_dir / "propagation_report.md", "\n".join(report_lines).rstrip() + "\n")

    # Update rolling state file.
    project_rel = os.path.relpath(project_dir, ATLAS_ROOT).replace("\\", "/")
    run_rel = os.path.relpath(runs_dir, ATLAS_ROOT).replace("\\", "/")

    state_md = _render_state_md(
        project_rel=project_rel,
        run_rel=run_rel,
        threads=threads,
        open_by_thread=open_by_thread,
        prop_by_thread=prop_by_thread,
        include_prop=bool(args.include_prop),
    )

    state_path = outputs_dir / "state.md"
    _write_text(state_path, state_md)

    # Append admission record.
    admissions_path = project_dir / "logs" / "admissions.jsonl"
    admissions_path.parent.mkdir(parents=True, exist_ok=True)

    record = {
        "ts": stamp,
        "project": project_rel,
        "intake": str(intake_dir).replace("\\", "/"),
        "marco": str(marco_path).replace("\\", "/"),
        "polo": str(polo_path).replace("\\", "/"),
        "run": run_rel,
        "include_prop": bool(args.include_prop),
        "repair_common_punct": bool(args.repair_common_punct),
        "artifacts": {
            "polo_typed": os.path.relpath(runs_dir / "polo_typed.md", ATLAS_ROOT).replace("\\", "/"),
            "polo_units": os.path.relpath(units_path, ATLAS_ROOT).replace("\\", "/"),
            "report": os.path.relpath(runs_dir / "propagation_report.md", ATLAS_ROOT).replace("\\", "/"),
            "state": os.path.relpath(state_path, ATLAS_ROOT).replace("\\", "/"),
        },
        "not_activated": ["todos", "cross-project mutations"],
    }

    with admissions_path.open("a", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps(record) + "\n")

    # Print short operator summary.
    state_rel = os.path.relpath(state_path, ATLAS_ROOT).replace("\\", "/")
    admissions_rel = os.path.relpath(admissions_path, ATLAS_ROOT).replace("\\", "/")
    sys.stdout.write(f"OK: wrote run artifacts to {run_rel}\n")
    sys.stdout.write(f"OK: updated state file {state_rel}\n")
    sys.stdout.write(f"OK: appended admission record {admissions_rel}\n")

    return 0


def main() -> int:
    p = argparse.ArgumentParser(prog="marcopolo-atlas")
    sub = p.add_subparsers(dest="cmd", required=True)

    pp = sub.add_parser("propagate", help="propagate approved typed POLO into state")
    pp.add_argument("--project", required=True, help="e.g. writeOS/marco-polo")
    pp.add_argument("--intake", default=str(DEFAULT_INTAKE))
    pp.add_argument("--marco", required=True, help="filename inside intake")
    pp.add_argument("--polo", required=True, help="filename inside intake")
    pp.add_argument("--include-prop", action="store_true", help="include PROP items in state.md")
    pp.add_argument("--repair-common-punct", action="store_true", default=False)
    pp.set_defaults(func=cmd_propagate)

    args = p.parse_args()
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())
