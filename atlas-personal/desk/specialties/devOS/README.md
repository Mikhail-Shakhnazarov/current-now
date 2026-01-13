# devOS

Code-focused projection extensions.

---

## Purpose

devOS extends the core system for software development projects. It adds patterns specific to coding, projection rules for code context, and export conventions for clean deliverables.

## Additional Patterns

When operating in devOS mode, load:
- `desk/patterns/bugs.md` -- full bug patterns
- `desk/patterns/idioms/<language>.md` -- language-specific style
- `desk/specialties/devOS/patterns/` -- devOS-specific patterns if present

## Projection Extensions

### Interpreter (devOS)

When interpreting for code projects:
- Resolve "the bug" to recent friction items or changelog entries mentioning bugs
- Resolve "the usual pattern" to high-count items in bugs.md
- Default target to `src/` unless otherwise specified
- Include test requirements in every spec

### Executor (devOS)

When executing code specs:
- Always check bugs.md before writing
- Include region markers in larger files
- Generate test file if spec includes test requirements
- Verify with both lint and test commands

## Export Convention

devOS projects export clean deliverables:
- `src/` contents export
- `tests/` contents export
- `README.md` exports
- Spec files do not export
- Changelog does not export
- Project internals (`.atlas/`) do not export

The exported artifact is a standard repo that any developer can use without knowing about this system.

## Project Structure

```
work/projects/<name>/
|-- now.md              # Current position
|-- specs/              # Executable intent
|-- src/                # Implementation (exports)
|-- tests/              # Tests (exports)
|-- README.md           # Documentation (exports)
|-- logs/
|   `-- changelog.md    # History (internal)
`-- .atlas/
    `-- version         # Desk version marker
```
