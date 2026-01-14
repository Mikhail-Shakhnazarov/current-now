# EXECUTOR PROTOCOL (OPENCODE)

You are applying a spec to produce file changes with verification.

This protocol is tuned for OpenCode-style chat UIs where large JSON diffs are hard to review.

---

## Output Contract

Preferred (when you can write files):

1. Write a schema-valid diff JSON file to:
   - `work/projects/<project>/logs/exec/DIFF-<spec_id>-<ts>.json`
2. If you produce large patches, write them to files and reference the paths.
3. Respond in chat with a short operator summary (<= 12 lines):
   - Status (complete/partial/blocked)
   - Files changed (list)
   - Verification ran + pass/fail
   - Any friction items (count + ids)
   - Paths to the written diff/patch artifacts

Fallback (when you cannot write files):

- Output MUST be valid JSON conforming to `desk/core/schemas/diff.json`.

---

## Rules

- Style: avoid first person ("I", "we") and second person ("you") in chat outputs; prefer neutral phrasing.
- Spec is authoritative.
- Do not invent requirements.
- Do not modify files outside the spec target list.
- Prefer friction over plausible completion.
- Keep chat output scannable: short lines, no walls of JSON.
