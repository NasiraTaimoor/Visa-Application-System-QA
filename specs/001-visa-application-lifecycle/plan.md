# Implementation Plan: Visa Application Lifecycle

**Branch**: `001-visa-application-lifecycle` | **Date**: 2026-08-12 | **Spec**: `specs/001-visa-application-lifecycle/spec.md`

**Input**: Feature specification from `specs/001-visa-application-lifecycle/spec.md`, QA scenarios from `specs/001-visa-application-lifecycle/qa-test-scenarios.md`, QA cases from `specs/001-visa-application-lifecycle/qa-test-cases.md`, and constitution from `.specify/memory/constitution.md`.

## Summary

Build the baseline Visa Application System as a secure, auditable web application and integration platform that manages applications from draft intake through document upload, OCR review, validation, wallet verification, sub-agency submission, main agency processing, GDRFA submission, payment, immigration processing, final outcome, notification, retention, and audit review. The plan uses conservative domain boundaries and explicit contracts so implementation can proceed without changing application code during this planning phase.

The architecture separates applicant-facing workflows, agency operations, financial lifecycle, external integrations, notification delivery, audit/event recording, and compliance controls. All state transitions are mediated by a lifecycle workflow service, authorization checks, idempotent command handling, immutable submitted snapshots, and durable audit events.

## Technical Context

**Language/Version**: NEEDS CLARIFICATION. The current repository contains specification artifacts only and the feature spec intentionally does not prescribe language, framework, storage, hosting, or protocol.

**Primary Dependencies**: NEEDS CLARIFICATION for final implementation stack. Required capability classes are identity and access management, relational case storage, object/document storage, OCR provider, document screening provider, wallet or ledger service, GDRFA integration, payment provider, immigration processing source, notification gateway, audit log store, monitoring, and test automation framework.

**Storage**: Planned logical storage includes transactional application data store, immutable audit/event store, protected object storage for documents, wallet/payment ledger integration records, notification delivery records, and operational recovery queues. Concrete product choice is NEEDS CLARIFICATION.

**Testing**: Planned test layers include unit tests, contract tests, API/integration tests, UI tests, accessibility checks, end-to-end workflow tests, regression suites, performance/load tests, security authorization tests, and idempotency/concurrency tests. Concrete tools are NEEDS CLARIFICATION.

**Target Platform**: Web application plus backend service APIs and asynchronous integration workers. Hosting/runtime is NEEDS CLARIFICATION.

**Project Type**: Web application with backend services, frontend user interfaces, external system integrations, background workers, and compliance/audit reporting.

**Performance Goals**: Support at least 10,000 active applications and 500 concurrent authorized users; 95% of supported valid uploads receive accept/reject and OCR status within 2 minutes; 95% of received GDRFA, payment, immigration, and notification status events are visible within 5 minutes; 98% of required notifications are queued within 1 minute; 99.5% of accepted sub-agency submissions create exactly one submission reference and no duplicate wallet reservation.

**Constraints**: WCAG 2.1 AA applicant-facing journeys; least-privilege and agency-scoped access; encryption in transit and at rest where platform support exists; no secrets or sensitive integration details in source, logs, bundles, notifications, or exports; production personal data excluded from non-production unless formally approved, minimized, and protected; submitted snapshots, final decisions, financial records, and audit records immutable except through authorized audited correction.

**Scale/Scope**: FR-001 through FR-042, seven primary user stories, full lifecycle transition matrix, action-level permission matrix, 42 QA scenarios, and 42 traceable QA test cases.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Initial Gate

- **Privacy and Security by Design**: PASS. Plan requires data minimization, role and agency authorization, encryption, masking, secure document handling, protected secrets, and documented third-party data flows.
- **Accurate, Traceable Case Records**: PASS. Plan makes lifecycle commands, document actions, validation results, wallet/payment events, integrations, privileged access, notifications, recovery, and retention actions auditable with actor/source, timestamp, action, result, reason, and correlation reference.
- **Applicant-Centred Accessibility**: PASS. Applicant-facing intake, upload, OCR review, validation errors, status, payment, and session recovery are planned against WCAG 2.1 AA and assistive technology requirements.
- **Testable, Reliable Workflows**: PASS. Plan includes automated tests for happy paths, authorization boundaries, failure handling, idempotency, integration retries, performance, regression, and E2E lifecycle coverage.
- **Minimal, Maintainable Change**: PASS. Plan avoids selecting unvalidated implementation technology and uses explicit bounded modules and versioned contracts rather than speculative product features.

No constitution violations are identified.

### Post-Design Gate

- **Privacy and Security by Design**: PASS. `data-model.md` records classification, retention, legal hold, and masking-relevant entities; contracts avoid exposing secrets and require source validation.
- **Accurate, Traceable Case Records**: PASS. `data-model.md` includes audit, status, submission, payment, wallet, notification, and error/recovery entities; contracts include audit and idempotency requirements.
- **Applicant-Centred Accessibility**: PASS. `quickstart.md` includes manual keyboard/screen-reader validation and automated accessibility checks for applicant workflows.
- **Testable, Reliable Workflows**: PASS. `quickstart.md` maps validation to QA scenarios/cases, API/integration tests, UI tests, E2E, regression, performance, and automation.
- **Minimal, Maintainable Change**: PASS. Contracts are interface-level planning artifacts only; no application code is modified.

## System Architecture

The planned architecture uses these logical modules:

- **Experience layer**: Applicant portal, sub-agency workspace, main agency operations workspace, finance workspace, support workspace, auditor/compliance workspace, and notification preference/status views.
- **API layer**: Versioned backend APIs for case intake, documents, OCR review, validation, wallet verification, submissions, agency processing, GDRFA handoff, payment, immigration updates, notifications, search/export, audit access, and recovery tasks.
- **Domain services**: Application lifecycle workflow service, validation/rules service, document service, OCR orchestration service, wallet/financial lifecycle service, agency processing service, external submission service, payment service, immigration status service, notification service, audit service, retention/compliance service, and authorization policy service.
- **Persistence and eventing**: Transactional case store, immutable submitted snapshots, document object store, audit/event store, idempotency key store, outbox queue, retry/dead-letter or recovery queue, and reporting/export read models.
- **External adapters**: OCR provider, document screening provider, wallet or ledger provider, GDRFA service, payment provider or payment operations source, immigration processing source, identity provider, notification gateways, monitoring, and incident process.

All mutating commands flow through authentication, role/scope authorization, lifecycle transition validation, idempotency validation, domain mutation, audit append, status timeline update, and notification/outbox publishing. External callbacks are matched by trusted source and business reference before they can alter case, financial, or terminal status.

## Application Lifecycle Workflow

Workflow is implemented as a state machine based on the specification transition matrix:

1. Draft created
2. Documents pending
3. OCR and validation
4. Ready for sub-agency review
5. Wallet verified
6. Submitted to main agency
7. Main agency processing
8. Correction requested or GDRFA submitted
9. Payment pending, paid, or payment failed
10. Immigration processing
11. Approved, rejected, cancelled, withdrawn, expired, or closed

Each transition declares allowed actors or external sources, preconditions, failure behavior, recovery owner, audit requirement, and notification rules. Rework loops return cases to the responsible party without deleting submitted snapshots, financial records, audit records, or retained documents.

## Feature Areas

### Applicant and Passport Data

Capture applicant identity, contact, nationality, sponsor, travel, visa type, consent, and passport fields with configurable visa-type requirements. Passport validity defaults to at least six months at sub-agency submission unless a configured exception applies. Drafts can be saved, resumed, abandoned, and retained according to documented policy.

### OCR Integration

Only documents that pass screening are submitted for OCR. OCR output remains advisory until an authorized user reviews, corrects, or confirms it. Critical confidence thresholds use the spec defaults: 85% warning threshold and 60% blocking/manual fallback threshold unless implementation policy config overrides them. Replacements invalidate stale OCR confirmation where required.

### Document Validation

Document service validates type, size, page count, quality, integrity, password protection, malware/security screening, document type fit, versioning, and retention classification. Validation findings classify severity as informational, warning, blocking, overrideable blocking, or non-overrideable blocking.

### Wallet Verification and Financial Lifecycle

Fees are calculated by visa type, agency relationship, stage, currency, and fee version. Sub-agency wallet verification checks available balance before main agency submission, creates exactly one reservation for accepted submission, and supports debit, release, refund, reconciliation, shortfall, reservation expiry, fee changes, and duplicate/concurrent attempts through business-reference idempotency.

### Sub-Agency Processing

Sub-agency officers can create/manage authorized cases, review readiness, correct applicant/document/OCR data, verify wallet balance, reserve funds, and submit validated snapshots to the main agency. Cross-agency wallet or case access is denied server-side and audited.

### Main Agency Processing

Main agency officers and supervisors process routed cases by queue, assignment, correction request, rejection, readiness approval, escalation, and GDRFA submission. Decisions require actor, timestamp, reason/rationale, supporting notes/attachments where required, and audit evidence.

### GDRFA Integration

GDRFA adapter submits readiness-approved snapshots, records payload reference, submission attempt, acknowledgement, rejection, action-required, timeout, retry, duplicate, and unavailable-service outcomes. Responses are source-validated and matched by external reference; unmatched or contradictory responses are quarantined for liaison/support recovery.

### Payment Integration

Payment service tracks required, pending, paid, failed, cancelled, refunded, disputed, and reconciled states. Paid state requires authorized provider confirmation or finance-approved manual reconciliation with receipt, amount, currency, source, and reason. Duplicate callbacks preserve one financial outcome.

### Immigration Processing

Immigration processing receives or records external status updates, action-required events, final decisions, withdrawal, cancellation, expiry, and closure. Terminal outcomes are locked from ordinary changes and any authorized correction is a new audited action.

### Status Management

Status timeline entries include lifecycle state, source, timestamp, responsible party, external reference, result, reason, next action, sensitivity classification, and role-based visibility. Invalid transitions are rejected without mutating case data.

### Notifications

Notification rules send minimal actionable messages for submission, correction, validation failure, wallet shortfall, payment outcomes, GDRFA responses, immigration events, and final decisions. Optional preferences are honored where allowed; mandatory operational/legal notices continue. Delivery attempts, retries, failures, recipient category, and support visibility are recorded.

### Roles and Permissions

Authorization enforces action-level permissions for Applicant, Sub-agency Officer, Main Agency Case Officer, Main Agency Supervisor, Finance Officer, Support Admin, Auditor/Compliance User, Immigration/GDRFA Liaison, Payment Provider, Integration Source, Notification Gateway, and System Service. Checks include role, agency scope, lifecycle state, ownership, source validation, and required business reason.

### Audit Logging

Audit events are durable, tamper-evident, least-privilege readable, searchable, and exportable for authorized compliance needs. Required fields include actor or service identity, role, agency scope, timestamp, action, affected case or record, result, reason where applicable, source, and correlation reference.

### Security

Security controls cover data minimization, encryption, masking, secure upload screening, trusted source validation, server-side authorization, session timeout/resume protection, stronger authentication for privileged roles, protected secrets, safe error messages, data retention/legal hold, incident recording, and privacy/threat review for high-risk changes.

### Accessibility

Applicant-facing forms, upload controls, OCR review, validation findings, status timelines, payment states, notifications, and confirmation messages must meet WCAG 2.1 AA. Required checks include keyboard-only operation, focus management, labels, screen-reader semantics, non-color-only errors, clear copy, timeout handling, and accessible fallback for OCR/manual document review.

## Testing Plan

### API and Integration Testing

Create automated contract and integration tests for case APIs, document upload/screening, OCR, validation, wallet ledger, sub-agency submission, main agency processing, GDRFA, payment, immigration, notifications, audit, search/export, and recovery. Include source validation, idempotency, timeout, retry, duplicate, late, out-of-order, contradictory, and malformed event tests.

### UI Testing

Automate primary applicant, sub-agency, main agency, finance, support, and audit views for forms, missing item guidance, OCR review, validation findings, wallet shortfall, payment status, correction requests, timeline visibility, role-based masking, and safe error messaging. Pair automation with manual exploratory checks for complex document/OCR and compliance workflows.

### End-to-End Testing

Validate applicant-led and sub-agency-led paths from draft through final decision, including document upload, OCR review, validation, wallet reservation, main agency review, GDRFA acknowledgement/rejection, payment, immigration processing, final outcome, notification, and audit review.

### Regression Testing

Maintain traceability from FR-001 through FR-042 to TS-FR-001 through TS-FR-042 and TC-FR-001 through TC-FR-042. Regression suites must cover rule/fee/status/integration changes, in-progress case preservation, authorization boundaries, immutable records, and all lifecycle transition matrix paths.

### Performance Testing

Load and endurance tests must model at least 10,000 active applications and 500 concurrent authorized users. Performance scenarios include application search, draft save/resume, upload/OCR queueing, validation, wallet verification, concurrent submission, integration event ingestion, notification queueing, audit search/export, and recovery queues.

### Test Automation

Automation strategy uses pyramid coverage: unit tests for domain rules and state transitions, contract tests for APIs and external adapters, integration tests for persistence/outbox/idempotency, UI tests for critical workflows, accessibility automation plus manual assistive technology review, E2E smoke and full lifecycle suites, and performance tests in representative environments with synthetic/minimized test data.

## Project Structure

### Documentation (this feature)

```text
specs/001-visa-application-lifecycle/
|-- plan.md
|-- research.md
|-- data-model.md
|-- quickstart.md
|-- contracts/
|   |-- api-contract.md
|   |-- integration-contracts.md
|   `-- ui-contract.md
|-- qa-test-scenarios.md
|-- qa-test-cases.md
|-- spec.md
`-- checklists/
    `-- requirements.md
```

### Source Code (future implementation target)

```text
backend/
|-- src/
|   |-- api/
|   |-- auth/
|   |-- applications/
|   |-- documents/
|   |-- ocr/
|   |-- validation/
|   |-- finance/
|   |-- agencies/
|   |-- integrations/
|   |-- notifications/
|   |-- audit/
|   |-- compliance/
|   `-- recovery/
|-- workers/
`-- tests/
    |-- unit/
    |-- contract/
    |-- integration/
    |-- e2e/
    |-- performance/
    `-- security/

frontend/
|-- src/
|   |-- applicant/
|   |-- sub-agency/
|   |-- main-agency/
|   |-- finance/
|   |-- support/
|   |-- audit/
|   |-- shared/
|   `-- accessibility/
`-- tests/
    |-- ui/
    |-- e2e/
    `-- accessibility/
```

**Structure Decision**: Select a web application with backend APIs/workers and frontend workspaces because the feature requires user-facing applicant flows, multi-role agency operations, external integrations, asynchronous processing, audit/export surfaces, and test automation. This is a planning structure only; no application code is created in this phase.

## Complexity Tracking

No constitution violations or complexity exceptions are required.
