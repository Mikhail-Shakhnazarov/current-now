# Changelog (marco-polo)

Append-only project history.

---

## [2026-01-13] INIT

**Artifact**: project
**Spec**: writeOS pilot initialization

- **Added**: writeOS project wrapper `work/projects/writeOS/marco-polo/`
- **Added**: Inputs copied into `drafts/` (`marco.md`, `polo.md`)

**Verification**: Files present in project scaffold
**Open**: None

## [2026-01-13] SPEC

**Artifact**: specs
**Spec**: SPEC-001 (open design)

- **Added**: `specs/SPEC-001.md` to define the marco->polo mapping design space
- **Added**: OPEN design questions (lossless vs semantic-lossless; labeling vs inference-tag)

**Verification**: Spec exists and is referenced by `now.md`
**Open**: OPEN-001, OPEN-002, OPEN-003, OPEN-004

## [2026-01-13] SPEC UPDATE

**Artifact**: specs
**Spec**: SPEC-001 (refine)

- **Changed**: SPEC-001 now explicitly includes graded verification and deterministic pre-processing
- **Added**: OPEN items for marco template/discipline and verification/pre-processing boundaries

**Verification**: Spec updated; project goals and design edges clarified
**Open**: OPEN-001, OPEN-002, OPEN-003, OPEN-004, OPEN-005, OPEN-006, OPEN-007

## [2026-01-13] SPEC UPDATE

**Artifact**: specs
**Spec**: SPEC-001 (clarify v1)

- **Changed**: Added v1 direct-throughput concept (project inbox drops)
- **Added**: OPEN-008 for direct-throughput syntax and filename convention
- **Added**: Created `drafts/inbox/` folder for future drops

**Verification**: `drafts/inbox/` exists; SPEC-001 mentions direct throughput
**Open**: OPEN-001, OPEN-002, OPEN-003, OPEN-004, OPEN-005, OPEN-006, OPEN-007, OPEN-008

## [2026-01-14] SPEC UPDATE

**Artifact**: specs
**Spec**: SPEC-001 (problem definition)

- **Changed**: Added an explicit problem definition section describing the marco-polo challenge

**Verification**: SPEC-001 includes the new section
**Open**: OPEN-001, OPEN-002, OPEN-003, OPEN-004, OPEN-005, OPEN-006, OPEN-007, OPEN-008

## [2026-01-14] SPEC UPDATE

**Artifact**: specs
**Spec**: SPEC-001 (airlock + interpreter flagging)

- **Changed**: Added v1 airlock admission contract (operator CLI, strict by default, overwrite in place)
- **Changed**: Clarified interpreter must flag ASCII/format violations if encountered
- **Added**: OPEN-009 for airlock CLI contract and canonical airlock location

**Verification**: SPEC-001 updated
**Open**: OPEN-001, OPEN-002, OPEN-003, OPEN-004, OPEN-005, OPEN-006, OPEN-007, OPEN-008, OPEN-009, OPEN-010

## [2026-01-14] SPEC UPDATE

**Artifact**: specs
**Spec**: SPEC-001 (tooling fork)

- **Changed**: Linked `devOS/marcopolo-atlas` as the in-house tooling project

**Verification**: SPEC-001 updated
**Open**: OPEN-001, OPEN-002, OPEN-003, OPEN-004, OPEN-005, OPEN-006, OPEN-007, OPEN-008, OPEN-009, OPEN-010


## [2026-01-14] SPEC UPDATE

**Artifact**: specs
**Spec**: SPEC-001 (implementation link)

- **Changed**: Linked to `work/projects/devOS/marcopolo/` as the implementation candidate
- **Changed**: Noted typed POLO (SRC/OPEN/PROP) as the deterministic interface direction

**Verification**: SPEC-001 updated
**Open**: OPEN-001, OPEN-002, OPEN-003, OPEN-004, OPEN-005, OPEN-006, OPEN-007, OPEN-008, OPEN-009, OPEN-010

## [2026-01-14] TOOL

**Artifact**: outputs/logs
**Spec**: POLO propagation v1

- **Added**: Deterministic propagation via `desk/tools/marcopolo_atlas.py`
- **Added**: Rolling state file at `outputs/state.md`
- **Added**: Append-only admission log at `logs/admissions.jsonl`

**Verification**: Propagation creates a run folder under `outputs/runs/`
**Open**: OPEN-009
