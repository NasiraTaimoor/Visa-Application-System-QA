# Feature Specification: Visa Application Lifecycle

**Feature Branch**: `[001-visa-application-lifecycle]`

**Created**: 2026-08-11

**Status**: Draft

**Input**: User description: "Create the baseline specification for a Visa Application System supporting applicant information, passport/document upload, OCR, validation, sub-agency wallet verification, sub-agency submission, main agency processing, GDRFA submission, payment, immigration processing, status tracking, notifications, audit logging, and error handling."

## Clarifications

### Session 2026-08-11

- QA review gaps were resolved using conservative, implementation-neutral business defaults for status transitions, validation severity, wallet lifecycle, integration retry and idempotency, action-level permissions, audit event coverage, and document/OCR thresholds.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Applicant starts and completes a visa application (Priority: P1)

An applicant or authorized sub-agency officer can create a visa application, enter required applicant, passport, contact, travel, and visa details, save progress, resume safely, and see what remains before submission.

**Why this priority**: Accurate intake is the foundation for every downstream validation, payment, agency, GDRFA, and immigration action.

**Independent Test**: Create a new application, complete required fields, interrupt and resume the session, and confirm the application reaches a complete-but-not-submitted state without exposing personal data.

**Acceptance Scenarios**:

1. **Given** an authorized user starts a new application, **When** all required applicant and travel fields are entered, **Then** the system marks the intake section complete and records the data with the application.
2. **Given** an application is partially completed, **When** the user resumes later after authentication, **Then** the system restores the draft and shows missing fields without displaying personal data to unauthorized users.

---

### User Story 2 - Applicant uploads documents and reviews OCR results (Priority: P1)

An applicant or sub-agency officer can upload passport and supporting documents, receive OCR-extracted information, review confidence warnings, correct extracted values, and submit only validated document data.

**Why this priority**: Document quality and data extraction directly affect eligibility checks, rework rates, and immigration processing accuracy.

**Independent Test**: Upload required documents, verify accepted and rejected file outcomes, review OCR output, correct a mismatch, and confirm the corrected data is used for validation.

**Acceptance Scenarios**:

1. **Given** a supported passport image is uploaded, **When** OCR completes with sufficient confidence, **Then** extracted passport details are shown for user review before they become final application data.
2. **Given** OCR finds a mismatch between the uploaded passport and entered applicant details, **When** the user views validation results, **Then** the system identifies the mismatch and requires correction or documented override before submission.

---

### User Story 3 - Sub-agency verifies wallet and submits to main agency (Priority: P1)

A sub-agency officer can review a completed application, verify that the sub-agency wallet has enough available balance for all required fees, reserve the amount, and submit the application to the main agency.

**Why this priority**: Submission without sufficient funds or review creates operational failures and payment disputes.

**Independent Test**: Prepare a validated application, perform a wallet check, submit with sufficient funds, and confirm duplicate submissions are blocked.

**Acceptance Scenarios**:

1. **Given** a validated application and sufficient available wallet balance, **When** the sub-agency submits the application, **Then** the system reserves the required amount and changes the case status to submitted to main agency.
2. **Given** available wallet balance is below the required amount, **When** the sub-agency attempts submission, **Then** the system blocks submission, explains the shortfall, and does not reserve funds.

---

### User Story 4 - Main agency processes and submits to GDRFA (Priority: P1)

A main agency case officer can review submitted applications, request corrections, approve internal readiness, submit eligible applications to GDRFA, and track acknowledgement or rejection from GDRFA.

**Why this priority**: Main agency processing is the controlled handoff between commercial intake and government processing.

**Independent Test**: Receive a sub-agency submission, request additional information, accept a corrected case, submit to GDRFA, and verify acknowledgement is reflected in the case timeline.

**Acceptance Scenarios**:

1. **Given** a submitted application with complete documents, **When** the main agency officer approves GDRFA readiness, **Then** the system records the decision rationale and prepares the case for GDRFA submission.
2. **Given** GDRFA rejects a submission due to validation issues, **When** the rejection is received, **Then** the application returns to a correction state with the reason visible to authorized users.

---

### User Story 5 - Payment and immigration processing are tracked end to end (Priority: P1)

Finance and operations users can initiate or confirm required payments, reconcile payment outcomes, track immigration processing status, and record final approval, rejection, cancellation, expiry, or withdrawal.

**Why this priority**: Payment and immigration status are high-impact events that determine whether the applicant receives the requested visa outcome.

**Independent Test**: Move a GDRFA-accepted case through payment, immigration processing, final decision, and status publication with a complete audit trail.

**Acceptance Scenarios**:

1. **Given** a case requires payment, **When** payment is confirmed by an authorized source, **Then** the system marks the payment as paid, records the receipt reference, and allows immigration processing to continue.
2. **Given** immigration issues a final decision, **When** the decision is recorded or received, **Then** the system moves the case to the appropriate terminal status and prevents unauthorized decision changes.

---

### User Story 6 - Users receive status updates and notifications (Priority: P2)

Applicants, sub-agencies, and main agency staff receive clear status updates and notifications for important case events, missing information, payment outcomes, and final decisions.

**Why this priority**: Timely communication reduces support load and prevents missed deadlines, but the core workflow can still proceed if notifications are delayed.

**Independent Test**: Trigger status changes and verify the correct recipients receive non-sensitive notification content while the full status remains available to authorized users.

**Acceptance Scenarios**:

1. **Given** an application status changes to action required, **When** notification rules are evaluated, **Then** the correct authorized recipients are notified with a clear next action and without unnecessary personal data.
2. **Given** a notification delivery fails, **When** retries are exhausted, **Then** the failure is recorded and visible to authorized support users without blocking the case workflow.

---

### User Story 7 - Auditors and support staff trace case history (Priority: P1)

Auditors and authorized support staff can inspect a complete, tamper-evident history of application changes, document actions, validations, wallet events, payments, external submissions, status updates, privileged access, and errors.

**Why this priority**: The constitution requires accurate, traceable case records for state changes, document actions, eligibility decisions, and privileged access.

**Independent Test**: Perform representative actions across the lifecycle and confirm each action appears in the audit history with actor, time, action, affected case, result, and reason where applicable.

**Acceptance Scenarios**:

1. **Given** a case has moved through intake, submission, payment, and decision, **When** an auditor opens the audit history, **Then** all lifecycle events are visible in chronological order with required audit attributes.
2. **Given** a support user accesses sensitive case data, **When** the access occurs, **Then** the system records the access event and business reason.

### Acceptance Criteria

- **AC-001**: A visa application cannot be submitted beyond draft until required applicant, passport, travel, contact, document, consent, and fee data pass validation for the selected visa type.
- **AC-002**: OCR-extracted data must remain reviewable and correctable before it is treated as user-confirmed application data.
- **AC-003**: Sub-agency submission must require sufficient available wallet balance and must create a single reservation or debit event for each accepted submission attempt.
- **AC-004**: Main agency officers must be able to approve, reject, request correction, and submit to GDRFA only within their authorized agency scope.
- **AC-005**: GDRFA, payment, and immigration status updates must be reflected in the application timeline with clear source, timestamp, result, and next action.
- **AC-006**: Terminal decisions must be protected from unauthorized alteration and any permitted correction must be separately recorded with reason and approval.
- **AC-007**: Applicants and agencies must receive actionable status and error messages that do not disclose unnecessary sensitive information.
- **AC-008**: Every state change, document action, validation decision, wallet event, payment event, external submission, notification event, privileged access, and error recovery action must create an audit record.

### Workflow

1. **Draft created**: Authorized user starts a new application and records applicant, contact, passport, travel, visa type, sponsor, and consent details.
2. **Documents pending**: Required passport and supporting documents are uploaded, checked for acceptability, and associated with the application.
3. **OCR and validation**: OCR extracts document data, the user reviews or corrects extracted values, and the system validates data consistency and visa-type requirements.
4. **Ready for sub-agency review**: The application is complete and available to the responsible sub-agency for review.
5. **Wallet verified**: Required fees are calculated, wallet availability is checked, and funds are reserved or submission is blocked.
6. **Submitted to main agency**: The application is locked for ordinary applicant edits and routed to the main agency.
7. **Main agency processing**: Main agency staff review, assign, request corrections, reject, approve for GDRFA, or escalate according to permission.
8. **GDRFA submitted**: The system records GDRFA submission details, acknowledgement, rejection, or action-required responses.
9. **Payment pending or paid**: Required payments are initiated, confirmed, failed, refunded, or reconciled with clear financial records.
10. **Immigration processing**: Immigration status updates are received or recorded and shown to authorized users.
11. **Final outcome**: The application becomes approved, rejected, cancelled, withdrawn, expired, or closed with final status, rationale, and audit history.
12. **Rework loops**: Any validation failure, agency correction request, GDRFA response, payment failure, or immigration action-required event returns the case to the responsible party with a clear next action.

**Status transition matrix**:

| From Status | Allowed To Status | Allowed Actors or Sources | Preconditions | Failure and Recovery Behavior | Audit Requirement | QA Acceptance Criteria |
|-------------|-------------------|---------------------------|---------------|-------------------------------|-------------------|------------------------|
| No case | Draft created | Applicant, Sub-agency Officer | Authorized user has valid agency or applicant scope and required consent step is available | Deny creation when scope or consent prerequisites fail; allow retry after correction | Record creation attempt, actor, scope, result, and case reference when created | Unauthorized creation is denied; authorized creation produces one draft and one audit event |
| Draft created | Documents pending | Applicant, Sub-agency Officer | Required intake fields are present enough to attach documents | Keep case in draft and show missing intake fields | Record intake completion check and missing-field result | Missing required intake data prevents document completion |
| Documents pending | OCR and validation | Applicant, Sub-agency Officer, System Service | Required documents uploaded and passed document screening | Reject failed documents and keep case editable for replacement | Record document screening result and OCR request eligibility | Unsupported, unsafe, or incomplete documents do not proceed to OCR validation |
| OCR and validation | Ready for sub-agency review | Applicant, Sub-agency Officer, System Service | OCR reviewed or manually confirmed; no blocking validation findings remain | Keep case in correction state with findings assigned to responsible party | Record OCR review, validation result, correction, and override if used | Case cannot become ready while blocking findings remain unresolved |
| Ready for sub-agency review | Wallet verified | Sub-agency Officer | User belongs to owning sub-agency; fees calculated; wallet has sufficient available balance | Show shortfall and keep case ready for review without reservation | Record fee calculation, balance check, result, and reservation decision | Insufficient wallet balance blocks submission and creates no reservation |
| Wallet verified | Submitted to main agency | Sub-agency Officer | Wallet reservation exists and application version matches validated snapshot | Prevent duplicate submission; return existing reference when retry repeats same accepted request | Record submission request, reservation reference, snapshot reference, and submission reference | Concurrent submit attempts produce one submission and one reservation/debit path |
| Submitted to main agency | Main agency processing | Main Agency Case Officer, Main Agency Supervisor | Case routed to correct main agency queue and assigned or claimable | Keep in submitted queue if routing or assignment fails; escalate to supervisor | Record assignment, queue, actor, and result | Only authorized main agency users can claim or process routed cases |
| Main agency processing | Correction requested | Main Agency Case Officer, Main Agency Supervisor | Reason and responsible party selected | Keep case with main agency if no actionable reason is provided | Record correction request, reason, due date if any, and responsible party | Correction request is visible to the responsible party and blocks onward submission |
| Main agency processing | GDRFA submitted | Main Agency Case Officer, Main Agency Supervisor, System Service | Main agency readiness approved; required snapshot, documents, and payment prerequisites for the visa type are satisfied | Keep case in main agency processing if prerequisites or external submission fail before acceptance | Record readiness approval, submission attempt, payload reference, and result | GDRFA submission cannot occur without readiness approval and required prerequisites |
| GDRFA submitted | Payment pending | GDRFA Submission Service, Main Agency Case Officer | GDRFA acknowledgement indicates payment is required or payment step is active for visa type | Keep GDRFA submitted status and assign recovery when response is incomplete | Record GDRFA response and payment requirement | Payment pending appears only after authorized source or officer confirms payment requirement |
| Payment pending | Paid | Payment Provider, Finance Officer | Authorized payment confirmation or approved manual reconciliation exists | Keep payment pending or failed; route disputed or unmatched confirmations to finance review | Record confirmation source, receipt, amount, currency, reconciler, and result | Payment cannot become paid without authorized confirmation or reconciliation approval |
| Payment pending | Payment failed | Payment Provider, Finance Officer | Failure, cancellation, expiry, or dispute is confirmed | Keep case recoverable for retry, replacement payment, or finance resolution | Record failure source, reason, and next action | Payment failure does not close the case unless business policy marks it expired or cancelled |
| Paid | Immigration processing | Immigration Processing Source, GDRFA or Immigration Liaison, System Service | Payment complete where required; external case reference exists | Keep paid status and assign recovery if external case is not confirmed | Record immigration handoff or received status | Immigration processing cannot start without required payment completion and external case reference |
| Immigration processing | Approved, Rejected, Cancelled, Withdrawn, Expired, or Closed | Immigration Processing Source, GDRFA or Immigration Liaison, Main Agency Supervisor for controlled manual closure | Final decision or authorized closure reason exists | Quarantine contradictory, unmatched, or unauthorized final status and require review | Record final source, decision, rationale/reference, actor, and terminal lock | Final status is immutable to ordinary users and creates a complete audit event |
| Any non-terminal status | Withdrawn | Applicant where allowed, Sub-agency Officer, Main Agency Supervisor | Withdrawal is allowed for current stage and legal retention notice is accepted | Deny withdrawal when external or legal processing stage forbids it; show responsible contact | Record withdrawal request, actor, reason, allowed/denied result | Withdrawal follows stage rules and never deletes required retained records |
| Any status | Closed | Main Agency Supervisor, Auditor or Compliance User for compliance hold closure where authorized | Case has terminal outcome, compliance closure reason, or expiry rule applies | Deny closure without terminal or policy reason | Record closure reason, actor, affected status, and retained records | Closure cannot hide audit history, payment obligations, or legal hold data |

### Edge Cases

- Passport expires before submission, before GDRFA submission, or before immigration decision.
- Passport validity is close to the minimum required period at submission time.
- OCR confidence is low, extracted text is incomplete, or extracted values conflict with user-entered data.
- The same passport or applicant appears in another active application.
- A file upload is interrupted, duplicated, corrupted, password-protected, unsupported, too large, or fails security screening.
- Required visa-type rules change while an application is in draft or under review.
- Wallet balance changes between fee display, reservation, and submission.
- Two authorized users edit or submit the same application at nearly the same time.
- GDRFA, payment, or immigration sends a duplicate, late, out-of-order, or contradictory status update.
- Applicant withdraws consent or requests deletion while legal retention or processing obligations still apply.
- Notification address is invalid, blocked, unreachable, or belongs to a different recipient.
- A legal hold, compliance investigation, or incident response requires preservation beyond normal retention.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST allow authorized users to create a visa application for a selected visa type and responsible agency relationship.
- **FR-002**: The system MUST capture required applicant identity, contact, passport, travel, sponsor, visa type, and consent information before submission.
- **FR-003**: The system MUST allow draft applications to be saved, resumed, and abandoned according to retention rules.
- **FR-004**: The system MUST show completion status and missing required items before agency submission.
- **FR-005**: The system MUST accept passport and supporting document uploads only when they meet configured document type, size, quality, and security requirements.
- **FR-006**: The system MUST record document metadata, upload actor, upload time, document type, verification status, and version history.
- **FR-007**: The system MUST perform OCR on eligible passport and document uploads and present extracted fields with confidence indicators.
- **FR-008**: The system MUST require user review of OCR-extracted data before it becomes confirmed application data.
- **FR-009**: The system MUST validate application data against required fields, document presence, passport rules, visa-type rules, duplicate-risk indicators, and agency processing rules.
- **FR-010**: The system MUST show validation findings with severity, affected field or document, responsible party, and required corrective action.
- **FR-011**: The system MUST prevent submission while blocking validation findings remain unresolved or explicitly authorized for override.
- **FR-012**: The system MUST calculate required fees and charges for the selected visa type, agency relationship, and processing stage.
- **FR-013**: The system MUST verify sub-agency wallet availability before submission to the main agency.
- **FR-014**: The system MUST reserve, debit, release, or refund wallet amounts according to case outcome and financial rules.
- **FR-015**: The system MUST prevent duplicate wallet reservations or debits for the same accepted submission attempt.
- **FR-016**: The system MUST allow sub-agency officers to submit validated applications to the main agency and receive a submission reference.
- **FR-017**: The system MUST route submitted applications to the correct main agency queue based on agency relationship and visa type.
- **FR-018**: The system MUST allow main agency officers to review applications, assign ownership, request corrections, approve readiness, reject, or escalate.
- **FR-019**: The system MUST record main agency decisions with actor, timestamp, decision, reason, and supporting notes or attachments where required.
- **FR-020**: The system MUST submit approved applications to GDRFA and record submission reference, submission time, response status, and response reason.
- **FR-021**: The system MUST handle GDRFA acknowledgement, rejection, action-required, timeout, duplicate response, and unavailable-service outcomes.
- **FR-022**: The system MUST manage payment-required, payment-pending, paid, failed, cancelled, refunded, and reconciled payment states.
- **FR-023**: The system MUST prevent a payment from being marked paid without an authorized confirmation or approved manual reconciliation.
- **FR-024**: The system MUST track immigration processing states, including received, under review, action required, approved, rejected, cancelled, withdrawn, expired, and closed.
- **FR-025**: The system MUST expose a status timeline to authorized applicants, sub-agencies, main agency users, finance users, support users, and auditors according to role permissions.
- **FR-026**: The system MUST notify relevant recipients for submission, correction request, validation failure, wallet shortfall, payment outcome, GDRFA update, immigration update, and final decision events.
- **FR-027**: The system MUST allow notification preferences where permitted while preserving mandatory operational and legal notices.
- **FR-028**: The system MUST record notification delivery attempts, results, retries, failures, and recipient category.
- **FR-029**: The system MUST create durable audit records for all application state changes, document actions, validation decisions, wallet events, payment events, external submissions, privileged access, administrative changes, and error recovery actions.
- **FR-030**: The system MUST prevent unauthorized modification or deletion of completed decisions, submitted application snapshots, financial records, and audit records.
- **FR-031**: The system MUST provide user-facing error messages that explain the issue, identify the responsible next action, and avoid exposing secrets or unnecessary personal data.
- **FR-032**: The system MUST support authorized search, filtering, and export of case, payment, status, error, and audit information for operations, finance, compliance, and support needs.
- **FR-033**: The system MUST enforce role-based and agency-scoped access for every case, document, wallet, payment, notification, and audit action.
- **FR-034**: The system MUST support retention, deletion, anonymisation, and legal hold handling for every personal data category used by the feature.
- **FR-035**: The system MUST preserve in-progress applications during rule, fee, status, or integration changes and identify any required revalidation to responsible users.
- **FR-036**: The system MUST enforce the defined status transition matrix for every lifecycle state change.
- **FR-037**: The system MUST classify validation findings as informational, warning, blocking, overrideable blocking, or non-overrideable blocking.
- **FR-038**: The system MUST make wallet reservation, debit, release, refund, and reconciliation actions traceable to one case, one fee calculation version, and one accepted submission or payment event.
- **FR-039**: The system MUST treat every external submission, payment confirmation, wallet action, immigration update, and notification retry as idempotent by business reference so repeated attempts do not duplicate case, financial, or audit outcomes.
- **FR-040**: The system MUST enforce action-level permissions for creation, edit, upload, OCR review, validation override, wallet action, submission, processing, payment, immigration update, notification management, support recovery, audit access, export, and closure.
- **FR-041**: The system MUST require mandatory audit fields before accepting any auditable lifecycle, access, financial, integration, or recovery event.
- **FR-042**: The system MUST apply document and OCR acceptance thresholds before a case can proceed beyond OCR and validation.

### Business Rules

- **BR-001**: Required fields and documents are determined by visa type, applicant category, sponsor type, nationality or issuing country where applicable, and current processing policy.
- **BR-002**: Passport validity must meet the active business rule at submission; baseline assumption is at least six months remaining at sub-agency submission unless a policy exception is configured and approved.
- **BR-003**: OCR output is advisory until reviewed and confirmed by an authorized user.
- **BR-004**: Blocking validation findings prevent submission unless an authorized role records an approved override reason.
- **BR-005**: A sub-agency may submit only cases that belong to its authorized scope and wallet.
- **BR-006**: Main agency users may process only cases assigned to their agency scope unless a supervised transfer or escalation is recorded.
- **BR-007**: Wallet balance must be available before reservation; pending, reserved, disputed, or legally held funds do not count as available balance.
- **BR-008**: Fee changes after wallet reservation require recalculation and either additional reservation, release, or documented exception.
- **BR-009**: Payment, wallet, and refund actions require traceable financial references and must reconcile to the case.
- **BR-010**: Duplicate applications must be flagged before submission when they share strong identity, passport, or active-case indicators.
- **BR-011**: Terminal decisions are immutable to ordinary users; permitted corrections require elevated permission, reason, approval, and a new audit event.
- **BR-012**: Notifications must minimize sensitive data and direct recipients to authenticate before viewing protected details.
- **BR-013**: External status updates must be matched to a known case and source reference before changing case status.
- **BR-014**: Data retention, deletion, anonymisation, and legal holds override ordinary user deletion requests where required by law, regulation, contract, or policy.
- **BR-015**: Validation findings use these severities: informational findings do not block progress; warnings require user acknowledgement; blocking findings require correction; overrideable blocking findings require elevated approval and reason; non-overrideable blocking findings cannot be bypassed.
- **BR-016**: Missing consent, missing required passport document, unsafe document, unsupported visa type, unauthorized agency relationship, and insufficient wallet balance are non-overrideable for submission.
- **BR-017**: Passport expiry below the active minimum validity is blocking; an exception may proceed only when the policy marks that exception as allowed and a main agency supervisor records approval before GDRFA submission.
- **BR-018**: OCR mismatches on passport number, legal name, date of birth, nationality, issuing country, issue date, or expiry date are blocking until the user confirms corrected values or an authorized officer records an override.
- **BR-019**: Document acceptance requires supported format, readable content, complete required pages, no password restriction, no detected security threat, and a document type matching a requirement for the selected visa type.
- **BR-020**: Baseline document size limit is 10 MB per file and baseline page limit is 20 pages per document unless a visa-type rule defines a stricter limit.
- **BR-021**: Baseline OCR confidence below 85% for any critical passport field requires manual confirmation; below 60% requires manual entry or replacement document before submission.
- **BR-022**: Wallet reservation occurs immediately before sub-agency submission to main agency and is tied to the validated application snapshot and fee calculation version.
- **BR-023**: Wallet debit occurs when the reserved amount becomes payable according to the active fee rule; if the case is rejected or withdrawn before debit eligibility, the reservation is released.
- **BR-024**: Wallet reservations expire after 24 hours if the application is not successfully submitted, unless a finance officer renews or releases the reservation with reason.
- **BR-025**: Concurrent wallet actions must be resolved so available balance cannot be reserved or debited more than once for the same funds.
- **BR-026**: A fee increase after reservation blocks onward processing until the additional amount is reserved, paid, or formally waived; a fee decrease releases the excess reserved amount.
- **BR-027**: External submissions and callbacks must use a stable business reference for duplicate detection, and repeats with the same reference must return or preserve the existing outcome.
- **BR-028**: Automated retries are allowed only for timeout, temporary unavailable, and delivery-failure outcomes; rejection, validation failure, unauthorized, and unmatched callback outcomes require human review.
- **BR-029**: Baseline retry policy is three attempts over 30 minutes for OCR, document screening, wallet, GDRFA, payment, immigration, and notification operations unless the external contract is stricter.
- **BR-030**: Failed retries create a recovery task assigned to the responsible role and must not silently advance or close the case.
- **BR-031**: Applicants may edit draft and correction-requested data within their scope; after sub-agency submission, applicant edits require a correction request or withdrawal path.
- **BR-032**: Sub-agency officers may act only on cases owned by their sub-agency; sub-agency admins may manage users and monitor cases but cannot bypass submission, wallet, or validation controls without separately granted approval.
- **BR-033**: Main agency case officers may process routed cases; main agency supervisors may approve overrides, transfers, terminal corrections, manual closures, and escalations with reason.
- **BR-034**: Finance officers may reconcile, release, refund, or dispute financial events but cannot change applicant identity, documents, validation results, immigration decisions, or audit history.
- **BR-035**: Support admins may perform controlled recovery actions only with a business reason and may not approve eligibility, financial, or terminal decision outcomes.
- **BR-036**: Audit events are valid only when they include event type, actor or service identity, role, agency scope, affected case, affected record where applicable, timestamp, action, before and after status where applicable, outcome, reason where applicable, source, and correlation reference.
- **BR-037**: State-changing audit events must record the previous status, new status, transition source, and transition authority.
- **BR-038**: Financial audit events must record amount, currency, fee version, wallet or payment reference, financial action, and reconciliation state.
- **BR-039**: Integration audit events must record external source, business reference, attempt number, request or response reference, outcome, retry eligibility, and recovery owner when failed.
- **BR-040**: Notification audit events must record triggering event, recipient category, channel, delivery result, retry count, and failure reason where available.

### Error Scenarios and Handling

| ID | Scenario | Expected Handling | Audit Requirement |
|----|----------|-------------------|-------------------|
| E-001 | Upload rejected due to file type, quality, size, corruption, or security screening | Explain the rejection, keep the application editable, and request a replacement document | Record upload attempt, reason, actor, and case |
| E-002 | OCR unavailable or low confidence | Allow manual entry or retry, mark OCR status, and require user confirmation | Record OCR status, confidence, and correction activity |
| E-003 | Blocking validation failure | Prevent submission and show corrective action by field or document | Record validation result and later resolution |
| E-004 | Insufficient wallet balance | Block submission, show shortfall to authorized sub-agency users, and avoid reservation | Record balance check outcome without exposing unrelated wallet data |
| E-005 | Duplicate submission attempt | Return the existing submission reference and prevent duplicate financial or external actions | Record duplicate attempt and resolved reference |
| E-006 | GDRFA or immigration service unavailable or times out | Keep case in pending external submission or pending response state and allow controlled retry | Record attempt, timeout, retry, and final outcome |
| E-007 | Payment confirmation fails or is disputed | Keep payment unresolved, prevent paid status, and route to finance review | Record payment event, reason, and finance action |
| E-008 | External callback cannot be matched to a case | Quarantine the event for review without changing case status | Record source, payload reference, and reviewer outcome |
| E-009 | Unauthorized access or action attempt | Deny the action and display a generic access message | Record actor, attempted action, target case, and result |
| E-010 | Concurrent edits conflict | Preserve the latest accepted state, show conflict to the later user, and require review before overwrite | Record both edit attempts and conflict resolution |
| E-011 | Invalid status transition attempted | Reject the transition, keep the current status, and show or assign the valid next action | Record attempted from/to status, actor/source, result, and reason |
| E-012 | Non-overrideable validation failure exists | Block submission or onward processing and assign correction to the responsible party | Record rule, severity, affected data, and blocked action |
| E-013 | Overrideable validation failure approved | Allow onward processing only after elevated approval and reason are recorded | Record approver, reason, affected rule, and resulting status |
| E-014 | Wallet reservation expires before submission | Release the reservation and require a fresh wallet check before submission | Record expiry, release, and next required action |
| E-015 | Wallet or payment duplicate event received | Preserve the original accepted financial outcome and attach the duplicate event to review history | Record duplicate reference, original reference, and resolution |
| E-016 | External retry limit reached | Stop automated retry, keep the case in recovery state, and assign a recovery owner | Record attempts, final failure, owner, and due action |
| E-017 | GDRFA, payment, or immigration sends contradictory status | Quarantine the update, prevent status change, and route to liaison or supervisor review | Record prior status, received status, source, and reviewer decision |
| E-018 | Document fails OCR because text is unreadable | Require replacement or manual entry where permitted and keep case before submission | Record OCR failure, document reference, and user recovery |
| E-019 | Action-level permission check fails | Deny the action, keep data unchanged, and show a generic authorization message | Record actor, role, agency scope, attempted action, and target |
| E-020 | Mandatory audit field is missing | Reject the auditable action or hold it in recovery until complete audit data is available | Record recovery record with missing audit fields where possible |

### Roles and Permissions

| Role | Core Permissions | Restrictions |
|------|------------------|--------------|
| Applicant | Create or view own application, enter data, upload documents, review OCR, respond to correction requests, withdraw where allowed, view permitted status | Cannot access agency wallets, other applicants, internal notes, audit-only data, or final decision controls |
| Sub-agency Officer | Create and manage applications for assigned applicants, review validation, verify wallet, submit to main agency, respond to corrections | Limited to assigned sub-agency cases and cannot alter main agency, GDRFA, immigration, or audit decisions |
| Sub-agency Admin | Manage sub-agency users, view wallet summary, monitor submissions, handle operational exceptions within scope | Cannot process main agency decisions or bypass financial controls without approval |
| Main Agency Case Officer | Review submitted cases, request corrections, approve readiness, submit to GDRFA, update processing notes | Limited to assigned main agency scope and cannot perform privileged financial overrides |
| Main Agency Supervisor | Reassign cases, approve overrides, resolve escalations, authorize exceptional corrections | Must provide reason for overrides and cannot erase audit history |
| Finance Officer | Review wallet events, payment states, refunds, reconciliation, and financial exceptions | Cannot change applicant identity, documents, or immigration decisions |
| GDRFA or Immigration Liaison | Record or verify external submission and status outcomes where manual follow-up is required | Cannot alter wallet balances or unrelated application data |
| Support Admin | Assist users, inspect error records, perform controlled recovery actions | Access must be justified, scoped, and audited; cannot approve final decisions |
| Auditor or Compliance User | Read case history, audit records, financial traces, and compliance evidence | Read-only access unless separately authorized for case holds or compliance flags |
| System Service | Perform scheduled validation, notification, integration, retention, and reconciliation actions | Must act under a traceable service identity and least privilege |

**Action-level permission matrix**:

| Action | Allowed Actors | Preconditions | Failure Behavior | Recovery Behavior | Audit Requirement | QA Acceptance Criteria |
|--------|----------------|---------------|------------------|-------------------|-------------------|------------------------|
| Create draft application | Applicant, Sub-agency Officer | Actor has applicant or agency scope and required consent path | Deny creation | Correct scope or consent and retry | Creation attempt and result | User outside scope cannot create a case |
| Edit draft intake data | Applicant, Sub-agency Officer | Case is draft or correction-requested and actor owns scope | Deny edit and keep data unchanged | Request correction access or transfer | Before/after changed fields where applicable | Submitted cases cannot be edited without correction workflow |
| Upload or replace document | Applicant, Sub-agency Officer | Case is draft, documents pending, OCR/validation, or correction-requested | Reject upload outside allowed state | Move case to correction-requested if replacement is needed | Upload, replacement, and screening result | Unauthorized or late replacement is blocked |
| Review OCR and confirm values | Applicant, Sub-agency Officer | OCR result exists and case is editable by actor | Prevent confirmation | Assign correction to authorized actor | OCR values, confidence, reviewer, correction | OCR values cannot be finalized by unauthorized users |
| Approve validation override | Main Agency Supervisor | Finding is overrideable and reason is provided | Deny override | Correct data or escalate policy exception | Rule, severity, approver, reason | Non-overrideable findings remain blocked |
| Verify wallet and reserve funds | Sub-agency Officer | Case ready for sub-agency review; actor belongs to wallet-owning agency | Block submission | Top up wallet, release stale reservation, or retry | Balance check and reservation result | Other agencies cannot reserve wallet funds |
| Submit to main agency | Sub-agency Officer | Validated snapshot and active wallet reservation exist | Block submission or return existing reference for duplicate | Resolve validation/wallet issue and retry | Submission reference and snapshot | Duplicate submit does not duplicate funds or case |
| Process main agency case | Main Agency Case Officer, Main Agency Supervisor | Case is routed to main agency scope | Deny action | Transfer or assign through supervisor path | Action, assignment, decision reason | Officer outside main agency scope cannot process |
| Submit to GDRFA | Main Agency Case Officer, Main Agency Supervisor, System Service | Readiness approved; required data, documents, and payment prerequisites met | Keep in main agency processing or recovery | Correct prerequisites or controlled retry | GDRFA submission attempt and reference | GDRFA cannot be submitted before readiness approval |
| Reconcile payment or refund | Finance Officer | Payment or wallet event exists and reason/reference is available | Keep unresolved financial state | Finance review or retry permitted action | Amount, currency, reference, reason | Non-finance users cannot mark paid or refunded |
| Record immigration update | Immigration Processing Source, GDRFA or Immigration Liaison, Main Agency Supervisor for controlled manual update | External reference exists and update matches case | Quarantine unmatched or contradictory update | Liaison review and controlled correction | Source, reference, status, reason | Unmatched status does not change case |
| Perform support recovery | Support Admin | Recovery task exists and business reason is provided | Deny recovery | Escalate to supervisor, finance, liaison, or compliance | Access reason, action, result | Support cannot approve financial or immigration outcome |
| View audit history/export | Auditor or Compliance User, authorized supervisors and support users | Actor has audit/export scope and business need | Deny view/export | Request compliance authorization | Access reason, filters, export result | Unauthorized users cannot read audit-only data |

### Data Requirements

- Applicant data includes legal name, date of birth, nationality, contact details, identity references, sponsor details, travel information, and consent records.
- Passport data includes passport number, issuing country, issue date, expiry date, machine-readable details where available, and document image references.
- Document data includes document type, file metadata, upload status, verification status, version, owning application, and retention classification.
- OCR data includes extracted fields, confidence level, extraction status, user-confirmed values, manual corrections, and correction reason where required.
- Validation data includes rule evaluated, result, severity, affected data, responsible party, override decision, and resolution.
- Wallet and payment data includes fee calculation, currency, available balance result, reservation, debit, release, refund, payment reference, reconciliation status, and dispute status.
- Case status data includes lifecycle state, source, timestamp, responsible party, external reference, reason, next action, and terminal outcome where applicable.
- Notification data includes recipient category, channel preference, event, message classification, delivery attempts, delivery result, and retry status.
- Audit and error data includes actor, role, agency scope, time, action, affected case or record, outcome, reason, correlation reference, and recovery action.
- All personal data must have documented classification, lawful processing basis, retention period, deletion or anonymisation path, and legal hold behavior before production use.
- Production personal data must not be used in test environments unless formally approved, minimized, and protected.

### Integrations

- **OCR service**: Extracts data from passport and supporting documents, returns confidence and extraction status, and supports retry or manual fallback.
- **Document screening service**: Checks uploaded documents for security, file integrity, and acceptability before downstream processing.
- **Wallet or ledger service**: Provides available balance checks, reservations, debits, releases, refunds, and reconciliation references for sub-agencies.
- **GDRFA submission service**: Receives approved applications, returns acknowledgement, rejection, action-required, and reference information.
- **Payment provider or payment operations source**: Confirms payment states, receipts, disputes, failures, refunds, and reconciliation outcomes.
- **Immigration processing source**: Provides or receives immigration case status, action-required events, final decisions, and closure information.
- **Identity and access management**: Authenticates users, provides roles, agency scope, privileged access signals, and session controls.
- **Notification gateways**: Send operational messages through approved channels and return delivery or failure outcomes.
- **Monitoring and incident process**: Receives operational, integration, and security events needed for support and incident handling.
- Each integration must have documented data flow, ownership, security responsibility, timeout behavior, retry behavior, duplicate handling, reconciliation approach, and failure procedure.

### Security Requirements

- The system must collect, store, display, and transmit only data needed for a defined visa processing purpose.
- Sensitive data must be encrypted in transit and at rest where supported by the platform.
- Access must follow least privilege, role-based authorization, and agency-level tenant boundaries.
- Privileged roles must use stronger authentication and must provide reasons for sensitive support, override, correction, refund, or audit access actions.
- Applicant sessions must protect personal data during resume, timeout, device change, and failed authentication flows.
- Uploads must be screened before use and rejected safely when unsafe, malformed, or unsupported.
- Secrets, credentials, tokens, and sensitive integration details must never be exposed in source control, logs, notification content, exports, or client-delivered bundles.
- Personal data must be masked or minimized in lists, notifications, logs, exports, and support views unless full detail is required for the user's authorized task.
- Security-sensitive changes affecting authentication, authorization, personal data, payments, eligibility, or external case-system interfaces require threat and privacy impact review before release.
- Incidents involving confidentiality, integrity, availability, payments, or incorrect decisions must be recorded, remediated, and used to improve safeguards.

### Audit Requirements

- Audit records must include actor or service identity, role, agency scope, timestamp, action, affected case or record, result, reason where applicable, and correlation reference.
- Audit records must be created for application creation, edits, submission, state changes, document upload, OCR review, validation result, override, wallet check, reservation, debit, release, payment, refund, external submission, external response, notification, privileged access, support action, retention action, legal hold, and error recovery.
- Audit history must be durable, tamper-evident, searchable by authorized users, exportable for compliance needs, and protected from ordinary modification or deletion.
- Submitted application snapshots, decision rationale, financial events, and final outcomes must be preserved according to applicable retention rules.
- Audit records must distinguish user actions, service actions, external events, automated rule evaluations, and administrative actions.
- Legal, regulatory, or policy exceptions must record owner, expiry, mitigation, and approval.

### Accessibility Requirements

- Applicant-facing journeys must meet WCAG 2.1 AA or a stricter applicable standard.
- All forms, upload controls, OCR review screens, validation findings, status timelines, and confirmation messages must be usable by keyboard and assistive technology.
- Field requirements, examples, validation errors, correction requests, payment status, and final outcomes must be written in clear, actionable language.
- Error messages must identify the field or document needing action and must not rely on color alone.
- Interrupted sessions must be recoverable without exposing personal data to unauthorized users.
- Timeouts, long-running OCR checks, external processing waits, and payment waits must communicate state and next action clearly.
- The system must support accessible alternatives for document upload and OCR review when automated extraction is unavailable or unusable.

### QA and Testing Considerations

- Test complete happy paths from draft through final immigration decision for applicant-led and sub-agency-led applications.
- Test authorization boundaries for every role, agency scope, wallet, document, payment, audit, support, and export action.
- Test validation rules, OCR correction flows, duplicate detection, missing document handling, and visa-type rule changes.
- Test wallet shortfall, fee change, reservation, debit, release, refund, and reconciliation scenarios.
- Test GDRFA, payment, immigration, notification, OCR, and document screening failures, retries, duplicates, late events, and out-of-order events.
- Test that submitted snapshots, final decisions, financial records, and audit records cannot be modified by unauthorized users.
- Test accessibility using automated checks and manual keyboard and screen reader review for primary applicant workflows.
- Test privacy controls for masking, notification content, logs, exports, session recovery, and use of production personal data in non-production environments.
- Test performance using expected operating volume, including at least 10,000 active applications and 500 concurrent authorized users unless planning revises the assumption.
- Test migration or rule-change behavior to confirm in-progress applications are not silently lost, duplicated, or misrouted.

### Key Entities *(include if feature involves data)*

- **Applicant**: Person applying for a visa; includes identity, contact, nationality, sponsor, consent, and relationship to applications.
- **Visa Application**: End-to-end case record connecting applicant, visa type, agency ownership, workflow status, submissions, payments, decisions, and audit history.
- **Passport**: Primary travel document with number, issuing country, issue date, expiry date, extracted fields, and document reference.
- **Document**: Uploaded file or evidence item required for a visa type; includes type, status, version, screening result, and retention classification.
- **OCR Result**: Extracted document data with confidence, source document, status, reviewed value, correction, and reviewer.
- **Validation Finding**: Rule result identifying missing, inconsistent, risky, or blocked data requiring action or override.
- **Agency**: Sub-agency or main agency organization with users, scope, wallet relationship, processing permissions, and case ownership.
- **Wallet Ledger Event**: Financial availability check, reservation, debit, release, refund, or reconciliation entry tied to a sub-agency and case.
- **Submission**: Transfer of a case from sub-agency to main agency or from main agency to GDRFA with references, status, and response.
- **Processing Task**: Work item assigned to agency, finance, support, GDRFA liaison, or immigration liaison users.
- **External Case Response**: Acknowledgement, rejection, action-required event, status update, or final decision from GDRFA, payment, or immigration sources.
- **Payment**: Financial obligation and outcome associated with the application, including amount, currency, state, receipt, dispute, and reconciliation.
- **Status Event**: Chronological case timeline entry visible according to user role and data sensitivity.
- **Notification**: Message generated from a lifecycle event with recipient category, channel, delivery status, and retry history.
- **Audit Event**: Durable trace record for actions, decisions, access, integration events, financial events, and recovery actions.
- **Error Record**: Operational or integration failure record with impact, status, recovery owner, and resolution.
- **Consent and Retention Policy**: Records lawful basis, consent, retention, deletion, anonymisation, and legal hold obligations for application data.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: At least 95% of applicants or sub-agency officers can complete required intake fields for a standard application in 15 minutes or less, excluding external wait time.
- **SC-002**: At least 95% of supported valid document uploads receive an accept/reject result and OCR status within 2 minutes.
- **SC-003**: 100% of OCR-extracted passport data presented for submission is reviewed or corrected by an authorized user before agency submission.
- **SC-004**: 99.5% of accepted sub-agency submissions create exactly one auditable submission reference and no duplicate wallet reservation.
- **SC-005**: 100% of insufficient-wallet submission attempts are blocked before main agency submission.
- **SC-006**: At least 95% of received GDRFA, payment, immigration, and notification status events are visible to authorized users within 5 minutes of receipt.
- **SC-007**: 100% of privileged access, state change, document action, validation decision, wallet event, payment event, external submission, and final decision events have complete audit records.
- **SC-008**: Applicant-facing workflows meet WCAG 2.1 AA, with at least 90% of representative users completing the primary application flow on first attempt during acceptance testing.
- **SC-009**: No release of this feature knowingly loses, duplicates, or misroutes an in-progress application during normal processing, retries, or documented rule changes.
- **SC-010**: At least 98% of required notification events are queued within 1 minute of the triggering lifecycle event, with failed delivery attempts visible to authorized support users.
- **SC-011**: 100% of attempted status changes either follow the transition matrix or are rejected without changing the case.
- **SC-012**: 100% of wallet reservation, debit, release, refund, and duplicate submission test cases produce one correct financial outcome and complete audit evidence.
- **SC-013**: 100% of integration retry tests preserve a single business outcome per external reference and create a recovery task when retry limits are reached.

## Assumptions

- The baseline visa policy requires at least six months of passport validity at sub-agency submission unless a configured policy exception applies.
- Applicants may create applications directly, and sub-agency officers may create or manage applications on behalf of applicants when authorized.
- GDRFA, payment, immigration, OCR, document screening, wallet, identity, and notification capabilities are external or separately governed services with documented contracts.
- Wallet verification applies to sub-agency submission before main agency processing; final payment timing may vary by visa type and external processing rule.
- The feature covers operational lifecycle management and does not define government policy, visa eligibility law, or external agency decision criteria.
- Standard active operating volume is assumed to include at least 10,000 active applications and 500 concurrent authorized users until refined during planning.
- Notification content must remain minimal and direct users to authenticated status views for sensitive details.
- Retention, deletion, anonymisation, and legal hold rules will be finalized with compliance owners before production release.

## Dependencies

- Current visa-type rules, document requirements, fee schedules, passport validity policies, and exception policies.
- Active agency hierarchy, sub-agency wallet ownership, main agency routing rules, and user role assignments.
- Access to OCR, document screening, wallet or ledger, GDRFA, payment, immigration, identity, notification, monitoring, and incident processes.
- Legal and compliance guidance for data classification, lawful processing basis, retention, deletion, anonymisation, and legal holds.
- Security and domain-owner review for authentication, authorization, personal data, payments, eligibility rules, and external case-system interfaces.
- Operational support procedures for failed integrations, disputed payments, quarantined external events, and applicant support.

## Constraints

- The specification defines business behavior only and does not prescribe implementation language, framework, storage, hosting, or integration protocol.
- The system must follow the project constitution, including privacy by design, traceable records, accessibility, reliable workflows, and minimal maintainable change.
- Secrets and sensitive integration details must not appear in source control, logs, client-delivered bundles, notifications, or exported support data.
- External systems may be unavailable, delayed, inconsistent, or manually reconciled; the feature must preserve case integrity during these conditions.
- Completed decisions, submitted snapshots, financial records, and audit records must not be changed except through authorized, audited correction procedures.
- Production personal data must not be used in development or test environments unless formally approved, minimized, and protected.
- Legal, regulatory, or policy requirements that conflict with ordinary product behavior take precedence and must be recorded in the relevant specification or exception record.
