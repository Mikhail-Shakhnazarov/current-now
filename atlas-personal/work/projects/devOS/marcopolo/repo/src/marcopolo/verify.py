from __future__ import annotations

from typing import Dict, List, Tuple

from .extract import Span, Unit
from .match import Edge

def _label_for(conf: float, bands: List[dict]) -> str:
    for b in bands:
        if conf >= b["min"] and conf < b["max"]:
            return b["label"]
    if bands and conf >= bands[-1]["min"]:
        return bands[-1]["label"]
    return "unknown"

def compute_report(
    spans: List[Span],
    units: List[Unit],
    edges: List[Edge],
    candidates_by_unit: Dict[str, List[Tuple[str, float]]],
    cfg: dict,
) -> Tuple[dict, str]:
    match_min = float(cfg.get("match_min", 0.22))
    eps = float(cfg.get("ambiguity_epsilon", 0.03))
    w = cfg.get("weights", {"coverage":0.55,"novelty":0.25,"ambiguity":0.15,"prop_ratio":0.05})
    bands = cfg.get("labels", [{"label":"low","min":0.0,"max":0.5},{"label":"medium","min":0.5,"max":0.8},{"label":"high","min":0.8,"max":1.0}])

    edge_by_polo = {e.polo_id: e for e in edges}
    referenced_marco = set(e.marco_id for e in edges if e.score >= match_min)
    coverage = (len(referenced_marco) / len(spans)) if spans else 0.0

    typed_units = [u for u in units if u.kind in ("src", "open", "prop")]
    unsupported_units = [u for u in typed_units if u.id not in edge_by_polo]

    novelty_score = 1.0 - (len(unsupported_units) / (len(typed_units) or 1))

    ambiguous = []
    for u in typed_units:
        cand = candidates_by_unit.get(u.id, [])
        if len(cand) >= 2 and cand[0][1] >= match_min:
            if abs(cand[0][1] - cand[1][1]) <= eps:
                ambiguous.append((u, cand[0], cand[1]))
    ambiguity_score = 1.0 - (len(ambiguous) / (len(typed_units) or 1))

    prop_units = [u for u in typed_units if u.kind == "prop"]
    prop_ratio = (len(prop_units) / (len(typed_units) or 1))
    prop_ratio_score = 1.0 - prop_ratio

    conf = (
        w.get("coverage", 0.55) * coverage +
        w.get("novelty", 0.25) * novelty_score +
        w.get("ambiguity", 0.15) * ambiguity_score +
        w.get("prop_ratio", 0.05) * prop_ratio_score
    )
    conf = max(0.0, min(1.0, conf))
    label = _label_for(conf, bands)

    report_obj = {
        "coverage": coverage,
        "unsupported_units": [u.id for u in unsupported_units],
        "unreferenced_spans": [sp.id for sp in spans if sp.id not in referenced_marco],
        "ambiguous_units": [u.id for u, _, _ in ambiguous],
        "prop_ratio": prop_ratio,
        "confidence": conf,
        "label": label,
        "params": {"match_min": match_min, "ambiguity_epsilon": eps, "weights": w, "labels": bands},
    }

    md = []
    md.append("# Verification report")
    md.append("")
    md.append(f"- Coverage: {coverage:.3f} ({len(referenced_marco)}/{len(spans)})")
    md.append(f"- Unsupported POLO units: {len(unsupported_units)}")
    md.append(f"- Ambiguous POLO units: {len(ambiguous)} (eps={eps})")
    md.append(f"- PROP ratio: {prop_ratio:.3f} ({len(prop_units)}/{len(typed_units)})")
    md.append("")
    md.append(f"## Confidence: {conf:.3f} ({label})")
    md.append("")
    md.append("## Unsupported units")
    if unsupported_units:
        for u in unsupported_units:
            md.append(f"- {u.id} [{u.kind.upper()}]: {u.text}")
    else:
        md.append("- (none)")
    md.append("")
    md.append("## Unreferenced MARCO spans")
    unref = [sp for sp in spans if sp.id not in referenced_marco]
    if unref:
        for sp in unref[:50]:
            excerpt = sp.text.replace("\n", " ")
            if len(excerpt) > 140:
                excerpt = excerpt[:140] + "..."
            md.append(f"- {sp.id} [{sp.kind}]: {excerpt}")
    else:
        md.append("- (none)")
    md.append("")
    md.append("## Ambiguities (top-2 candidates)")
    if ambiguous:
        for u, c1, c2 in ambiguous:
            md.append(f"- {u.id} [{u.kind.upper()}]: {u.text}")
            md.append(f"  - cand1: {c1[0]} score={c1[1]:.3f}")
            md.append(f"  - cand2: {c2[0]} score={c2[1]:.3f}")
    else:
        md.append("- (none)")

    return report_obj, "\n".join(md) + "\n"
