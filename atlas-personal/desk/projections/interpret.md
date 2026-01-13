# Projection: Interpret

Context assembly rules for interpretation operations.

---

## Load Order

1. `desk/core/kernel.md` -- constitutional constraints (sandwich top)
2. `desk/protocols/interpreter.md` -- role framing
3. `desk/patterns/*.md` -- accumulated knowledge
4. `work/projects/<project>/specs/*.md` where status=active -- current specs
5. `work/logs/changelog.md` tail (last 20 entries) -- recent history
6. `work/friction/log.md` where status=open -- unresolved items
7. **[OPERATOR INPUT]** -- the signal to interpret (sandwich middle)
8. `desk/core/schemas/spec.json` -- output schema (sandwich bottom)

## Selection Rules

**Patterns**: Load all patterns from `desk/patterns/`. If specialty is active, also load `desk/specialties/<specialty>/patterns/`.

**Specs**: Load only specs with `status: active` from current project. Skip archived/superseded.

**Changelog**: Load last 20 entries. More recent = more relevant for reference resolution.

**Friction**: Load only open friction. Resolved friction is historical.

## Context Budget

If total context exceeds model limits:
1. Reduce changelog to last 10 entries
2. Load only specs referenced in operator input
3. Load only patterns for languages mentioned
4. Never reduce kernel or protocol

## Sandwich Structure

```
[KERNEL.md content]
---
[INTERPRETER PROTOCOL content]
---
[PATTERNS content]
---
[ACTIVE SPECS content]
---
[CHANGELOG TAIL content]
---
[OPEN FRICTION content]
---
OPERATOR INPUT:
[raw operator input here]
---
OUTPUT SCHEMA:
[spec.json content]
Your response must be valid JSON conforming to this schema.
```
