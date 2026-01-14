# Trace Graph Primer

Marco-Polo verification reduces to a trace graph:

- MarcoSpan: a unit of operator signal.
- PoloUnit: a unit of stabilized projection.
- Edge: a typed link PoloUnit -> MarcoSpan with a score and rationale.

Why this matters:
- Coverage becomes measurable: which signal spans are represented.
- Novelty becomes detectable: which projection units lack support.
- Ambiguity becomes visible: which mapping is unclear.

How to read the report:
- Start with coverage: missing spans are drift risk.
- Inspect unsupported POLO units: either add support or retype as PROP.
- Resolve ambiguities by splitting/clarifying units or tightening parameters.

Edges are evidence, not authority. Authority remains with the operator via explicit promotion.
