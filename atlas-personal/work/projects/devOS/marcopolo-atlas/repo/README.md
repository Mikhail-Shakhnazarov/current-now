# Marco-Polo

Trace-first verification and conservative preprocessing for MARCO/POLO pairs.

MARCO is operator signal (a high-throughput note). POLO is a stabilized projection (threads, OPEN questions, and non-binding routing proposals). The core primitive is a trace graph: typed edges that link POLO units back to MARCO spans. This makes verification graded and explainable by construction.

This repository is intended to stand alone: any developer can run it without needing Atlas.

## Guarantees (v1)

ASCII-only admission is strict by default. Verification and drafting are deterministic and conservative. No activation happens by default: outputs are staged artifacts only (no task creation, no state mutation).

## Concepts

Typed POLO is the deterministic interface.

POLO lines are typed:

SRC: grounded paraphrase or quote of MARCO (expects strong trace support)
OPEN: a decision/question required (expects trace to explicit ambiguity markers)
PROP: a non-binding suggestion (allowed but must be labeled and trace-linked)

See `docs/SPEC_PACK_V0.md` for the artifact formats and rules.

## Installation

Python 3.10+ recommended.

Option A (editable install):

pip install -e .

Option B (requirements file):

pip install -r requirements.txt

## Quick start

Draft POLO from MARCO (writes outputs under `out/`):

python -m marcopolo.cli draft examples/marco.md --out out

Verify a MARCO/POLO pair:

python -m marcopolo.cli verify examples/marco.md examples/polo.md --out out

Run airlock admission check (writes `airlock_report.json`):

python -m marcopolo.cli airlock examples/marco.md examples/polo.md --out out

## Outputs

The CLI produces portable artifacts suitable for audit and downstream tooling:

marco_spans.jsonl: segmented MARCO spans
polo_units.jsonl: typed POLO units
trace_edges.jsonl: typed edges PoloUnit -> MarcoSpan with scores
verify_report.md / verify_report.json: graded verification report
polo_draft.md: conservative draft generated from MARCO

## Development

Run tests:

python -m pytest

See also:

- `docs/PROJECT_PROPOSAL.md`
- `docs/SPEC_PACK_V0.md`
- `docs/TRACE_GRAPH_PRIMER.md`

## License

MIT. See `LICENSE`.

Copyright (c) 2026 Mikhail Shakhnazarov.
