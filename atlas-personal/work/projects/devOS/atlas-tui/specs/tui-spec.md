# Atlas TUI: TUI Component Handoff Spec (v2)

Status: draft
Date: 2026-01-14
Owner: devOS/atlas-tui

## Purpose

Define the standalone TUI component requirements for Atlas TUI v2.

This document is a handoff spec for implementing the terminal UI layer as an isolated deliverable. The TUI must remain thin: it owns rendering, input handling, and user-facing state, while delegating context assembly and model-request construction to an engine boundary.

## Product definition

Atlas TUI is a chat-first terminal application for working inside a single repository. The app is launched from anywhere inside the target repo, discovers the correct roots, and provides an operator cockpit that combines chat with repo and project state visibility.

Model providers (OpenAI, Anthropic) and a mode switch (interpret/plan/execute) exist as first-class UI controls. Mode is not cosmetic: it changes what context the engine assembles and what output contract is expected.

The v2 goal is verification of context assembly. Real API calls, streaming responses, and automated execution remain out of scope for the TUI handoff.

## Key constraints

The managed repository must remain clean. Persistent system artifacts must be written outside the repo when an Atlas project wrapper exists, or into a single well-scoped local state directory when no wrapper exists.

The UI must be usable with keyboard only and must remain responsive while background work runs.

## Outputs (three facets)

The UI surface is defined around three concurrent output facets.

Chat is the primary interaction surface. It shows the conversational transcript and user inputs. Let there be a toggle to log the chat transcript (including model "thoughts") to a log file or files (tbd), but logging is important here. Logs are data and may reveal useful patterns. 

Repo state and health is a continuously visible indication of what is happening in the managed repository. This includes a tree view and basic health signals.

Project state is the Atlas wrapper surface area: now.md visibility, active specs, open items, and recent logs.

## Screen layout (first pass)

A minimal but complete layout is a three-panel screen.

Left panel: repository tree and repo health summary.

Center panel: chat transcript (scrollable) and message composer.

Right panel: project state and engine inspection signals.

A compact top bar provides mode selection, provider selection, and model selection, plus a visible workspace indicator (repo root and project root if discovered).

A bottom status bar shows transient status (busy/idle), last action, and last log path.

## Workspace discovery and identity

The TUI must compute a Workspace object at startup.

If an Atlas project wrapper root is discovered (directory containing now.md, specs/, logs/, .atlas/version, and repo/), it becomes the authoritative project root, and the managed repo root is project_root/repo.

If no wrapper exists, the managed repo root is the nearest .git root. Project root is None.

The computed roots must be visible in the UI.

## Core user flows

### Flow A: send message and inspect assembled context

The operator enters a message in the composer and submits.

The UI packages an EngineInput with current mode, provider, model, workspace roots, and the user message.

The engine returns an AssembledContext and a ProviderRequest.

The UI writes a context log entry to disk for inspection.

The UI displays the log path and a short, safe preview indicator (system length and a truncated preview) without dumping large blobs into the chat pane.

No provider network request is performed in this flow.

### Flow B: mode and model switching

Switching mode updates the visible mode label and the short mode description.

Switching provider updates the available model choices and default model value.

Mode changes must not mutate any repo files by themselves.

### Flow C: inspect repo tree and repo health

The repo tree reflects the current filesystem state of the managed repo.

A refresh mechanism exists (manual keybind and optional auto-refresh) so changes are visible during work.

Repo health indicators for v2 are informational only. Examples: dirty status, last modified files count, and presence of expected project wrapper folders. These metrics will be provided by the atlas engine, so no evaluation is necessary in the TUI component.

### Flow D: inspect project state

If a project wrapper exists, the TUI can show now.md, active specs list, and recent project logs.

If no wrapper exists, project state is reduced to a minimal placeholder indicating wrapper is absent. Add basic trigger to build up atlas scaffolding - just a button with an output. We will then make that actionable via atlas engine tooling, automatic root buildup is easy.

## Interaction model

Keyboard shortcuts must be defined and displayed via a help overlay.

The input focus model must be predictable: chat composer is default focus; panel focus switches via shortcuts.

Scrolling and selection must not block background work.

## Engine boundary contract (TUI-facing)

The TUI must not assemble prompts itself.

A single entry function is sufficient for v2: submit EngineInput and receive EngineOutput.

EngineInput fields required for v2:

- workspace.repo_root
- workspace.project_root (optional)
- mode (interpret/plan/execute)
- provider (openai/anthropic)
- model
- user_message
- optional ui_state metadata (focused file path, selection hints)

EngineOutput fields required for v2:

- assembled_context.system (large string)
- assembled_context.mode
- provider_request (system + user + model + provider)
- optional diagnostics (sizes, selected artifacts list) as structured data

The TUI owns writing the inspection log file, unless the engine explicitly owns that responsibility in the current implementation.

## Logging and inspection requirements

Every message submission in v2 must produce a deterministic log record that can be inspected to verify context assembly.

Log write location:

- If workspace.project_root exists: project_root/logs/atlas-tui/assembled/
- Else: repo_root/.atlas-tui/logs/assembled/

The log payload must include mode, provider, model, user message, system length, and a truncated system preview.

The UI must display the last log path.

## Repo tree requirements

A tree view must support browsing directories and opening files.

Opening a file must not modify it. In v2, the minimum behavior is to show file contents in a preview pane or to display the path and a short preview.

A light-weight file watcher is optional in v2. Manual refresh is required.

Large repos must not freeze the UI. If the tree is expensive, the tree should load lazily or paginate.

## Project state requirements

Project state view is sourced from Atlas wrapper artifacts when present.

Minimum useful artifacts:

- now.md contents preview
- specs list with detection of active specs (simple heuristic acceptable in v2)
- logs list (recent files under logs/)

Open items visibility is desired but may be stubbed if open items are not represented in a machine-readable way yet.

## Mode semantics (UI-level expectations)

Interpret mode is presented as an intake mode. The UI expectation is that outputs are intent checks and structured artifacts.

Plan mode is presented as a scoping mode. The UI expectation is that outputs are phased plans and explicit open questions.

Execute mode is presented as an application mode. In v2, execution is explicitly stubbed; the UI must make that clear and must not imply that code changes are being applied.

## Lessons from existing TUIs (design guidance)

Mode and model must be visible at all times. Hidden mode state causes incorrect assumptions.

Context inspection is a core debugging surface. A small, stable place to see what the engine assembled is more valuable than sophisticated rendering.

Fast keyboard navigation is mandatory. Mouse support is optional.

Long operations must not lock the UI. Background work must surface progress and completion status.

The UI must keep safety boundaries explicit. Any future action that writes to disk must require a clear confirmation step.

## Non-goals (v2 handoff)

No provider API calls, no streaming tokens, and no auth flows.

No automatic file modifications.

No multi-repo or multi-project switching.

No daemon orchestration.

## Acceptance criteria

The TUI launches from any directory inside a managed repo and shows the resolved workspace roots.

A message can be submitted from the chat composer.

Submitting a message produces a context assembly log file at the expected location.

Switching mode changes which mode is logged and which protocol/projection is used by the engine.

Repo tree is navigable and refreshable without freezing.

Project state panel renders meaningful information when an Atlas wrapper exists and degrades gracefully when absent.
