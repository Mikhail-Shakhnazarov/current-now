### Feature: Local Provider Harness with Hybrid HTTP Surfaces

**Intent.** Provide a local, credential-free API environment that exercises Atlas’ provider-call plumbing and makes request/response behavior observable. This is not a “big model runtime.” It is a deterministic integration harness that can optionally forward to a small local model backend.

**Core idea.** One local service exposes two HTTP faces that resolve into the same internal handler:

1. **Atlas-native endpoint** (canonical, foundational): speaks Atlas domain objects directly and returns structured diagnostics suitable for UI inspection.
    
2. **OpenAI-compatible endpoint** (compatibility facade): implements a minimal OpenAI-ish dialect for easy boilerplate interoperability and drop-in use from existing clients/tools.
    

The OpenAI-compatible surface exists because it is cheap and useful; the Atlas endpoint exists because it is the stable kernel surface for Atlas UIs.

---

### Functional scope

**In scope (v0–v1).**

- A local HTTP server binds to loopback by default (e.g. `127.0.0.1`) and exposes:
    
    - `POST /atlas/submit` (canonical)
        
    - `POST /v1/chat/completions` (compat facade; subset only)
        
    - `GET /health` (status + build/version info)
        
- Deterministic, inspectable request/response behavior:
    
    - stable request IDs
        
    - stable log records
        
    - explicit error shapes
        
    - explicit timing + size diagnostics
        
- Two backend modes:
    
    - **mock mode**: deterministic canned behaviors (echo, summarize diagnostics, JSON template response)
        
    - **forward mode**: optional passthrough to a small local model backend (details out of scope here; treated as pluggable)
        

**Out of scope (initial).**

- Auth, multi-user, network exposure beyond localhost
    
- High-throughput inference, batching, GPU scheduling
    
- Tool execution, file modification, agent loops
    
- Full OpenAI API surface (only the minimal subset needed for testing)
    

---

### Canonical Atlas endpoint: `/atlas/submit`

**Purpose.** Make Atlas’ internal contract explicit and stable. This endpoint is the foundational surface that Atlas TUI/web/IDE can target in the future (directly or via engine).

**Input shape.** Accepts an `EngineInput`-like payload (or a small superset), including:

- workspace roots (repo_root, optional project_root)
    
- mode (interpret/plan/execute)
    
- provider/model identifiers (logical labels; “local” is allowed)
    
- user message
    
- optional UI state hints (focused path, pinned/excluded paths, context profile/budget)
    

**Behavior.**

- Constructs a normalized provider request internally (messages/system/user).
    
- Produces a response object that mirrors Atlas’ inspection needs:
    
    - assembled_context (system string + metadata)
        
    - provider_request (what would be sent to a provider)
        
    - provider_response (mock or forwarded result)
        
    - diagnostics (timings, sizes, selected artifacts list, budgets, errors)
        

**Output shape.** Returns an `EngineOutput`-like object with additional optional `provider_response` and richer diagnostics. Responses must be deterministic given the same inputs in mock mode.

---

### OpenAI-compatible facade: `/v1/chat/completions`

**Purpose.** Allow off-the-shelf clients, curl scripts, and “OpenAI-compatible local servers” workflows to operate against Atlas’ harness with minimal friction.

**Input subset.**

- `model`
    
- `messages[]` (role/content)
    
- optional `stream` (may be stubbed initially)
    
- optional small set of common fields (`temperature`, `max_tokens`) accepted but not necessarily honored in mock mode
    

**Behavior.**

- Translates OpenAI-ish input into the canonical internal request form.
    
- Routes through the same handler as `/atlas/submit`.
    
- Translates the internal result into an OpenAI-ish response object.
    

**Guarantees.**

- The same request should yield equivalent assistant content whether sent via `/atlas/submit` or `/v1/chat/completions`, modulo formatting differences inherent to the dialect.
    

---

### Logging and inspection (foundational)

**Goal.** Every call produces artifacts that allow debugging without guesswork.

**Required log record fields.**

- request id, timestamp, endpoint used
    
- normalized request (after translation, before backend)
    
- response payload
    
- diagnostics: timing breakdown, sizes, failure mode, backend mode (mock/forward)
    

**Write location.**

- If project_root exists: `project_root/logs/atlas-local-provider/…`
    
- Else: `repo_root/.atlas-local-provider/logs/…`
    

(Repo-clean rule preserved.)

---

### Failure injection (test environment feature)

**Purpose.** Exercise timeouts, retries, and error rendering deterministically.

**Mechanisms.**

- Header or query parameter, e.g. `X-Atlas-Fail: timeout|500|malformed|slow`
    
- Optional latency injection, e.g. `X-Atlas-Sleep-Ms: 2500`
    

**Expected behaviors.**

- Timeout: no response within configured window (or explicit timeout error)
    
- 500: structured error body
    
- malformed: intentionally broken JSON for client robustness tests
    
- slow: delayed but valid response
    

---

### Compatibility and evolution rules

- `/atlas/submit` is **the authoritative contract** and will be versioned explicitly (e.g. `/atlas/v1/submit` later).
    
- `/v1/chat/completions` compatibility is **best-effort subset**, frozen to what Atlas needs for harnessing; no promise to track every upstream change.
    
- Both surfaces must remain “thin” and must not accumulate business logic that belongs in the Atlas engine.
    

---

### Acceptance (feature-level)

- Local server starts and serves `/health`.
    
- The same logical request can be sent via `/atlas/submit` and `/v1/chat/completions` and produces equivalent assistant content.
    
- Each request produces a deterministic log record in the correct location.
    
- Failure injection works and is observable in logs and client behavior.
    
- Default bind is localhost; no repo pollution beyond scoped state/log dirs.
    

If useful, the next step is to write a single-page “contract doc” enumerating the exact JSON shapes for v0 (Atlas submit + OpenAI subset + error objects) so that engine work later is frictionless.