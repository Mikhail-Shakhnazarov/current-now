# Bugs (atlas-tui)

Append-only bug log.

---

## [2026-01-14] UI-001: `App.tree` attribute collision

**Symptom**: `AttributeError: property 'tree' of 'AtlasTUIApp' object has no setter`

**Cause**: Textual `App` defines a read-only `tree` property; the cockpit assigned `self.tree = DirectoryTree(...)`.

**Fix**: Renamed UI field to `self.repo_tree`.

**Location**: `work/projects/devOS/atlas-tui/repo/src/atlas_tui/ui/app.py`

## [2026-01-14] UI-002: transcript widget API mismatch

**Symptom**: `AttributeError: 'Static' object has no attribute 'plain'`

**Cause**: transcript was a `Static` widget but code treated it like a log widget.

**Fix**: swapped transcript to a log-like widget and simplified transcript append logic.

**Location**: `work/projects/devOS/atlas-tui/repo/src/atlas_tui/ui/app.py`

## [2026-01-14] UI-003: `NoneType` has no attribute `get_height`

**Symptom**: `AttributeError: 'NoneType' object has no attribute 'get_height'` during startup / early transcript writes.

**Hypothesis**: Textual/rich layout not fully initialized when transcript writes occur, or a version-specific widget rendering issue.

**Mitigation**: transcript append is wrapped in `try/except` so UI does not crash.

**Next**:
- Capture full traceback (deepest Textual/rich frames) to identify the originating widget.
- If tied to a specific widget type, pin a compatible Textual version or switch transcript widget implementation.

**Location**: `work/projects/devOS/atlas-tui/repo/src/atlas_tui/ui/app.py`

## [2026-01-14] UI-004: transcript rendering stability

**Symptom**: continued transcript-related startup instability.

**Mitigation**: transcript widget is a read-only `TextArea`; transcript updates are deferred until `on_ready` and rendered from a separate in-memory buffer.

**Location**: `work/projects/devOS/atlas-tui/repo/src/atlas_tui/ui/app.py`
