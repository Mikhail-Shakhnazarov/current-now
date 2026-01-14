# Now: marco-polo

## Current State

writeOS pilot project.

Inputs are copied into `drafts/`:
- `drafts/marco.md` (operator note)
- `drafts/polo.md` (derived breakdown)

## Intent

Work on the semantic relationship between marco and polo:
- Evaluate mapping fidelity (coverage, non-invention, decomposition quality)
- Define an analysis workflow that can become tooling (subsidiarity)

## Next

1. Work from `specs/SPEC-001.md` (design question).
2. Start from `inbox-airlock/operator-obsidian-render/marcopolo-intake/MARCO_TEMPLATE.md`, then generate a typed POLO in Obsidian and drop it in `inbox-airlock/operator-obsidian-render/marcopolo-intake/`.
3. Run propagation from root: `python atlas-personal/desk/tools/marcopolo_atlas.py propagate --project writeOS/marco-polo --marco <file> --polo <file> [--include-prop]`.
4. Read the rolling state at `outputs/state.md`.

## v2

See `outputs/challenge.md` for the portable challenge statement with acceptance criteria.
