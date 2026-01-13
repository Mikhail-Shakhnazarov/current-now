# Learnings

Cross-project insights. Higher-level than bug patterns.

---

## Process

**Context projection compounds.** Well-assembled context produces better outputs than multiple clarification rounds. Invest in projection quality.

**Schemas create verification surfaces.** Every schema boundary is a place where failures can be caught mechanically. More schemas = more catchable failures.

**Narrow beats broad for execution.** Interpreter needs broad context for reference resolution. Executor needs narrow context for literal application. Different operations, different projections.

**Friction is signal.** Friction items indicate where the system lacks information. High friction count on a topic suggests missing pattern or unclear convention.

## Architecture

**Separation enables attribution.** When roles don't share context, failures point to responsible component. Mixed context hides failure sources.

**Files are the truth.** Conversation is ephemeral. Files persist. If it's not in a file, it's not part of the system state.

**Protocols shape behavior.** Same model capability, different protocols, different outputs. The protocol is the behavioral specification.

## Anti-Patterns

**Context flooding.** Loading everything "just in case" dilutes attention. Load what's relevant to this operation.

**Schema avoidance.** Skipping validation because "it looks right" lets malformed output corrupt state. Always validate.

**Friction suppression.** Guessing instead of returning friction creates invisible debt. Explicit friction is cheaper than implicit confusion.
