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
