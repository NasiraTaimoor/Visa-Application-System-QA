# API Contract: Visa Application Lifecycle

All APIs are planned as versioned service contracts. Concrete protocol and framework remain implementation decisions.

## Common Requirements

- Requests require authenticated actor or trusted service identity unless explicitly public for callback verification handshake.
- Mutating requests require correlation reference and audit context.
- Idempotent operations require a stable business idempotency key.
- Authorization checks include role, agency scope, lifecycle state, ownership, source validation, and required business reason.
- Responses must not expose secrets, stack traces, internal endpoints, full sensitive payloads, or unrelated applicant data.

## Application APIs

| Operation | Purpose | Key Inputs | Key Outputs |
|---|---|---|---|
| Create application | Create draft case | applicant or agency scope, visa type, agency relationship, consent path | case reference, draft status, audit reference |
| Update intake | Save applicant, contact, passport, travel, sponsor, visa, consent data | case reference, version, changed fields | updated version, missing items, audit reference |
| Resume draft | Restore authorized draft context | case reference, actor scope | draft summary, missing items, masked data |
| Abandon draft | Mark draft abandoned under policy | case reference, reason | abandoned status or retention action |
| Validate application | Evaluate configured rules | case reference, version, rule set version | findings, readiness state |

## Document and OCR APIs

| Operation | Purpose | Key Inputs | Key Outputs |
|---|---|---|---|
| Upload document | Attach document and request screening | case reference, document type, file metadata, file content reference | document id, version, screening status |
| Replace document | Version document replacement | case reference, document id, new file reference | new version, invalidated OCR/review state |
| Get OCR result | Show extracted fields for review | document id, actor scope | extracted fields, confidence, warnings |
| Confirm OCR values | Confirm or correct extracted values | OCR result id, reviewed values, correction reason | confirmed values, audit reference |

## Workflow APIs

| Operation | Purpose | Key Inputs | Key Outputs |
|---|---|---|---|
| Verify wallet | Check balance and create reservation | case reference, fee version, amount, currency, idempotency key | reservation result, shortfall or reservation reference |
| Submit to main agency | Submit validated snapshot | case reference, snapshot version, reservation reference, idempotency key | submission reference, submitted status |
| Process main agency action | Assign, correct, reject, escalate, approve readiness | case reference, action, reason, attachments | new task/status/decision record |
| Submit to GDRFA | Send readiness-approved case | case reference, snapshot id, idempotency key | GDRFA submission reference or recovery task |
| Record immigration update | Apply or quarantine immigration status | external reference, status, source, reason, idempotency key | status event or quarantine record |

## Finance APIs

| Operation | Purpose | Key Inputs | Key Outputs |
|---|---|---|---|
| Calculate fees | Calculate fee breakdown | visa type, agency relationship, stage | amount, currency, fee version, breakdown |
| Record wallet event | Reserve, debit, release, refund, reconcile | case reference, wallet reference, amount, event type, reason | wallet event reference |
| Record payment event | Pending, paid, failed, cancelled, refunded, disputed, reconciled | case reference, provider/reference, amount, currency, state | payment state, audit reference |
| Manual reconciliation | Finance-approved correction | payment id, receipt, amount, currency, reason | reconciliation record |

## Status, Notification, Audit, and Recovery APIs

| Operation | Purpose | Key Inputs | Key Outputs |
|---|---|---|---|
| Get status timeline | Return authorized status view | case reference, actor scope | role-filtered timeline |
| Search cases | Operational search/filter | filters, actor scope, business need | masked results |
| Export records | Authorized export | filters, export type, business reason | export reference, audit event |
| Get audit history | Compliance/audit trace | case reference, filters, business reason | audit events |
| Create notification preference | Update allowed preferences | recipient, channel preference | preference state |
| Get recovery tasks | Support/operations queue | filters, actor scope | recovery tasks |
| Resolve recovery task | Complete controlled recovery | task id, action, reason | task result, audit event |

## Implementation Mapping (T190)

Concrete realized endpoints (all under `/api/v1`, backend `src/api/*_routes.py`), tech stack Python/FastAPI + React/TypeScript per plan.md's post-implementation stack decision:

| Contract operation | Realized route | Handler module |
|---|---|---|
| Create application | `POST /applications` | `applications/intake/create_application.py` |
| Update intake | `PATCH /applications/{id}` | `applications/intake/update_intake.py` |
| Resume draft | `GET /applications/{id}/resume` | `applications/intake/resume_draft.py` |
| Abandon draft | `POST /applications/{id}/abandon` | `applications/intake/abandon_draft.py` |
| Validate application | `POST /applications/{id}/validate` | `validation/validation_engine.py` |
| Upload/Replace document | `POST /applications/{id}/documents`, `POST .../documents/{doc_id}/replace` | `documents/document_service.py` |
| Get OCR result / Confirm OCR values | `GET /documents/{doc_id}/ocr`, `POST /applications/{id}/documents/{doc_id}/ocr/confirm` | `ocr/ocr_review_service.py` |
| Approve validation override | `POST /validation/findings/{finding_id}/override` | `validation/override_service.py` |
| Calculate fees | `GET /applications/{id}/fees` | `finance/fee_calculation_service.py` |
| Verify wallet | `POST /applications/{id}/wallet/verify` | `finance/wallet_lifecycle_service.py` |
| Submit to main agency | `POST /applications/{id}/submit` | `applications/submission/sub_agency_submission_service.py` |
| Process main agency action | `POST /applications/{id}/claim`, `.../correction-request`, `.../correction-resolve`, `.../readiness-approve` | `agencies/main_agency_queue_service.py`, `correction_request_service.py`, `readiness_approval_service.py` |
| Submit to GDRFA | `POST /applications/{id}/gdrfa/submit` | `integrations/gdrfa_response_service.py` |
| Record payment event / Manual reconciliation | `POST /applications/{id}/payment/confirm`, `.../payment/reconcile` | `finance/payment_service.py`, `finance/reconciliation_service.py` |
| Record immigration update | `POST /applications/{id}/immigration/update` | `agencies/immigration_status_service.py` |
| Get status timeline | `GET /applications/{id}/status-timeline` | `applications/status/status_timeline_service.py` |
| Create notification preference | `POST /applications/{id}/notification-preferences` | `notifications/preference_service.py` |
| Get audit history | `GET /audit/events` | `audit/audit_search_service.py` |
| Export records | `POST /audit/export` | `compliance/export_service.py` |
| Get/Resolve recovery task | `GET /recovery/tasks`, `POST /recovery/tasks/{id}/resolve` | `recovery/recovery_task_service.py` |
| Search cases (masked) | `POST /support/cases/{id}/access` | `audit/support_access_service.py` |

All routes enforce the Common Requirements above via `src/api/deps.py` (identity, correlation reference, idempotency key extraction) and each service's own `authorize()`/`record_audit_event()` calls. Backed by 166 backend tests (`backend/tests/{contract,integration,unit,e2e,regression,performance,security}`) and 37 frontend tests (`frontend/tests/{ui,accessibility}`).
