# SPEC-001: Project Timing Tool v1 - CLI

> Status: active
> Created: 2026-01-13
> Updated: 2026-01-13
> Target: `repo/`
> Supersedes: N/A
> Superseded by: N/A

---

## Summary

Build an operational CLI tool for tracking project time, starting with the Task Timer CLI sample and enhancing it for project workflows. This enables users to associate timers with projects, persist data reliably, generate reports, and configure settings, laying groundwork for v2 GUI while keeping v1 focused on CLI reliability.

---

## Scope

**In:** CLI tool with project tagging, SQLite database for persistence, CSV/Markdown exports, configuration file for settings and alerts, error recovery for interruptions.

**Out:** GUI interface, concurrent timers, historical analytics beyond daily reports, integrations with external systems.

---

## Requirements

### MUST

1. **PT-001** -- Implement project association: Timers link to project IDs from a registry, auto-associating on start without manual input.
   - Acceptance: CLI accepts project ID on start; validates against registry; displays project context in status.

2. **PT-002** -- Upgrade persistence to SQLite: Replace JSON with database for concurrent access and background operation.
   - Acceptance: No data corruption during simultaneous timer runs; data survives restarts.

3. **PT-003** -- Add export functionality: Generate CSV or Markdown reports by project, date range, or total time.
   - Acceptance: Command outputs valid files with time summaries; handles edge cases like empty data.

4. **PT-004** -- Configuration file: Support defaults for time zone, work hours, threshold alerts.
   - Acceptance: Tool reads config on startup; alerts trigger on exceedances; cross-platform path handling.

### SHOULD

1. **PT-005** -- Error handling and recovery: Log interrupted sessions; offer resumption on restart.
   - Acceptance: Tool detects interruptions; provides clear options to continue or discard.

2. **PT-006** -- Basic notifications: Alert on timer thresholds or session ends.
   - Acceptance: Configurable alerts via CLI or system notifications.

### MAY

1. **PT-007** -- Modular design for GUI: Structure code to allow v2 GUI as a wrapper reading the same database.
   - Acceptance: Separate CLI logic from data layer for easy extension.

---

## Interfaces

**Inputs:** CLI commands (start/stop/status/report/export), project registry file (JSON), config file (YAML/JSON).

**Outputs:** Console status, exported files (CSV/MD), database updates.

**Dependencies:** Python with SQLite, no external APIs required.

---

## Constraints

1. CLI-only -- No GUI in v1 to focus on backend reliability.
2. Cross-platform -- Must work on Windows/Linux/Mac for distributed teams.
3. Single-user focus -- No multi-user sync in v1.

---

## Open

| ID | Description | Closure |
|----|-------------|---------|
| OPEN-001 | Confirm export formats (CSV vs Markdown vs both) | Operator decision on preferred output |

Executor: return friction on OPEN items, do not resolve.

---

## Notes

Build on existing patterns from `desk/specialties/devOS/samples.md` (Task Timer CLI). Reference `desk/patterns/idioms/python.md` and the Python sections in `desk/patterns/bugs.md`. Avoid common pitfalls like time zone mishandling or file locking. Keep code modular for v2 GUI integration.

---

## Verification

1. Start timer for project X, stop after 1 hour -- Database records accurate time; status shows correct elapsed.
2. Export daily report -- File contains summarized times by project; handles zero-time entries.
3. Interrupt and resume -- Tool detects gap; offers recovery without data loss.
4. Invalid project ID -- Clear error message; no timer start.

---

## Lifecycle

| Date | Status | Note |
|------|--------|------|
| 2026-01-13 | active | Operator approved |
