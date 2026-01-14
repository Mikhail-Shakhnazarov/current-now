# Architecture (v2)

Atlas TUI v2 is a chat-first terminal cockpit that operates only on the repository it is launched from.

The operator types messages into a chat UI. The message is not sent directly to a model provider. Instead, a long-lived engine subprocess assembles the concrete provider request payload. In v2, provider API calls are intentionally out of scope; the focus is making context assembly inspectable and repeatable.

The architecture is split into three components.

The TUI component owns terminal rendering, chat UX, mode/provider/model selection, and displaying repo and project state.

The engine component owns deterministic context assembly and provider request construction, exposed via a JSONL stdin/stdout protocol so that the UI stays thin and the engine can evolve toward a daemon later.

The documents component packages Atlas-specific templates that are loaded by the engine. This includes kernel constraints, role framing protocols, projections, and output schemas.

In the current codebase these components map to:

The TUI component is `src/atlas_tui/ui/app.py` and `src/atlas_tui/ui/widgets.py`.

The engine boundary is `src/atlas_tui/engine_client.py` and the default local engine is `src/atlas_tui/dummy_engine.py`.

Bundled documents are `src/atlas_tui/assets/atlas/` and are included as package data.

## Modes

Interpret mode exists for converting messy input into structured artifacts.

Plan mode exists for scoping and phased plan generation.

Execute mode exists for applying repo changes against a spec and verifying results.

In v2, modes primarily affect which protocol and projection templates are loaded by the engine. Automatic execution and verification are deferred.

## Inspection logs

Every submit writes a deterministic assembled-context log file.

If an Atlas wrapper exists, logs are written under `<project_root>/logs/atlas-tui/`.

If no wrapper exists, logs are written under `<repo_root>/.atlas-tui/logs/`.
