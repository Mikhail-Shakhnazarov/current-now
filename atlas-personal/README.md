# Atlas

A context engineering system for complex work with LLM runtimes.

---

## Structure

```
atlas-personal/
|-- desk/                    # Operating infrastructure
|   |-- core/
|   |   |-- kernel.md        # Constitutional constraints
|   |   `-- schemas/         # Validation contracts
|   |-- protocols/           # Loadable context for roles
|   |-- projections/         # Context assembly rules
|   |-- patterns/            # Accumulated knowledge
|   `-- specialties/         # Domain extensions
|
|-- work/                    # Portable work artifacts
|   |-- projects/            # Active projects
|   |-- sessions/            # Compressed history
|   |-- friction/            # Blocked states
|   `-- logs/                # Execution history
|
`-- docs/                    # Human-facing documentation
    |-- doctrine.md          # Principles explained
    |-- reflections.md       # Philosophy and assumptions
    `-- theory/              # Academic treatment
```

## Quick Start

1. Load `desk/core/kernel.md` -- constitutional constraints
2. Load `desk/protocols/interpreter.md` or `desk/protocols/executor.md` -- role framing
3. Assemble projection per `desk/projections/*.md` -- context sandwich
4. Call model with assembled context
5. Validate output against `desk/core/schemas/*.json`
6. If valid, commit to `work/`

## Key Concepts

**Projection**: Transform file state into bounded context window. The projection shapes model behavior.

**Sandwich structure**: Kernel constraints at boundaries (high attention). Payload in middle. Schema at end. Bounds generation space.

**Schema validation**: Every model output validates before commit. Invalid output returns with explicit violations.

**Role separation**: Interpreter uses broad context for meaning work. Executor uses narrow context for literal application. Different projections, different behaviors.

**Operator authority**: Models propose transformations. Operator authorizes commits. Nothing changes state without review.

## Specialties

- **devOS**: Code-focused extensions -- bug patterns, idioms, clean export
- **writeOS**: Text-focused extensions -- semantic schemas, transforms, meaning preservation

## License

Dual-licensed (see `NOTICE.txt`):
- Code/templates: MIT (`LICENSE`)
- Writings/other artifacts: CC BY 4.0 (`LICENSE-CC-BY-4.0.txt`)
