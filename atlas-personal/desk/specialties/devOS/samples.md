# devOS Sample Projects

Projects for demonstrating devOS workflow.

---

## Task Timer CLI

**Difficulty**: Beginner | **Language**: Python | **Sessions**: 1

A CLI tool for tracking time on tasks. Start/stop timers, show status, generate reports.

**Scope in**: start, stop, status, report commands. JSON persistence.
**Scope out**: GUI, concurrent timers, historical reports.

Exercises: file I/O, CLI parsing, time handling, state persistence.

---

## Markdown Link Checker

**Difficulty**: Beginner | **Language**: Python/Node | **Sessions**: 1-2

Scan markdown files, find links, verify they're reachable.

**Scope in**: Recursive scan, extract links, check HTTP status, check file existence.
**Scope out**: Fix links, check anchors, rate limiting.

Exercises: file traversal, regex, HTTP requests, async operations.

---

## Config Validator

**Difficulty**: Intermediate | **Language**: TypeScript | **Sessions**: 2

Schema-based validation for JSON/YAML config files.

**Scope in**: Schema definition, parse configs, validate, report violations, CI exit codes.
**Scope out**: Schema generation, auto-fix, complex constraints.

Exercises: schema design, recursive validation, error accumulation.

---

## Git Hooks Manager

**Difficulty**: Intermediate | **Language**: Bash+Python | **Sessions**: 2

Manage git hooks across repositories from central config.

**Scope in**: Config file, install command, update command, status command.
**Scope out**: Hook templates, remote repos, testing framework.

Exercises: git internals, file permissions, symlinks, shell escaping.

---

## API Mock Server

**Difficulty**: Intermediate | **Language**: Node/TypeScript | **Sessions**: 2-3

Mock API endpoints from config file.

**Scope in**: Route config, static responses, request matching, response delays, hot reload.
**Scope out**: Recording, stateful mocks, proxy mode, auth simulation.

Exercises: HTTP server, file watching, route matching.
