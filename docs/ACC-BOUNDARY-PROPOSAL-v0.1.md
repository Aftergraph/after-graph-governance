# ACC Boundary Proposal v0.1 (for PLATFORM-BOUNDARY-CHARTER)

**Status:** Proposal — not executed. Companion to `Aftergraph/context-continuity` (Draft 0.1).
**Date:** 2026-09-07.

## Proposed module

| Module | Role | Description |
|--------|------|-------------|
| **ACC** | Portable continuity/state-transfer | Owns transfer of actionable context/state across model/agent/session/runtime boundaries. Machine-readable Continuity Capsules, delta semantics, receiver handshake, omission manifest, freshness. Nothing else. |

## Non-overlap statement

- Mission Contract (ISR SPEC-001) owns **what must be achieved and verified**. ACC never defines success — it carries a mission defined elsewhere.
- AIE owns **who may act/delegate**. ACC carries authority boundaries; it never grants authority.
- WORKS owns **execution**. ACC capsules are inert data until a runtime acts on them.
- Evidence layer owns **proof**. ACC carries references/hashes, never replaces evidence.
- skills-vault owns **adapters**. Skills (first: `chatgpt-message-summarizer`) compile/render capsules; they never own the contract.
- No existing repo owned portable cross-runtime handoff capsules at audit time (2026-09-07, all 15 org repos); hence a dedicated repo, no competing contract.

## Claim discipline

ACC claims integrity (hashes), never semantic truth. Research claims live in
`claims/CLAIMS.md` in the ACC repo under the ISR evidence protocol; no
platform claim inherits ACC evidence automatically.

## Request

Record ACC as proposed module with the boundary above; promote only on
V1 gate evidence (schema green, SLR = 0, >= 2 model families, baseline
comparison complete, raw results retained).
