# Template: writeOS Project Wrapper

Purpose: create a system wrapper for a text transformation pipeline.

## Target Location

Create at:
- `atlas-personal/work/projects/writeOS/<project>/`

## Minimum Wrapper Folders

- `now.md`
- `specs/` (transform specs)
- `drafts/` (raw input)
- `schemas/` (extracted structure)
- `outputs/` (final generated forms)
- `logs/changelog.md`
- `.atlas/version`

## Starter now.md

```
# Now: <project>

## Current State

- Project initialized with `drafts/`, `schemas/`, and `outputs/`.

## Next

1. Add raw material to `drafts/`.
2. Interpret into a spec and schema.
3. Execute transform into `outputs/`.
4. Record results in `logs/changelog.md`.
```

## Starter .atlas/version

```
2026-01-13
```
