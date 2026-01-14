# Projection: Plan (OpenCode)

Context assembly rules for planning operations in OpenCode.

This projection exists to support scoping and phased planning. It is intentionally lightweight in v2.

## Load Order (v2 stub)

Kernel constraints and a planning protocol are loaded first, followed by minimal repo state summaries and the operator input.

The output should be a phased plan plus explicit OPEN items.
