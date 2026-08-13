# Tasks: Visa Application Lifecycle

**Input**: Design documents from `specs/001-visa-application-lifecycle/`
**Prerequisites**: `plan.md`, `spec.md`, `research.md`, `data-model.md`, `contracts/`, `quickstart.md`, `.specify/memory/constitution.md`

**Tests**: Included. The feature spec's "QA and Testing Considerations" section and constitution Principle IV ("Testable, Reliable Workflows") explicitly require automated tests for expected paths, authorization boundaries, and failure handling, so contract, integration, UI, e2e, regression, performance, security, and accessibility tasks are included throughout.

**Organization**: Tasks are grouped by user story (from `spec.md`) to enable independent implementation and testing of each story, following a Setup → Foundational → User Story 1..7 → Polish structure.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no unmet dependencies)
- **[Story]**: Maps the task to a user story (US1–US7); Setup, Foundational, and Polish tasks carry no story label
- Every task states an exact file path

## Path Conventions

Paths follow the Project Structure in `plan.md`:

- Backend: `backend/src/<module>/...`, `backend/workers/`, `backend/tests/{unit,contract,integration,e2e,performance,security}/`
- Frontend: `frontend/src/<workspace>/...`, `frontend/tests/{ui,e2e,accessibility}/`

`plan.md` Technical Context intentionally leaves implementation language/framework as `NEEDS CLARIFICATION` (a deliberate, constitution-aligned decision to avoid selecting unvalidated technology during planning). File paths below are therefore given without a language-specific extension; the concrete extension/module convention is fixed once a technology stack is selected, before implementation begins, without changing the module boundaries or task structure below.

## Traceability

Story and polish tasks reference `qa-test-scenarios.md` (`TS-FR-###`) and `qa-test-cases.md` (`TC-FR-###`), which already map to `spec.md` functional requirements `FR-001`–`FR-042`.

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [ ] T001 Create backend and frontend project directory structure per `plan.md` Project Structure (`backend/src/`, `backend/workers/`, `backend/tests/`, `frontend/src/`, `frontend/tests/`)
- [ ] T002 [P] Initialize backend project scaffold and dependency manifest in `backend/`
- [ ] T003 [P] Initialize frontend project scaffold and dependency manifest in `frontend/`
- [ ] T004 [P] Configure backend linting and formatting tooling in `backend/`
- [ ] T005 [P] Configure frontend linting and formatting tooling in `frontend/`
- [ ] T006 [P] Configure environment/policy configuration management (visa types, document requirements, fee schedules, passport validity policy, agency hierarchy, routing rules, notification rules, retention policy, permission matrix) in `backend/src/config/`
- [ ] T007 [P] Set up CI pipeline skeleton wiring lint, unit, contract, integration, UI, e2e, performance, security, and accessibility stages in `.ci/pipeline`
- [ ] T008 [P] Provision sandbox/stub integration configuration for OCR, document screening, wallet/ledger, GDRFA, payment provider, immigration processing, identity, notification gateways, and monitoring in `backend/tests/fixtures/integrations/`
- [ ] T009 [P] Create synthetic/minimized test data fixtures per `quickstart.md` prerequisites in `backend/tests/fixtures/data/`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [ ] T010 Set up transactional application data store schema and migrations framework in `backend/src/db/`
- [ ] T011 Set up immutable audit/event store schema separate from the transactional store in `backend/src/audit/store/`
- [ ] T012 Set up protected document object storage adapter in `backend/src/documents/storage/`
- [ ] T013 [P] Implement identity and access management integration (authentication, roles, agency scope, privileged-access signals, session controls) in `backend/src/auth/identity_provider.py`
- [ ] T014 [P] Implement role/agency-scope authorization policy service in `backend/src/auth/authorization_policy.py`
- [ ] T015 Implement Agency model and agency hierarchy/routing rules in `backend/src/agencies/models/agency.py` (depends on T010)
- [ ] T016 Implement Visa Application core model and lifecycle status field in `backend/src/applications/models/visa_application.py` (depends on T010, T015)
- [ ] T017 Implement Status Event model in `backend/src/applications/models/status_event.py` (depends on T016)
- [ ] T018 Implement lifecycle workflow state machine enforcing the spec's status transition matrix in `backend/src/applications/workflow/state_machine.py` (depends on T016, T017)
- [ ] T019 Implement Audit Event model and append-only write path in `backend/src/audit/models/audit_event.py` (depends on T011)
- [ ] T020 Implement mandatory audit field validation and an audit-write middleware applied to all mutating commands in `backend/src/audit/audit_middleware.py` (depends on T019)
- [ ] T021 [P] Implement idempotency key store and idempotent-command handling in `backend/src/applications/idempotency/idempotency_store.py` (depends on T010)
- [ ] T022 [P] Implement outbox queue and retry/dead-letter recovery queue in `backend/src/recovery/outbox_queue.py` (depends on T010)
- [ ] T023 [P] Implement Error Record model and base recovery task service in `backend/src/recovery/models/error_record.py` (depends on T010)
- [ ] T024 [P] Implement Consent and Retention Policy model and base policy enforcement in `backend/src/compliance/models/consent_retention_policy.py` (depends on T010)
- [ ] T025 Implement API routing and middleware structure (authentication, authorization, idempotency, audit) applied globally in `backend/src/api/router.py` (depends on T013, T014, T020, T021)
- [ ] T026 Implement centralized error handling with safe user-facing messages and protected diagnostic references in `backend/src/api/error_handler.py` (depends on T023)
- [ ] T027 [P] Configure structured logging with secret/PII masking in `backend/src/observability/logging.py`
- [ ] T028 [P] Configure monitoring and incident event emission hooks in `backend/src/observability/monitoring.py`
- [ ] T029 [P] Implement shared frontend design-system primitives (accessible form controls, error summary, focus management) in `frontend/src/shared/components/`
- [ ] T030 [P] Implement role-based frontend routing/layout shell for applicant, sub-agency, main agency, finance, support, and audit workspaces in `frontend/src/shared/layout/`
- [ ] T031 [P] Set up backend test harness (unit, contract, integration, e2e, performance, security) with shared fixtures in `backend/tests/`
- [ ] T032 [P] Set up frontend test harness (UI, e2e, accessibility) with shared fixtures in `frontend/tests/`
- [ ] T033 [P] Configure automated WCAG 2.1 AA accessibility testing tooling in `frontend/tests/accessibility/`

**Checkpoint**: Foundation ready — user story implementation can now begin.

---

## Phase 3: User Story 1 - Applicant starts and completes a visa application (Priority: P1) 🎯 MVP

**Goal**: Applicant or sub-agency officer can create an application, enter required applicant/passport/contact/travel/visa/consent data, save progress, resume safely, and see what remains before submission.

**Independent Test**: Create a new application, complete required fields, interrupt and resume the session, and confirm the application reaches a complete-but-not-submitted state without exposing personal data to unauthorized users.

### Tests for User Story 1

- [ ] T034 [P] [US1] Contract test for Create application API in `backend/tests/contract/test_create_application.py`
- [ ] T035 [P] [US1] Contract test for Update intake API in `backend/tests/contract/test_update_intake.py`
- [ ] T036 [P] [US1] Contract test for Resume draft API in `backend/tests/contract/test_resume_draft.py`
- [ ] T037 [P] [US1] Contract test for Abandon draft API in `backend/tests/contract/test_abandon_draft.py`
- [ ] T038 [P] [US1] Integration test for draft save/interrupt/resume/missing-item journey in `backend/tests/integration/test_intake_lifecycle.py`
- [ ] T039 [P] [US1] Integration test denying unauthorized draft creation/resume (scope/consent prerequisites) in `backend/tests/integration/test_intake_authorization.py`

### Implementation for User Story 1

- [ ] T040 [P] [US1] Implement Applicant model in `backend/src/applications/models/applicant.py`
- [ ] T041 [P] [US1] Implement Passport intake-fields model in `backend/src/applications/models/passport.py`
- [ ] T042 [US1] Implement consent capture linked to Consent and Retention Policy in `backend/src/applications/intake/consent_service.py` (depends on T040, T024)
- [ ] T043 [US1] Implement intake completeness/missing-item calculation service in `backend/src/applications/intake/completeness_service.py` (depends on T040, T041, T016)
- [ ] T044 [US1] Implement Create application command (scope/consent check, single draft, single audit event) in `backend/src/applications/intake/create_application.py` (depends on T018, T042)
- [ ] T045 [US1] Implement Update intake command (save applicant/contact/passport/travel/sponsor/visa/consent fields with versioning) in `backend/src/applications/intake/update_intake.py` (depends on T044, T043)
- [ ] T046 [US1] Implement Resume draft command with role-based data masking in `backend/src/applications/intake/resume_draft.py` (depends on T044)
- [ ] T047 [US1] Implement Abandon draft command per retention rules in `backend/src/applications/intake/abandon_draft.py` (depends on T044, T024)
- [ ] T048 [US1] Wire Create/Update/Resume/Abandon commands to API routes in `backend/src/api/applications_routes.py` (depends on T025, T044, T045, T046, T047)
- [ ] T049 [US1] Emit audit events for creation, edit, resume, and abandon actions in `backend/src/applications/intake/create_application.py`, `update_intake.py`, `resume_draft.py`, `abandon_draft.py` (depends on T020, T044, T045, T046, T047)
- [ ] T050 [P] [US1] Build application creation screen in `frontend/src/applicant/pages/create_application`
- [ ] T051 [P] [US1] Build draft intake form with field requirements/examples in `frontend/src/applicant/pages/draft_intake`
- [ ] T052 [P] [US1] Build missing-items summary component in `frontend/src/applicant/components/missing_items`
- [ ] T053 [P] [US1] Build session recovery / resume flow with masked-data handling in `frontend/src/applicant/pages/session_recovery`
- [ ] T054 [US1] Build sub-agency intake-on-behalf entry point in `frontend/src/sub-agency/pages/create_on_behalf` (depends on T050)
- [ ] T055 [P] [US1] UI test for intake creation, save, resume, and missing-item guidance in `frontend/tests/ui/test_intake_flow`
- [ ] T056 [P] [US1] Accessibility test (keyboard + screen reader) for intake forms in `frontend/tests/accessibility/test_intake_a11y`
- [ ] T057 [US1] Record User Story 1 traceability to `TS-FR-001`–`TS-FR-004` and `TC-FR-001`–`TC-FR-004` in `backend/tests/integration/test_intake_lifecycle.py`

**Checkpoint**: User Story 1 is fully functional and independently testable.

---

## Phase 4: User Story 2 - Applicant uploads documents and reviews OCR results (Priority: P1)

**Goal**: Upload passport/supporting documents, receive OCR-extracted data, review confidence warnings, correct extracted values, and submit only validated document data.

**Independent Test**: Upload required documents, verify accepted and rejected file outcomes, review OCR output, correct a mismatch, and confirm the corrected data is used for validation.

### Tests for User Story 2

- [ ] T058 [P] [US2] Contract test for Upload document API in `backend/tests/contract/test_upload_document.py`
- [ ] T059 [P] [US2] Contract test for Replace document API in `backend/tests/contract/test_replace_document.py`
- [ ] T060 [P] [US2] Contract test for Get OCR result API in `backend/tests/contract/test_get_ocr_result.py`
- [ ] T061 [P] [US2] Contract test for Confirm OCR values API in `backend/tests/contract/test_confirm_ocr_values.py`
- [ ] T062 [P] [US2] Contract test for Validate application API in `backend/tests/contract/test_validate_application.py`
- [ ] T063 [P] [US2] Integration test for upload → screen → OCR → review → correct → validate flow in `backend/tests/integration/test_document_ocr_validation.py`
- [ ] T064 [P] [US2] Integration test for rejected uploads (type/size/quality/corruption/security) keeping the case editable in `backend/tests/integration/test_upload_rejection.py`
- [ ] T065 [P] [US2] Integration test for OCR mismatch blocking submission until correction or authorized override in `backend/tests/integration/test_ocr_mismatch.py`

### Implementation for User Story 2

- [ ] T066 [P] [US2] Implement Document model with versioning and retention classification in `backend/src/documents/models/document.py`
- [ ] T067 [P] [US2] Implement OCR Result model in `backend/src/ocr/models/ocr_result.py`
- [ ] T068 [P] [US2] Implement Validation Finding model with severity classification in `backend/src/validation/models/validation_finding.py`
- [ ] T069 [US2] Implement document screening adapter (type/size/page/quality/integrity/password/malware checks) in `backend/src/documents/screening_adapter.py` (depends on T066, T012)
- [ ] T070 [US2] Implement document upload/replace service with version history in `backend/src/documents/document_service.py` (depends on T066, T069)
- [ ] T071 [US2] Implement OCR orchestration service gated on passed screening in `backend/src/ocr/ocr_orchestration_service.py` (depends on T067, T069)
- [ ] T072 [US2] Implement OCR review/confirmation service applying confidence thresholds (85% warning, 60% blocking) in `backend/src/ocr/ocr_review_service.py` (depends on T071)
- [ ] T073 [US2] Implement validation rules engine (required fields, document presence, passport rules, visa-type rules, duplicate risk, agency rules) with severity outcomes in `backend/src/validation/validation_engine.py` (depends on T068, T072)
- [ ] T074 [US2] Implement override approval handling for overrideable blocking findings in `backend/src/validation/override_service.py` (depends on T073)
- [ ] T075 [US2] Wire upload/replace/OCR/validate endpoints to API routes in `backend/src/api/documents_routes.py` (depends on T025, T070, T071, T072, T073, T074)
- [ ] T076 [US2] Emit audit events for upload, replacement, screening, OCR review, validation, and override actions in `backend/src/documents/document_service.py`, `backend/src/ocr/ocr_review_service.py`, `backend/src/validation/validation_engine.py` (depends on T020, T070, T072, T073, T074)
- [ ] T077 [P] [US2] Build document upload screen with boundary guidance in `frontend/src/applicant/pages/document_upload`
- [ ] T078 [P] [US2] Build OCR review and correction screen in `frontend/src/applicant/pages/ocr_review`
- [ ] T079 [P] [US2] Build validation findings screen with corrective action guidance in `frontend/src/applicant/pages/validation_findings`
- [ ] T080 [P] [US2] Build accessible manual fallback for unavailable/unusable OCR in `frontend/src/applicant/pages/ocr_manual_fallback`
- [ ] T081 [P] [US2] UI test for upload, OCR review, correction, and validation findings in `frontend/tests/ui/test_document_ocr_flow`
- [ ] T082 [P] [US2] Accessibility test for upload controls and OCR review in `frontend/tests/accessibility/test_document_ocr_a11y`
- [ ] T083 [US2] Record User Story 2 traceability to `TS-FR-005`–`TS-FR-011`, `TS-FR-037`, `TS-FR-042` and matching `TC-FR` entries in `backend/tests/integration/test_document_ocr_validation.py`

**Checkpoint**: User Stories 1 AND 2 both work independently.

---

## Phase 5: User Story 3 - Sub-agency verifies wallet and submits to main agency (Priority: P1)

**Goal**: Review a completed application, verify sub-agency wallet availability, reserve the required amount, and submit to the main agency.

**Independent Test**: Prepare a validated application, perform a wallet check, submit with sufficient funds, and confirm duplicate submissions are blocked.

### Tests for User Story 3

- [ ] T084 [P] [US3] Contract test for Calculate fees API in `backend/tests/contract/test_calculate_fees.py`
- [ ] T085 [P] [US3] Contract test for Verify wallet / Record wallet event APIs in `backend/tests/contract/test_wallet_events.py`
- [ ] T086 [P] [US3] Contract test for Submit to main agency API in `backend/tests/contract/test_submit_main_agency.py`
- [ ] T087 [P] [US3] Integration test for sufficient-balance submission creating exactly one reservation and one submission reference in `backend/tests/integration/test_wallet_submit_success.py`
- [ ] T088 [P] [US3] Integration test for insufficient-balance submission blocked without reservation in `backend/tests/integration/test_wallet_shortfall.py`
- [ ] T089 [P] [US3] Integration test for concurrent/duplicate submission attempts producing one reservation and one submission in `backend/tests/integration/test_submission_idempotency.py`

### Implementation for User Story 3

- [ ] T090 [P] [US3] Implement Wallet Ledger Event model in `backend/src/finance/models/wallet_ledger_event.py`
- [ ] T091 [P] [US3] Implement Submission model (sub-agency submission type) in `backend/src/applications/models/submission.py`
- [ ] T092 [US3] Implement fee calculation service (visa type, agency relationship, stage, fee version) in `backend/src/finance/fee_calculation_service.py` (depends on T090)
- [ ] T093 [US3] Implement wallet adapter for available-balance checks, reservation, debit, release, refund, and reconciliation in `backend/src/integrations/wallet_adapter.py` (depends on T090)
- [ ] T094 [US3] Implement wallet financial-lifecycle service (verify, reserve, debit, release, refund, reconcile) enforcing BR-007, BR-022, BR-024, BR-025, BR-026 in `backend/src/finance/wallet_lifecycle_service.py` (depends on T092, T093)
- [ ] T095 [US3] Implement sub-agency submission service (snapshot lock, single reservation, submission reference, idempotency key) in `backend/src/applications/submission/sub_agency_submission_service.py` (depends on T091, T094, T021)
- [ ] T096 [US3] Wire fee/wallet/submission endpoints to API routes with agency-scope enforcement in `backend/src/api/finance_routes.py` (depends on T025, T092, T093, T094, T095)
- [ ] T097 [US3] Emit audit events for fee calculation, balance checks, reservation, and submission in `backend/src/finance/wallet_lifecycle_service.py`, `backend/src/applications/submission/sub_agency_submission_service.py` (depends on T020, T092, T094, T095)
- [ ] T098 [P] [US3] Build wallet verification and shortfall screen in `frontend/src/sub-agency/pages/wallet_verification`
- [ ] T099 [P] [US3] Build submission confirmation and submitted-snapshot lock screen in `frontend/src/sub-agency/pages/submission_confirmation`
- [ ] T100 [P] [US3] UI test for wallet verification, shortfall display, and submission in `frontend/tests/ui/test_wallet_submission_flow`
- [ ] T101 [US3] Record User Story 3 traceability to `TS-FR-012`–`TS-FR-016`, `TS-FR-038` and matching `TC-FR` entries in `backend/tests/integration/test_wallet_submit_success.py`

**Checkpoint**: User Stories 1–3 all work independently.

---

## Phase 6: User Story 4 - Main agency processes and submits to GDRFA (Priority: P1)

**Goal**: Review submitted applications, request corrections, approve internal readiness, submit eligible applications to GDRFA, and track acknowledgement or rejection.

**Independent Test**: Receive a sub-agency submission, request additional information, accept a corrected case, submit to GDRFA, and verify acknowledgement is reflected in the case timeline.

### Tests for User Story 4

- [ ] T102 [P] [US4] Contract test for Process main agency action API in `backend/tests/contract/test_process_main_agency_action.py`
- [ ] T103 [P] [US4] Contract test for Submit to GDRFA API in `backend/tests/contract/test_submit_gdrfa.py`
- [ ] T104 [P] [US4] Integration test for routing, assignment, correction request, and readiness approval in `backend/tests/integration/test_main_agency_processing.py`
- [ ] T105 [P] [US4] Integration test for GDRFA acknowledgement, rejection, action-required, timeout, and duplicate outcomes in `backend/tests/integration/test_gdrfa_outcomes.py`
- [ ] T106 [P] [US4] Integration test denying cross-agency case processing in `backend/tests/integration/test_main_agency_authorization.py`

### Implementation for User Story 4

- [ ] T107 [P] [US4] Implement Processing Task model in `backend/src/agencies/models/processing_task.py`
- [ ] T108 [P] [US4] Implement External Case Response model in `backend/src/integrations/models/external_case_response.py`
- [ ] T109 [US4] Implement main agency routing/queue/assignment service in `backend/src/agencies/main_agency_queue_service.py` (depends on T015, T107)
- [ ] T110 [US4] Implement correction request service (reason, responsible party, due date) in `backend/src/agencies/correction_request_service.py` (depends on T109)
- [ ] T111 [US4] Implement readiness approval and escalation service in `backend/src/agencies/readiness_approval_service.py` (depends on T109)
- [ ] T112 [US4] Implement GDRFA submission adapter (payload reference, submission attempt, idempotency key) in `backend/src/integrations/gdrfa_adapter.py` (depends on T108, T021)
- [ ] T113 [US4] Implement GDRFA response handling service (ack/reject/action-required/timeout/duplicate/unavailable, source validation, quarantine) in `backend/src/integrations/gdrfa_response_service.py` (depends on T112)
- [ ] T114 [US4] Wire main agency processing and GDRFA endpoints to API routes with agency-scope enforcement in `backend/src/api/main_agency_routes.py` (depends on T025, T109, T110, T111, T112, T113)
- [ ] T115 [US4] Emit audit events for assignment, decisions, GDRFA submission, and GDRFA responses in `backend/src/agencies/readiness_approval_service.py`, `backend/src/integrations/gdrfa_response_service.py` (depends on T020, T109, T110, T111, T113)
- [ ] T116 [P] [US4] Build routed queue and assignment screen in `frontend/src/main-agency/pages/case_queue`
- [ ] T117 [P] [US4] Build case review, correction request, and decision/rationale capture screen in `frontend/src/main-agency/pages/case_review`
- [ ] T118 [P] [US4] Build readiness approval and GDRFA submission/response screen in `frontend/src/main-agency/pages/gdrfa_submission`
- [ ] T119 [P] [US4] UI test for main agency queue, correction request, readiness approval, and GDRFA response handling in `frontend/tests/ui/test_main_agency_flow`
- [ ] T120 [US4] Record User Story 4 traceability to `TS-FR-017`–`TS-FR-021` and matching `TC-FR` entries in `backend/tests/integration/test_main_agency_processing.py`

**Checkpoint**: User Stories 1–4 all work independently.

---

## Phase 7: User Story 5 - Payment and immigration processing are tracked end to end (Priority: P1)

**Goal**: Initiate/confirm required payments, reconcile payment outcomes, track immigration processing status, and record final approval, rejection, cancellation, expiry, or withdrawal.

**Independent Test**: Move a GDRFA-accepted case through payment, immigration processing, final decision, and status publication with a complete audit trail.

### Tests for User Story 5

- [ ] T121 [P] [US5] Contract test for Record payment event API in `backend/tests/contract/test_record_payment_event.py`
- [ ] T122 [P] [US5] Contract test for Manual reconciliation API in `backend/tests/contract/test_manual_reconciliation.py`
- [ ] T123 [P] [US5] Contract test for Record immigration update API in `backend/tests/contract/test_record_immigration_update.py`
- [ ] T124 [P] [US5] Integration test for payment pending-to-paid via authorized confirmation in `backend/tests/integration/test_payment_success.py`
- [ ] T125 [P] [US5] Integration test for payment failure/dispute/refund routing to finance review in `backend/tests/integration/test_payment_failure.py`
- [ ] T126 [P] [US5] Integration test for duplicate payment callback preserving one financial outcome in `backend/tests/integration/test_payment_idempotency.py`
- [ ] T127 [P] [US5] Integration test for immigration processing through action-required to final decision and terminal lock in `backend/tests/integration/test_immigration_final_decision.py`
- [ ] T128 [P] [US5] Integration test for contradictory/unmatched immigration status quarantine in `backend/tests/integration/test_immigration_quarantine.py`

### Implementation for User Story 5

- [ ] T129 [P] [US5] Implement Payment model in `backend/src/finance/models/payment.py`
- [ ] T130 [US5] Implement payment provider adapter (initiation, confirmation, receipt, dispute, refund) in `backend/src/integrations/payment_adapter.py` (depends on T129, T021)
- [ ] T131 [US5] Implement payment state service (required/pending/paid/failed/cancelled/refunded/disputed/reconciled) enforcing payment business rules and triggering wallet debit/release per BR-023 in `backend/src/finance/payment_service.py` (depends on T129, T130, T094)
- [ ] T132 [US5] Implement finance-approved manual reconciliation service in `backend/src/finance/reconciliation_service.py` (depends on T131)
- [ ] T133 [US5] Implement immigration processing adapter (received/under review/action required/final decision) in `backend/src/integrations/immigration_adapter.py` (depends on T108, T021)
- [ ] T134 [US5] Implement immigration status service with source validation and quarantine of contradictory/unmatched updates in `backend/src/agencies/immigration_status_service.py` (depends on T133)
- [ ] T135 [US5] Implement terminal outcome locking service preventing unauthorized changes to final status in `backend/src/applications/workflow/terminal_lock_service.py` (depends on T018, T134)
- [ ] T136 [US5] Wire payment, reconciliation, and immigration-update endpoints to API routes in `backend/src/api/payment_immigration_routes.py` (depends on T025, T131, T132, T134, T135)
- [ ] T137 [US5] Emit audit events for payment events, reconciliation, immigration updates, and terminal lock in `backend/src/finance/payment_service.py`, `backend/src/agencies/immigration_status_service.py` (depends on T020, T131, T132, T134, T135)
- [ ] T138 [P] [US5] Build finance payment queue and reconciliation screen in `frontend/src/finance/pages/payment_queue`
- [ ] T139 [P] [US5] Build immigration processing status and final outcome screen in `frontend/src/applicant/pages/final_outcome`
- [ ] T140 [P] [US5] UI test for payment states and final outcome display in `frontend/tests/ui/test_payment_immigration_flow`
- [ ] T141 [US5] Record User Story 5 traceability to `TS-FR-022`–`TS-FR-024` and matching `TC-FR` entries in `backend/tests/integration/test_payment_success.py`

**Checkpoint**: User Stories 1–5 work independently — the full P1 lifecycle (draft through final decision) is complete.

---

## Phase 8: User Story 6 - Users receive status updates and notifications (Priority: P2)

**Goal**: Applicants, sub-agencies, and main agency staff receive status updates and notifications for important case events, missing information, payment outcomes, and final decisions.

**Independent Test**: Trigger status changes and verify the correct recipients receive non-sensitive notification content while the full status remains available to authorized users.

### Tests for User Story 6

- [ ] T142 [P] [US6] Contract test for Create notification preference API in `backend/tests/contract/test_notification_preference.py`
- [ ] T143 [P] [US6] Contract test for Get status timeline API in `backend/tests/contract/test_status_timeline.py`
- [ ] T144 [P] [US6] Integration test for notification triggering on submission, correction, validation failure, wallet shortfall, payment, GDRFA, immigration, and final-decision events in `backend/tests/integration/test_notification_triggers.py`
- [ ] T145 [P] [US6] Integration test for notification retry exhaustion recorded and visible to support without blocking the case workflow in `backend/tests/integration/test_notification_failure.py`

### Implementation for User Story 6

- [ ] T146 [P] [US6] Implement Notification model in `backend/src/notifications/models/notification.py`
- [ ] T147 [US6] Implement notification rules engine mapping lifecycle events to recipient categories and minimal content in `backend/src/notifications/notification_rules_engine.py` (depends on T146)
- [ ] T148 [US6] Implement notification gateway adapter with delivery attempt/result/retry tracking in `backend/src/integrations/notification_gateway_adapter.py` (depends on T146, T021)
- [ ] T149 [US6] Implement notification preference management honoring mandatory operational/legal notices in `backend/src/notifications/preference_service.py` (depends on T147)
- [ ] T150 [US6] Implement role-filtered status timeline query service in `backend/src/applications/status/status_timeline_service.py` (depends on T017)
- [ ] T151 [US6] Wire notification and status-timeline endpoints to API routes in `backend/src/api/notifications_routes.py` (depends on T025, T147, T148, T149, T150)
- [ ] T152 [US6] Emit audit events for notification delivery attempts, retries, and failures in `backend/src/notifications/notification_rules_engine.py`, `backend/src/integrations/notification_gateway_adapter.py` (depends on T020, T147, T148)
- [ ] T153 [P] [US6] Build notification preferences screen in `frontend/src/applicant/pages/notification_preferences`
- [ ] T154 [P] [US6] Build role-appropriate status timeline component shared across workspaces in `frontend/src/shared/components/status_timeline`
- [ ] T155 [P] [US6] UI test for status timeline visibility and notification preferences in `frontend/tests/ui/test_notifications_status`
- [ ] T156 [US6] Record User Story 6 traceability to `TS-FR-025`–`TS-FR-028` and matching `TC-FR` entries in `backend/tests/integration/test_notification_triggers.py`

**Checkpoint**: User Stories 1–6 all work independently.

---

## Phase 9: User Story 7 - Auditors and support staff trace case history (Priority: P1)

**Goal**: Auditors and authorized support staff can inspect a complete, tamper-evident history of application changes, document actions, validations, wallet events, payments, external submissions, status updates, privileged access, and errors.

**Independent Test**: Perform representative actions across the lifecycle and confirm each action appears in the audit history with actor, time, action, affected case, result, and reason where applicable.

### Tests for User Story 7

- [ ] T157 [P] [US7] Contract test for Get audit history API in `backend/tests/contract/test_audit_history.py`
- [ ] T158 [P] [US7] Contract test for Search cases and Export records APIs in `backend/tests/contract/test_search_export.py`
- [ ] T159 [P] [US7] Contract test for Get/Resolve recovery task APIs in `backend/tests/contract/test_recovery_tasks.py`
- [ ] T160 [P] [US7] Integration test verifying a complete audit trail across intake, submission, payment, and decision actions in `backend/tests/integration/test_audit_trace_complete.py`
- [ ] T161 [P] [US7] Integration test recording a support access event and business reason in `backend/tests/integration/test_support_access_audit.py`
- [ ] T162 [P] [US7] Security test denying unauthorized audit/export access in `backend/tests/security/test_audit_access_control.py`

### Implementation for User Story 7

- [ ] T163 [US7] Implement audit search/query service with role-based access and masking in `backend/src/audit/audit_search_service.py` (depends on T019)
- [ ] T164 [US7] Implement compliance export service with audited export events in `backend/src/compliance/export_service.py` (depends on T163)
- [ ] T165 [US7] Implement recovery task query and resolution service in `backend/src/recovery/recovery_task_service.py` (depends on T022, T023)
- [ ] T166 [US7] Implement support access reason capture and audit linkage in `backend/src/audit/support_access_service.py` (depends on T019)
- [ ] T167 [US7] Wire audit, search, export, and recovery endpoints to API routes with compliance-scope enforcement in `backend/src/api/audit_routes.py` (depends on T025, T163, T164, T165, T166)
- [ ] T168 [P] [US7] Build audit history and lifecycle timeline screen in `frontend/src/audit/pages/audit_history`
- [ ] T169 [P] [US7] Build export filters and retention/legal-hold view in `frontend/src/audit/pages/export_compliance`
- [ ] T170 [P] [US7] Build support recovery task and masked case lookup screen in `frontend/src/support/pages/recovery_tasks`
- [ ] T171 [P] [US7] UI test for audit history, export controls, and support recovery in `frontend/tests/ui/test_audit_support_flow`
- [ ] T172 [US7] Record User Story 7 traceability to `TS-FR-029`–`TS-FR-034`, `TS-FR-036`, `TS-FR-039`–`TS-FR-041` and matching `TC-FR` entries in `backend/tests/integration/test_audit_trace_complete.py`

**Checkpoint**: All user stories are independently functional.

---

## Phase 10: Polish & Cross-Cutting Concerns

**Purpose**: Coverage and hardening that spans multiple user stories

- [ ] T173 [P] Validate full `FR-001`–`FR-042` to `TS-FR`/`TC-FR` regression traceability matrix in `backend/tests/regression/test_traceability_matrix.py`
- [ ] T174 [P] Regression suite for lifecycle transition matrix enforcement across all statuses in `backend/tests/regression/test_status_transition_matrix.py`
- [ ] T175 [P] Regression suite for action-level permission matrix enforcement across all roles in `backend/tests/regression/test_permission_matrix.py`
- [ ] T176 [P] Regression suite confirming immutability of submitted snapshots, final decisions, financial records, and audit records in `backend/tests/regression/test_immutable_records.py`
- [ ] T177 [P] Regression suite for in-progress case preservation during rule/fee/routing/integration changes in `backend/tests/regression/test_rule_change_preservation.py`
- [ ] T178 [P] End-to-end applicant-led full lifecycle smoke suite (draft through final decision) in `backend/tests/e2e/test_e2e_applicant_led.py`
- [ ] T179 [P] End-to-end sub-agency-led full lifecycle smoke suite in `backend/tests/e2e/test_e2e_sub_agency_led.py`
- [ ] T180 [P] End-to-end rework-path suite (validation failure, correction, GDRFA rejection, payment failure, immigration action-required) in `backend/tests/e2e/test_e2e_rework_paths.py`
- [ ] T181 [P] Performance/load test for 10,000 active applications and 500 concurrent users across search, draft save/resume, upload/OCR queueing, wallet verification, concurrent submission, integration ingestion, notification queueing, and audit search/export in `backend/tests/performance/test_load_scale.py`
- [ ] T182 [P] Performance test validating SC-002, SC-006, SC-010 timing thresholds (2-minute OCR/upload status, 5-minute integration visibility, 1-minute notification queueing) in `backend/tests/performance/test_sla_thresholds.py`
- [ ] T183 [P] Security test sweep for authorization boundaries across all roles and agency scopes in `backend/tests/security/test_authorization_boundaries.py`
- [ ] T184 [P] Security test for secrets/PII exclusion from logs, notifications, exports, and client bundles in `backend/tests/security/test_secrets_pii_exclusion.py`
- [ ] T185 [P] Security test for encryption-in-transit/at-rest configuration verification in `backend/tests/security/test_encryption_config.py`
- [ ] T186 [P] Full WCAG 2.1 AA automated accessibility sweep across applicant-facing screens in `frontend/tests/accessibility/test_wcag_full_sweep`
- [ ] T187 Execute the manual keyboard/screen-reader accessibility review checklist and record results in `specs/001-visa-application-lifecycle/checklists/accessibility-manual-review.md`
- [ ] T188 [P] Idempotency/concurrency regression suite for submissions, wallet events, payments, immigration updates, and notification retries in `backend/tests/regression/test_idempotency_concurrency.py`
- [ ] T189 Execute the full `quickstart.md` validation flow end-to-end and record results in `specs/001-visa-application-lifecycle/quickstart.md`
- [ ] T190 [P] Update API, integration, and UI contract documentation to reflect the final implementation in `specs/001-visa-application-lifecycle/contracts/`
- [ ] T191 Code cleanup and refactoring pass across `backend/src/` and `frontend/src/` modules

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — can start immediately.
- **Foundational (Phase 2)**: Depends on Setup completion — BLOCKS all user stories.
- **User Stories (Phase 3–9)**: All depend on Foundational phase completion.
  - US1–US5 and US7 are Priority P1; US6 is Priority P2.
  - Stories can proceed in parallel (if staffed) or sequentially in priority order.
  - US3 (wallet) depends on validated data from US2; US4 (GDRFA) depends on submissions from US3; US5 (payment/immigration) depends on GDRFA acceptance from US4; US7 (audit) depends on Audit Event infrastructure from Phase 2 and reads events emitted by every other story; US6 (notifications) depends on Status Event infrastructure from Phase 2 and reads events emitted by every other story. Despite these data dependencies, each story remains independently testable using the fixtures/stubs from Phase 1/2.
- **Polish (Phase 10)**: Depends on all desired user stories being complete.

### Within Each User Story

- Tests are written first and must fail before implementation.
- Models before services.
- Services before endpoints.
- Core implementation before UI, UI before UI tests.
- Story complete (checkpoint) before moving to the next priority.

### Parallel Opportunities

- All Setup tasks marked `[P]` can run in parallel.
- All Foundational tasks marked `[P]` can run in parallel within Phase 2.
- Once Foundational completes, US1, US2 (after US1 models), US6, and US7 (after Phase 2 audit infra) can start in parallel; US3 needs US2's validated-data path, US4 needs US3's submission, US5 needs US4's GDRFA acceptance.
- All tests for a user story marked `[P]` can run in parallel.
- Models within a story marked `[P]` can run in parallel.
- Different user stories can be worked on in parallel by different developers once their upstream data dependency exists.

---

## Parallel Example: User Story 1

```bash
# Launch all tests for User Story 1 together:
Task: "Contract test for Create application API in backend/tests/contract/test_create_application.py"
Task: "Contract test for Update intake API in backend/tests/contract/test_update_intake.py"
Task: "Contract test for Resume draft API in backend/tests/contract/test_resume_draft.py"
Task: "Contract test for Abandon draft API in backend/tests/contract/test_abandon_draft.py"
Task: "Integration test for draft save/interrupt/resume/missing-item journey in backend/tests/integration/test_intake_lifecycle.py"

# Launch all models for User Story 1 together:
Task: "Implement Applicant model in backend/src/applications/models/applicant.py"
Task: "Implement Passport intake-fields model in backend/src/applications/models/passport.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL — blocks all stories)
3. Complete Phase 3: User Story 1
4. **STOP and VALIDATE**: Test User Story 1 independently
5. Deploy/demo if ready

### Incremental Delivery (recommended for this feature)

Because 6 of 7 stories are Priority P1 and each depends on data produced by the previous stage of the lifecycle, deliver in this order:

1. Setup + Foundational → Foundation ready
2. US1 (intake) → Test independently → Demo (MVP)
3. US2 (documents/OCR/validation) → Test independently → Demo
4. US3 (wallet/sub-agency submission) → Test independently → Demo
5. US4 (main agency/GDRFA) → Test independently → Demo
6. US5 (payment/immigration/final outcome) → Test independently → Demo — full P1 lifecycle complete
7. US7 (audit/support trace) → Test independently → Demo — can be built in parallel with US2–US5 since it only needs Phase 2 audit infrastructure
8. US6 (notifications, P2) → Test independently → Demo — deferrable without blocking the core lifecycle

### Parallel Team Strategy

With multiple developers, after Foundational completes:

- Developer A: US1 → US3 → US5 (core applicant/financial path)
- Developer B: US2 (documents/OCR), then US4 (main agency/GDRFA)
- Developer C: US7 (audit/support), then US6 (notifications)

Stories integrate at their checkpoints; US3–US5 require their upstream story's data contract (snapshot, submission reference, GDRFA acceptance) to be stable before their own checkpoint can be validated end-to-end.

---

## Notes

- `[P]` tasks touch different files with no unmet dependencies.
- `[Story]` label maps each task to its user story for traceability; Setup, Foundational, and Polish tasks carry no story label.
- Each user story is independently completable and testable given Phase 1/2 fixtures and stubs, even though US3–US6 consume artifacts produced by earlier stories in a full end-to-end run.
- Verify tests fail before implementing.
- Commit after each task or logical group.
- Stop at any checkpoint to validate a story independently.
- Avoid: vague tasks, same-file conflicts, and cross-story dependencies that break independent testability.
