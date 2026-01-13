# writeOS

Text-focused projection extensions.

---

## Purpose

writeOS extends the core system for text transformation projects. It adds schema concepts for semantic structure, transform patterns for format conversion, and verification for meaning preservation.

## Core Concepts

### Schemas (semantic structure)

Every text has extractable semantic structure:
- **Claims**: Assertions that can be true or false
- **Evidence**: Support for claims
- **Definitions**: Terms with specific meaning
- **Structure**: How claims relate
- **Anchors**: Semantic handles for reference

The schema is the source of truth. Outputs derive from schema.

### Transforms (format conversion)

A transform maps schema to output format:
- Source schema (what semantic content)
- Target format (blog, academic, tweet, etc.)
- Mapping rules (how to present)
- Constraints (length, tone, structure)

Same schema, different transforms, different outputs. Meaning preserved.

## Projection Extensions

### Interpreter (writeOS)

When interpreting for text projects:
- Extract schema from drafts
- Identify claims, evidence, definitions
- Map structure relationships
- Create semantic anchors
- Spec includes schema + transform definition

### Executor (writeOS)

When executing text specs:
- Generate from schema, not from draft
- Verify coverage (all claims present)
- Verify fidelity (no claims added)
- Verify format compliance
- Return friction if schema insufficient for transform

## Project Structure

```
work/projects/<n>/
|-- now.md
|-- specs/              # Transform specifications
|-- drafts/             # Raw input material
|-- schemas/            # Extracted semantic structure
|-- outputs/            # Generated final forms
|-- logs/
|   `-- changelog.md
`-- .atlas/
    `-- version
```

## Export Convention

writeOS exports include process:
- `drafts/` shows thinking
- `schemas/` shows structure
- `outputs/` shows results

This demonstrates rigor. The complete pipeline is the deliverable.
