# Doctrine

Operational principles explained for human readers. This is documentation, not operational context.

---

## Core Insight

The system is a context engineering framework. Model behavior emerges from context projection, not from instruction or agent autonomy. Assemble the right context, frame it with the right protocol, validate against the right schema -- and the model produces reliable transformations.

## Why Projection

Language models complete patterns. They attend to context and generate continuations that fit. This is powerful for transformation: given input plus framing, produce structured output. It is dangerous for autonomy: the model has no persistent goals, no stable memory, no judgment about what matters.

The system exploits the strength (pattern completion) while constraining the weakness (no judgment). Projection assembles context that makes desired output the natural completion. Schemas validate that output conforms. The operator provides judgment. The model provides transformation capacity.

## Why Separation

Desk and work separate because they evolve at different rates. The desk (protocols, patterns, schemas) improves through use. Work (projects, specs, sessions) accumulates through execution. Upgrading the desk should not break active work. Migrating work should not require desk modification.

Roles separate because they need different contexts. Interpretation needs broad context for reference resolution and intent inference. Execution needs narrow context for literal application. Mixing them produces either over-interpretation (execution invents requirements) or under-interpretation (specs lack clarity). Separation enables attribution: bad spec points to interpreter, bad diff points to executor.

## Why Schemas

Stochastic processes produce variable outputs. Schema validation converts variability into reliability. Conforming output proceeds. Non-conforming output fails with explicit reasons. The schema boundary is where you catch errors before they corrupt state.

Schemas also define interfaces. Signal schema specifies what interpreter receives. Spec schema specifies what executor receives. Diff schema specifies what commits to state. These contracts make the system composable and verifiable.

## Why Operator Authority

Models propose, operators dispose. Every transformation produces output that requires review. Nothing commits without operator authorization. This preserves accountability (operator approved it), enables correction (operator catches errors), and maintains competence (operator stays engaged).

The system is designed to make operator review cheap. Structured outputs are faster to review than prose. Schemas catch obvious errors mechanically. Verification provides evidence. The operator reviews quality, not correctness of format.

## Why Files

Files are the only durable state. Conversation is ephemeral -- it vanishes when context resets. Model "memory" is unreliable -- it reconstructs rather than recalls. Files persist. Files diff. Files can be inspected, versioned, migrated.

The system treats conversation as scratch space for generating file updates. If something isn't written to a file, it doesn't exist in the system. This is not bureaucracy; it is epistemic hygiene.
