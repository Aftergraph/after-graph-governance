# Institution Layer Research v4 — Absorbed Findings

Source: `After_Graph_The_Institution_Layer_Research_Standards_v4_2026.pdf` (35 pages, Revision 4.0, evidence cut 2026-09-03, archived in Downloads/AIE/). This doc absorbs the roadmap-relevant claims into the governance repo so the PDF stays an archived reference.

## 1. External signal: OWASP ACS (FACT)

OWASP published the **Agent Control Standard (ACS) 2026-09-01** — runtime control is moving from vendor category to open standardization. Per TG `AIES-POSITIONING.md` §6: ACS is the *how* (runtime hooks/enforcement), AIE is the *by whom* (the semantics those hooks enforce). Complementary, not competing. AIE MUST NOT replace ACS, MCP or A2A (manifesto point 8).

## 2. The 10-point AIE manifesto (verbatim from the standard proposal)

1. Autonomy without authority boundaries is an incident waiting for a timestamp.
2. A graph is a map of coordination, not a constitution.
3. Every agent is a principal; every consequential action needs a resolved authority.
4. Delegation must conserve permissions, budget and accountability.
5. Organizations are runtime state, not static diagrams.
6. Policies must be externally enforceable and versioned.
7. Evidence is an output of execution, not an afterthought.
8. Control standards and protocols compose under shared semantics; AIE does not replace ACS/MCP/A2A.
9. Humans need explicit takeover, approval and revocation primitives.
10. A standard earns its name through interoperability and conformance, not a launch post.

## 3. AIE-compliance minimum claim

A system may claim **AIE C0 conformance** only if it satisfies Draft 0.3 Core requirements AND passes the public conformance suite. Separate profiles: D1 (Delegation), T1 (Dynamic Topology), F1 (Federation), E1 (Economic). Interoperability claims require ≥2 independent runtimes passing cross-implementation tests — schema compatibility alone is insufficient.

## 4. Credible-introduction checklist (binds the P2 gate)

- Publish an RFC before a manifesto thread.
- Open-source schemas, reference runtime and tests (done: aie repo public).
- Bind to ACS/MCP/A2A/SPIFFE/OPA/OTel rather than compete.
- Demonstrate three hard cases: revocation propagation, cross-org delegation, dynamic topology under budget.
- Invite maintainers from distributed systems, IAM, MAS, workflow engines into governance.
- Measure interoperability, failure containment, evidence completeness. Marketing after the graphs stop catching fire.

## 5. Manifesto-point status vs our repos (verified 2026-09-04)

| Point | Status | Evidence |
|---|---|---|
| 3 resolved authority per action | SATISFIED | AIE admit + TH-12 revalidate (aie commit abc8df4, 189/189) |
| 4 delegation conserves budget | PARTIAL | Spec has attenuateScope/conserveBudget; WORKS BudgetLedger exists; triple-tracking (WE/AIE/TG) gap documented in reconciliation matrix |
| 7 evidence as execution output | SATISFIED | WORKS bundle.go HMAC-SHA256 signed, content-addressed |
| 8 compose not replace | SATISFIED | TG AIES-POSITIONING §6; WORKS standards mappings |
| 9 human takeover primitives | PARTIAL | TG approval flow exists; takeover/revocation UX not built |
| 10 conformance over launch | SATISFIED | AIE S1.1 MCP PASS, S2 A2A PASS (TCK 2026-09-04) |
| 1, 2, 5, 6 | SATISFIED | TG enforcement plane + governance docs |

## 6. P2 roadmap implications

1. **ACS interoperability** as explicit P2 gate item: map TG runtime hooks to ACS enforcement points; AIE stays the normative semantics layer.
2. **C0 conformance publication** (RFC-style) unlocks credible standard naming — schemas/runtime/tests already open.
3. **Three hard-case demos** (revocation propagation, cross-org delegation, dynamic topology under budget) map to existing STUDY-011 assets + WORKS scheduler — propose as the independent-reproduction vehicle for P2.
4. **Naming discipline**: no public "standard" claims for AIE until C0 + 2 independent runtimes (TG rule already enforced).
