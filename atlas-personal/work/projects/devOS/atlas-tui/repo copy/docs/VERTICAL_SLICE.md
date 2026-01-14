# Vertical slice (v2)

V2 is a single-repo, launched-in-place cockpit. The current working directory is used to discover the managed repo root and an optional Atlas wrapper root.

The v2 vertical slice goal is to demonstrate that user chat input plus UI state is transformed into a provider request payload by an Atlas-style context assembly step, and that this payload is inspectable on disk.

Launching `atlas-tui` starts a Textual cockpit and an engine subprocess.

Submitting a message sends a structured EngineInput over JSONL to the engine.

The engine returns an assembled context and a provider request payload without calling provider APIs.

The cockpit writes an assembled-context inspection log file and displays its path.

This validates the prompt assembly mechanics and the mode/projection wiring before the provider-call pipeline is added.
