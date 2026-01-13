# Template: devOS Project Wrapper

Purpose: create a system wrapper around a client-facing code repo.

## Target Location

Create at:
- `atlas-personal/work/projects/devOS/<project>/`

Keep the client repo inside:
- `atlas-personal/work/projects/devOS/<project>/repo/`

## Minimum Wrapper Files

- `now.md`
- `specs/SPEC-001.md` (or next spec)
- `logs/changelog.md`
- `.atlas/version`
- `repo/` (client-facing repo; keep clean)

## Starter now.md

```
# Now: <project>

## Current State

- Wrapped project with clean client repo at `repo/`.

## Next

1. Write or select next spec in `specs/`.
2. Execute spec with the executor projection.
3. Record results in `logs/changelog.md`.
```

## Starter .atlas/version

```
2026-01-13
```

## Notes

- Specs and logs do not live inside `repo/`.
- Keep `repo/` exportable as a standalone repository.
