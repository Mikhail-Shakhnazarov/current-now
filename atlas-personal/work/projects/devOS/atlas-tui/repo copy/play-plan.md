# Atlas TUI Play Plan (Repo Copy)

Purpose: Use the repo copy as a sandbox to redesign and pressure-test Atlas-TUI
with a "3D printing" approach: build observable layers first, then iterate
predictably.

Status: sandbox-only (do not merge directly into stable repo).

## Inputs
- Current Atlas-TUI baseline: functional UI with small keybinding/UX edge cases.
- Operator constraint: no direct provider calls; build for inspection + logs.

## Guiding Principles (3D printing)
1. Build to debug: every behavior emits observable signals.
2. Layered deposition: add features only after observability and checks exist.
3. Explicit binding: document how signals map to checks and failure modes.
4. Deterministic checks: tests assert stable artifacts, not UI pixels.

## Phase 0: "Print the calibration cube"
Goal: Lock down the smallest end-to-end loop with observability.

- UI event vocabulary (structured):
  - focus_changed(panel, widget_id)
  - key_handled(key, action, screen_stack_depth, result)
  - submit_started(request_id, mode, provider, model)
  - submit_done(request_id, ok, system_chars)
  - log_written(path, bytes)
  - glass_pointer_updated(path)
- Single "debug snapshot" (JSON):
  - focused_panel, focused_widget_id
  - screen_stack (types)
  - selected_path (repo-relative)
  - mode/provider/model
  - last_request_id, last_log_path
  - prefs (context profile, budget, pins, excludes)
- Minimal smoke tests:
  - Esc behavior: close modal -> no modal -> quit confirm open/close
  - F1 help open/close
  - F2 focus cycle
  - Submit writes log and latest pointer

Deliverable: "UI observability v1" + "smoke tests v1".

## Phase 1: Test seams (TUI / engine / web)
Goal: Make component boundaries testable and artifacts stable.

- Versioned JSON schemas for UI events and snapshots (v1).
- Deterministic session/request identifiers in logs (no absolute paths in outputs).
- Headless test seams:
  - engine protocol roundtrip without network calls
  - log writer and latest pointer behavior without UI rendering

Deliverable: "test seams v1" + "artifact checks v1".

## Phase 2: Context selection and artifacts
Goal: Make context selection legible and testable.

- Emit selected_artifacts list from engine (already in dummy engine).
- Add UI summary of selection and top exclusions/pins.
- Add a "why these files" panel (no extra engine calls; explain from inputs).

Deliverable: "Context visibility v1".

## Phase 3: Glass as debugging surface
Goal: Web view mirrors UI observables for postmortems.

- Add UI event stream (lightweight JSON) to logs.
- Glass: optional "UI tab" that reads latest UI snapshot.

Deliverable: "UI timeline in Glass".

## Binding Schema (for each feature)
For each feature, define:
- Invariant(s)
- Observable signal(s)
- Check(s) that assert invariants
- Failure modes and diagnostic path

Example (Esc handling):
- Invariant: Esc closes top modal; if none, opens quit confirm.
- Observables: key_handled + screen_stack depth change.
- Check: press Esc -> stack depth-- or confirm opened.
- Failure modes:
  - key not handled (binding shadowed by widget)
  - pop attempted with empty stack (screen mismatch)

## Agentic Workflow (operator + assistant)
1. Add observability for a behavior.
2. Write a smoke test that reads those signals.
3. Run tests; if failed, inspect signals and update binding schema.
4. Only then add the next feature layer.

## Non-goals (for sandbox)
- Do not integrate delegated builds directly.
- Do not add provider calls.
- Do not optimize performance beyond measured pain points.

## Exit Criteria (for merging back)
- All Phase 0 tests green.
- Binding schema covers at least 5 critical behaviors.
- Glass shows UI snapshot for the latest session.

## Implementation Plan (Printed Repo)
Goal: Describe both modular restructuring and the build-up sequence if we were
printing this repo from scratch.

### A. Modular restructuring plan
1. Define module boundaries first (no code moves yet):
   - ui/ (screens, widgets, styling, focus policy)
   - engine/ (protocol, client, dummy engine)
   - logging/ (assembled logs, chat logs, latest pointer)
   - state/ (prefs, snapshots)
   - web/ (glass server + static assets)
   - assets/ (atlas docs, test fixtures)
2. Draw the public API for each module:
   - ui -> emits UI events + snapshot JSON
   - engine -> takes EngineInput, returns EngineOutput
   - logging -> write_assembled_log + write_latest_pointer
   - state -> load/save prefs + snapshot
3. Move code last, in small steps:
   - Add new module packages + re-export current functions.
   - Update imports gradually; keep compatibility shims.
4. Pin explicit contracts:
   - One dataclass per cross-module payload (UI event, snapshot, log index).
   - One "golden" JSON shape for logs and snapshots (versioned).

### B. Build-up sequence (3D printing)
Layer 0: Frame + calibration
- Create UI event vocabulary and snapshot format.
- Add a single "debug dump" command in the UI.
- Add a minimal smoke suite that reads only those signals.

Layer 1: Minimal loop
- Implement: open app -> submit -> log written -> latest pointer updated.
- Bind checks to the signals (log_written, pointer_updated).

Layer 2: Interaction stability
- Implement Esc/F1/F2 as invariants (close modal, help, focus cycle).
- Emit key_handled events and assert via smoke tests.

Layer 3: Context visibility
- Add selection summary (selected_artifacts, pins/excludes).
- Persist in logs + show in UI/Glass.

Layer 4: Glass inspection surface
- Glass reads latest snapshot and event log artifacts.
- Add a minimal web smoke check for core endpoints.

Layer 5: Modularization pass
- Split into modules using the boundaries defined in A.
- Verify all prior tests still pass.

### C. Printed-repo checklists
- Each layer adds observability first, behavior second.
- Every layer ends with a testable artifact (log, snapshot, event).
- No new feature without a binding schema update.

## System Practice Implications (Generalized)
This pattern scales beyond Atlas-TUI. It is a system practice for building
inspectable software with low-cost verification and predictable iteration.

### Implications for how we build
- Every component owns an observable vocabulary (events, snapshots, logs).
- Features ship with a binding schema (invariants -> signals -> checks).
- Tests are lightweight and signal-driven (not pixel-perfect or exhaustive).
- Debug UX is part of the feature, not an afterthought.

### Implications for how we operate
- Operators get deterministic inspection routes for common failures.
- Postmortems use artifacts, not memory (events + snapshots in logs).

### Implications for tooling
- A shared "observability DSL" for UI + engine events.
- A standard log layout so Glass and tooling can read across projects.
- A small set of reusable smoke tests that can be ported across apps.

### Implications for team contracts
- "Done" means: feature + instrumentation + binding schema + smoke checks.
- New behaviors must declare their observables and failure modes up front.
- Regression risk is mitigated by keeping checks close to signals.
