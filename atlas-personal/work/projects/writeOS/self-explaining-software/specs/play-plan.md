# Atlas TUI Play Plan (Repo Copy)

Purpose: Use the repo copy as a sandbox to redesign and pressure-test Atlas-TUI
with a "3D printing" approach: build observable layers first, then iterate
predictably. This plan is inspired by MARCO-002 and the self-introducing system
idea (cheap model for onboarding and self-explanation).

Status: sandbox-only (do not merge directly into stable repo).

## Inputs
- MARCO-002: self-introducing systems, cheap model onboarding, progressive
  disclosure.
- Current Atlas-TUI baseline: functional UI with small keybinding/UX edge cases.
- Operator constraint: no direct provider calls; build for inspection + logs.

## Guiding Principles (3D printing)
1. Build to debug: every behavior emits observable signals.
2. Layered deposition: add features only after observability and checks exist.
3. Explicit binding: document how signals map to checks and failure modes.
4. Cheap onboarding: self-introduce the system using structured prompts.

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

## Phase 1: Self-introduction (onboarding)
Goal: System can explain itself to a new operator using cheap model prompts.

- Onboarding pack (new file): WELCOME_PACK.md
  - 3-5 quick profiling questions
  - Branch table: response -> recommended doc path
  - "30s, 2m, deep dive" variants
- UI affordance: one-click "Welcome" panel or command in Help overlay.
- Logs: onboarding steps logged as events (for testability).

Deliverable: "WELCOME_PACK + onboarding event flow".

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
- WELCOME_PACK exists and is referenced in Help.
- Binding schema covers at least 5 critical behaviors.
- Glass shows UI snapshot for the latest session.

## System Practice Implications (Generalized)
This pattern scales beyond Atlas-TUI. It is a system practice for building
self-explaining software with low-cost verification and predictable iteration.

### Implications for how we build
- Every component owns an observable vocabulary (events, snapshots, logs).
- Features ship with a binding schema (invariants -> signals -> checks).
- Tests are lightweight and signal-driven (not pixel-perfect or exhaustive).
- Debug UX is part of the feature, not an afterthought.

### Implications for how we operate
- Cheap models can do first-pass triage and onboarding (WELCOME_PACK).
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
