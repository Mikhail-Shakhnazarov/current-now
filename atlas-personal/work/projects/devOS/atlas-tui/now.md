# Now: atlas-tui

## Current state

A v2 cockpit exists in the exportable repo and is runnable as a Textual application with a long-lived engine subprocess. The UI is a three-panel operator cockpit with chat in the center, a repo tree and basic repo health on the left, and project/inspection panels on the right.

The engine subprocess is intentionally non-networked in v2. Its job is to assemble the concrete provider request payload that would be sent to OpenAI or Anthropic. In this phase, the primary output is not model responses, but deterministic inspection logs that capture the assembled context pack for review and debugging.

The default engine implementation reads the packaged Atlas templates (kernel + mode-specific protocol + mode-specific projection) from `atlas_tui` assets and assembles a `system` string accordingly. The UI treats the system prompt as opaque and only previews it, while writing a full record to disk.

## Intent

Ship a client-facing Atlas TUI that can be launched from anywhere inside a managed repo and immediately provides re-entry. The operator interacts through chat, but the text passed to any model is mediated by Atlas context assembly rules rather than raw chat transcript.

Mode selection (interpret/plan/execute) is a first-class UI control that changes which protocol and projection are loaded. Interpret is for marco-to-polo transformations, plan is for scoping and phased planning, and execute is for spec-driven repo changes and verification. The semantics are being established in v2, while real execution and provider calls are deferred.

## What changed recently (decision deltas)

The delegated TUI implementation has been assimilated into the client-facing repo. The v2 entrypoint is the delegated-style CLI (`atlas_tui.cli:main`) and the architecture keeps the engine boundary as a subprocess speaking a JSONL protocol.

Packaging remains in the current client repo (setuptools) while dependencies were aligned to support the richer cockpit. The older minimal v1 scaffolding modules have been removed to avoid competing implementations.

## Next

Run the cockpit locally to validate the full loop: launch, workspace discovery, message submit, engine assembly, and log creation. Then replace the default engine implementation with a real engine server that performs Atlas context retrieval and compaction against the live workspace, while keeping the JSONL protocol stable.

After the engine is stable, add provider call plumbing (OpenAI and Anthropic) and authentication workflows. API keys are expected first; subscription-based logins are explicitly desired but remain an open design problem.
