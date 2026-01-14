from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

from .util import airlock_text
from .extract import extract_marco_spans, extract_polo_units, write_spans_jsonl, write_units_jsonl
from .match import match_units_to_spans, write_edges_jsonl
from .verify import compute_report
from .draft import draft_polo_from_marco

def _load_cfg(cfg_path: str | None) -> dict:
    if cfg_path is None:
        here = Path(__file__).resolve().parents[3]
        default_path = here / "config" / "defaults.json"
        with open(default_path, "r", encoding="utf-8") as f:
            return json.load(f)
    with open(cfg_path, "r", encoding="utf-8") as f:
        return json.load(f)

def cmd_airlock(args: argparse.Namespace) -> int:
    out = {"files": {}}
    ok = True
    for p in args.paths:
        with open(p, "r", encoding="utf-8") as f:
            raw = f.read()
        fixed, rep = airlock_text(raw, repair_common_punct=args.repair_common_punct)
        out["files"][p] = rep
        if fixed is None:
            ok = False
    out["ascii_ok"] = ok
    os.makedirs(args.out, exist_ok=True)
    with open(os.path.join(args.out, "airlock_report.json"), "w", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps(out, indent=2) + "\n")
    return 0 if ok else 2

def cmd_verify(args: argparse.Namespace) -> int:
    cfg = _load_cfg(args.config)

    with open(args.marco, "r", encoding="utf-8") as f:
        marco_raw = f.read()
    with open(args.polo, "r", encoding="utf-8") as f:
        polo_raw = f.read()

    marco_txt, rep_m = airlock_text(marco_raw, repair_common_punct=args.repair_common_punct)
    polo_txt, rep_p = airlock_text(polo_raw, repair_common_punct=args.repair_common_punct)
    if marco_txt is None or polo_txt is None:
        os.makedirs(args.out, exist_ok=True)
        with open(os.path.join(args.out, "airlock_report.json"), "w", encoding="utf-8", newline="\n") as f:
            f.write(json.dumps({"marco": rep_m, "polo": rep_p}, indent=2) + "\n")
        return 2

    spans = extract_marco_spans(marco_txt)
    units = extract_polo_units(polo_txt)

    edges, candidates = match_units_to_spans(
        spans, units,
        match_min=float(cfg.get("match_min", 0.22)),
        top_k=5
    )

    report_obj, report_md = compute_report(spans, units, edges, candidates, cfg)

    os.makedirs(args.out, exist_ok=True)
    write_spans_jsonl(spans, os.path.join(args.out, "marco_spans.jsonl"))
    write_units_jsonl(units, os.path.join(args.out, "polo_units.jsonl"))
    write_edges_jsonl(edges, os.path.join(args.out, "trace_edges.jsonl"))
    with open(os.path.join(args.out, "verify_report.json"), "w", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps(report_obj, indent=2) + "\n")
    with open(os.path.join(args.out, "verify_report.md"), "w", encoding="utf-8", newline="\n") as f:
        f.write(report_md)

    return 0

def cmd_draft(args: argparse.Namespace) -> int:
    cfg = _load_cfg(args.config)

    with open(args.marco, "r", encoding="utf-8") as f:
        marco_raw = f.read()

    marco_txt, rep = airlock_text(marco_raw, repair_common_punct=args.repair_common_punct)
    if marco_txt is None:
        os.makedirs(args.out, exist_ok=True)
        with open(os.path.join(args.out, "airlock_report.json"), "w", encoding="utf-8", newline="\n") as f:
            f.write(json.dumps({"marco": rep}, indent=2) + "\n")
        return 2

    spans = extract_marco_spans(marco_txt)
    polo_draft = draft_polo_from_marco(spans)

    units = extract_polo_units(polo_draft)
    edges, candidates = match_units_to_spans(
        spans, units,
        match_min=float(cfg.get("match_min", 0.22)),
        top_k=5
    )
    report_obj, report_md = compute_report(spans, units, edges, candidates, cfg)

    os.makedirs(args.out, exist_ok=True)
    with open(os.path.join(args.out, "polo_draft.md"), "w", encoding="utf-8", newline="\n") as f:
        f.write(polo_draft)

    write_spans_jsonl(spans, os.path.join(args.out, "marco_spans.jsonl"))
    write_units_jsonl(units, os.path.join(args.out, "polo_units.jsonl"))
    write_edges_jsonl(edges, os.path.join(args.out, "trace_edges.jsonl"))
    with open(os.path.join(args.out, "verify_report.json"), "w", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps(report_obj, indent=2) + "\n")
    with open(os.path.join(args.out, "verify_report.md"), "w", encoding="utf-8", newline="\n") as f:
        f.write(report_md)

    return 0

def main() -> None:
    p = argparse.ArgumentParser(prog="marcopolo")
    sub = p.add_subparsers(dest="cmd", required=True)

    pa = sub.add_parser("airlock", help="ASCII admission check (optional repair)")
    pa.add_argument("paths", nargs="+")
    pa.add_argument("--repair-common-punct", action="store_true")
    pa.add_argument("--out", default="out")
    pa.set_defaults(func=cmd_airlock)

    pv = sub.add_parser("verify", help="Verify MARCO/POLO pair (trace + graded report)")
    pv.add_argument("marco")
    pv.add_argument("polo")
    pv.add_argument("--repair-common-punct", action="store_true")
    pv.add_argument("--config", default=None)
    pv.add_argument("--out", default="out")
    pv.set_defaults(func=cmd_verify)

    pd = sub.add_parser("draft", help="Draft POLO from MARCO (conservative) + verify draft")
    pd.add_argument("marco")
    pd.add_argument("--repair-common-punct", action="store_true")
    pd.add_argument("--config", default=None)
    pd.add_argument("--out", default="out")
    pd.set_defaults(func=cmd_draft)

    args = p.parse_args()
    raise SystemExit(args.func(args))

if __name__ == "__main__":
    main()
