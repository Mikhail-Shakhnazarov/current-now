Two surfaces exist now: cockpit (TUI) and glass (web inspector). The polish pass is mainly about:
- information hierarchy
- path and ID legibility
- reducing always-on verbosity
- making the two surfaces feel like the same instrument

Global design targets (shared)

1) Identity vs event
Separate workspace identity (repo name, wrapper present, roots) from last event (request_id, mode/provider/model, log path, timing). Both UIs still mix identity and event in a way that feels noisy.

2) Repo-relative first, absolute on demand
Both screens drown in Windows absolute paths. Display repo-relative paths by default; show absolute paths only behind a reveal/copy action.

3) Compact by default, drill-down on demand
Especially for logs, system previews, and raw JSON. The debug payload is correct, but its default presentation is too heavy.

4) One stable mode strip
Mode/provider/model should read like flight instrumentation: always visible, high contrast, unambiguous.

Glass (web) - what to improve

A) Header and metadata compression
Current: request_id + mode + provider/model + long roots + log path as wrapped paragraphs.

Improve:
- Two-line header:
  - Line 1: mode badge, provider/model badge, request_id (monospace), timestamp
  - Line 2: repo (short + rel root), project (short), log (rel path)
- Copy buttons for request_id and log path
- Absolute roots in a collapsible Details block (not default)

B) Context card: make it diagnostic, not decorative
Current: system_chars and ui_state keys only.

Improve:
- Compact grid: system_chars, budget_target, est_used_bytes, selected_artifacts_count, assemble_ms
- Show focused_path (repo-relative) and context_profile explicitly (not just ui_state keys)

C) Selected artifacts table: upgrade legibility
Current: paths only.

Improve:
- Columns: path (monospace), reason, bytes, kind, maybe role
- Filter input (client-side)
- Copy path affordance
- Optional grouping by reason (pinned, focused, profile:debug, etc.)

D) Raw JSON: keep it, but gate it harder
Current: raw JSON dominates.

Improve:
- Default-collapsed, plus a download link for the JSON file
- View tabs: Summary | JSON | System | ProviderRequest
- If inline JSON remains: monospace, no-wrap option, Copy button

E) Theme alignment with TUI
Current: Glass is light; TUI is dark.

Improve:
- Dark theme toggle (or auto via prefers-color-scheme)
- Shared palette vocabulary (accent + warning colors match)

TUI - what to improve

A) Top bar information hierarchy
Top bar should be a compact workspace + mode strip:
- Left: repo:<name> project:<name|None> wrapper:yes/no
- Center: [Interpret|Plan|Execute] (highlight active)
- Right: provider/model + engine status

Absolute roots should be behind an on-demand UI action (e.g. a Details button), not always-on.

B) Status bar compaction and truncation
Current: status bar can become noisy (full URLs/paths).

Improve:
- Always: engine, mode, provider/model, busy/idle, chatlog on/off, glass on/off
- On demand (toggle): last log path + glass URL + last action details
- Truncate paths with a stable rule (e.g. ...\\assembled\\20260114_184215_<id>.json) and provide copy actions

C) Panel density and readability
Chat:
- Reduce repeated bracketed "system-like" lines for stable facts
- Keep stable identity in top strip / status bar so chat reads like chat
- Ensure multi-line editing is pleasant

Repo:
- Add quick search/filter (even crude type-to-filter)
- Show selected_path (repo-relative) since it directly affects context assembly

Project and Inspection:
- Clamp now.md preview to N lines with expand
- Render last assembly summary as a compact box (system chars, artifacts count, delta) rather than narrative

D) Visual hierarchy
Borders and accent colors should not compete:
- Thinner/lower-contrast borders
- Reserve bright accent for active focus + active mode
- Make focused panel obvious

End-to-end coherence improvements (small, high leverage)

- Single naming: use the same labels everywhere (selected_artifacts, focused_path, budget, system_chars). Avoid "ui_state keys" as a primary concept in Glass; show values.
- Cross-linking:
  - TUI: "Open Glass" action (when glass enabled)
  - Glass: "Copy log path" and best-effort "Open log folder"
- Comparison readiness:
  - Glass: prev/next navigation by timestamp
  - Clear delta view between submissions (even before full browsing)

Suggested polish backlog (ordered)

1) Repo-relative path display + copy affordances (both UIs)
2) Mode/provider/model always-visible strip in TUI; metadata header compression in Glass
3) Status bar compaction + toggled details in TUI
4) Glass: artifacts table columns + filtering; raw JSON gated behind tabs/collapse
5) Theme alignment (dark mode for Glass + shared palette)
6) Focus clarity (active panel highlight + show selected_path explicitly)
