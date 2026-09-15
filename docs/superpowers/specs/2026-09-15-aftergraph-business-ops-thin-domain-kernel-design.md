# Aftergraph Business Ops — Thin Domain Kernel Design

**Status:** Owner-approved architecture direction in chat on 2026-09-15; implementation remains gated on written-spec review.

**Date:** 2026-09-15

**Owner:** Aftergraph portfolio control

**Scope:** Define the target architecture, ownership boundaries, canonical service-business domain, Rendetalje pilot composition, migration rules, evidence gates and repository topology for Aftergraph Business Ops.

**Evidence cut:** Governance `2734f62fce42b8008b8d3ed2b390d96357adf87a`; `JonasAbde/rendetalje-workspace` main `bf00053a33aa1ebc86d0d908562acfc8e32e2858`; `JonasAbde/Renos-Control` main `d3e405b4612e12313a3e8806a97ac57d99c7d9b3`; live production observations taken 2026-09-15. Live `app.rendetalje.dk` is observed healthy but its exact deployed Git SHA is not yet independently proven.

---

## 1. Decision

Aftergraph will build Business Ops as a **thin, generic service-business domain kernel**, not as a new permanent platform plane and not as a generalized copy of RenOS.

Rendetalje is the first full production tenant and reference implementation.

The governing dependency rule is:

```text
Business Ops must compile and operate without Rendetalje installed.
Rendetalje may depend on Business Ops.
Business Ops must never depend on Rendetalje.
```

The product thesis is:

```text
conversation / event
      ↓
resolved business context
      ↓
domain decision / proposed effect
      ↓
AIE authority semantics
      ↓
Trust admission / approval
      ↓
Runtime orchestration
      ↓
WORKS durable execution
      ↓
provider receipt / read-back
      ↓
domain state update + evidence reference
      ↓
independent verification where required
```

Business Ops owns the **service-business state and invariants** in the middle of this chain. It does not duplicate the platform owners around it.

---

## 2. Why this exists

Rendetalje has accumulated multiple generations of software for customers, leads, bookings, jobs, invoicing, Gmail, Calendar, AI assistants and operational automation. The useful behavior is real, but responsibilities are spread across incompatible models and several historical runtime approaches.

P−1 archaeology established four important facts:

1. `rendetalje-workspace/renos` is the broad current RenOS production donor and `app.rendetalje.dk` is the observed production surface.
2. `Renos-Control` is an additive successor/control-plane line whose isolated V5.1 database applies `000 + 073–080`; it is not a clone of the production RenOS business data plane.
3. Valuable semantics exist in both lines, especially tenant isolation, booking execution gates, service agreements, work orders, provider-intent safety and evidence handling.
4. Existing Aftergraph repositories already own authority, trust, runtime, execution, interaction, billing and verification responsibilities. Business Ops must compose them rather than recreate them.

Therefore migration is based on **verified behavior and explicit semantics**, not source-file copying.

---

## 3. Architectural placement

Business Ops is a domain/product repository with no new permanent architecture plane.

Proposed topology record:

```yaml
name: business-ops
canonical_branch: main
visibility: private
architecture_plane: null
system_class: service-business-domain
role: canonical-service-business-domain
lifecycle: active
owns: Canonical service-business state, invariants, domain transitions, domain contracts and domain adapter interfaces.
must_not_own: AIE authority, Trust admission or secrets, Runtime orchestration, WORKS durable execution, Studio conversation truth, generic provider execution, generic evidence storage, independent verification or invoice/payment platform truth.
```

Rendetalje is a separate domain composition/tenant repository:

```yaml
name: rendetalje
canonical_branch: main
visibility: private
architecture_plane: null
system_class: tenant-domain
role: rendetalje-reference-tenant
lifecycle: active
owns: Rendetalje-specific cleaning semantics, pricing policies, estimator behavior, playbooks, communication policy, tenant configuration, migration mappings and tenant-specific adapters.
must_not_own: Generic Business Ops contracts, platform authority, generic runtime, generic execution, generic integration fabric or cross-tenant semantics.
```

The public branded website remains a separate surface and is not a source of internal business authority. Its target ownership may be transferred into the Aftergraph organization only after secret/history review. It may become `Aftergraph/rendetalje-web` while continuing to serve `rendetalje.dk`.

No legacy repository is transferred merely to satisfy naming or organization aesthetics. Credential-containing or operational-data-containing history must be remediated before any transfer.

---

## 4. Permanent ownership boundaries

### 4.1 Business Ops owns

Business Ops owns canonical service-business facts and invariant-preserving transitions for:

- Party/Customer references used by service operations;
- leads and lead lifecycle;
- service locations;
- service definitions and service norms;
- estimates as domain calculations;
- proposals/quotes as commercial offers;
- service agreements and immutable agreement versions;
- work orders;
- assignments and assignment membership;
- execution actuals and corrections;
- charge-source facts derived from governed business rules;

`ChargeFact` is a **read-only domain projection emitted by Business Ops for Aftergraph Billing consumption**. It contains tenant scope, verified execution references, the governing policy/version reference and provenance digest/reference. It is not a ledger entry, invoice line, invoice, delivery record or payment record. The exact `ChargeFact` schema is a P1 deliverable and must be characterized before implementation.
- domain exceptions and their lifecycle;
- domain evidence references and provenance links;
- domain events required to reconstruct or project Business Ops state.

### 4.2 Business Ops does not own

The following remain canonical elsewhere:

| Concern | Canonical owner |
|---|---|
| Principal, authority, delegation, budget, revocation semantics | AIE |
| Tenant/session runtime binding, admission, approval, secrets, action audit | Trust Gateway |
| Agent lifecycle, orchestration, model/runtime routing, checkpoints | Runtime |
| Durable attempts, retries, recovery, execution evidence | WORKS |
| Conversation threads, turns, multimodal UX, assistant/operator experience | Studio / Interaction Fabric |
| Human operator/control projection | Relay |
| Invoice generation/delivery/payment workflow | Aftergraph Billing domain, currently incubated in `Aftergraph/studio`; `docs/billing/EXTRACTION.md` defines the target extraction boundary to `Aftergraph/billing` |
| Charge-source fact emission and provenance | Business Ops domain |
| Code verification | Sentinel |
| Non-code outcome verification | registered independent domain verifier |
| Semantic capability identity/provider implementation routing | Capability Fabric / Runtime |
| Scheduled observation with zero execution authority | Cron/Proactivity fabrics |

No Business Ops table may become a shadow replacement for these owners.

---

## 5. Thin Domain Kernel

The first kernel is intentionally small.

### 5.1 Core entities

```text
PartyRef
Customer
Lead
ServiceLocation
ServiceDefinition
ServiceNorm
Estimate
Proposal
ServiceAgreement
ServiceAgreementVersion
WorkOrder
Assignment
AssignmentMember
ExecutionActuals
ChargeFact
OperationalException
EvidenceRef
```

### 5.2 Hard semantic separations

The implementation must preserve these distinctions:

```text
Estimate != Proposal != ServiceAgreement
```

An estimate is a calculation. A proposal is an offer. A service agreement is accepted commercial/operational truth.

```text
ServiceNorm != WorkOrderChecklistRun
```

A norm defines expected work or policy. A checklist run is execution evidence for one specific work instance.

```text
ExecutionCompleted != OutcomeVerified
```

Execution can complete without independent verification. Verification must never be inferred from process exit, UI state, provider acceptance or a domain boolean alone.

```text
ConversationContext != BusinessTruth
```

Conversation history may reference business entities but never substitutes for canonical domain reads.

```text
Assignment != AuthorityDelegation
```

Scheduling a worker to a job is a service-business fact. It does not grant AIE authority.

### 5.3 IDs

All new canonical entities use opaque globally unique identifiers. Tenant-qualified uniqueness is mandatory where identities are scoped.

Legacy identifiers are never silently reused as canonical identifiers. Migration records carry explicit source namespace, source ID, target ID, confidence and status.

---

## 6. Rendetalje pack

Rendetalje-specific behavior stays outside the generic kernel until evidence from another tenant justifies generalization.

Initial Rendetalje pack responsibilities:

- cleaning service taxonomy;
- cleaning scope and exclusions;
- recurring-cleaning rules;
- pricing policy identity and version;
- deterministic cleaning estimator;
- uncertainty/risk drivers for estimates;
- cleaning checklists and evidence requirements;
- access instructions and special-property rules;
- staffing/time conventions specific to Rendetalje;
- customer communication voice and examples;
- lead-source mappings;
- complaint/damage handling playbooks;
- Rendetalje-specific billing-source mapping;
- tenant adapter configuration for Gmail, Calendar, Drive and current production RenOS during migration.

Current price fixtures such as `349 DKK/hour` and `698 DKK minimum` are historical/current-policy evidence, not Business Ops constants. Every commercial calculation must bind a policy version and provenance.

---

## 7. Conversation and agent interaction

The user-facing experience is one business agent, initially `Rendetalje Ops`, available through web chat and Telegram and later voice/other clients.

The agent is a presentation and orchestration composition, not a database.

Required context flow:

```text
message / voice / attachment
       ↓
Studio conversation reference
       ↓
Context Resolver
       ├─ Business Ops canonical domain reads
       ├─ Rendetalje pack rules/policies
       ├─ bounded provider observations
       ├─ relevant WORKS knowledge/evidence refs
       └─ current mission/run references
       ↓
Runtime worker/model
```

The context resolver must mark source, freshness and uncertainty. Missing state is represented as unknown/degraded; it must not be filled from conversational guesswork.

Operator-facing agent voice and customer-facing Rendetalje writing style are separate versioned profiles.

Internally the single visible agent may delegate to specialist workers such as Inbox, Pipeline, Scheduling, Customer Care, Dispatch, Billing, Follow-up and Reconciliation workers. Worker identity never changes authority.

---

## 8. Action lifecycle

A consequential external effect follows one governed lifecycle:

```text
Domain intent
  -> capability request
  -> AIE authority evaluation
  -> Trust admission / approval if required
  -> Runtime dispatch
  -> WORKS attempt
  -> provider execution
  -> provider receipt
  -> independent read-back
  -> domain reconciliation
  -> evidence reference
```

Business Ops may create a domain-level proposed effect or command request, but must not treat intent creation as execution.

### 8.1 Initial Rendetalje authority policy

| Class | Default |
|---|---|
| Read/search/classify/reconcile/calculate | autonomous |
| Draft customer/staff communication | autonomous preparation |
| Internal low-consequence state update | policy-controlled |
| Send customer/staff communication | owner approval |
| Create/reschedule/cancel customer booking | owner approval |
| Send invoice / change agreed commercial scope | owner approval |
| Refund/payment/price override/destructive action/access/security | explicit per-action approval |

Autonomy may only expand from evidence, never from convenience.

### 8.2 Exactly-once safety

All mutation capabilities require:

- immutable intent identity;
- tenant + actor binding;
- idempotency key;
- admission/approval evidence where required;
- provider receipt;
- read-back confirmation before reconciliation;
- fail-closed handling of ambiguous `executing` states;
- no agent self-approval for owner-gated actions.

The behavior in `Renos-Control` provider-intent tests is a characterization donor, not a platform ownership transfer.

---

## 9. Ports and adapters

Business Ops exposes domain ports. Provider SDKs and legacy applications are adapters.

Initial ports:

```text
CustomerRepository
LeadRepository
ServiceAgreementRepository
WorkOrderRepository
AssignmentRepository
ExecutionActualsRepository
ChargeFactRepository
DomainEventSink
EvidenceReferencePort
CapabilityRequestPort
KnowledgeQueryPort
```

Migration-only adapters:

```text
LegacyRenOSReadAdapter
RenosControlReadAdapter
LegacyIdentityMappingAdapter
LegacyBillingSourceAdapter
```

Provider-facing adapters do not live in the domain kernel. Gmail, Calendar, Drive, WhatsApp, payment providers and model providers are capabilities resolved through the platform integration/capability boundary.

The public Rendetalje website emits normalized lead observations with provenance. It does not write canonical customer/job state directly.

---

## 10. Legacy semantic extraction

### 10.1 `rendetalje-workspace/renos`

Primary donor for:

- current production domain semantics;
- customer/lead/booking relational history;
- tenant-isolation migrations;
- booking execution and quality gates;
- time-entry behavior;
- recurring booking rules;
- deterministic estimator and calibration/backtest behavior;
- Nora read-only policy, context, limits and eval cases;
- current public/internal RenOS product behavior.

Disposition: **EXTRACT + CHARACTERIZE + MIGRATE**.

### 10.2 `Renos-Control`

Primary donor for:

- ServiceLocation;
- ServiceNorm;
- versioned ServiceAgreement;
- WorkOrder;
- Assignment/AssignmentMember;
- Execution/ExecutionActuals correction semantics;
- ChargeSource/charge-readiness concepts;
- provider-intent idempotency, approval, receipt and read-back tests;
- explicit legacy mapping/quarantine semantics.

Disposition: **EXTRACT SEMANTICS + PORT TESTS + REIMPLEMENT OWNERSHIP**.

Generic outbox/runtime/approval/provider/evidence tables from 073–080 are not copied where Aftergraph already has a canonical platform owner.

### 10.3 Historical agent/assistant repositories

Historical Gmail agents, Clawdbot workspaces, assistants, dashboards and backend prototypes may donate:

- communication examples;
- channel/routing UX lessons;
- test cases;
- edge cases;
- operational vocabulary.

They may not donate credentials, operational datasets, ambient authority or obsolete runtime ownership.

Disposition: **CHARACTERIZE SELECTIVELY; RETIRE RUNTIME**.

---

## 11. Migration model

The migration is a strangler migration, one semantic responsibility at a time.

Required lifecycle:

```text
legacy exists
  -> target contract exists
  -> characterization tests pass
  -> target implementation exists
  -> shadow comparison
  -> target becomes authoritative
  -> legacy becomes read-only
  -> all consumers prove migration
  -> legacy archived
```

No big-bang database rewrite is allowed.

### 11.1 Source mapping

Every migrated record must be representable by a migration mapping containing:

```text
source_system
source_entity_type
source_entity_id
target_entity_type
target_entity_id
mapping_status
confidence
source_version_or_snapshot
created_at
reviewed_at?
```

Ambiguous identity mappings are quarantined. They are never guessed.

### 11.2 Initial capability order

The intended order is:

```text
read-only identity/customer
-> leads
-> service location/agreement
-> work orders
-> assignments
-> execution actuals
-> charge facts
-> governed provider actions
-> proactive exception handling
```

Billing invoice truth stays outside Business Ops; Business Ops supplies governed source facts.

---

## 12. Data and event rules

Business Ops must support reproducible state transitions and provenance without becoming a duplicate WORKS ledger.

Rules:

1. Domain state tables represent current canonical business state.
2. Domain events record domain-relevant transitions, not generic runtime attempts.
3. WORKS holds durable execution attempts, retry/recovery and execution evidence.
4. `EvidenceRef` points to evidence with type, source, subject, digest/reference and verification state; it does not duplicate generic raw evidence storage.
5. Corrections are explicit. Historical execution actuals are never destructively rewritten without correction history.
6. Projections may be rebuilt and are never canonical merely because they are convenient.
7. Calendar is a scheduling/dispatch projection and provider surface, not the source of customer/job truth.
8. Gmail/WhatsApp are communication providers/observation sources, not customer-state databases.

---

## 13. API and contract versioning

Business Ops contracts are versioned independently from provider APIs and Rendetalje policy versions.

Minimum version identities:

```text
business-ops-domain/<major.minor>
rendetalje-policy/<version>
rendetalje-estimator/<version>
capability-action/<version or registered experimental ref>
```

Breaking domain changes require a major contract version or an explicit governed migration. Provider adapter changes must not silently alter domain semantics.

External standards such as OAGIS/UBL are interoperability mappings, not the internal object model. Where mappings are introduced, conformance must be tested separately from Business Ops domain conformance.

---

## 14. Characterization and test gates

Implementation starts by porting behavior tests before porting implementation.

Mandatory characterization families:

1. tenant/actor isolation;
2. conversation continuity vs business truth;
3. bounded/redacted agent reads;
4. immutable action intent;
5. approval separation and no self-approval;
6. idempotent provider execution;
7. provider receipt + read-back;
8. append-only/correctable evidence semantics;
9. booking/work-order readiness gates;
10. completion quality gate;
11. verified actuals -> charge readiness;
12. lead identity/intake dedupe;
13. deterministic estimator behavior;
14. communication profile separation;
15. cancellation/failure truth;
16. exception deduplication and attention policy;
17. legacy mapping/quarantine;
   - ambiguous source-to-target identity mappings must produce a quarantined mapping record with `status=AMBIGUOUS`;
   - they must not create or attach a canonical target entity;
   - downstream reads must expose unknown/degraded identity rather than a guessed match;
18. non-compensable authorization/privacy/safety eval gates.

A test pass proves only the bounded contract under test. It does not prove production deployment, data migration correctness or independent outcome verification.

---

## 15. Security migration gate

P−1 found legacy repositories containing tracked credential-like artifacts and operational data artifacts. No secret values are copied into Business Ops, the Rendetalje pack, documentation, issues or model context.

Before a legacy repository is transferred into the Aftergraph organization or used as an import source, security remediation must classify it as one of:

```text
safe-history
history-rewrite-required
credential-revocation-required
operational-data-redaction-required
archive-in-place
```

Rules:

- tracked OAuth/client-secret material is assumed compromised until proven otherwise;
- revocation/rotation precedes reuse;
- deleting a file from the latest commit is insufficient if secret history remains;
- migration tooling must use allowlisted source paths rather than repository-wide copy;
- production credentials are injected through canonical secret handling and never stored in domain configuration.

Security remediation is parallel to P0/P1 design work but blocks affected repo transfer and production adapter activation.

---

## 16. Deployment topology

### 16.1 Primary runtime

The VDS remains the intended always-on execution host for the Rendetalje pilot where Aftergraph runtime services are appropriate.

It may host:

- Runtime workers/adapters;
- Telegram gateway;
- event consumers;
- scheduler hooks;
- Relay/operator services;
- Business Ops application/API deployments as selected by the implementation plan.

The VDS is not the semantic owner merely because it hosts a service.

### 16.2 Lenovo edge node

The Lenovo machine is an optional edge/computer worker for:

- browser automation;
- desktop-only applications;
- local files;
- GPU/local inference;
- explicitly delegated computer-use work.

Normal Business Ops operation must not depend on the Lenovo being online.

### 16.3 Current Rendetalje production

`app.rendetalje.dk` remains authoritative until a capability-specific cutover is proven. No Business Ops implementation may claim production authority because the new repository or schema exists.

Exact deployed source identity for current RenOS must be established before production cutover evidence can rely on exact-head claims.

---

## 17. Proactive operations

Proactivity is an observation/attention function, not ambient authority.

Examples:

- new lead without response;
- unanswered customer message;
- booking/customer mismatch;
- missing access information;
- tomorrow readiness blocker;
- completed execution missing charge source;
- stale lead or follow-up;
- provider reconciliation failure.

These become domain exceptions or attention candidates with provenance, materiality and deduplication. They may automatically start read-only analysis missions where policy permits. They may not grant themselves consequential execution authority.

The primary operator UX is exception-first: completed routine work is summarized, and human interruption is reserved for decisions, material changes and unresolved risk.

---

## 18. Pilot definition of done

Rendetalje Business Ops is not done when a chatbot can answer questions.

The pilot is production-capable only when the following chain is proven for declared workflows:

```text
customer/provider event
  -> identity resolved with provenance
  -> canonical business entity matched
  -> context assembled from authoritative state
  -> domain next action selected
  -> mission/capability request created
  -> authority/admission evaluated
  -> approval obtained when required
  -> provider action executed
  -> provider receipt captured
  -> read-back reconciled
  -> domain state updated
  -> evidence referenced
  -> lifecycle continues without hidden competing truth
```

Required pilot metrics include:

- response latency;
- orphan/stale lead rate;
- scheduling conflict rate;
- first-contact resolution where applicable;
- verified-success rate for governed actions;
- human minutes per operational workflow;
- approval acceptance/rejection rate;
- provider failure/read-back mismatch rate;
- cost per verified outcome;
- exception precision and operator interruption volume.

No target threshold is invented in this design. Baselines must be measured before promotion thresholds are set.

---

## 19. Repository migration policy

Aftergraph becomes canonical technology owner by creating or transferring **current canonical responsibilities**, not by copying every historical repository.

Target repository set for this programme is intentionally small:

```text
Aftergraph/business-ops      generic service-business domain kernel
Aftergraph/rendetalje        Rendetalje tenant/domain pack + migration adapters
Aftergraph/rendetalje-web    optional transferred public surface after security/history review
```

Existing JonasAbde Rendetalje/RenOS repositories are migration donors. Each receives one terminal disposition:

```text
TRANSFER-SAFELY
ARCHIVE-IN-PLACE
RETAIN-AS-PROVENANCE
RETIRE-AFTER-EXTRACTION
```

No legacy repo is copied into a fresh Aftergraph repo merely to make ownership look complete.

---

## 20. P0 exit criteria

P0 design is complete when all of the following are approved and machine-recordable:

1. `business-ops` is accepted as `architecture_plane: null` and `system_class: service-business-domain`.
2. `rendetalje` is accepted as a tenant-domain composition, not a fork of Business Ops.
3. Business Ops ownership and `must_not_own` boundaries are registered.
4. The thin kernel entity list and hard semantic separations are frozen for P1.
5. The Rendetalje-specific pack boundary is explicit.
6. The action lifecycle binds AIE, Trust, Runtime and WORKS instead of duplicating them.
7. The characterization backlog is mapped to donor tests.
8. The source-of-truth transition map is accepted.
9. Security remediation is a blocking gate for affected repo transfer/credential reuse.
10. Current production remains unchanged until shadow/conformance/cutover evidence exists.
11. Production deployment provenance gate: before any capability-specific cutover can be declared complete, the implementation plan must define how exact deployed source identity will be established through build attestation, deploy-log digest, immutable release reference or equivalent evidence. Absence of this provenance invalidates exact-head/cutover verification claims.

### 20.1 P1 readiness gate

P1 implementation planning may begin only when the following are machine-recorded:

1. The four independent-review changes accepted on 2026-09-15 are present in this specification.
2. A `ChargeFact` schema draft and at least one characterization vector exist.
3. A legacy-ID ambiguity/quarantine characterization vector exists.
4. The production deployed-source provenance resolution strategy is documented, even if production attestation execution remains deferred until cutover.
5. Security-remediation status is recorded for every P−1 repository flagged for credential/history risk.
6. The current production database migration ledger/schema inventory has been inspected read-only or, if inaccessible, is explicitly recorded as a blocking dependency with an owner and acquisition method.
7. Privacy-safe cardinality/reconciliation baselines are defined for Customer, Lead, Booking/WorkOrder and Assignment migration classes; raw customer data is not copied into Governance evidence.

After written-spec approval, the next step is an implementation plan. No production migration, repository transfer, domain-schema deployment or provider write is authorized by this document alone.

---

## 21. Architecture invariants

These invariants are normative for the implementation plan:

```text
I-01 Business Ops has no dependency on Rendetalje.
I-02 Rendetalje-specific semantics do not enter the generic kernel without cross-tenant evidence.
I-03 Conversation/session memory is never canonical customer/job/billing truth.
I-04 Domain scheduling assignment is never treated as authority delegation.
I-05 Intent/approval/provider acceptance never equals verified outcome.
I-06 No provider mutation is considered reconciled without receipt + read-back.
I-07 Business Ops does not create a duplicate generic runtime, outbox, approval or evidence plane.
I-08 Legacy identity mapping is explicit; ambiguous mappings quarantine.
I-09 Pricing and estimator behavior bind explicit policy/version provenance.
I-10 Proactivity may create attention or analysis, never ambient execution authority.
I-11 Current production stays authoritative until capability-specific cutover proof exists.
I-12 Repository transfer never bypasses secret/history remediation.
```

These invariants are the acceptance boundary for the subsequent implementation plan.