# Changelog (atlas-tui)

Append-only project history.

---

## [2026-01-14] INIT

**Artifact**: project
**Spec**: atlas-tui stub

- **Added**: devOS project wrapper `work/projects/devOS/atlas-tui/`

**Verification**: Wrapper scaffold present
**Open**: None

## [2026-01-14] V2-SCAFFOLD

**Artifact**: client repo
**Spec**: v2 cockpit + inspection logging

- **Integrated**: Textual cockpit UI into `work/projects/devOS/atlas-tui/repo/src/atlas_tui/ui/`
- **Added**: JSONL engine subprocess protocol client `work/projects/devOS/atlas-tui/repo/src/atlas_tui/engine_client.py`
- **Added**: local engine implementation `work/projects/devOS/atlas-tui/repo/src/atlas_tui/dummy_engine.py` that assembles `system` from bundled Atlas templates
- **Added**: deterministic inspection logs `work/projects/devOS/atlas-tui/repo/src/atlas_tui/log_writer.py`
- **Changed**: CLI entrypoint is `atlas_tui.cli:main` (engine subprocess remains in v2)
- **Added**: TUI delegation spec `work/projects/devOS/atlas-tui/specs/tui-spec.md`

**Verification**: Structure present; entrypoint updated
**Open**: Replace local v2 engine with real Atlas engine server; add provider call pipeline and auth later

## [2026-01-14] DOCS-UPDATE

**Artifact**: docs
**Spec**: v2 repo state alignment

- **Updated**: repo `README.md` to reflect UI-first cockpit + engine subprocess
- **Updated**: project `now.md` to reflect v2 decisions and current implementation
- **Updated**: v2 docs in `repo/docs/` (architecture/auth/vertical slice) to match subprocess engine boundary

**Verification**: Docs updated
**Open**: None
