# Bug Patterns

Accumulated bug patterns by language. Check before writing, append after encountering.

---

## Python

| ID | Pattern | Fix | Count |
|----|---------|-----|-------|
| PY-001 | Mutable default argument | Use `None`, then `x = x or []` | 0 |
| PY-002 | Bare except clause | Specify exception type | 0 |
| PY-003 | Threading without lock | Use `threading.Lock()` for shared state | 0 |
| PY-004 | f-string in logging | Use `%s` formatting for lazy evaluation | 0 |
| PY-005 | Import side effects | Guard with `if __name__ == "__main__"` | 0 |
| PY-006 | Path string concatenation | Use `pathlib.Path` | 0 |

## JavaScript / TypeScript

| ID | Pattern | Fix | Count |
|----|---------|-----|-------|
| JS-001 | State mutation | Spread: `{...state, key: val}` | 0 |
| JS-002 | useEffect missing deps | Include all refs in deps array | 0 |
| JS-003 | Missing key in map | Stable unique key prop | 0 |
| JS-004 | Handler recreated each render | Wrap in `useCallback` | 0 |
| JS-005 | Async in useEffect | Create inner async function | 0 |
| TS-001 | `any` type escape | Define proper interface | 0 |
| TS-002 | Non-null assertion abuse | Use proper null checks | 0 |

## Shell

| ID | Pattern | Fix | Count |
|----|---------|-----|-------|
| SH-001 | Unquoted variable | Always quote: `"$var"` | 0 |
| SH-002 | Missing error handling | Add `set -euo pipefail` | 0 |
| SH-003 | Command substitution in condition | Capture first: `result=$(cmd)` | 0 |

## General

| ID | Pattern | Fix | Count |
|----|---------|-----|-------|
| GEN-001 | Hardcoded config | Extract to constants or config file | 0 |
| GEN-002 | Silent error swallow | Log or surface all errors | 0 |
| GEN-003 | Magic numbers | Named constant with comment | 0 |
| GEN-004 | Timezone assumptions | Always use UTC internally | 0 |

---

## Usage Protocol

**Before execution**: Check patterns for target language. Note high-count items.

**After encountering bug**: Fix in code, increment count or add new row.

**Count threshold**: When count reaches 6, consider lint rule or tooling solution.
