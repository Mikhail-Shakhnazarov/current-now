# Projection: Execute

Context assembly rules for execution operations.

---

## Load Order

1. `desk/core/kernel.md` -- constitutional constraints (sandwich top)
2. `desk/protocols/executor.md` -- role framing
3. `work/projects/<project>/specs/SPEC-NNN.md` -- the spec to execute
4. Target files as listed in spec.target -- current file state
5. `desk/patterns/bugs.md` section for target language -- bug prevention
6. `desk/patterns/idioms/<language>.md` if exists -- style guidance
7. `desk/core/schemas/diff.json` -- output schema (sandwich bottom)

## Selection Rules

**Spec**: Load exactly one spec. The spec being executed. No other specs.

**Target files**: Load only files listed in `spec.target`. No adjacent files, no related files.

**Patterns**: Load only patterns relevant to the execution language. If Python, load Python bugs and Python idioms. Not JavaScript patterns.

## Context Budget

Execution context should be narrow. If it exceeds limits:
1. Load spec summary + requirements only (not full spec prose)
2. Load only the functions being modified, not entire files
3. Load only high-count patterns (count > 3)
4. Never reduce kernel or protocol

## Sandwich Structure

```
[KERNEL.md content]
---
[EXECUTOR PROTOCOL content]
---
SPEC TO EXECUTE:
[SPEC-NNN.md content]
---
TARGET FILES:
[file1.py content]
---
[file2.py content]
---
PATTERNS:
[relevant bug patterns]
[relevant idioms]
---
OUTPUT SCHEMA:
[diff.json content]
Your response must be valid JSON conforming to this schema.
```

## Verification Environment

Before calling execution, ensure:
- Target files exist and are readable
- Test commands in spec.verification are runnable
- Build tools are available if spec requires them

If environment is not ready, return friction before calling model.
