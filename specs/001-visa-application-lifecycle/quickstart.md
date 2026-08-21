# Quickstart: Visa Application Lifecycle Validation

This guide defines validation activities for the implementation phase. It does not include application code or automation scripts.

## Prerequisites

- Test users for Applicant, Sub-agency Officer, Main Agency Case Officer, Main Agency Supervisor, Finance Officer, Support Admin, Auditor/Compliance User, Immigration or GDRFA Liaison, and trusted system/service identities.
- Configured visa types, document requirements, fee schedules, passport validity policy, agency hierarchy, routing rules, wallet accounts, notification rules, retention policy, and permission matrix.
- Stubbed or sandbox integrations for OCR, document screening, wallet/ledger, GDRFA, payment provider, immigration processing, identity, notification gateways, monitoring, and incident/recovery queues.
- Synthetic or formally approved minimized test data only.

## Core Validation Flow

1. Create an applicant-led draft and a sub-agency-led draft.
2. Complete applicant, contact, passport, travel, sponsor, visa type, and consent fields.
3. Save, log out, resume, and verify missing-item guidance and data masking.
4. Upload valid and invalid documents, including boundary size/page/quality cases.
5. Run OCR on screened documents, review confidence, correct mismatches, and confirm values.
6. Run validation and resolve or override findings according to severity and permissions.
7. Verify sub-agency wallet availability, reserve funds, and submit to main agency.
8. Process the case in main agency queue, request correction, approve readiness, and submit to GDRFA.
9. Process GDRFA acknowledgement, rejection, timeout, duplicate, and action-required responses.
10. Move payment through pending, paid, failed, refund, dispute, and reconciliation scenarios.
11. Move immigration processing through action-required and final decision scenarios.
12. Verify final status locking, notification delivery history, audit history, export controls, and retention/legal hold behavior.

## API and Integration Testing

- Validate every command and callback contract in `contracts/api-contract.md` and `contracts/integration-contracts.md`.
- Cover authentication, role/scope authorization, lifecycle preconditions, idempotency keys, audit metadata, error responses, and recovery task creation.
- Test duplicate, late, out-of-order, contradictory, malformed, unauthorized, timeout, retry-limit, and unavailable-service cases for GDRFA, payment, immigration, OCR, document screening, wallet, and notifications.

## UI Testing

- Validate the UI contract in `contracts/ui-contract.md`.
- Cover applicant intake, draft resume, document upload, OCR review, validation findings, status timeline, correction requests, wallet shortfall, payment status, final outcome, agency work queues, finance reconciliation, support recovery, audit search, and export.
- Verify role-based masking and that unavailable actions are hidden or disabled in the UI while server-side authorization remains authoritative.

## End-to-End Testing

- Run at least two complete happy paths: applicant-led and sub-agency-led.
- Run at least one rework path through validation failure, correction request, GDRFA rejection, payment failure, and immigration action-required.
- Confirm every status change creates a status event, notification eligibility evaluation, and audit event.

## Regression Testing

- Maintain traceability to `qa-test-scenarios.md` and `qa-test-cases.md` for FR-001 through FR-042.
- Include regression suites for lifecycle transition matrix enforcement, permission matrix enforcement, immutable snapshots/decisions/financial/audit records, rule changes, fee changes, routing changes, integration contract changes, and in-progress case preservation.

## Performance Testing

- Model at least 10,000 active applications and 500 concurrent authorized users.
- Measure draft save/resume, upload screening, OCR queueing, validation, wallet verification, concurrent submission, integration event ingestion, notification queueing, audit search/export, and recovery queue processing.
- Verify success criteria for upload/OCR status within 2 minutes, integration status visibility within 5 minutes, notification queueing within 1 minute, and duplicate-free accepted submissions.

## Accessibility Testing

- Run automated WCAG checks for applicant-facing screens.
- Perform manual keyboard-only and screen-reader review for intake forms, upload controls, OCR review, validation findings, status timeline, payment status, timeout/session recovery, and final confirmation.
- Confirm errors are field-specific, actionable, not color-only, and focus moves predictably to correction points.

## Test Automation

- Unit tests: validation rules, severity behavior, state machine, permission rules, financial calculations, masking rules.
- Contract tests: APIs and external adapter payloads.
- Integration tests: persistence, outbox, idempotency, queues, callbacks, audit append, retention jobs.
- UI tests: critical workflows and role-specific views.
- E2E tests: full lifecycle happy paths and rework paths.
- Security tests: authorization boundaries, denied attempts, secrets/log masking, sensitive export controls.
- Performance tests: load, concurrency, endurance, queue latency, and export volume.

## Validation Results (T189)

**Executed**: 2026-08-13, against a live `uvicorn` instance of the FastAPI backend (SQLite scaffold store, mocked integrations), driven with real HTTP requests (not the in-process test client), plus the full automated suite.

**Automated suite**: 166 backend tests (contract, integration, unit, e2e, regression, performance-smoke, security) and 37 frontend tests (UI, accessibility) — all passing.

**Core Validation Flow (steps 1-12)**: executed live end to end for an applicant-led tourist-visa case (`VA-000001`) — draft creation, intake completion, resume with correct missing-item guidance and date-of-birth masking, document upload (accepted case), OCR review and confirmation, validation reaching `ready_for_sub_agency_review`, wallet verification and reservation, sub-agency submission, main agency claim and readiness approval, GDRFA acknowledgement, payment confirmation, and immigration final decision (`approved`). The resulting status timeline showed all 11 lifecycle transitions in order, and the audit history showed 21 correctly-ordered audit events including notification dispatch records. A parallel sub-agency-led run (student visa, `VA-000002`) and the four rework paths (validation failure → correction, GDRFA rejection → correction-resolve, payment failure → manual reconciliation, immigration action-required → final decision) are covered by `backend/tests/e2e/`.

**Finding and fix during this execution**: the live resume response for `VA-000001` still listed both required documents as missing *after* they had been uploaded and accepted (and the case had already reached `approved`). Root cause: `completeness_service.calculate_missing_items` unconditionally listed every visa-type-required document type — its own comment noted the result was meant to be "narrowed to 'not yet confirmed uploaded' by caller," but neither `update_intake` nor `resume_draft` performed that narrowing. Fixed by adding `get_accepted_document_types()` and passing it through from both callers; re-verified live that `missing_items` is empty once both documents are accepted. All 166 backend tests still pass.

**Not executed in this pass** (require infrastructure or human participants beyond this session's scope, tracked separately): literal 10,000-application/500-concurrent-user load against real infrastructure (T181/T182 use representative scaled/timing-budget checks instead); manual keyboard/screen-reader accessibility review (T187); moderated usability acceptance session (T192).
