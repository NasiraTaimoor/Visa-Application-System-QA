# Integration Contracts: Visa Application Lifecycle

All integration adapters must document ownership, data flow, security responsibility, timeout behavior, retry behavior, duplicate handling, reconciliation approach, failure procedure, and audit mapping before production use.

## Common Adapter Rules

- Validate source identity before accepting callbacks or status updates.
- Match every external event to case, submission, payment, wallet, or notification business reference.
- Use idempotency keys or provider references to preserve one business outcome.
- Quarantine unmatched, unauthorized, contradictory, out-of-order, or malformed events.
- Store protected payload references rather than exposing raw sensitive payloads in UI, logs, notifications, or exports.
- Emit audit events for attempts, accepted outcomes, duplicate handling, quarantine, retry exhaustion, and recovery.

## OCR Service

**Outbound**: screened document reference, document type, requested fields, correlation reference.

**Inbound**: extraction status, extracted fields, confidence by field, overall confidence, warnings, failure reason, payload reference.

**Failure handling**: Timeout or service failure creates retry or manual fallback task. Unsafe or failed-screening documents are never submitted to OCR.

## Document Screening Service

**Outbound**: file reference, file metadata, declared document type, correlation reference.

**Inbound**: screening status, accept/reject reason category, size/page/quality/security result, protected diagnostic reference.

**Failure handling**: Rejected documents remain replaceable in allowed workflow states. Security details are not exposed to applicants.

## Wallet or Ledger Service

**Outbound**: agency wallet reference, case reference, fee version, amount, currency, event type, idempotency key.

**Inbound**: available balance result, reservation/debit/release/refund/reconciliation reference, event status, reason.

**Failure handling**: Insufficient wallet blocks submission without reservation. Timeout retries must return existing result when the original succeeded.

## GDRFA Submission Service

**Outbound**: approved snapshot reference, required application data, document references, readiness approval reference, idempotency key.

**Inbound**: acknowledgement, rejection, action-required, external reference, response reason, timestamp, duplicate marker.

**Failure handling**: Timeout or unavailable service creates retry/recovery task. Rejections return case to correction state with authorized visibility.

## Payment Provider or Payment Operations Source

**Outbound**: payment initiation or reconciliation request where applicable, case reference, amount, currency, fee version, idempotency key.

**Inbound**: payment required, pending, paid, failed, cancelled, refunded, disputed, receipt reference, amount, currency, provider reference.

**Failure handling**: Unmatched, unauthorized, mismatched amount/currency, or contradictory provider events are quarantined for finance review.

## Immigration Processing Source

**Outbound**: external case reference and status query or manual liaison update where applicable.

**Inbound**: received, under review, action required, final approved/rejected/cancelled/withdrawn/expired/closed status, rationale/reference.

**Failure handling**: Final decisions lock ordinary changes. Contradictory or unmatched final decisions are quarantined.

## Notification Gateways

**Outbound**: recipient category, approved channel, minimal message content, template reference, correlation reference.

**Inbound**: accepted, delivered, failed, blocked, bounced, retry callback, provider reference.

**Failure handling**: Retry until configured limit, then record support-visible failure without blocking case workflow.

## Identity and Access Management

**Inbound dependency**: authenticated identity, roles, agency scopes, privileged-access signals, session status, stronger-authentication status where required.

**Failure handling**: Missing, expired, revoked, or insufficient identity denies action without data change and records denied attempt where auditable.

## Monitoring and Incident Process

**Outbound**: operational, integration, security, queue, performance, and recovery events with correlation references and minimized data.

**Failure handling**: Incidents involving confidentiality, integrity, availability, payments, or incorrect decisions must be recorded and linked to remediation actions.
