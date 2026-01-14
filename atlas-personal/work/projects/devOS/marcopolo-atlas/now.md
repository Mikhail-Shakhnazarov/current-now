# Now: marcopolo-atlas

## Current State

In-house tooling copy of the standalone `devOS/marcopolo` repository.

- Standalone repo (keep pristine): `work/projects/devOS/marcopolo/repo/`
- In-house fork for Atlas integration: `work/projects/devOS/marcopolo-atlas/repo/`

## Intent

Provide Atlas-specific glue as deterministic tooling:

- Root-invoked operator CLI to run airlock admission (overwrite in place) and generate typed POLO artifacts.
- Project-local output placement conventions for writeOS projects.
- Keep behavior strict by default and non-activating (anti-spam).

## Next

Define the v1 CLI contract (command name and flags) and wire it to `writeOS/marco-polo/`.
