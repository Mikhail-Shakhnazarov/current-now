# Reflections

On what this system is, what it assumes, and how it might evolve.

---

## What This Is

This is a context engineering system for managing complex work with LLM runtimes. The core operation is projection: transforming durable state (files) into bounded context (what the model sees) that shapes model behavior toward correct transformations. The system does not rely on model memory, conversational continuity, or agent autonomy. It relies on explicit state, structured projections, schema validation, and operator authority.

The system is not an agent framework. There are no autonomous actors. There are LLM API calls shaped by projections. The "roles" -- Interpreter and Executor -- are projection templates plus validation contracts, not persistent entities with goals.

The system is not a workflow engine. There is no orchestration layer managing task queues. Operations are independent: assemble projection, call model, validate output, commit if valid. The file state is the coordination mechanism.

## The Core Mechanism

Every operation follows the same pattern:

1. Select artifacts based on operation type (projection template)
2. Assemble into sandwich structure (kernel at boundaries, payload in middle)
3. Call model API with assembled context
4. Validate response against schema
5. If valid, commit to file state
6. If invalid, return to operator with explicit errors

The sandwich structure exploits transformer attention bias. Models attend most strongly to context boundaries. Placing constraints at these positions bounds the generation space. The model cannot easily produce output that violates constraints because the constraints occupy high-attention positions.

## Assumptions Made in This Restructure

**Model capability**: Assumes access to frontier LLMs capable of following complex instructions, generating structured JSON, and operating within protocol constraints. Tested with Claude and GPT-4 class models. May degrade with smaller models.

**CLI or API access**: Assumes operator can either use a CLI tool with model access (like OpenCode, Aider) or can call model APIs directly. The system is interface-agnostic but requires some way to send projections and receive responses.

**Operator engagement**: Assumes a single human operator who reviews outputs and authorizes commits. The system does not support autonomous operation or multi-user coordination.

**File-based state**: Assumes all meaningful state lives in files. No database, no external services, no persistent processes. This is a deliberate constraint for simplicity and portability.

**JSON Schema validation**: Assumes validation can be performed with standard tools (jq, jsonschema libraries). Schemas are JSON Schema draft-07 format.

**Semantic extraction requires LLM**: The input pipeline cannot mechanically extract semantic structure from natural language. Assumes that intent inference, reference resolution, and signal structuring require LLM pattern matching, shaped by projection. True mechanical operations are limited to encoding normalization and syntactic pattern extraction.

**Context limits are real**: Assumes model context windows have practical limits. Projection templates include selection rules for managing context budget. The system must work within these constraints.

**Projection quality matters**: Assumes that what enters the context window shapes output quality more than instruction sophistication. Investment in projection assembly produces better returns than investment in prompt engineering.

## What This Enables

**Portability**: Work folders migrate between desk versions. Upgrade the desk without breaking active projects. The interface between desk and work is the schemas.

**Verifiability**: Every schema boundary is a verification surface. Malformed output fails before corrupting state. Failures attribute to specific components.

**Re-entry**: Session briefs compress completed work. Changelogs provide execution trace. Friction logs track blocked states. Operator returns after time gaps and immediately sees current state.

**Accumulation**: Patterns capture repeated insights. Bugs become bug patterns. Idioms become idiom files. The desk improves through use without changing core architecture.

## What This Does Not Do

**Automate thinking**: The system provides surfaces for externalized cognition. It does not replace operator judgment. Operator decides what to build, reviews specs, authorizes commits.

**Eliminate errors**: Schema validation catches format errors. It does not catch semantic errors. A well-formed spec can still specify the wrong thing. Operator review catches semantic errors.

**Scale to teams**: Single operator assumed. Multi-user coordination would require additional infrastructure (locking, merge handling, role assignment) not present here.

**Integrate external services**: Current scope is file-based. Integration with Trello, calendars, external APIs would require output pipeline extensions not yet designed.

## How This Might Evolve

**Tooling sophistication**: Current assumption is minimal tooling (bash, jq). As workflow friction becomes clear, build targeted tools. The system can generate its own tooling through interpretation and execution.

**Specialty proliferation**: devOS and writeOS are two specialties. Others could emerge: researchOS for literature work, designOS for visual projects, teachOS for educational content.

**Projection optimization**: Current projection templates are handwritten. Could develop heuristics for dynamic projection based on operation type and context budget.

**Validation depth**: Current schemas validate structure. Could add semantic validators (e.g., verify that spec requirements are actually verifiable, verify that diffs trace to spec clauses).

## On the Relationship to Earlier Frames

Earlier iterations used "port" terminology (Port A, Port B) emphasizing role separation. The reframe to "projection" emphasizes context engineering. Both describe the same phenomenon: different contexts produce different behaviors from the same model capability.

The hermeneutic frame (from the monograph) remains valid: interpretation is circular, meaning emerges from context, artifacts stabilize meaning across time. The projection frame is the implementation: how do you actually construct context that produces reliable interpretation?

The cybernetic frame (from the monograph) remains valid: the system is a control loop with feedback. Friction is the error signal. Validation is the measurement. Commits are the actuator. The projection frame adds specificity: the control loop operates through context assembly.

The media theory frame (from the monograph) remains valid: LLM interaction is a medium with biases. The projection architecture is a counter-medium that exploits attention patterns rather than fighting them.

## On Building Cognitive Exoskeletons

This system is one instance of augmented cognition tooling: external structure that extends cognitive capacity. The operator thinks through the system -- writing is the thinking, not reporting on thinking. Specs externalize intent. Schemas externalize validity criteria. Projections externalize attention management.

The system does not make the operator smarter. It makes certain kinds of work possible that would otherwise exceed working memory: complex tasks spanning weeks, multiple interacting specifications, accumulated patterns from past work. The exoskeleton holds what the mind cannot hold.

Trust shifts from memory to artifacts. Instead of "I remember we decided X", consult the spec. Instead of "the model should know Y", check what's in the projection. The artifacts are the shared ground between operator and model, not the conversation.

## Final Note

This document is documentation, not operational context. It exists for human readers trying to understand the system. It does not load into model projections. The operational truth lives in desk/core/kernel.md and desk/protocols/*.
