# Projection: Execute (OpenCode)

Context assembly rules for execution operations in OpenCode.

This is identical to `desk/projections/execute.md` for context, but changes the expected output handling:
- Prefer writing execution artifacts to files and returning a short operator summary in chat.

---

## Load Order

1. `desk/core/kernel.md` -- constitutional constraints (sandwich top)
2. `desk/protocols/executor-opencode.md` -- role framing (OpenCode)
3. `work/projects/<project>/specs/SPEC-NNN.md` -- the spec to execute
4. Target files as listed in spec.target -- current file state
5. `desk/patterns/bugs.md` section for target language -- bug prevention
6. `desk/patterns/idioms/<language>.md` if exists -- style guidance
7. `desk/core/schemas/diff.json` -- output schema (sandwich bottom)

## Output Handling

Preferred:
- Write `work/projects/<project>/logs/exec/DIFF-<spec_id>-<ts>.json`
- Write any large patches to files
- Chat response is a short operator summary + paths

Fallback:
- Chat response is schema-valid JSON only
