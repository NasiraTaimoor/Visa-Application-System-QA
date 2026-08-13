# UI Contract: Visa Application Lifecycle

The UI contract defines expected role-specific surfaces and validation obligations. It does not prescribe framework or visual implementation.

## Common UI Rules

- Applicant-facing UI must meet WCAG 2.1 AA.
- Forms must expose clear labels, requirements, examples, validation errors, and correction links.
- Errors must identify the field, document, or action requiring correction and must not rely on color alone.
- Personal, payment, audit, and internal notes must be masked or hidden unless required for the user's authorized task.
- Hidden or disabled controls are advisory only; server-side authorization remains authoritative.
- Long-running OCR, screening, payment, GDRFA, immigration, and notification states must show current state and next action.

## Applicant Portal

**Screens**: application creation, draft intake, missing items, document upload, OCR review, validation findings, correction requests, status timeline, payment status where applicable, final outcome, notification preferences, session recovery.

**Required behavior**: Save/resume drafts safely, confirm OCR before submission, show actionable validation errors, recover from timeout without exposing personal data, and show role-appropriate timeline details.

## Sub-Agency Workspace

**Screens**: assigned applications, intake-on-behalf, readiness review, document/OCR review, validation findings, wallet verification, wallet shortfall, submission reference, correction handling, status timeline.

**Required behavior**: Enforce agency scope, display fee version and wallet result to authorized users, block duplicate submissions, and show submitted snapshot lock state.

## Main Agency Workspace

**Screens**: routed queues, case assignment, review detail, correction request, decision/rationale capture, readiness approval, GDRFA submission, GDRFA response handling, escalation.

**Required behavior**: Require reasons for decisions and correction requests, protect internal notes from unauthorized roles, and show recovery tasks for failed or quarantined external responses.

## Finance Workspace

**Screens**: payment queue, wallet event history, reservation/debit/release/refund/reconciliation detail, disputes, unmatched provider events.

**Required behavior**: Restrict paid/refund/reconciliation actions to authorized finance users and require amount, currency, receipt/reference, reason, and audit context.

## Support Workspace

**Screens**: recovery tasks, integration failures, notification failures, safe case lookup, masked applicant context, support action reason capture.

**Required behavior**: Support users cannot approve financial or immigration outcomes unless separately authorized; privileged access requires business reason and audit record.

## Auditor and Compliance Workspace

**Screens**: audit history, lifecycle timeline, export filters, retention/legal hold view, privileged access history, immutable record references.

**Required behavior**: Audit data is searchable and exportable only with authorized scope and business need. Export actions are audited and masked according to policy.

## Accessibility Acceptance

- Keyboard-only users can complete intake, upload, OCR review, validation correction, payment/status review, and notification preferences.
- Screen-reader users receive meaningful names, roles, states, and error messages.
- Focus moves to errors and returned correction points predictably.
- Timeout and interrupted session states are recoverable after authentication.
- Accessible manual fallback exists when OCR is unavailable or unusable.
