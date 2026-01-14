# Projection: Interpret (OpenCode)

Context assembly rules for interpretation operations in OpenCode.

This is identical to `desk/projections/interpret.md` for context, but changes the expected output handling:
- Prefer writing spec artifacts to files and returning a short operator summary in chat.

---

## Load Order

1. `desk/core/kernel.md` -- constitutional constraints (sandwich top)
2. `desk/protocols/interpreter-opencode.md` -- role framing (OpenCode)
3. `desk/patterns/*.md` -- accumulated knowledge
4. `work/projects/<project>/specs/*.md` where status=active -- current specs
5. `work/logs/changelog.md` tail (last 20 entries) -- recent history
6. `work/friction/log.md` where status=open -- unresolved items
7. [OPERATOR INPUT] -- the signal to interpret (sandwich middle)
8. `desk/core/schemas/spec.json` -- output schema (sandwich bottom)

## Output Handling

Preferred:
- Write `work/projects/<project>/specs/SPEC-NNN.json`
- Write `work/projects/<project>/specs/SPEC-NNN.md`
- Chat response is a short operator summary + paths

Fallback:
- Chat response is schema-valid JSON only
