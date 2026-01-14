## Thread 1: Intake pipeline and provenance

SRC: Priority on building a marco-polo pairs ledger, ideally deterministic.
OPEN: Define the canonical ledger artifact (pointer-based, no copies), and the entry creation rule.
PROP: Track this as an implementation concern under `devOS/intake-pipeline`.

## Thread 2: Operator input conventions

SRC: Interest in adding hash tags (examples given) for provenance/learning signals.
PROP: Keep hash tags out of v1; park as v2 consideration if needed.
OPEN: Decide whether project mention aliases such as `@intake_pipeline` resolve to canonical paths.

## Thread 3: New devOS project seed (Kleinanzeigen manager)

SRC: Proposal for a Kleinanzeigen manager to manage sales during apartment restructuring.
PROP: Create a new exportable devOS project wrapper (candidate: `devOS/kleinanzeigen-manager`).
OPEN: Define scope for v1 (inventory tracking only vs listing workflow support).

## Thread 4: Publishable components and packaging

SRC: System components can be published as standalone tools; Marco-Polo is the exemplar.
SRC: Atlas could become a TUI app as a client-facing devOS tool, while writeOS stays internal initially.
PROP: Treat standalone repos as a first-class output format (README/license/tests as baseline).
OPEN: Decide whether Atlas TUI is a distinct exportable repo (`devOS/atlas-tui`) vs part of core system tooling.

## Thread 5: System imaging (desk portability)

SRC: Need for a system image to migrate the desk and store system state detached from a specific user.
OPEN: Define snapshot scope (desk vs work), exclusions, and storage format.
PROP: Treat as foundational infrastructure and split into its own devOS project (candidate: `devOS/system-imaging`).

## Thread 6: Monograph transformation (writeOS flagship)

SRC: Monograph should become a writeOS project with a transformation pipeline toward a PhD dissertation.
OPEN: Define current manuscript structure and dissertation target requirements.
PROP: Create a writeOS project wrapper (candidate: `writeOS/monograph`) with a transformation spec.

## Thread 7: Compaction as a general pattern

SRC: Marco->Polo resembles a compaction mechanism: bounded context produced from high-dimensional input.
PROP: Treat the intake pipeline as a context compiler; reuse the pattern for other pipelines.

## Thread 8: Multimodal coherence and binding

SRC: Multimodal models require coherent multimodal context, including explicit semantic bindings (text/diagram relationships).
OPEN: Decide the first modality pair to target and the relationship schema.
PROP: Park as a future writeOS feature line (candidate: `writeOS/multimodal-binding`).

## Thread 9: Monetization and sustainability

SRC: Patreon is proposed as a monetization platform.
OPEN: Define the offer, cadence, and tiers.
PROP: Treat as a parallel track; avoid coupling to v1 intake pipeline scope.

## Thread 10: Embedded direction block

SRC: The later section contains a structured landscape interpretation, tiering, questions, and proposed actions.
PROP: Treat this block as proposals and questions (not authoritative facts) during compilation.
PROP: Convert the tier structure into non-binding priority suggestions rather than requirements.

## OPEN summary

OPEN: Ledger artifact and retention policy.
OPEN: Alias policy for `@<project>` mentions.
OPEN: System imaging scope and format.
OPEN: Monograph inputs and dissertation target requirements.
OPEN: Atlas TUI repo boundary and v1 feature set.
OPEN: Kleinanzeigen manager scope.
OPEN: Multimodal binding v1 target.
OPEN: Patreon offer definition.
