UI Clean-up Pass (cockpit + glass)

Status: draft
Date: 2026-01-14
Owner: devOS/atlas-tui

Goal

Improve legibility and information hierarchy across the Textual cockpit and the Glass web inspector, without changing core behavior (engine boundary, logging, or safety posture).

Scope

In scope
- Reduce always-on verbosity in both surfaces.
- Make repo-relative paths the default presentation.
- Make identity (workspace) distinct from last event (request).
- Improve visual hierarchy (mode strip, focused panel highlight).
- Improve Glass usability (metadata layout, artifacts table, raw JSON gating).

Out of scope
- Provider API calls / streaming / auth.
- Any automated repo writes beyond existing logs/state.
- Reworking the engine protocol.

Current observations

- Identity vs event is mixed: workspace roots, request_id, mode/provider/model, and log path compete for attention.
- Windows absolute paths dominate; repo-relative is not consistently used.
- Debug payload is useful but presented too heavily (raw JSON, long previews).
- Glass is light themed while cockpit is dark; they feel like different instruments.

Phased plan

Phase 1: Shared naming + repo-relative display

Deliverables
- Standardize labels across both UIs: selected_artifacts, focused_path, budget, system_chars.
- In cockpit: ensure selected_path displayed and logged is repo-relative.
- In glass: display repo-relative log path and selected artifact paths by default; keep absolute paths behind a Details block.

Acceptance
- No default UI area shows absolute Windows paths unless explicitly expanded/copied.
- Labels match across both surfaces.

Phase 2: Cockpit top strip + status bar compaction

Deliverables
- Top strip becomes a compact instrument panel:
  - Left: repo name, project name, wrapper yes/no
  - Center: mode strip with clear active highlight
  - Right: provider/model and engine status
- Status bar becomes compact-by-default:
  - Always: busy/idle, engine, glass on/off, chatlog on/off
  - Details toggle reveals: last log path, glass URL, last action detail
- Truncate long paths with a stable rule and add copy actions.

Acceptance
- Status bar never wraps due to full paths/URLs in the default view.
- Glass URL is visible and copyable when enabled.

Phase 3: Cockpit panel density improvements

Deliverables
- Chat:
  - Reduce repeated bracketed system-like lines for stable facts.
  - Keep stable identity out of the transcript where possible.
- Repo:
  - Add basic filter (type-to-filter) for DirectoryTree.
  - Show selected_path explicitly in the repo panel.
- Project/Inspection:
  - Clamp now.md preview with expand.
  - Render last assembly summary as a compact box (system chars, artifacts count, delta) rather than narrative.

Acceptance
- Operator can tell at-a-glance what is selected, what was assembled, and where logs live, without scrolling.

Phase 4: Glass header, cards, and raw JSON gating

Deliverables
- Header becomes a two-line bar:
  - Line 1: mode badge, provider/model, request_id, timestamp
  - Line 2: repo (short + rel root), project (short), log (rel path)
- Add Copy buttons for request_id and log path.
- Context card shows a compact grid: system_chars, budget target, estimated used bytes, selected_artifacts_count, assemble_ms, focused_path, context_profile.
- Selected artifacts table columns: path, reason, bytes, kind, role (when available).
- Add filter input (client-side).
- Raw JSON default-collapsed; add tabs: Summary | JSON | System | ProviderRequest; add Download link.

Acceptance
- Glass loads quickly and shows the “what happened” summary without immediately dumping large JSON.

Phase 5: Theme alignment

Deliverables
- Add dark theme toggle (or auto via prefers-color-scheme) to Glass.
- Align accent colors to cockpit palette.

Acceptance
- Glass feels like a companion diagnostic view, not a separate app.

Verification checklist

- Submit a message and verify:
  - Cockpit shows mode/provider/model clearly.
  - Log path is discoverable and copyable.
  - Glass updates from latest.json and displays the same key fields.
- Verify repo-relative rendering for:
  - selected_path
  - selected_artifacts paths
  - log path

