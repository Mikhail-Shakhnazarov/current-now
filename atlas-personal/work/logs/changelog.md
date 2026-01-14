# Changelog

Append-only execution history.

---

## [2026-01-13] RESTRUCTURE

**Artifact**: infrastructure
**Spec**: architectural reframe from role-based to projection-based

- **Changed**: Directory structure to desk/work/docs separation
- **Changed**: Protocols from documentation to loadable context
- **Added**: JSON schemas for validation (signal, spec, diff, friction)
- **Added**: Projection templates (interpret, execute)
- **Moved**: Documentation to docs/ (non-operational)
- **Moved**: Patterns under desk/patterns/
- **Moved**: Specialties under desk/specialties/

**Verification**: Structure created, files in place
**Open**: None

## [2026-01-13] PROJECT

**Artifact**: work/projects
**Spec**: initialize writeOS pilot

- **Added**: `work/projects/writeOS/marco-polo/` project wrapper
- **Added**: Copied operator artifacts into `work/projects/writeOS/marco-polo/drafts/`

**Verification**: Project scaffold present; drafts copied
**Open**: None

## [2026-01-13] SPEC

**Artifact**: writeOS/marco-polo
**Spec**: SPEC-001 (open design)

- **Added**: `work/projects/writeOS/marco-polo/specs/SPEC-001.md` (define marco->polo mapping design space)

**Verification**: Spec exists; project `now.md` points to it
**Open**: OPEN-001, OPEN-002, OPEN-003, OPEN-004

## [2026-01-14] SPEC

**Artifact**: writeOS/marco-polo
**Spec**: SPEC-001 (problem definition)

- **Changed**: Added explicit problem definition section to SPEC-001

**Verification**: SPEC-001 updated
**Open**: OPEN-001, OPEN-002, OPEN-003, OPEN-004, OPEN-005, OPEN-006, OPEN-007, OPEN-008

## [2026-01-14] OUTPUT

**Artifact**: writeOS/marco-polo
**Spec**: portable challenge (v2)

- **Added**: `work/projects/writeOS/marco-polo/outputs/challenge.md` (shareable problem statement + acceptance criteria)

**Verification**: Challenge artifact exists
**Open**: OPEN-010

## [2026-01-14] PROJECT

**Artifact**: work/projects
**Spec**: import marcopolo implementation

- **Added**: `work/projects/devOS/marcopolo/` wrapper
- **Added**: Imported repo into `work/projects/devOS/marcopolo/repo/`

**Verification**: Repo present; wrapper initialized
**Open**: None

## [2026-01-14] DOCS

**Artifact**: devOS/marcopolo
**Spec**: standalone readiness

- **Changed**: Standardized authorship in `work/projects/devOS/marcopolo/repo/LICENSE`
- **Changed**: Formalized standalone `work/projects/devOS/marcopolo/repo/README.md` and added contributor docs

**Verification**: Docs and license updated
**Open**: None

## [2026-01-14] PROJECT

**Artifact**: work/projects
**Spec**: create marcopolo-atlas fork

- **Added**: `work/projects/devOS/marcopolo-atlas/` wrapper
- **Added**: Copied `devOS/marcopolo/repo/` into `devOS/marcopolo-atlas/repo/` for Atlas-specific glue

**Verification**: Project exists; repo copy present
**Open**: None

## [2026-01-14] SPEC

**Artifact**: writeOS/marco-polo
**Spec**: SPEC-001 (implementation link)

- **Changed**: Linked `writeOS/marco-polo` spec to `devOS/marcopolo` implementation candidate
- **Changed**: Noted typed POLO (SRC/OPEN/PROP) as the deterministic interface direction

**Verification**: Link recorded in SPEC-001
**Open**: OPEN-001, OPEN-002, OPEN-003, OPEN-004, OPEN-005, OPEN-006, OPEN-007, OPEN-008, OPEN-009, OPEN-010

## [2026-01-14] TOOL

**Artifact**: desk/tools
**Spec**: marcopolo propagation v1

- **Added**: `desk/tools/marcopolo_atlas.py` (root-invoked deterministic POLO propagation)
- **Changed**: Locked v1 intake path and propagation rules in `work/projects/writeOS/marco-polo/specs/SPEC-001.md`

**Verification**: Tool exists; spec updated
**Open**: OPEN-009

## [2026-01-14] PROJECT

**Artifact**: work/projects
**Spec**: intake pipeline proposal

- **Added**: `work/projects/devOS/intake-pipeline/` wrapper
- **Added**: `work/projects/devOS/intake-pipeline/specs/SPEC-001.md` (project proposal)

**Verification**: Project scaffold present
**Open**: None

## [2026-01-14] PROJECT

**Artifact**: work/projects
**Spec**: atlas-tui stub

- **Added**: `work/projects/devOS/atlas-tui/` wrapper

**Verification**: Wrapper scaffold present
**Open**: None
