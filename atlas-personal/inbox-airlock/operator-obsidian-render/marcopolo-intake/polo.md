# polo.md - Operator Input Breakdown (Example)

Source: `marco.md`
Goal: convert semi-structured operator text into clear, actionable threads without solving them yet.
Operator: Mikhail Shakhnazarov
Year: 2026

## Meta

- Intent: test "input assimilation" for multi-theme operator notes.
- Output requested: a breakdown into separate threads/themes, attached to relevant projects/surfaces.
- Non-goal: answer/solve the threads in this stage; produce clearer signal and staging.

## Threads (Themes -> Work Items)

### T1: OpenCode output readability (UI-facing)

- Core claim: default OpenCode chat rendering makes long outputs (esp. JSON) hard to review.
- Desired change: make system output more readable/friendly in the OpenCode interface.
- Likely surfaces:
  - Desk protocols: interpreter/executor output contracts
  - Desk projections: prefer writing artifacts to files; chat summary only
  - Tooling: renderers/formatters; small artifacts rather than blobs
- Stage: active design topic (needs concrete constraints from OpenCode UI).

### T2: Subsidiarity and deterministic tooling

- Core claim: delegate lowest-level operations to deterministic tools when possible.
- Interpretation: in this system, authority is binary (operator termination), so subsidiarity means:
  - Use tools for mechanical transforms (normalization, formatting, rendering, lint/test runs)
  - Keep model roles for semantic work (interpretation/specification and constrained execution)
- Likely surfaces:
  - Desk/core/kernel.md (rules)
  - Desk/tools/* (scripts)
  - Protocols (when to emit friction vs. delegate)
- Stage: policy -> tooling roadmap.

### T3: OpenCode observability and potential fork/assimilation

- Core claim: OpenCode context composition view is valuable; we can expose more state.
- Questions raised:
  - What additional data should be visible (context packs, raw messages, tool I/O)?
  - If forking OpenCode, what attribution is required and how should it be expressed?
- Likely surfaces:
  - Separate project: "opencode-fork" or "opencode-integration"
  - Logging tooling: deterministic logging of context composition and raw exchanges
- Stage: exploratory; needs a scoped spec and legal/attribution decision.

### T4: Model choice is about cognitive engagement, not just size

- Core claim: model selection should track how much "cognitive work" a role must do.
- Proposed heuristic:
  - Use cheaper/free models for shallow interpretation/execution when task is narrow
  - Reserve stronger models for deep context / high ambiguity / multi-artifact reasoning
- Concepts introduced:
  - Context depth vs. context breadth as orthogonal controls
  - Context volume as composite budget matched to task
- Likely surfaces:
  - Desk/projections/*.md (context budget rules)
  - Desk/protocols/* (model selection guidance)
- Stage: needs formal definitions + operator-facing knobs.

### T5: Sequential pipeline and scaling as threads/cores

- Core claim: the process is necessarily sequential like a CPU pipeline.
- Scaling idea:
  - Parallelize where possible via multiple independent threads/cores/kernels
  - Treat Atlas/Work-OS as orchestrator (scheduling + handoff)
- Likely surfaces:
  - Future orchestrator tooling (task queue, concurrency boundaries)
  - Project policy for parallel work and merge/verification
- Stage: research/design; not immediately required for current boot.

### T6: Output templates by specialty (devOS/writeOS)

- devOS template needs mentioned:
  - TypeScript template
  - Google Apps Script template (consulting ecosystem)
  - SuperCollider (music) template
  - Web-UI template
- writeOS template/output formats mentioned:
  - "research/thought/idea dump" suitable for RAG / NotebookLM-style tools
  - Two output types:
    - context packs for further processing
    - human-facing end products (papers, etc.)
- Meta: if response format is defined, input hygiene can be exported to upstream tools.
- Likely surfaces:
  - Desk/templates/* (project templates)
  - Desk/specialties/devOS/* and writeOS/* (output format contracts)
  - Hygiene pipeline contracts (what upstream tools must emit)
- Stage: near-term; can become a set of small specs.

### T7: Work-OS as context-engineering playground

- Core claim: use Work-OS to develop/prove context-engineering techniques.
- Pipeline claim: proven techniques should become tooling via subsidiarity.
- Stage: guiding principle; suggests tracking "promotions" from practice -> tool.

## Attach Threads to Projects (Proposed)

### Project: self (system development)

- Owns: T1 (output readability), T2 (subsidiarity rules/tooling), T4 (model selection knobs), T6 (templates), T7 (promotion pipeline)
- Potential artifacts:
  - specs describing output contracts and template requirements
  - tools for rendering/formatting and hygiene

### Project: OpenCode integration/fork (new)

- Owns: T3 (observability + fork/attribution)
- Requires an OPEN decision:
  - attribution requirements and desired integration strategy

## OPEN Items (Decisions Needed)

- OPEN-001: What is the target OpenCode UI behavior?
  - Closure: define the minimum "good" operator view (max lines, layout, link style, file artifacts).

- OPEN-002: OpenCode fork vs. plugin vs. upstream contribution?
  - Closure: choose integration strategy and attribution approach.

- OPEN-003: Model selection policy knobs.
  - Closure: define depth/breadth/volume and when to switch models.

- OPEN-004: Template priority order.
  - Closure: rank devOS templates (TS, GAS, SuperCollider, Web-UI) and writeOS outputs to implement first.

## Suggested Next Step (Still Not Solving)

- Convert T1 + T2 into a single small spec: "Operator-readable outputs in OpenCode via file artifacts + deterministic renderers".
- Create a new project wrapper for OpenCode integration only if you choose to pursue T3.
