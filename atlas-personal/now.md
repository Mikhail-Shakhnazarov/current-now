# Now (Atlas Personal)

Operator: Mikhail Shakhnazarov
Year: 2026

## Boot Hot Set

- Kernel: `desk/core/kernel.md`
- Protocols: `desk/protocols/interpreter.md`, `desk/protocols/executor.md`
- Projections: `desk/projections/interpret.md`, `desk/projections/execute.md`
- OpenCode projections: `desk/projections/interpret-opencode.md`, `desk/projections/execute-opencode.md`
- Schemas: `desk/core/schemas/`
- Hygiene: `desk/tools/ascii_hygiene.py`

## Work Surfaces

- Work now: `work/now.md`
- Global changelog: `work/logs/changelog.md`
- Global friction: `work/friction/log.md`
- Projects index: `work/projects/INDEX.md`

## Today

- Review `work/friction/log.md`
- Pick one active project and open its `now.md`
- Continue: `work/projects/writeOS/marco-polo/now.md`
- If starting new work: interpret operator input into a spec

## Design Principle (Stub)

Prefer slow communication: when operator input is messy or multi-threaded, convert it into durable artifacts (breakdowns, threads, OPEN items) and keep chat output short and scannable. Over time, this becomes tooling surfaces (dashboard: when input arrived, what files were written/updated).

## Preflight

- Run: `python atlas-personal/desk/tools/ascii_hygiene.py --check`
