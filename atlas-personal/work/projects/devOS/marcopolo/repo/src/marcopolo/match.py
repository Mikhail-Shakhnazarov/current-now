from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Dict, List, Tuple

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from .extract import Span, Unit
from .util import normalize_ascii

REL_BY_KIND = {
    "src": "supports",
    "open": "unanswered",
    "prop": "proposes",
    "thread": "mentions",
}

@dataclass
class Edge:
    polo_id: str
    marco_id: str
    rel: str
    score: float
    features: Dict[str, float]
    rationale: str

def _tokens(s: str) -> List[str]:
    s = normalize_ascii(s).lower()
    cleaned = "".join([ch if ch.isalnum() else " " for ch in s])
    return [t for t in cleaned.split() if len(t) >= 3]

def match_units_to_spans(
    spans: List[Span],
    units: List[Unit],
    match_min: float = 0.22,
    top_k: int = 5,
) -> Tuple[List[Edge], Dict[str, List[Tuple[str, float]]]]:
    span_texts = [sp.text for sp in spans]
    unit_texts = [u.text for u in units]

    if not span_texts or not unit_texts:
        return [], {}

    vec = TfidfVectorizer(lowercase=True, stop_words="english")
    X = vec.fit_transform(span_texts)
    Y = vec.transform(unit_texts)

    sims = cosine_similarity(Y, X)  # (units, spans)

    edges: List[Edge] = []
    candidates: Dict[str, List[Tuple[str, float]]] = {}

    for ui, u in enumerate(units):
        row = sims[ui]
        idxs = np.argsort(-row)[:top_k]
        cand = [(spans[i].id, float(row[i])) for i in idxs]
        candidates[u.id] = cand

        best_id, best_score = cand[0]
        if best_score < match_min:
            continue

        rel = REL_BY_KIND.get(u.kind, "mentions")

        ut = set(_tokens(u.text))
        st = set(_tokens(spans[int(idxs[0])].text))
        shared = sorted(list(ut.intersection(st)))[:6]
        rationale = "shared:" + (",".join(shared) if shared else "(none)")

        edges.append(Edge(
            polo_id=u.id,
            marco_id=best_id,
            rel=rel,
            score=best_score,
            features={"tfidf_cosine": best_score},
            rationale=rationale,
        ))

    return edges, candidates

def write_edges_jsonl(edges: List[Edge], path: str) -> None:
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        for e in edges:
            f.write(json.dumps({
                "polo_id": e.polo_id,
                "marco_id": e.marco_id,
                "rel": e.rel,
                "score": e.score,
                "features": e.features,
                "rationale": e.rationale,
            }) + "\n")
