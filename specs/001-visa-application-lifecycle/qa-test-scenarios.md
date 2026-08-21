# QA Test Scenarios: Visa Application Lifecycle

**Source specification**: `specs/001-visa-application-lifecycle/spec.md`  
**Constitution reference**: `.specify/memory/constitution.md`  
**Scope**: Functional requirements FR-001 through FR-042 only. This document defines manual QA test scenarios and does not define automation or implementation changes.

## Scenario Matrix

### FR-001

- **Requirement ID**: FR-001
- **Test Scenario ID**: TS-FR-001
- **Test Scenario**: Verify authorized users can create a visa application for a selected visa type and responsible agency relationship.
- **Preconditions**: Applicant and sub-agency officer accounts exist with valid scope; visa types and agency relationships are configured.
- **Expected Result**: One draft application is created with selected visa type, agency relationship, case reference, initial status, and audit record.
- **Positive scenarios**: Applicant creates own application; sub-agency officer creates an application for an assigned applicant.
- **Negative scenarios**: Unauthenticated user, unauthorized agency user, unsupported visa type, or invalid agency relationship is denied.
- **Edge cases**: Duplicate create click; session timeout during creation; visa type disabled between page load and submit.
- **Security considerations**: Enforce authentication, agency scope, consent path, least privilege, and generic authorization error messages.
- **Priority**: P1

### FR-002

- **Requirement ID**: FR-002
- **Test Scenario ID**: TS-FR-002
- **Test Scenario**: Verify required applicant identity, contact, passport, travel, sponsor, visa type, and consent data is captured before submission.
- **Preconditions**: Draft application exists; visa-type data requirements are configured.
- **Expected Result**: Submission is allowed only after all required fields are present, valid, and retained with the application.
- **Positive scenarios**: Complete all required fields for a standard visa type; save sponsor and consent records.
- **Negative scenarios**: Missing consent, invalid passport dates, missing contact details, or incomplete sponsor data blocks submission.
- **Edge cases**: Conditional fields become required after nationality, sponsor type, or visa type changes.
- **Security considerations**: Mask sensitive identity data in summaries and prevent over-collection beyond defined visa processing purpose.
- **Priority**: P1

### FR-003

- **Requirement ID**: FR-003
- **Test Scenario ID**: TS-FR-003
- **Test Scenario**: Verify draft applications can be saved, resumed, and abandoned according to retention rules.
- **Preconditions**: User has a draft application and retention policy is configured.
- **Expected Result**: Draft data is saved, recoverable only by authorized users, and abandoned drafts follow configured retention or deletion behavior.
- **Positive scenarios**: Save partial draft; resume after logout; abandon a draft where policy allows.
- **Negative scenarios**: Unauthorized user cannot resume; abandoned draft cannot be submitted; expired draft follows retention handling.
- **Edge cases**: Resume from a different device; timeout while editing; retention period expires during inactivity.
- **Security considerations**: Do not expose personal data during resume, timeout, failed authentication, or abandoned-draft recovery.
- **Priority**: P1

### FR-004

- **Requirement ID**: FR-004
- **Test Scenario ID**: TS-FR-004
- **Test Scenario**: Verify completion status and missing required items are shown before agency submission.
- **Preconditions**: Draft or validation-stage application exists with complete and incomplete sections.
- **Expected Result**: The system clearly identifies completed sections, missing fields, missing documents, and next actions.
- **Positive scenarios**: Display complete intake and documents; show actionable missing item list.
- **Negative scenarios**: Attempt agency submission with missing items remains blocked and explains required corrections.
- **Edge cases**: Requirement changes while user is reviewing completion; multiple missing items across sections.
- **Security considerations**: Show only data and missing items allowed for the user's role and agency scope.
- **Priority**: P1

### FR-005

- **Requirement ID**: FR-005
- **Test Scenario ID**: TS-FR-005
- **Test Scenario**: Verify passport and supporting uploads are accepted only when configured type, size, quality, and security requirements pass.
- **Preconditions**: Application is in a document-uploadable state; document rules and screening service are available.
- **Expected Result**: Valid documents are accepted; invalid, unsafe, oversized, unsupported, corrupted, unreadable, or password-protected files are rejected.
- **Positive scenarios**: Upload valid passport image and required supporting document within limits.
- **Negative scenarios**: Upload unsupported extension, file over 10 MB baseline, malware-positive file, corrupted file, or wrong document type.
- **Edge cases**: Interrupted upload; duplicate upload; 20-page baseline limit boundary; stricter visa-type limit.
- **Security considerations**: Screen before processing, block unsafe content, avoid returning sensitive scanner details, and audit attempts.
- **Priority**: P1

### FR-006

- **Requirement ID**: FR-006
- **Test Scenario ID**: TS-FR-006
- **Test Scenario**: Verify document metadata, upload actor, upload time, document type, verification status, and version history are recorded.
- **Preconditions**: User can upload or replace documents for an application.
- **Expected Result**: Each upload and replacement creates a traceable document record with version and verification status.
- **Positive scenarios**: Initial upload records metadata; replacement creates a new version and preserves prior version history.
- **Negative scenarios**: Unauthorized replacement is denied and does not alter metadata or version history.
- **Edge cases**: Same filename uploaded twice; concurrent replacement attempts; timezone display for upload time.
- **Security considerations**: Store only required metadata, protect document references, and audit document actions.
- **Priority**: P1

### FR-007

- **Requirement ID**: FR-007
- **Test Scenario ID**: TS-FR-007
- **Test Scenario**: Verify OCR runs on eligible documents and displays extracted fields with confidence indicators.
- **Preconditions**: Eligible document has passed upload screening; OCR service is configured.
- **Expected Result**: OCR status, extracted values, and confidence are visible for authorized review.
- **Positive scenarios**: High-confidence passport OCR extracts critical fields; low-confidence fields are flagged.
- **Negative scenarios**: Ineligible, unsafe, unsupported, or failed-screening documents are not sent to OCR.
- **Edge cases**: OCR timeout; partial extraction; critical field confidence below 85% or below 60%.
- **Security considerations**: Limit OCR data exposure to authorized users and avoid leaking OCR payloads or service credentials.
- **Priority**: P1

### FR-008

- **Requirement ID**: FR-008
- **Test Scenario ID**: TS-FR-008
- **Test Scenario**: Verify OCR-extracted data requires user review before becoming confirmed application data.
- **Preconditions**: OCR result exists for an editable application.
- **Expected Result**: Extracted values remain advisory until an authorized user confirms or corrects them.
- **Positive scenarios**: User confirms matching OCR values; user corrects mismatched passport number with reason where required.
- **Negative scenarios**: System blocks submission when OCR review is incomplete or reviewer is unauthorized.
- **Edge cases**: OCR values change after document replacement; reviewer confirms then edits before submission.
- **Security considerations**: Audit reviewer, corrections, confidence, and source document while preserving least-privilege access.
- **Priority**: P1

### FR-009

- **Requirement ID**: FR-009
- **Test Scenario ID**: TS-FR-009
- **Test Scenario**: Verify validation covers required fields, document presence, passport rules, visa-type rules, duplicate risk, and agency processing rules.
- **Preconditions**: Application contains intake data, documents, OCR results, and selected visa type.
- **Expected Result**: Validation produces accurate pass or finding results for all configured rule categories.
- **Positive scenarios**: Complete valid application passes; duplicate-risk indicator is flagged without automatic data loss.
- **Negative scenarios**: Missing document, expired passport, unsupported visa type, or unauthorized agency route creates blocking findings.
- **Edge cases**: Passport validity exactly at minimum; visa rules change while draft exists; same passport in another active case.
- **Security considerations**: Avoid exposing other applicants' personal data when showing duplicate-risk findings.
- **Priority**: P1

### FR-010

- **Requirement ID**: FR-010
- **Test Scenario ID**: TS-FR-010
- **Test Scenario**: Verify validation findings show severity, affected field or document, responsible party, and required corrective action.
- **Preconditions**: Application has validation findings across multiple severities.
- **Expected Result**: Findings are clear, actionable, role-appropriate, and tied to the correct data or document.
- **Positive scenarios**: Informational, warning, blocking, overrideable blocking, and non-overrideable blocking findings display correctly.
- **Negative scenarios**: Findings with missing severity, owner, or corrective action are not accepted as complete.
- **Edge cases**: Multiple findings on same field; finding responsibility changes after workflow state changes.
- **Security considerations**: Do not reveal restricted internal rules or unrelated applicant details in user-facing findings.
- **Priority**: P1

### FR-011

- **Requirement ID**: FR-011
- **Test Scenario ID**: TS-FR-011
- **Test Scenario**: Verify submission is blocked while blocking findings remain unresolved or lack authorized override.
- **Preconditions**: Application has blocking and overrideable validation findings.
- **Expected Result**: Submission remains unavailable until findings are corrected or an authorized override is approved with reason.
- **Positive scenarios**: Correct blocking issue and submit; approve overrideable finding by supervisor with reason.
- **Negative scenarios**: Applicant bypass attempt, non-overrideable finding, or override without reason blocks submission.
- **Edge cases**: Finding is resolved while another blocking finding remains; concurrent submit during override review.
- **Security considerations**: Enforce elevated permission for overrides and audit rule, approver, reason, and outcome.
- **Priority**: P1

### FR-012

- **Requirement ID**: FR-012
- **Test Scenario ID**: TS-FR-012
- **Test Scenario**: Verify required fees and charges are calculated for visa type, agency relationship, and processing stage.
- **Preconditions**: Fee schedule and agency relationship are configured.
- **Expected Result**: Fee calculation returns amount, currency, fee version, stage, and charge breakdown.
- **Positive scenarios**: Standard visa fee; agency-specific charge; processing-stage fee.
- **Negative scenarios**: Missing fee schedule or unsupported currency blocks onward financial action.
- **Edge cases**: Fee changes after draft completion or after wallet reservation; rounding at currency precision.
- **Security considerations**: Prevent unauthorized fee override and audit fee version used for financial events.
- **Priority**: P1

### FR-013

- **Requirement ID**: FR-013
- **Test Scenario ID**: TS-FR-013
- **Test Scenario**: Verify sub-agency wallet availability is checked before submission to the main agency.
- **Preconditions**: Validated application is ready for sub-agency review; wallet service is available.
- **Expected Result**: Available balance is checked and submission proceeds only when sufficient funds are available.
- **Positive scenarios**: Sufficient wallet balance passes check; exact balance equal to required amount passes.
- **Negative scenarios**: Insufficient, reserved, disputed, pending, or legally held funds do not count as available.
- **Edge cases**: Balance changes between fee display and wallet verification; wallet service timeout.
- **Security considerations**: Show wallet shortfall only to authorized sub-agency users and audit balance check result.
- **Priority**: P1

### FR-014

- **Requirement ID**: FR-014
- **Test Scenario ID**: TS-FR-014
- **Test Scenario**: Verify wallet amounts are reserved, debited, released, or refunded according to case outcome and financial rules.
- **Preconditions**: Wallet event exists or case reaches a financial transition point.
- **Expected Result**: Correct financial action is applied once and traceably based on case state and active fee rule.
- **Positive scenarios**: Reserve before submission; debit when payable; release on eligible rejection; refund by finance approval.
- **Negative scenarios**: Unauthorized refund, debit without reservation, or release after debit is blocked.
- **Edge cases**: Reservation expiry after 24 hours; fee increase or decrease after reservation; withdrawal before debit.
- **Security considerations**: Restrict financial actions by role and audit amount, currency, fee version, reference, and reason.
- **Priority**: P1

### FR-015

- **Requirement ID**: FR-015
- **Test Scenario ID**: TS-FR-015
- **Test Scenario**: Verify duplicate wallet reservations or debits are prevented for the same accepted submission attempt.
- **Preconditions**: Validated case with wallet reservation flow enabled.
- **Expected Result**: Repeated or concurrent attempts preserve one reservation or debit outcome.
- **Positive scenarios**: Retried submit returns existing reservation or submission reference.
- **Negative scenarios**: Double-click, duplicate API request, or concurrent users do not create duplicate financial events.
- **Edge cases**: Retry after timeout where original request succeeded; duplicate event arrives after debit.
- **Security considerations**: Use business reference idempotency and complete audit trail for original and duplicate attempts.
- **Priority**: P1

### FR-016

- **Requirement ID**: FR-016
- **Test Scenario ID**: TS-FR-016
- **Test Scenario**: Verify sub-agency officers can submit validated applications to the main agency and receive a submission reference.
- **Preconditions**: Application is validated, wallet reservation exists, and officer belongs to owning sub-agency.
- **Expected Result**: Case status changes to submitted to main agency, ordinary edits lock, and a submission reference is returned.
- **Positive scenarios**: Owning sub-agency officer submits successfully.
- **Negative scenarios**: Non-owning sub-agency, applicant, unresolved validation finding, or missing reservation cannot submit.
- **Edge cases**: Application version changed after validation; duplicate submit attempt.
- **Security considerations**: Enforce agency scope, snapshot version match, idempotency, and audit submission reference.
- **Priority**: P1

### FR-017

- **Requirement ID**: FR-017
- **Test Scenario ID**: TS-FR-017
- **Test Scenario**: Verify submitted applications route to the correct main agency queue based on agency relationship and visa type.
- **Preconditions**: Submitted application exists; routing rules are configured.
- **Expected Result**: Case appears in the correct queue and is not visible in unauthorized queues.
- **Positive scenarios**: Route by visa type; route by agency relationship.
- **Negative scenarios**: Missing route configuration keeps case in recovery or submitted queue without misrouting.
- **Edge cases**: Agency relationship changes before submission; routing rule changes during processing.
- **Security considerations**: Maintain tenant boundaries and audit queue, assignment, actor or service, and result.
- **Priority**: P1

### FR-018

- **Requirement ID**: FR-018
- **Test Scenario ID**: TS-FR-018
- **Test Scenario**: Verify main agency officers can review, assign ownership, request corrections, approve readiness, reject, or escalate.
- **Preconditions**: Case is routed to main agency scope; officer or supervisor has proper permissions.
- **Expected Result**: Authorized processing actions update case state or task ownership with required reason where applicable.
- **Positive scenarios**: Assign case; request correction; approve readiness; reject; escalate to supervisor.
- **Negative scenarios**: Officer outside agency scope or unsupported action for current state is denied.
- **Edge cases**: Two officers claim same case; correction requested without actionable reason; escalation after prior rejection.
- **Security considerations**: Enforce role and agency scope, require reasons for decisions, and audit all processing actions.
- **Priority**: P1

### FR-019

- **Requirement ID**: FR-019
- **Test Scenario ID**: TS-FR-019
- **Test Scenario**: Verify main agency decisions record actor, timestamp, decision, reason, and supporting notes or attachments where required.
- **Preconditions**: Main agency decision action is available for a case.
- **Expected Result**: Decision record is complete, traceable, and visible to authorized roles.
- **Positive scenarios**: Approve readiness with rationale; reject with reason and attachment.
- **Negative scenarios**: Decision without mandatory reason, actor, timestamp, or required attachment is rejected.
- **Edge cases**: Attachment upload fails during decision; supervisor amends decision through approved correction process.
- **Security considerations**: Protect internal notes and attachments from unauthorized applicant or agency access.
- **Priority**: P1

### FR-020

- **Requirement ID**: FR-020
- **Test Scenario ID**: TS-FR-020
- **Test Scenario**: Verify approved applications are submitted to GDRFA and submission reference, time, response status, and response reason are recorded.
- **Preconditions**: Main agency readiness is approved and GDRFA prerequisites are satisfied.
- **Expected Result**: GDRFA submission is performed once, tracked, and reflected in case timeline.
- **Positive scenarios**: Successful GDRFA acknowledgement records external reference and timestamp.
- **Negative scenarios**: Missing readiness approval, missing documents, or unauthorized actor cannot submit.
- **Edge cases**: Submission accepted after timeout; duplicate submission request; response reason absent or malformed.
- **Security considerations**: Do not expose integration secrets or full payloads in UI, logs, notifications, or exports.
- **Priority**: P1

### FR-021

- **Requirement ID**: FR-021
- **Test Scenario ID**: TS-FR-021
- **Test Scenario**: Verify GDRFA acknowledgement, rejection, action-required, timeout, duplicate response, and unavailable-service outcomes are handled.
- **Preconditions**: Case has been submitted or is ready to submit to GDRFA.
- **Expected Result**: Each GDRFA outcome updates status, recovery task, retry, or correction flow according to rules.
- **Positive scenarios**: Acknowledgement advances; rejection returns to correction; action-required assigns responsible party.
- **Negative scenarios**: Unauthorized, unmatched, or contradictory response is quarantined and does not change case status.
- **Edge cases**: Duplicate response; late response after manual recovery; service unavailable for retry limit.
- **Security considerations**: Match external reference before status changes and audit source, attempt, result, and recovery owner.
- **Priority**: P1

### FR-022

- **Requirement ID**: FR-022
- **Test Scenario ID**: TS-FR-022
- **Test Scenario**: Verify payment-required, payment-pending, paid, failed, cancelled, refunded, and reconciled payment states are managed.
- **Preconditions**: Case reaches a payment stage or receives payment event.
- **Expected Result**: Payment state changes follow allowed transitions and are visible to authorized users.
- **Positive scenarios**: Payment required becomes pending; pending becomes paid; refund and reconciliation are recorded by finance.
- **Negative scenarios**: Invalid state transition or unsupported actor is denied without changing payment state.
- **Edge cases**: Disputed payment; late failure after paid; refund after case withdrawal.
- **Security considerations**: Restrict payment data by role and avoid exposing full payment references where not required.
- **Priority**: P1

### FR-023

- **Requirement ID**: FR-023
- **Test Scenario ID**: TS-FR-023
- **Test Scenario**: Verify payment cannot be marked paid without authorized confirmation or approved manual reconciliation.
- **Preconditions**: Payment is pending or unresolved.
- **Expected Result**: Paid status is accepted only from authorized provider confirmation or finance-approved reconciliation.
- **Positive scenarios**: Provider confirms paid; finance officer reconciles with receipt and reason.
- **Negative scenarios**: Applicant, support admin, or unverified callback attempts to mark paid are denied or quarantined.
- **Edge cases**: Duplicate confirmation; amount mismatch; currency mismatch; receipt reference reused.
- **Security considerations**: Require traceable source, receipt, amount, currency, reconciler, and audit evidence.
- **Priority**: P1

### FR-024

- **Requirement ID**: FR-024
- **Test Scenario ID**: TS-FR-024
- **Test Scenario**: Verify immigration processing states are tracked from received through terminal outcomes.
- **Preconditions**: Case has payment completion where required and an external case reference.
- **Expected Result**: Immigration statuses update timeline and terminal statuses lock ordinary changes.
- **Positive scenarios**: Received, under review, action required, approved, rejected, cancelled, withdrawn, expired, and closed states display correctly.
- **Negative scenarios**: Unmatched or contradictory status update is quarantined and does not alter the case.
- **Edge cases**: Final decision arrives before intermediate status; withdrawal requested during external processing.
- **Security considerations**: Restrict final decision entry, protect terminal decisions from unauthorized alteration, and audit source and rationale.
- **Priority**: P1

### FR-025

- **Requirement ID**: FR-025
- **Test Scenario ID**: TS-FR-025
- **Test Scenario**: Verify status timeline is exposed to authorized users according to role permissions.
- **Preconditions**: Case has multiple status events across lifecycle.
- **Expected Result**: Users see only timeline entries and details permitted by their role, scope, and business need.
- **Positive scenarios**: Applicant sees own actionable statuses; auditor sees full authorized audit timeline; finance sees payment-related status.
- **Negative scenarios**: Non-owner applicant, unrelated agency, or unauthorized role cannot view restricted timeline data.
- **Edge cases**: Mask internal notes; timeline with out-of-order external event; terminal case with legal hold.
- **Security considerations**: Enforce role-based masking and agency tenant boundaries for case, payment, audit, and internal notes.
- **Priority**: P1

### FR-026

- **Requirement ID**: FR-026
- **Test Scenario ID**: TS-FR-026
- **Test Scenario**: Verify relevant recipients are notified for submission, correction, validation failure, wallet shortfall, payment, GDRFA, immigration, and final decision events.
- **Preconditions**: Notification rules and recipient contacts are configured.
- **Expected Result**: Correct recipients receive actionable, minimal notifications and full details remain behind authenticated access.
- **Positive scenarios**: Correction request to responsible party; wallet shortfall to sub-agency; final decision notice to applicant and agency.
- **Negative scenarios**: Unrelated user or wrong agency recipient does not receive notification.
- **Edge cases**: Invalid contact address; blocked channel; notification event generated during outage.
- **Security considerations**: Minimize personal data, avoid sensitive details in message content, and audit recipient category and delivery attempt.
- **Priority**: P2

### FR-027

- **Requirement ID**: FR-027
- **Test Scenario ID**: TS-FR-027
- **Test Scenario**: Verify notification preferences are allowed where permitted while mandatory operational and legal notices are preserved.
- **Preconditions**: User has notification preference settings and mandatory notice categories are configured.
- **Expected Result**: Optional preferences are honored; mandatory notices continue regardless of opt-out.
- **Positive scenarios**: User changes optional channel preference; mandatory legal notice still sends.
- **Negative scenarios**: User cannot disable mandatory operational or legal notices.
- **Edge cases**: Preference changed immediately before event; inaccessible or invalid preferred channel.
- **Security considerations**: Confirm preference changes require authenticated user and do not expose other recipient contact data.
- **Priority**: P2

### FR-028

- **Requirement ID**: FR-028
- **Test Scenario ID**: TS-FR-028
- **Test Scenario**: Verify notification delivery attempts, results, retries, failures, and recipient category are recorded.
- **Preconditions**: Notification event is triggered.
- **Expected Result**: Delivery history records attempts, result, retry count, failure reason where available, and recipient category.
- **Positive scenarios**: Successful delivery recorded; failed delivery retries and then records failure.
- **Negative scenarios**: Missing recipient category or delivery result prevents complete notification audit record.
- **Edge cases**: Duplicate retry callback; provider timeout; retry limit reached and support visibility required.
- **Security considerations**: Do not log message secrets, tokens, or unnecessary personal data in notification records.
- **Priority**: P2

### FR-029

- **Requirement ID**: FR-029
- **Test Scenario ID**: TS-FR-029
- **Test Scenario**: Verify durable audit records are created for state changes, document actions, validation decisions, wallet events, payment events, external submissions, privileged access, administrative changes, and error recovery.
- **Preconditions**: Representative lifecycle actions can be performed by authorized users and services.
- **Expected Result**: Every auditable action has a durable audit record with required fields and correlation reference.
- **Positive scenarios**: Audit records appear for intake edit, upload, OCR review, validation, wallet, payment, GDRFA, access, and recovery.
- **Negative scenarios**: Action with missing mandatory audit data is rejected or placed in recovery.
- **Edge cases**: Service action; external callback; failed action; retry attempt.
- **Security considerations**: Audit history must be tamper-evident, least-privilege readable, and protected from ordinary deletion.
- **Priority**: P1

### FR-030

- **Requirement ID**: FR-030
- **Test Scenario ID**: TS-FR-030
- **Test Scenario**: Verify unauthorized modification or deletion of completed decisions, submitted snapshots, financial records, and audit records is prevented.
- **Preconditions**: Case has submitted snapshot, financial event, final decision, and audit records.
- **Expected Result**: Ordinary users cannot modify or delete protected records; permitted corrections require elevated audited process.
- **Positive scenarios**: Supervisor performs allowed terminal correction with reason and new audit event.
- **Negative scenarios**: Applicant, sub-agency, support admin, or direct ordinary edit cannot alter protected records.
- **Edge cases**: Correction attempted after legal hold; export followed by deletion request; concurrent correction attempts.
- **Security considerations**: Protect record integrity, enforce immutable storage behavior where available, and audit denied attempts.
- **Priority**: P1

### FR-031

- **Requirement ID**: FR-031
- **Test Scenario ID**: TS-FR-031
- **Test Scenario**: Verify user-facing error messages explain the issue, identify next action, and avoid exposing secrets or unnecessary personal data.
- **Preconditions**: Error conditions can be triggered across forms, upload, wallet, payment, authorization, and integrations.
- **Expected Result**: Messages are actionable, role-appropriate, and free of sensitive implementation details.
- **Positive scenarios**: Missing field error identifies field; upload error requests replacement; wallet shortfall explains next action to authorized user.
- **Negative scenarios**: Stack trace, token, internal endpoint, unrelated personal data, or full sensitive payload is never shown.
- **Edge cases**: Multiple simultaneous errors; external service timeout; access denied.
- **Security considerations**: Use generic security errors where needed and keep detailed diagnostics in protected logs only.
- **Priority**: P1

### FR-032

- **Requirement ID**: FR-032
- **Test Scenario ID**: TS-FR-032
- **Test Scenario**: Verify authorized search, filtering, and export of case, payment, status, error, and audit information for operations, finance, compliance, and support needs.
- **Preconditions**: Test data exists across cases, payments, statuses, errors, and audit records; role permissions are configured.
- **Expected Result**: Search, filter, and export return only data allowed for the user's role and scope.
- **Positive scenarios**: Finance exports payment records; compliance exports audit history; support filters error records.
- **Negative scenarios**: Unauthorized user cannot search or export restricted data; cross-agency data is excluded.
- **Edge cases**: Large export; empty result set; masked fields in export; legal hold case.
- **Security considerations**: Require business need for sensitive exports, mask personal data where possible, and audit export access.
- **Priority**: P1

### FR-033

- **Requirement ID**: FR-033
- **Test Scenario ID**: TS-FR-033
- **Test Scenario**: Verify role-based and agency-scoped access is enforced for every case, document, wallet, payment, notification, and audit action.
- **Preconditions**: Users exist for applicant, sub-agency, main agency, finance, support, auditor, and service roles.
- **Expected Result**: Each action is allowed only for authorized role and agency scope; denied actions leave data unchanged.
- **Positive scenarios**: Each role performs permitted actions within scope.
- **Negative scenarios**: Cross-agency access, privilege escalation, and role misuse are denied.
- **Edge cases**: User belongs to multiple agencies; role revoked during session; transferred case.
- **Security considerations**: Enforce least privilege server-side and audit privileged access and denied attempts.
- **Priority**: P1

### FR-034

- **Requirement ID**: FR-034
- **Test Scenario ID**: TS-FR-034
- **Test Scenario**: Verify retention, deletion, anonymisation, and legal hold handling for every personal data category.
- **Preconditions**: Data categories have classification, lawful basis, retention period, deletion or anonymisation path, and legal hold behavior.
- **Expected Result**: Personal data follows configured lifecycle rules and legal holds override deletion where required.
- **Positive scenarios**: Eligible draft is abandoned and anonymised or deleted; legal hold preserves required records.
- **Negative scenarios**: Deletion request does not remove legally retained submitted snapshot, audit, or financial record.
- **Edge cases**: Consent withdrawn during processing; retention expires while case is terminal; legal hold added before scheduled deletion.
- **Security considerations**: Prevent production personal data use in test environments unless approved, minimized, and protected.
- **Priority**: P1

### FR-035

- **Requirement ID**: FR-035
- **Test Scenario ID**: TS-FR-035
- **Test Scenario**: Verify in-progress applications are preserved during rule, fee, status, or integration changes and required revalidation is identified.
- **Preconditions**: In-progress applications exist across draft, validation, submitted, payment, and immigration states.
- **Expected Result**: Cases are not lost, duplicated, or misrouted; affected users see required revalidation or next action.
- **Positive scenarios**: Visa rule change flags draft for revalidation; fee change triggers additional reservation or release.
- **Negative scenarios**: Change does not silently advance, close, or delete a case.
- **Edge cases**: Integration contract changes during retry; routing rule changes after submission; status matrix changes.
- **Security considerations**: Audit rule or configuration version impacts and protect data integrity during migration.
- **Priority**: P1

### FR-036

- **Requirement ID**: FR-036
- **Test Scenario ID**: TS-FR-036
- **Test Scenario**: Verify the defined status transition matrix is enforced for every lifecycle state change.
- **Preconditions**: Cases exist in each non-terminal and terminal lifecycle status.
- **Expected Result**: Allowed transitions succeed with required preconditions; invalid transitions are rejected without data change.
- **Positive scenarios**: Draft to documents pending; wallet verified to submitted; immigration processing to approved.
- **Negative scenarios**: Draft directly to paid, paid without payment confirmation, terminal status altered by ordinary user.
- **Edge cases**: Withdrawal from different stages; duplicate or late external status; concurrent transition attempts.
- **Security considerations**: Enforce transition authority, source validation, and audit previous status, new status, and result.
- **Priority**: P1

### FR-037

- **Requirement ID**: FR-037
- **Test Scenario ID**: TS-FR-037
- **Test Scenario**: Verify validation findings are classified as informational, warning, blocking, overrideable blocking, or non-overrideable blocking.
- **Preconditions**: Validation rules exist for all severity categories.
- **Expected Result**: Severity controls workflow behavior, display, acknowledgement, correction, and override eligibility.
- **Positive scenarios**: Informational does not block; warning requires acknowledgement; overrideable blocking proceeds only after approval.
- **Negative scenarios**: Non-overrideable finding cannot be bypassed; blocking finding cannot proceed without correction.
- **Edge cases**: Severity changes after policy update; multiple findings with mixed severities.
- **Security considerations**: Restrict override actions and avoid revealing sensitive duplicate-risk details beyond authorized need.
- **Priority**: P1

### FR-038

- **Requirement ID**: FR-038
- **Test Scenario ID**: TS-FR-038
- **Test Scenario**: Verify wallet reservation, debit, release, refund, and reconciliation actions trace to one case, fee calculation version, and accepted submission or payment event.
- **Preconditions**: Financial events are available for cases across submission and payment states.
- **Expected Result**: Each financial action has a single traceable relationship to case, fee version, and business event.
- **Positive scenarios**: Reservation traces to validated snapshot; refund traces to payment event and finance approval.
- **Negative scenarios**: Orphan financial event or mismatched fee version is rejected or routed to finance review.
- **Edge cases**: Fee recalculation after reservation; duplicate provider callback; partial refund.
- **Security considerations**: Protect financial references and audit amount, currency, action, reconciliation state, and actor.
- **Priority**: P1

### FR-039

- **Requirement ID**: FR-039
- **Test Scenario ID**: TS-FR-039
- **Test Scenario**: Verify external submissions, payment confirmations, wallet actions, immigration updates, and notification retries are idempotent by business reference.
- **Preconditions**: Stable business references exist for external and financial operations.
- **Expected Result**: Repeated attempts preserve or return the original outcome without duplicate case, financial, or audit outcomes.
- **Positive scenarios**: Duplicate GDRFA response maps to existing submission; duplicate payment confirmation keeps single paid result.
- **Negative scenarios**: Same payload with different unauthorized reference is quarantined or rejected.
- **Edge cases**: Retry after timeout where first call succeeded; out-of-order duplicate after terminal status; notification retry callback repeated.
- **Security considerations**: Validate source and business reference before mutation and audit original plus duplicate handling.
- **Priority**: P1

### FR-040

- **Requirement ID**: FR-040
- **Test Scenario ID**: TS-FR-040
- **Test Scenario**: Verify action-level permissions for creation, edit, upload, OCR review, validation override, wallet action, submission, processing, payment, immigration update, notification management, support recovery, audit access, export, and closure.
- **Preconditions**: Permission matrix is configured for all roles and actions.
- **Expected Result**: Every protected action checks role, agency scope, lifecycle state, and required business reason where applicable.
- **Positive scenarios**: Each role performs every action explicitly allowed by the permission matrix.
- **Negative scenarios**: Role without permission, wrong agency scope, missing reason, or invalid state is denied.
- **Edge cases**: User role changes mid-session; supervisor temporary access; support recovery attempted without task.
- **Security considerations**: Enforce authorization server-side and audit privileged and denied actions.
- **Priority**: P1

### FR-041

- **Requirement ID**: FR-041
- **Test Scenario ID**: TS-FR-041
- **Test Scenario**: Verify mandatory audit fields are required before accepting auditable lifecycle, access, financial, integration, or recovery events.
- **Preconditions**: Auditable actions can be triggered with complete and incomplete audit metadata.
- **Expected Result**: Complete events are accepted; incomplete auditable actions are rejected or held in recovery until audit data is complete.
- **Positive scenarios**: State change records actor, role, scope, timestamp, action, affected case, outcome, reason where applicable, source, and correlation reference.
- **Negative scenarios**: Missing actor, timestamp, affected case, or correlation reference prevents acceptance.
- **Edge cases**: Service identity action; external callback missing optional reason; recovery event for missing audit data.
- **Security considerations**: Ensure audit records cannot be spoofed, omitted, or modified by ordinary users.
- **Priority**: P1

### FR-042

- **Requirement ID**: FR-042
- **Test Scenario ID**: TS-FR-042
- **Test Scenario**: Verify document and OCR acceptance thresholds are applied before a case proceeds beyond OCR and validation.
- **Preconditions**: Documents and OCR results exist at boundary, below-threshold, and above-threshold quality/confidence values.
- **Expected Result**: Only documents and OCR results meeting configured thresholds or allowed manual recovery can proceed.
- **Positive scenarios**: Supported readable document passes; OCR critical fields above threshold proceed after review.
- **Negative scenarios**: Unsafe document, unreadable text, confidence below 60%, or unresolved mismatch blocks progression.
- **Edge cases**: Confidence exactly 85%; confidence exactly 60%; replacement document after failed OCR; manual entry fallback.
- **Security considerations**: Keep unsafe documents isolated, protect OCR outputs, and audit threshold result and recovery action.
- **Priority**: P1

