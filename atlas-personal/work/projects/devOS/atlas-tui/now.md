# Now: atlas-tui

## Current State

Project stub created.

This is intended as a clean, exportable devOS client-facing repository for an Atlas TUI.

## Intent

Provide a terminal UI that makes re-entry and project switching easy. The tui should be oriented as a specifically repo-management tool. Role separation between interpreter/executor can be similar to the build/plan mode switch in opencode/claude code/other tui apps. User should be able to use anthropic/OpenAI subscripitions (plus/pro) in addition to regular API key workflow. The backend processing is where the magic happens - we process and package context in teh background using the compaction and context assemoby methods that the atlas system itsel fuses. WriteOS text transform functionality is explicitly out of scope for client-facing features here, even if the logic exists in the project, we make no mention of that. Text transform will be a future add-on.

Scope emphasis (v1): project navigation, state inspection, and deterministic command triggers.

WriteOS remains internal initially.

## Links

- Intake pipeline proposal: `work/projects/devOS/intake-pipeline/specs/SPEC-001.md`
- Compaction pattern: `work/projects/devOS/compaction/specs/SPEC-001.md`

## Next

1. Define v1 features and boundaries.
2. Choose stack (Python textual vs Rust ratatui vs other).
3. Draft a minimal CLI/TUI integration plan.
