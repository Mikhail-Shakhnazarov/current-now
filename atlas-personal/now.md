# Now (Atlas Personal)

Operator: Mikhail Shakhnazarov
Year: 2026

## Boot Hot Set

- Kernel: `desk/core/kernel.md`
- Protocols: `desk/protocols/interpreter.md`, `desk/protocols/executor.md`
- Projections: `desk/projections/interpret.md`, `desk/projections/execute.md`
- OpenCode projections: `desk/projections/interpret-opencode.md`, `desk/projections/execute-opencode.md`
- Schemas: `desk/core/schemas/`
- Hygiene: `desk/tools/repo_hygiene.py`
  - Note: repo hygiene is preparation for the tooling layer (operator CLI triggers) so interpreter models do not spend tool calls on substrate enforcement.

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

Style preference: avoid first person ("I", "we") and second person ("you") in chat outputs and written artifacts; prefer neutral phrasing.

Formalize what makes a "good repo" for subprojects: standalone README, license/authorship, reproducible CLI usage, and a minimal test command.

Consider a RAG-ready context pack for each repo/project (structured, portable summaries and key artifacts) that can be dropped into tools like NotebookLM. This is tracked in `work/projects/devOS/intake-pipeline/` (pair ledger is part of this).

Consider explicit two-step sequential processing with a handoff point (plan/interpret -> agentic/execute), designed so work can be parallelized where safe. The key is to make plans and artifacts optimized for parallel execution (independent threads, clear boundaries, deterministic propagation). This is tracked in `work/projects/devOS/intake-pipeline/`.

## Themes (Throttled)

Publishable components: `work/projects/devOS/marcopolo/` (standalone demo), `work/projects/devOS/marcopolo-atlas/` (in-house glue), `work/projects/devOS/intake-pipeline/` (pipeline proposal).

System imaging: stub pending (target: `work/projects/devOS/system-imaging/`).

Multimodal coherence: stub pending (target: `work/projects/writeOS/multimodal-binding/`).

Patreon: planning thread (no project stub yet).

Throttling and promotion rules belong to `work/projects/devOS/intake-pipeline/`. These theme lines should always carry an owner path or a stub target so re-entry is immediate.

## Preflight

- Run: `python atlas-personal/desk/tools/repo_hygiene.py --check`
