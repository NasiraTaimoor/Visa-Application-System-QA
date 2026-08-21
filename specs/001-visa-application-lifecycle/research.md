# Research: Visa Application Lifecycle

## Decision: Keep implementation technology unresolved in this plan

**Rationale**: The feature specification explicitly defines business behavior only and does not prescribe language, framework, storage, hosting, or integration protocol. The repository currently contains specification artifacts only, so choosing a concrete stack during planning would exceed validated requirements.

**Alternatives considered**: Selecting a default web stack now was rejected because it would create speculative implementation constraints and conflict with the constitution's minimal, maintainable change principle.

## Decision: Use a modular web application and backend service architecture

**Rationale**: The feature requires applicant-facing journeys, agency operations, finance operations, compliance/audit surfaces, external integrations, background retries, and status notifications. Logical modules allow the implementation to enforce least privilege, test boundaries independently, and preserve traceability without requiring premature microservice decomposition.

**Alternatives considered**: A single monolithic module was rejected because it would blur financial, document, audit, integration, and authorization responsibilities. A distributed microservice-first design was rejected because the repository lacks implementation constraints and the baseline can be planned with bounded modules first.

## Decision: Represent lifecycle behavior as a governed state machine

**Rationale**: The specification includes a status transition matrix with actors/sources, preconditions, failure behavior, audit requirements, and QA acceptance criteria. A state machine makes invalid transitions rejectable without data mutation and supports deterministic tests for all lifecycle paths.

**Alternatives considered**: Ad hoc status updates in each workflow screen were rejected because they increase risk of unauthorized, duplicate, or inconsistent transitions.

## Decision: Treat submitted snapshots, financial records, terminal decisions, and audit events as immutable records

**Rationale**: The constitution requires accurate, traceable records and prevention of unauthorized alteration of completed decisions. Immutable records also support payment disputes, compliance export, incident response, and in-progress case protection during changes.

**Alternatives considered**: Mutable latest-state-only records were rejected because they cannot prove decision rationale, financial lineage, or historical status integrity.

## Decision: Use business-reference idempotency for submissions, wallet events, payments, integrations, and notifications

**Rationale**: QA cases require duplicate clicks, concurrent submission, provider callbacks, retry-after-timeout, late events, and out-of-order events to produce one business outcome. Idempotency keyed by stable case/submission/payment/external references preserves reliability across network and provider failures.

**Alternatives considered**: Request timestamp deduplication was rejected because it is fragile for retries and concurrent operations. Blind replay was rejected because it can duplicate reservations, debits, submissions, and notifications.

## Decision: Orchestrate OCR only after document screening and require human confirmation before use

**Rationale**: The spec requires safe upload handling, OCR confidence warnings, correction of extracted values, and explicit review before OCR data becomes confirmed application data. This keeps low-confidence or mismatched extraction from silently affecting visa processing.

**Alternatives considered**: Directly applying OCR output to passport fields was rejected because it fails AC-002 and SC-003.

## Decision: Use configurable validation rules with severity classes

**Rationale**: Validation must cover required fields, document presence, passport rules, visa-type rules, duplicate risk, agency routing, and rule changes. Severity classes control workflow behavior, override eligibility, display, responsible party, and tests.

**Alternatives considered**: Hard-coded validation checks without severity metadata were rejected because they cannot support overrideable versus non-overrideable findings or role-specific correction flows.

## Decision: Separate wallet lifecycle from payment lifecycle while preserving financial traceability

**Rationale**: Wallet verification happens before sub-agency submission, while provider or operational payments may occur later depending on visa type and external rules. Separate but linked financial records support reservations, debits, releases, refunds, disputes, reconciliation, and fee-version traceability.

**Alternatives considered**: A single payment flag was rejected because it cannot represent wallet reservation, sub-agency funds, provider confirmation, reconciliation, refund, and dispute states safely.

## Decision: Quarantine unmatched, unauthorized, contradictory, or malformed external events

**Rationale**: GDRFA, payment, immigration, and notification providers may produce duplicate, late, out-of-order, incomplete, or contradictory events. Quarantine protects case integrity while preserving operational visibility and audit evidence.

**Alternatives considered**: Rejecting without records was rejected because it loses support evidence. Applying external statuses optimistically was rejected because it risks unauthorized or incorrect decisions.

## Decision: Keep notification content minimal and direct users to authenticated status views

**Rationale**: Notifications must be actionable but avoid unnecessary personal data disclosure. Full status details are available through authorized authenticated views with role-based masking.

**Alternatives considered**: Including full case details in messages was rejected due to privacy, wrong-recipient, and channel security risks.

## Decision: Define test strategy from the QA traceability set

**Rationale**: The specification and QA artifacts already map FR-001 through FR-042 to scenarios and test cases. The plan should preserve that traceability and extend it into automation layers covering API/integration, UI, E2E, regression, performance, accessibility, security, and idempotency.

**Alternatives considered**: Writing unrelated test categories was rejected because it would weaken traceability and increase maintenance cost.
