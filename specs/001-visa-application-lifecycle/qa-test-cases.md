# QA Test Cases: Visa Application Lifecycle

**Source specification**: `specs/001-visa-application-lifecycle/spec.md`  
**Source scenarios**: `specs/001-visa-application-lifecycle/qa-test-scenarios.md`  
**Constitution reference**: `.specify/memory/constitution.md`  
**Scope**: Functional requirements FR-001 through FR-042.  
**Purpose**: Define detailed manual QA test cases with requirement, scenario, and test-case traceability. This document does not define application code or Playwright automation.

## Traceability Matrix

| Requirement ID | Test Scenario ID | Test Case ID |
|---|---|---|
| FR-001 | TS-FR-001 | TC-FR-001 |
| FR-002 | TS-FR-002 | TC-FR-002 |
| FR-003 | TS-FR-003 | TC-FR-003 |
| FR-004 | TS-FR-004 | TC-FR-004 |
| FR-005 | TS-FR-005 | TC-FR-005 |
| FR-006 | TS-FR-006 | TC-FR-006 |
| FR-007 | TS-FR-007 | TC-FR-007 |
| FR-008 | TS-FR-008 | TC-FR-008 |
| FR-009 | TS-FR-009 | TC-FR-009 |
| FR-010 | TS-FR-010 | TC-FR-010 |
| FR-011 | TS-FR-011 | TC-FR-011 |
| FR-012 | TS-FR-012 | TC-FR-012 |
| FR-013 | TS-FR-013 | TC-FR-013 |
| FR-014 | TS-FR-014 | TC-FR-014 |
| FR-015 | TS-FR-015 | TC-FR-015 |
| FR-016 | TS-FR-016 | TC-FR-016 |
| FR-017 | TS-FR-017 | TC-FR-017 |
| FR-018 | TS-FR-018 | TC-FR-018 |
| FR-019 | TS-FR-019 | TC-FR-019 |
| FR-020 | TS-FR-020 | TC-FR-020 |
| FR-021 | TS-FR-021 | TC-FR-021 |
| FR-022 | TS-FR-022 | TC-FR-022 |
| FR-023 | TS-FR-023 | TC-FR-023 |
| FR-024 | TS-FR-024 | TC-FR-024 |
| FR-025 | TS-FR-025 | TC-FR-025 |
| FR-026 | TS-FR-026 | TC-FR-026 |
| FR-027 | TS-FR-027 | TC-FR-027 |
| FR-028 | TS-FR-028 | TC-FR-028 |
| FR-029 | TS-FR-029 | TC-FR-029 |
| FR-030 | TS-FR-030 | TC-FR-030 |
| FR-031 | TS-FR-031 | TC-FR-031 |
| FR-032 | TS-FR-032 | TC-FR-032 |
| FR-033 | TS-FR-033 | TC-FR-033 |
| FR-034 | TS-FR-034 | TC-FR-034 |
| FR-035 | TS-FR-035 | TC-FR-035 |
| FR-036 | TS-FR-036 | TC-FR-036 |
| FR-037 | TS-FR-037 | TC-FR-037 |
| FR-038 | TS-FR-038 | TC-FR-038 |
| FR-039 | TS-FR-039 | TC-FR-039 |
| FR-040 | TS-FR-040 | TC-FR-040 |
| FR-041 | TS-FR-041 | TC-FR-041 |
| FR-042 | TS-FR-042 | TC-FR-042 |

## Test Cases

### TC-FR-001 - Create visa application with authorized scope

| Field | Details |
|---|---|
| Test Case ID | TC-FR-001 |
| Requirement ID | FR-001 |
| Test Scenario ID | TS-FR-001 |
| Module | Application Intake / Case Creation |
| Test Case Title | Authorized user creates a visa application for selected visa type and agency relationship |
| Objective | Verify only authorized applicants and sub-agency officers can create one draft case with the selected visa type, responsible agency relationship, initial status, case reference, and audit record. |
| Preconditions | Applicant account, sub-agency officer account, unauthorized agency account, visa types, consent path, and agency relationships are configured. |
| Test Data | Valid applicant profile; valid sub-agency officer; invalid agency relationship; disabled visa type; duplicate create attempt; expired session. |
| Test Steps | 1. Log in as an applicant and start a new application with a valid visa type and agency relationship. 2. Save the case creation request. 3. Review the generated case reference, visa type, agency relationship, draft status, and audit event. 4. Repeat as an authorized sub-agency officer for an assigned applicant. 5. Attempt creation as an unauthenticated user, unrelated agency user, invalid agency relationship, and disabled visa type. 6. Repeat the valid creation request using duplicate submission or browser refresh. 7. Attempt creation after session timeout. |
| Expected Result | Valid applicant and authorized sub-agency creation requests create exactly one draft application each, with the selected visa type, agency relationship, case reference, initial status, and audit record. Unauthorized, unauthenticated, invalid relationship, disabled visa type, and expired-session attempts are denied without case creation and with a generic, actionable error. Duplicate attempts do not create duplicate cases. |
| Priority | P1 |
| Test Type | Functional, Security, Authorization, Audit, Error Handling, Idempotency, Accessibility |
| Positive/Negative | Positive and Negative |
| Automation Candidate | Yes |
| Traceability | FR-001 -> TS-FR-001 -> TC-FR-001 |

### TC-FR-002 - Capture mandatory intake data before submission

| Field | Details |
|---|---|
| Test Case ID | TC-FR-002 |
| Requirement ID | FR-002 |
| Test Scenario ID | TS-FR-002 |
| Module | Application Intake / Data Capture |
| Test Case Title | Required applicant, contact, passport, travel, sponsor, visa type, and consent data gate submission |
| Objective | Verify required intake fields are captured, validated, retained, and protected before submission is allowed. |
| Preconditions | Draft application exists; visa-type-specific required fields, sponsor rules, passport rules, consent requirements, and contact validations are configured. |
| Test Data | Complete standard application; missing consent; invalid passport dates; missing contact; incomplete sponsor; nationality or visa type requiring conditional fields; excessive non-required personal data. |
| Test Steps | 1. Complete all required identity, contact, passport, travel, sponsor, visa type, and consent fields for a standard visa type. 2. Save and attempt to submit or advance to the next workflow gate. 3. Remove each required data category one at a time and repeat the submission attempt. 4. Enter invalid passport issue and expiry dates. 5. Change nationality, sponsor type, or visa type so conditional fields become required. 6. Review summaries and logs for masking and over-collection. 7. Use keyboard and assistive technology to reach fields, errors, and consent controls. |
| Expected Result | Complete valid data permits the next workflow step. Missing consent, missing required data, invalid passport dates, and incomplete conditional fields block submission with field-specific, actionable errors. Sensitive identity data is masked where summaries do not require full detail, unnecessary personal data is not requested, and accessibility labels and focus behavior support correction. |
| Priority | P1 |
| Test Type | Functional, Validation, Boundary, Data Integrity, Security, Accessibility |
| Positive/Negative | Positive and Negative |
| Automation Candidate | Yes |
| Traceability | FR-002 -> TS-FR-002 -> TC-FR-002 |

### TC-FR-003 - Save, resume, and abandon draft applications

| Field | Details |
|---|---|
| Test Case ID | TC-FR-003 |
| Requirement ID | FR-003 |
| Test Scenario ID | TS-FR-003 |
| Module | Draft Lifecycle / Retention |
| Test Case Title | Draft applications are saved, resumed, and abandoned under retention rules |
| Objective | Verify draft data can be safely saved and resumed by authorized users, abandoned drafts cannot proceed, and retention behavior protects personal data. |
| Preconditions | Retention policy is configured; applicant and authorized sub-agency user have editable drafts; unauthorized user exists. |
| Test Data | Partial draft; draft with sensitive passport data; abandoned draft; expired draft; different-device resume; timeout during edit. |
| Test Steps | 1. Save a partial draft and log out. 2. Resume the draft after reauthentication from the same device. 3. Resume from a different device after successful authentication. 4. Attempt resume as a non-owner applicant and unrelated agency user. 5. Trigger session timeout while editing and then reauthenticate. 6. Abandon the draft where policy permits. 7. Attempt to submit or resume the abandoned or expired draft. 8. Review audit, retention, deletion, or anonymisation records. |
| Expected Result | Authorized users can resume saved drafts with missing-field context. Unauthorized users cannot view or recover the draft. Timeout and device-change flows require authentication and do not expose personal data. Abandoned or expired drafts follow retention rules and cannot be submitted unless the policy permits recovery. Save, resume, abandon, denial, and retention actions are audited. |
| Priority | P1 |
| Test Type | Functional, Security, Privacy, Recovery, Retention, Audit, Accessibility |
| Positive/Negative | Positive and Negative |
| Automation Candidate | Yes |
| Traceability | FR-003 -> TS-FR-003 -> TC-FR-003 |

### TC-FR-004 - Display completion status and missing items

| Field | Details |
|---|---|
| Test Case ID | TC-FR-004 |
| Requirement ID | FR-004 |
| Test Scenario ID | TS-FR-004 |
| Module | Intake Progress / Readiness |
| Test Case Title | Completion status and missing required items are visible before agency submission |
| Objective | Verify the application readiness view accurately identifies completed sections, missing fields, missing documents, validation blockers, and role-appropriate next actions. |
| Preconditions | Applications exist with complete intake, incomplete intake, missing documents, and validation findings. |
| Test Data | Complete application; application missing contact, consent, passport image, supporting document, and visa-type conditional field; rule change during review. |
| Test Steps | 1. Open a complete application and review the completion status. 2. Open an incomplete application and review missing item grouping by section. 3. Attempt agency submission with missing fields and documents. 4. Apply a visa-type requirement change while the user is on the readiness page and refresh or retry submission. 5. Log in as applicant, sub-agency officer, and unrelated user to compare visible detail. 6. Navigate missing item links using keyboard only. |
| Expected Result | Complete sections are marked complete and incomplete sections list clear missing fields, documents, validation blockers, and next actions. Submission remains blocked while required items are missing. Rule changes trigger updated readiness or revalidation without silent advancement. Users see only details allowed by role and agency scope, and missing-item controls are accessible. |
| Priority | P1 |
| Test Type | Functional, Validation, Authorization, Data Integrity, Accessibility |
| Positive/Negative | Positive and Negative |
| Automation Candidate | Yes |
| Traceability | FR-004 -> TS-FR-004 -> TC-FR-004 |

### TC-FR-005 - Accept only valid and safe document uploads

| Field | Details |
|---|---|
| Test Case ID | TC-FR-005 |
| Requirement ID | FR-005 |
| Test Scenario ID | TS-FR-005 |
| Module | Document Upload / Screening |
| Test Case Title | Passport and supporting documents pass type, size, quality, and security checks before acceptance |
| Objective | Verify valid documents are accepted and unsafe, invalid, oversized, corrupted, duplicated, interrupted, or unsupported files are rejected safely. |
| Preconditions | Application is in a document-uploadable state; document type rules, size limits, page limits, quality checks, and screening service are configured. |
| Test Data | Valid passport image; valid support document; unsupported extension; file over 10 MB; exactly 10 MB file; 20-page and 21-page files; malware-positive file; corrupted file; unreadable image; password-protected file; wrong document type. |
| Test Steps | 1. Upload valid passport and supporting document within configured limits. 2. Upload files at size and page-count boundaries. 3. Upload unsupported, oversized, corrupted, unreadable, password-protected, wrong-type, and malware-positive files. 4. Interrupt an upload and retry. 5. Upload the same file twice. 6. Review user errors, document records, screening result, and audit entries. 7. Verify upload controls and errors are keyboard and screen-reader usable. |
| Expected Result | Valid files are accepted and associated with the application. Boundary files are accepted or rejected according to configured thresholds. Unsafe or invalid files are rejected before downstream processing, with no sensitive scanner details exposed. Interrupted uploads recover cleanly, duplicate uploads do not corrupt document state, and all attempts are audited. |
| Priority | P1 |
| Test Type | Functional, Negative, Boundary, Security, Integration, Error Handling, Recovery, Accessibility |
| Positive/Negative | Positive and Negative |
| Automation Candidate | Partial |
| Traceability | FR-005 -> TS-FR-005 -> TC-FR-005 |

### TC-FR-006 - Record document metadata and version history

| Field | Details |
|---|---|
| Test Case ID | TC-FR-006 |
| Requirement ID | FR-006 |
| Test Scenario ID | TS-FR-006 |
| Module | Document Management |
| Test Case Title | Upload metadata, actor, time, status, and versions are traceable |
| Objective | Verify every document upload and replacement creates accurate metadata, verification status, version history, protected references, and audit evidence. |
| Preconditions | User can upload and replace documents in allowed states; unauthorized user exists; timezone display is configured. |
| Test Data | Initial passport upload; replacement file; same filename twice; concurrent replacement requests; unauthorized replacement attempt. |
| Test Steps | 1. Upload an initial passport document and inspect metadata. 2. Replace it with a new document version. 3. Upload a different file using the same filename. 4. Attempt concurrent replacements from two authorized sessions. 5. Attempt replacement by an unauthorized user and in a disallowed workflow state. 6. Verify displayed upload time across timezone settings. 7. Review audit trail and prior version preservation. |
| Expected Result | Each accepted upload records document type, actor, upload time, verification status, metadata, protected file reference, and version. Replacement preserves prior versions and creates a new version. Unauthorized or disallowed replacement is denied without altering metadata. Concurrent replacement resolves deterministically without version loss. Audit records identify the action and outcome. |
| Priority | P1 |
| Test Type | Functional, Data Integrity, Authorization, Audit, Boundary |
| Positive/Negative | Positive and Negative |
| Automation Candidate | Yes |
| Traceability | FR-006 -> TS-FR-006 -> TC-FR-006 |

### TC-FR-007 - Run OCR on eligible documents and show confidence

| Field | Details |
|---|---|
| Test Case ID | TC-FR-007 |
| Requirement ID | FR-007 |
| Test Scenario ID | TS-FR-007 |
| Module | OCR / Document Extraction |
| Test Case Title | Eligible documents receive OCR with extracted fields and confidence indicators |
| Objective | Verify OCR is requested only for eligible screened documents and authorized users can review extraction status, values, and confidence indicators. |
| Preconditions | OCR service is configured; documents exist with pass and fail screening outcomes. |
| Test Data | High-confidence passport; low-confidence passport; document below 60 percent confidence; document near 85 percent confidence; unsupported document; unsafe document; OCR timeout; partial extraction. |
| Test Steps | 1. Upload a screened valid passport and trigger OCR. 2. Review extracted fields, OCR status, confidence values, and low-confidence flags. 3. Submit ineligible, unsafe, unsupported, and failed-screening documents and confirm OCR is not requested. 4. Simulate OCR timeout and partial extraction. 5. Log in as unauthorized user and attempt to view OCR output. 6. Review service identity and audit records without exposing OCR payload secrets. |
| Expected Result | Eligible documents proceed to OCR and display extracted fields with confidence indicators to authorized users. Ineligible or unsafe documents are not sent to OCR. Low confidence, partial extraction, and timeout produce actionable review or recovery states. Unauthorized users cannot access OCR output, and service credentials or raw sensitive payloads are not exposed. |
| Priority | P1 |
| Test Type | Functional, Integration, Security, Error Handling, Recovery, Accessibility |
| Positive/Negative | Positive and Negative |
| Automation Candidate | Partial |
| Traceability | FR-007 -> TS-FR-007 -> TC-FR-007 |

### TC-FR-008 - Require review before OCR data becomes confirmed

| Field | Details |
|---|---|
| Test Case ID | TC-FR-008 |
| Requirement ID | FR-008 |
| Test Scenario ID | TS-FR-008 |
| Module | OCR Review / Data Confirmation |
| Test Case Title | OCR-extracted values remain advisory until authorized review or correction |
| Objective | Verify OCR values cannot become confirmed application data until reviewed, corrected where needed, and confirmed by an authorized user. |
| Preconditions | OCR result exists for an editable application; users with authorized and unauthorized roles exist. |
| Test Data | Matching OCR values; passport number mismatch; document replacement after OCR; reviewer correction reason; unauthorized reviewer; incomplete OCR review. |
| Test Steps | 1. Open OCR results with matching values and confirm them as an authorized user. 2. Open OCR results with mismatched passport number and correct the value with required reason. 3. Attempt submission before OCR review is complete. 4. Attempt confirmation as an unauthorized user. 5. Replace the source document after OCR review and inspect confirmed data state. 6. Review audit details for source document, confidence, reviewer, correction, and reason. |
| Expected Result | OCR values remain advisory until authorized confirmation. Corrected values become confirmed data only after required reason capture where applicable. Submission is blocked while OCR review is incomplete or reviewer is unauthorized. Document replacement invalidates or reopens review according to configured rules without stale confirmed data. |
| Priority | P1 |
| Test Type | Functional, Validation, Authorization, Data Integrity, Audit, Accessibility |
| Positive/Negative | Positive and Negative |
| Automation Candidate | Yes |
| Traceability | FR-008 -> TS-FR-008 -> TC-FR-008 |

### TC-FR-009 - Validate application rule categories

| Field | Details |
|---|---|
| Test Case ID | TC-FR-009 |
| Requirement ID | FR-009 |
| Test Scenario ID | TS-FR-009 |
| Module | Validation Engine |
| Test Case Title | Application data validates required fields, documents, passport, visa-type, duplicate-risk, and agency rules |
| Objective | Verify validation evaluates all configured rule categories and produces accurate pass or finding outcomes without data loss or unauthorized disclosure. |
| Preconditions | Application contains intake data, documents, OCR review, selected visa type, agency route, and duplicate-risk test data. |
| Test Data | Complete valid application; missing required document; expired passport; passport exactly at minimum validity; unsupported visa type; duplicate passport in another active case; unauthorized agency route; visa rule change during draft. |
| Test Steps | 1. Validate a complete application that satisfies all rule categories. 2. Validate cases with missing document, expired passport, unsupported visa type, and invalid agency route. 3. Validate passport validity exactly at the configured minimum. 4. Validate a case with same passport or applicant in another active application. 5. Change visa rules while a draft exists and rerun validation. 6. Review finding details, responsible party, masking, and audit records. |
| Expected Result | Complete valid data passes validation. Invalid cases produce accurate findings by category and block only when severity requires. Boundary validity is handled according to policy. Duplicate-risk findings do not expose unrelated applicant personal data or delete data. Rule changes trigger revalidation and traceable version impact. |
| Priority | P1 |
| Test Type | Functional, Validation, Boundary, Data Integrity, Security, Audit |
| Positive/Negative | Positive and Negative |
| Automation Candidate | Yes |
| Traceability | FR-009 -> TS-FR-009 -> TC-FR-009 |

### TC-FR-010 - Display actionable validation findings

| Field | Details |
|---|---|
| Test Case ID | TC-FR-010 |
| Requirement ID | FR-010 |
| Test Scenario ID | TS-FR-010 |
| Module | Validation Findings / User Guidance |
| Test Case Title | Validation findings show severity, affected item, owner, and corrective action |
| Objective | Verify findings are complete, understandable, role-appropriate, accessible, and tied to the correct field or document. |
| Preconditions | Application has informational, warning, blocking, overrideable blocking, and non-overrideable blocking findings. |
| Test Data | Findings on one field; multiple findings on same field; findings without severity or owner; responsibility change after workflow state change; restricted internal rule. |
| Test Steps | 1. Trigger validation findings across all severity categories. 2. Review each finding for severity, affected field or document, responsible party, and corrective action. 3. Trigger multiple findings on the same field. 4. Move the case to a new workflow state and verify responsible party changes where applicable. 5. Attempt to accept a finding with missing severity, owner, or corrective action. 6. Review applicant-facing and staff-facing wording for sensitive-rule disclosure. 7. Validate keyboard focus and screen-reader announcement for findings. |
| Expected Result | Findings display complete and actionable information appropriate to the user's role. Incomplete finding records are rejected or placed in recovery. Multiple findings remain distinguishable. Responsibility changes align with workflow state. Restricted internal rules and unrelated applicant data are not exposed. |
| Priority | P1 |
| Test Type | Functional, Validation, Security, Accessibility, Data Integrity |
| Positive/Negative | Positive and Negative |
| Automation Candidate | Yes |
| Traceability | FR-010 -> TS-FR-010 -> TC-FR-010 |

### TC-FR-011 - Block submission with unresolved blocking findings

| Field | Details |
|---|---|
| Test Case ID | TC-FR-011 |
| Requirement ID | FR-011 |
| Test Scenario ID | TS-FR-011 |
| Module | Validation Gate / Submission Control |
| Test Case Title | Blocking findings prevent submission until corrected or authorized override exists |
| Objective | Verify submission cannot proceed when blocking findings remain unresolved unless an authorized overrideable finding is approved with a reason. |
| Preconditions | Application contains blocking, overrideable blocking, and non-overrideable blocking findings; supervisor user exists. |
| Test Data | Correctable blocking issue; overrideable finding; non-overrideable finding; override without reason; concurrent submit during override review; applicant bypass attempt. |
| Test Steps | 1. Attempt submission with unresolved blocking findings. 2. Correct one blocking issue while another remains and retry. 3. Approve an overrideable blocking finding as a supervisor with reason and retry. 4. Attempt override without reason and as unauthorized user. 5. Attempt to bypass submission gate as applicant or by stale page state. 6. Attempt concurrent submission while override is pending. 7. Review audit entries for rule, severity, approver, reason, and outcome. |
| Expected Result | Submission is blocked until all blocking findings are corrected or valid overrides exist. Non-overrideable findings cannot be bypassed. Override requires elevated permission and reason. Stale, concurrent, or bypass attempts leave the case unchanged and are audited. |
| Priority | P1 |
| Test Type | Functional, Negative, Authorization, Security, Audit, Concurrency |
| Positive/Negative | Positive and Negative |
| Automation Candidate | Yes |
| Traceability | FR-011 -> TS-FR-011 -> TC-FR-011 |

### TC-FR-012 - Calculate fees by visa type, agency, and stage

| Field | Details |
|---|---|
| Test Case ID | TC-FR-012 |
| Requirement ID | FR-012 |
| Test Scenario ID | TS-FR-012 |
| Module | Fees / Financial Calculation |
| Test Case Title | Required fees and charges are calculated with amount, currency, version, stage, and breakdown |
| Objective | Verify fee calculation uses selected visa type, agency relationship, and processing stage, and handles missing schedules, currency, rounding, and fee changes. |
| Preconditions | Fee schedules, currencies, agency relationships, and stage rules are configured. |
| Test Data | Standard visa fee; agency-specific charge; stage-specific charge; missing schedule; unsupported currency; amount with rounding precision; fee increase and decrease after draft completion or reservation. |
| Test Steps | 1. Calculate fees for a standard visa type and valid agency relationship. 2. Calculate agency-specific and stage-specific charges. 3. Validate amount, currency, fee version, stage, and charge breakdown. 4. Attempt calculation with missing fee schedule and unsupported currency. 5. Test rounding at configured currency precision. 6. Change fee rules after draft completion and after reservation. 7. Attempt unauthorized fee override. |
| Expected Result | Valid calculation returns accurate amount, currency, fee version, stage, and breakdown. Missing schedule or unsupported currency blocks onward financial action. Rounding follows currency rules. Fee changes are versioned and produce required revalidation, reservation, release, or additional charge behavior. Unauthorized overrides are denied and audited. |
| Priority | P1 |
| Test Type | Functional, Boundary, Data Integrity, Security, Audit |
| Positive/Negative | Positive and Negative |
| Automation Candidate | Yes |
| Traceability | FR-012 -> TS-FR-012 -> TC-FR-012 |

### TC-FR-013 - Verify wallet availability before main agency submission

| Field | Details |
|---|---|
| Test Case ID | TC-FR-013 |
| Requirement ID | FR-013 |
| Test Scenario ID | TS-FR-013 |
| Module | Wallet / Availability Check |
| Test Case Title | Sub-agency wallet availability gates submission to main agency |
| Objective | Verify wallet availability is checked before submission and only sufficient available balance permits the submission flow. |
| Preconditions | Validated application is ready for sub-agency review; wallet service is configured; sub-agency and non-owning agency users exist. |
| Test Data | Sufficient balance; exact required balance; insufficient balance; reserved funds; disputed funds; pending funds; legally held funds; wallet timeout; balance change between display and verification. |
| Test Steps | 1. Verify wallet with sufficient balance and exact balance equal to required fee. 2. Verify wallet with insufficient, reserved, disputed, pending, and legally held funds. 3. Attempt wallet check as a non-owning agency user. 4. Change wallet balance between fee display and verification. 5. Simulate wallet service timeout. 6. Review shortfall messaging, recovery path, and audit records. |
| Expected Result | Sufficient available balance and exact balance pass. Insufficient or unavailable funds block submission without reservation. Non-owning agencies cannot check or reserve wallet funds. Balance changes are handled at verification time. Wallet timeout keeps the case ready for review or recovery without financial mutation. Shortfall details are shown only to authorized users and audit records are complete. |
| Priority | P1 |
| Test Type | Functional, Boundary, Integration, Authorization, Error Handling, Recovery, Audit |
| Positive/Negative | Positive and Negative |
| Automation Candidate | Partial |
| Traceability | FR-013 -> TS-FR-013 -> TC-FR-013 |

### TC-FR-014 - Apply wallet reserve, debit, release, and refund rules

| Field | Details |
|---|---|
| Test Case ID | TC-FR-014 |
| Requirement ID | FR-014 |
| Test Scenario ID | TS-FR-014 |
| Module | Wallet / Ledger Lifecycle |
| Test Case Title | Wallet financial actions follow case outcome and financial rules |
| Objective | Verify reservations, debits, releases, and refunds occur once, at the correct lifecycle point, and only by authorized actors or sources. |
| Preconditions | Cases exist at submission, debit, rejection, withdrawal, and refund stages; finance officer and unauthorized users exist. |
| Test Data | Reservation before submission; debit when payable; release on eligible rejection; refund approval; unauthorized refund; debit without reservation; release after debit; reservation expiry after 24 hours; fee increase or decrease after reservation. |
| Test Steps | 1. Reserve wallet amount during accepted submission. 2. Debit according to payable case outcome. 3. Release reserved funds on eligible rejection or withdrawal before debit. 4. Process refund as finance officer with approval reason. 5. Attempt unauthorized refund, debit without reservation, and release after debit. 6. Expire a reservation after 24 hours and retry. 7. Change fee after reservation and verify additional reservation or release handling. |
| Expected Result | Each financial action occurs according to case state and financial rules, exactly once, with amount, currency, fee version, reference, actor/source, and reason. Unauthorized or invalid financial actions are blocked without mutation. Expired reservations require controlled retry or recovery. Fee changes are reconciled without duplicate or orphan ledger events. |
| Priority | P1 |
| Test Type | Functional, Financial, Authorization, Boundary, Data Integrity, Audit, Recovery |
| Positive/Negative | Positive and Negative |
| Automation Candidate | Partial |
| Traceability | FR-014 -> TS-FR-014 -> TC-FR-014 |

### TC-FR-015 - Prevent duplicate wallet reservations or debits

| Field | Details |
|---|---|
| Test Case ID | TC-FR-015 |
| Requirement ID | FR-015 |
| Test Scenario ID | TS-FR-015 |
| Module | Wallet / Idempotency |
| Test Case Title | Duplicate submission attempts do not duplicate wallet reservation or debit |
| Objective | Verify repeated, concurrent, retried, or duplicate accepted submission attempts preserve one financial outcome. |
| Preconditions | Validated case is ready for wallet reservation and main agency submission; idempotency business reference exists. |
| Test Data | Double-click submit; duplicate API request; concurrent users; retry after timeout where original succeeded; duplicate debit event after debit. |
| Test Steps | 1. Submit a valid case and capture reservation and submission references. 2. Repeat the same request immediately. 3. Double-click or resubmit from two authorized sessions. 4. Retry after simulating a timeout where the original request succeeded. 5. Send a duplicate debit event after debit. 6. Review ledger, case state, submission references, and audit history. |
| Expected Result | Only one reservation or debit path is created for the accepted submission. Repeated attempts return or reference the existing outcome. Concurrent attempts are serialized or rejected without duplicate financial mutation. Duplicate debit events do not create additional debits. Original and duplicate handling are auditable. |
| Priority | P1 |
| Test Type | Functional, Idempotency, Concurrency, Financial, Data Integrity, Audit |
| Positive/Negative | Positive and Negative |
| Automation Candidate | Yes |
| Traceability | FR-015 -> TS-FR-015 -> TC-FR-015 |

### TC-FR-016 - Submit validated application to main agency

| Field | Details |
|---|---|
| Test Case ID | TC-FR-016 |
| Requirement ID | FR-016 |
| Test Scenario ID | TS-FR-016 |
| Module | Sub-Agency Submission |
| Test Case Title | Owning sub-agency submits validated application and receives submission reference |
| Objective | Verify an owning sub-agency officer can submit only a validated, version-matched application with an active wallet reservation. |
| Preconditions | Application is validated; active wallet reservation exists; owning and non-owning sub-agency users exist. |
| Test Data | Validated snapshot; unresolved finding; missing reservation; changed application version after validation; duplicate submit attempt; applicant user. |
| Test Steps | 1. Submit a validated application as the owning sub-agency officer. 2. Verify status, edit lock, submission reference, snapshot reference, and audit record. 3. Attempt submission as non-owning sub-agency officer and applicant. 4. Attempt submission with unresolved validation finding, missing reservation, and stale validated snapshot. 5. Repeat a duplicate submit attempt. |
| Expected Result | Owning sub-agency submission succeeds, changes status to submitted to main agency, locks ordinary edits, and returns one submission reference. Unauthorized users, unresolved findings, missing reservation, and stale snapshot are blocked. Duplicate submit returns the existing reference or is safely ignored without duplicate funds or case submission. |
| Priority | P1 |
| Test Type | Functional, Authorization, Data Integrity, Idempotency, Audit |
| Positive/Negative | Positive and Negative |
| Automation Candidate | Yes |
| Traceability | FR-016 -> TS-FR-016 -> TC-FR-016 |

### TC-FR-017 - Route submitted applications to correct main agency queue

| Field | Details |
|---|---|
| Test Case ID | TC-FR-017 |
| Requirement ID | FR-017 |
| Test Scenario ID | TS-FR-017 |
| Module | Routing / Main Agency Queue |
| Test Case Title | Submitted cases route by agency relationship and visa type without unauthorized visibility |
| Objective | Verify submitted applications appear in the correct main agency queue and are not visible in unauthorized queues. |
| Preconditions | Routing rules are configured by visa type and agency relationship; submitted cases exist; main agency users for multiple scopes exist. |
| Test Data | Case for visa type A; case for visa type B; agency relationship route; missing route configuration; changed agency relationship before submission; routing rule change during processing. |
| Test Steps | 1. Submit cases for configured visa types and agency relationships. 2. Verify each appears in the correct main agency queue. 3. Log in as users from unrelated queues and confirm cases are not visible. 4. Submit a case with missing route configuration. 5. Change agency relationship before submission and verify selected route. 6. Change routing rule during processing and verify existing case behavior and audit. |
| Expected Result | Cases route to the correct queue based on applicable rules. Unauthorized queues cannot view or claim the case. Missing route configuration keeps the case in a recoverable submitted or routing-error state without misrouting. Rule changes preserve case integrity and are auditable. |
| Priority | P1 |
| Test Type | Functional, Authorization, Data Integrity, Recovery, Audit |
| Positive/Negative | Positive and Negative |
| Automation Candidate | Yes |
| Traceability | FR-017 -> TS-FR-017 -> TC-FR-017 |

### TC-FR-018 - Main agency processing actions

| Field | Details |
|---|---|
| Test Case ID | TC-FR-018 |
| Requirement ID | FR-018 |
| Test Scenario ID | TS-FR-018 |
| Module | Main Agency Processing |
| Test Case Title | Main agency officers process, assign, correct, approve, reject, and escalate within scope |
| Objective | Verify authorized main agency users can perform supported processing actions only within agency scope and workflow state. |
| Preconditions | Case is routed to main agency scope; case officer and supervisor users exist; unrelated officer exists. |
| Test Data | Assignable case; correction reason; readiness approval; rejection reason; escalation path; two officers claiming same case; unsupported action for state. |
| Test Steps | 1. Assign or claim a routed case as an authorized officer. 2. Request correction with actionable reason and responsible party. 3. Approve readiness, reject with reason, and escalate to supervisor. 4. Attempt processing as officer outside agency scope. 5. Attempt unsupported action for current state. 6. Have two officers claim the same case concurrently. 7. Request correction without actionable reason. |
| Expected Result | Authorized actions update case state or task ownership and require reasons where applicable. Out-of-scope and unsupported actions are denied without data change. Concurrent claim allows one owner or controlled conflict resolution. Correction without actionable reason is blocked. All processing actions are audited. |
| Priority | P1 |
| Test Type | Functional, Authorization, Workflow, Concurrency, Audit |
| Positive/Negative | Positive and Negative |
| Automation Candidate | Yes |
| Traceability | FR-018 -> TS-FR-018 -> TC-FR-018 |

### TC-FR-019 - Record complete main agency decisions

| Field | Details |
|---|---|
| Test Case ID | TC-FR-019 |
| Requirement ID | FR-019 |
| Test Scenario ID | TS-FR-019 |
| Module | Main Agency Decision Records |
| Test Case Title | Main agency decisions capture actor, timestamp, decision, reason, notes, and attachments |
| Objective | Verify decision records are complete, traceable, permission-controlled, and protected from unauthorized visibility. |
| Preconditions | Main agency decision actions are available; attachment upload is configured; applicant and staff users exist. |
| Test Data | Readiness approval rationale; rejection reason; supporting attachment; missing reason; missing attachment; attachment upload failure; supervisor amendment. |
| Test Steps | 1. Approve readiness with rationale and review decision record fields. 2. Reject a case with required reason and attachment. 3. Attempt decision without mandatory reason, actor, timestamp, or attachment. 4. Simulate attachment upload failure during decision. 5. Amend a decision through approved supervisor correction process. 6. Verify applicant and agency visibility of internal notes and attachments. |
| Expected Result | Decisions record actor, timestamp, decision, reason, notes, and attachments where required. Incomplete decisions are rejected. Attachment failure prevents incomplete decision acceptance or creates recoverable draft decision state. Supervisor amendments follow authorized audited correction. Internal notes and attachments are visible only to authorized roles. |
| Priority | P1 |
| Test Type | Functional, Validation, Authorization, Error Handling, Audit, Data Integrity |
| Positive/Negative | Positive and Negative |
| Automation Candidate | Yes |
| Traceability | FR-019 -> TS-FR-019 -> TC-FR-019 |

### TC-FR-020 - Submit approved applications to GDRFA

| Field | Details |
|---|---|
| Test Case ID | TC-FR-020 |
| Requirement ID | FR-020 |
| Test Scenario ID | TS-FR-020 |
| Module | GDRFA Submission |
| Test Case Title | Approved applications submit to GDRFA with tracked reference, time, status, and reason |
| Objective | Verify GDRFA submission occurs only after readiness approval and prerequisites, and records submission and response details once. |
| Preconditions | Main agency readiness is approved; required data, documents, and payment prerequisites are configured; GDRFA service is available. |
| Test Data | Approved ready case; missing readiness approval; missing document; unauthorized actor; successful acknowledgement; timeout then accepted response; duplicate request; malformed response reason. |
| Test Steps | 1. Submit an approved ready case to GDRFA. 2. Verify submission reference, time, response status, response reason, case timeline, and audit. 3. Attempt submission without readiness approval, with missing prerequisites, and as unauthorized actor. 4. Simulate timeout followed by accepted response. 5. Repeat duplicate submission request. 6. Simulate absent or malformed response reason. 7. Inspect UI, logs, notifications, and exports for integration secrets or full payload exposure. |
| Expected Result | Eligible approved case is submitted once and tracked with external reference, time, response status, reason, timeline entry, and audit. Ineligible or unauthorized submissions are denied. Timeout and duplicate handling preserve one business outcome. Malformed response reason is handled through recovery or clear status without exposing secrets or sensitive payloads. |
| Priority | P1 |
| Test Type | Functional, Integration, Authorization, Idempotency, Error Handling, Security, Audit |
| Positive/Negative | Positive and Negative |
| Automation Candidate | Partial |
| Traceability | FR-020 -> TS-FR-020 -> TC-FR-020 |

### TC-FR-021 - Handle GDRFA responses and failures

| Field | Details |
|---|---|
| Test Case ID | TC-FR-021 |
| Requirement ID | FR-021 |
| Test Scenario ID | TS-FR-021 |
| Module | GDRFA Response Handling |
| Test Case Title | GDRFA acknowledgements, rejections, action-required, timeouts, duplicates, and outages are handled |
| Objective | Verify each GDRFA outcome updates case status, correction, retry, or recovery path according to rules and source validation. |
| Preconditions | Case is ready for or already in GDRFA submission; external reference matching is configured. |
| Test Data | Acknowledgement; rejection with validation reason; action-required response; timeout; duplicate response; unavailable service past retry limit; unmatched response; contradictory response; late response after manual recovery. |
| Test Steps | 1. Process valid acknowledgement and verify advancement. 2. Process rejection and verify correction state with reason. 3. Process action-required and verify responsible party assignment. 4. Simulate timeout and unavailable service through retry limit. 5. Send duplicate, late, unmatched, unauthorized, and contradictory responses. 6. Review status, recovery task, retry history, audit source, and authorized visibility. |
| Expected Result | Valid GDRFA responses drive the correct status, correction, or responsible-party state. Timeouts and outages create retry or recovery tasks without losing case integrity. Duplicate responses are idempotent. Unmatched, unauthorized, late contradictory, or invalid responses are quarantined and do not change the case. |
| Priority | P1 |
| Test Type | Functional, Integration, Negative, Recovery, Idempotency, Security, Audit |
| Positive/Negative | Positive and Negative |
| Automation Candidate | Partial |
| Traceability | FR-021 -> TS-FR-021 -> TC-FR-021 |

### TC-FR-022 - Manage payment lifecycle states

| Field | Details |
|---|---|
| Test Case ID | TC-FR-022 |
| Requirement ID | FR-022 |
| Test Scenario ID | TS-FR-022 |
| Module | Payment Lifecycle |
| Test Case Title | Payment-required, pending, paid, failed, cancelled, refunded, and reconciled states follow allowed transitions |
| Objective | Verify payment states transition only through authorized sources and valid workflow rules with role-appropriate visibility. |
| Preconditions | Case reaches payment stage; payment provider and finance roles are configured. |
| Test Data | Payment required; pending payment; provider paid confirmation; failure; cancellation; refund; finance reconciliation; invalid transition; disputed payment; late failure after paid; refund after withdrawal. |
| Test Steps | 1. Move a case to payment required and pending states. 2. Process provider paid confirmation. 3. Process failure, cancellation, refund, and finance reconciliation. 4. Attempt invalid state transitions and unsupported actor changes. 5. Process disputed payment and late failure after paid. 6. Refund after withdrawal according to policy. 7. Review payment timeline, role visibility, audit, and masking of references. |
| Expected Result | Payment state changes follow allowed transitions and authorized sources. Invalid or unauthorized transitions are denied without state change. Disputes and late events route to finance review or quarantine. Refunds after withdrawal follow policy. Payment references are masked where not required and all state changes are audited. |
| Priority | P1 |
| Test Type | Functional, Financial, Authorization, Negative, Recovery, Data Integrity, Audit |
| Positive/Negative | Positive and Negative |
| Automation Candidate | Partial |
| Traceability | FR-022 -> TS-FR-022 -> TC-FR-022 |

### TC-FR-023 - Prevent unauthorized paid status

| Field | Details |
|---|---|
| Test Case ID | TC-FR-023 |
| Requirement ID | FR-023 |
| Test Scenario ID | TS-FR-023 |
| Module | Payment Confirmation / Reconciliation |
| Test Case Title | Payment cannot become paid without authorized provider confirmation or finance reconciliation |
| Objective | Verify paid status is accepted only from trusted payment confirmation or approved manual reconciliation with required evidence. |
| Preconditions | Payment is pending or unresolved; payment provider trust rules and finance officer role are configured. |
| Test Data | Authorized provider callback; finance reconciliation with receipt and reason; applicant paid attempt; support admin paid attempt; unverified callback; duplicate confirmation; amount mismatch; currency mismatch; reused receipt reference. |
| Test Steps | 1. Mark payment paid using authorized provider confirmation. 2. Mark payment paid through finance reconciliation with receipt, amount, currency, and reason. 3. Attempt paid status as applicant, support admin, and unverified callback source. 4. Send duplicate confirmation. 5. Send amount mismatch, currency mismatch, and reused receipt reference. 6. Review quarantine, finance review, audit, and case state. |
| Expected Result | Authorized provider and finance-approved reconciliation can mark paid. Unauthorized users and untrusted callbacks are denied or quarantined. Duplicate confirmation preserves one paid outcome. Amount, currency, or reused receipt mismatches do not mark paid automatically and route to finance review. Audit records include source, receipt, amount, currency, reconciler, and result. |
| Priority | P1 |
| Test Type | Functional, Security, Financial, Integration, Idempotency, Audit |
| Positive/Negative | Positive and Negative |
| Automation Candidate | Partial |
| Traceability | FR-023 -> TS-FR-023 -> TC-FR-023 |

### TC-FR-024 - Track immigration processing and terminal outcomes

| Field | Details |
|---|---|
| Test Case ID | TC-FR-024 |
| Requirement ID | FR-024 |
| Test Scenario ID | TS-FR-024 |
| Module | Immigration Processing |
| Test Case Title | Immigration processing statuses and terminal outcomes are tracked and locked |
| Objective | Verify immigration statuses update the case timeline, terminal outcomes lock ordinary changes, and invalid updates are quarantined. |
| Preconditions | Case has required payment completion and external case reference; immigration source and liaison roles are configured. |
| Test Data | Received; under review; action required; approved; rejected; cancelled; withdrawn; expired; closed; unmatched update; contradictory update; final decision before intermediate status; withdrawal during external processing. |
| Test Steps | 1. Process received, under review, and action-required immigration statuses. 2. Process approved, rejected, cancelled, withdrawn, expired, and closed terminal outcomes. 3. Attempt ordinary edit or decision change after terminal status. 4. Send unmatched and contradictory updates. 5. Send final decision before intermediate status. 6. Request withdrawal during external processing. 7. Review source, rationale, timeline, terminal lock, and audit. |
| Expected Result | Valid immigration updates are reflected in authorized timeline views. Terminal outcomes lock ordinary changes and preserve decision rationale. Unmatched or contradictory updates are quarantined. Final decision without intermediate status is handled according to transition rules without losing audit context. Withdrawal follows stage rules and legal retention obligations. |
| Priority | P1 |
| Test Type | Functional, Integration, Status Transition, Security, Data Integrity, Audit |
| Positive/Negative | Positive and Negative |
| Automation Candidate | Partial |
| Traceability | FR-024 -> TS-FR-024 -> TC-FR-024 |

### TC-FR-025 - Expose status timeline by role permissions

| Field | Details |
|---|---|
| Test Case ID | TC-FR-025 |
| Requirement ID | FR-025 |
| Test Scenario ID | TS-FR-025 |
| Module | Status Timeline / Role-Based Views |
| Test Case Title | Authorized users see permitted timeline details only |
| Objective | Verify status timeline entries and sensitive details are visible according to role, agency scope, and business need. |
| Preconditions | Case has lifecycle, payment, audit, correction, and external status events; users exist for applicant, sub-agency, main agency, finance, support, and auditor roles. |
| Test Data | Owner applicant; non-owner applicant; owning sub-agency; unrelated agency; finance user; auditor; internal notes; payment reference; legal hold; out-of-order external event. |
| Test Steps | 1. View timeline as owner applicant and verify actionable statuses. 2. View as sub-agency and main agency users within scope. 3. View as finance, support, and auditor with role-specific detail. 4. Attempt access as non-owner applicant and unrelated agency. 5. Verify internal notes, payment references, audit-only data, and legal hold details are masked or shown according to role. 6. Review timeline ordering for out-of-order external events. |
| Expected Result | Each authorized role sees only permitted timeline entries and detail. Unauthorized users are denied. Sensitive internal notes, audit-only details, payment references, and legal hold information are masked unless required for authorized task. Out-of-order external events are displayed with source timing and do not distort case integrity. |
| Priority | P1 |
| Test Type | Functional, Authorization, Security, Data Privacy, Audit, Accessibility |
| Positive/Negative | Positive and Negative |
| Automation Candidate | Yes |
| Traceability | FR-025 -> TS-FR-025 -> TC-FR-025 |

### TC-FR-026 - Notify relevant recipients for lifecycle events

| Field | Details |
|---|---|
| Test Case ID | TC-FR-026 |
| Requirement ID | FR-026 |
| Test Scenario ID | TS-FR-026 |
| Module | Notifications |
| Test Case Title | Submission, correction, validation, wallet, payment, GDRFA, immigration, and final decision notifications reach relevant recipients |
| Objective | Verify notification rules select correct recipients and send minimal, actionable content without unnecessary personal data. |
| Preconditions | Notification rules, recipient contacts, channel preferences, and lifecycle events are configured. |
| Test Data | Submission event; correction request; validation failure; wallet shortfall; payment outcome; GDRFA update; immigration update; final decision; invalid address; blocked channel; outage; wrong agency recipient. |
| Test Steps | 1. Trigger each configured notification event. 2. Verify recipient categories and delivery targets. 3. Review message content for next action and data minimization. 4. Attempt to notify unrelated user or wrong agency recipient. 5. Simulate invalid contact, blocked channel, and notification gateway outage. 6. Verify full sensitive status details remain behind authenticated access. 7. Review notification audit records. |
| Expected Result | Correct recipients receive actionable minimal notifications. Unrelated users or wrong agency recipients are not notified. Invalid or blocked channels and outages create retry or failure records without blocking core case workflow. Sensitive details are omitted from message content and available only after authenticated access. |
| Priority | P2 |
| Test Type | Functional, Integration, Security, Privacy, Error Handling, Recovery, Audit |
| Positive/Negative | Positive and Negative |
| Automation Candidate | Partial |
| Traceability | FR-026 -> TS-FR-026 -> TC-FR-026 |

### TC-FR-027 - Honor permitted preferences and mandatory notices

| Field | Details |
|---|---|
| Test Case ID | TC-FR-027 |
| Requirement ID | FR-027 |
| Test Scenario ID | TS-FR-027 |
| Module | Notification Preferences |
| Test Case Title | Optional preferences are honored while mandatory operational and legal notices remain enabled |
| Objective | Verify users can control permitted notification preferences without disabling mandatory notices. |
| Preconditions | Notification preference settings and mandatory notice categories are configured; authenticated user exists. |
| Test Data | Optional channel preference; opt-out request; mandatory legal notice; mandatory operational notice; preference changed immediately before event; invalid preferred channel; unauthenticated preference change. |
| Test Steps | 1. Change optional notification channel as authenticated user. 2. Trigger an optional notification and verify preference is honored. 3. Attempt to disable mandatory legal and operational notices. 4. Trigger mandatory notices after opt-out attempt. 5. Change preference immediately before event. 6. Configure inaccessible or invalid preferred channel. 7. Attempt preference change without authentication or for another user. |
| Expected Result | Optional preferences are saved and honored where permitted. Mandatory notices cannot be disabled and still send or queue according to rules. Immediate preference changes apply consistently based on event timing. Invalid channels route to fallback or failure handling. Preference changes require authentication and do not expose other recipients' contact data. |
| Priority | P2 |
| Test Type | Functional, Security, Validation, Boundary, Accessibility |
| Positive/Negative | Positive and Negative |
| Automation Candidate | Yes |
| Traceability | FR-027 -> TS-FR-027 -> TC-FR-027 |

### TC-FR-028 - Record notification attempts and results

| Field | Details |
|---|---|
| Test Case ID | TC-FR-028 |
| Requirement ID | FR-028 |
| Test Scenario ID | TS-FR-028 |
| Module | Notification Audit / Delivery Tracking |
| Test Case Title | Notification delivery attempts, retries, failures, results, and recipient category are recorded |
| Objective | Verify notification delivery history is complete, traceable, privacy-preserving, and visible to authorized support users. |
| Preconditions | Notification event is triggered; notification gateway can return success, timeout, retry, duplicate callback, and failure outcomes. |
| Test Data | Successful delivery; failed delivery; retry count; provider timeout; duplicate retry callback; missing recipient category; missing delivery result; retry limit reached; message secret or token. |
| Test Steps | 1. Trigger successful notification and inspect delivery record. 2. Trigger failed delivery with retries and final failure. 3. Simulate provider timeout and duplicate retry callback. 4. Attempt to save delivery record missing recipient category or result. 5. Reach retry limit and verify support visibility. 6. Inspect records and logs for message secrets, tokens, and unnecessary personal data. |
| Expected Result | Delivery history records recipient category, attempts, result, retry count, failure reason where available, and retry status. Missing mandatory notification audit fields prevent complete acceptance or create recovery. Duplicate callbacks do not duplicate outcomes. Support users can see failed delivery status, and secrets or unnecessary personal data are not logged. |
| Priority | P2 |
| Test Type | Functional, Integration, Audit, Error Handling, Recovery, Security |
| Positive/Negative | Positive and Negative |
| Automation Candidate | Partial |
| Traceability | FR-028 -> TS-FR-028 -> TC-FR-028 |

### TC-FR-029 - Create durable audit records for lifecycle actions

| Field | Details |
|---|---|
| Test Case ID | TC-FR-029 |
| Requirement ID | FR-029 |
| Test Scenario ID | TS-FR-029 |
| Module | Audit Logging |
| Test Case Title | State, document, validation, wallet, payment, external, privileged, admin, and recovery actions are audited |
| Objective | Verify all required lifecycle and privileged actions create durable audit records with required attributes and correlation references. |
| Preconditions | Representative lifecycle actions can be performed; auditor and unauthorized users exist; audit storage is available. |
| Test Data | Intake edit; document upload; OCR review; validation finding; wallet check; payment event; GDRFA submission; privileged access; admin change; failed action; service action; external callback; retry; recovery action. |
| Test Steps | 1. Perform representative actions across intake, documents, OCR, validation, wallet, payment, external submission, admin, and recovery. 2. Access sensitive case data as support user with business reason. 3. Trigger failed action, service action, external callback, retry, and recovery event. 4. Inspect audit records for actor/service identity, role, scope, timestamp, action, affected case, result, reason where applicable, and correlation reference. 5. Attempt ordinary modification or deletion of audit records. 6. Verify authorized auditor search and unauthorized access denial. |
| Expected Result | Every auditable action creates a durable, tamper-evident audit record with required fields. Failed and recovery actions are audited. Audit history is searchable by authorized users and protected from ordinary modification or deletion. Unauthorized audit access is denied and audited where required. |
| Priority | P1 |
| Test Type | Audit, Functional, Security, Data Integrity, Compliance |
| Positive/Negative | Positive and Negative |
| Automation Candidate | Partial |
| Traceability | FR-029 -> TS-FR-029 -> TC-FR-029 |

### TC-FR-030 - Protect completed decisions and immutable records

| Field | Details |
|---|---|
| Test Case ID | TC-FR-030 |
| Requirement ID | FR-030 |
| Test Scenario ID | TS-FR-030 |
| Module | Record Integrity / Immutability |
| Test Case Title | Completed decisions, snapshots, financial records, and audit records cannot be modified or deleted without authorized correction |
| Objective | Verify protected records are immutable to ordinary users and authorized corrections are separately recorded with reason and approval. |
| Preconditions | Case has submitted snapshot, financial event, final decision, audit records, legal hold option, and correction process. |
| Test Data | Applicant edit attempt; sub-agency edit attempt; support admin edit attempt; supervisor correction; legal hold; export followed by deletion request; concurrent correction attempts. |
| Test Steps | 1. Attempt to modify submitted snapshot, financial event, final decision, and audit record as ordinary users. 2. Perform a permitted supervisor correction with reason and approval. 3. Attempt deletion of protected records after export and under legal hold. 4. Attempt concurrent corrections. 5. Review original and corrected records, audit trail, terminal lock, and visibility. |
| Expected Result | Ordinary users cannot modify or delete protected records. Authorized correction creates a separate record and audit event without overwriting required history. Legal hold prevents deletion where required. Concurrent corrections are controlled without record corruption. Denied attempts are audited. |
| Priority | P1 |
| Test Type | Security, Data Integrity, Audit, Compliance, Negative |
| Positive/Negative | Positive and Negative |
| Automation Candidate | Partial |
| Traceability | FR-030 -> TS-FR-030 -> TC-FR-030 |

### TC-FR-031 - Provide safe and actionable error messages

| Field | Details |
|---|---|
| Test Case ID | TC-FR-031 |
| Requirement ID | FR-031 |
| Test Scenario ID | TS-FR-031 |
| Module | Error Handling / User Messaging |
| Test Case Title | User-facing errors explain issue and next action without exposing secrets or unnecessary personal data |
| Objective | Verify errors across forms, uploads, wallet, payment, authorization, and integrations are clear, role-appropriate, secure, and accessible. |
| Preconditions | Error scenarios can be triggered across primary workflows; protected logs are available for diagnostics. |
| Test Data | Missing field; invalid document; wallet shortfall; payment failure; authorization denied; external timeout; multiple simultaneous errors; internal stack trace; token; endpoint; unrelated personal data. |
| Test Steps | 1. Trigger validation, upload, wallet, payment, authorization, and integration errors. 2. Review each user-facing message for issue description, responsible next action, role appropriateness, and field or document reference. 3. Trigger multiple simultaneous errors. 4. Verify stack traces, tokens, internal endpoints, full payloads, and unrelated personal data are not shown. 5. Inspect protected logs for diagnostic detail and audit correlation. 6. Validate keyboard focus, screen-reader announcement, and non-color-only error indicators. |
| Expected Result | User-facing errors are actionable, accessible, and appropriately specific. Security-sensitive errors remain generic where needed. Detailed diagnostics are limited to protected logs. No secrets, tokens, endpoints, stack traces, or unnecessary personal data are exposed. Errors create audit or error records where required. |
| Priority | P1 |
| Test Type | Functional, Negative, Security, Accessibility, Error Handling, Audit |
| Positive/Negative | Positive and Negative |
| Automation Candidate | Yes |
| Traceability | FR-031 -> TS-FR-031 -> TC-FR-031 |

### TC-FR-032 - Authorized search, filter, and export

| Field | Details |
|---|---|
| Test Case ID | TC-FR-032 |
| Requirement ID | FR-032 |
| Test Scenario ID | TS-FR-032 |
| Module | Operations Search / Export |
| Test Case Title | Case, payment, status, error, and audit search and export enforce role and scope |
| Objective | Verify authorized operational users can search, filter, and export permitted data while unauthorized and cross-agency access is blocked. |
| Preconditions | Test data exists across cases, payments, statuses, errors, and audit records; export and audit permissions are configured. |
| Test Data | Finance export; compliance audit export; support error filter; operations case filter; unauthorized user; cross-agency data; large export; empty result; masked fields; legal hold case; missing business need. |
| Test Steps | 1. Search and filter case, payment, status, error, and audit data as authorized roles. 2. Export payment records as finance and audit history as compliance. 3. Attempt search/export as unauthorized user and across agency boundaries. 4. Execute large export and empty-result export. 5. Verify masking in search results and exports. 6. Attempt sensitive export without business need. 7. Review export audit records and legal hold handling. |
| Expected Result | Authorized users receive only data permitted by role, agency scope, and business need. Unauthorized and cross-agency searches or exports are denied. Large and empty exports are handled predictably. Sensitive fields are masked where required. Legal hold cases remain protected and export access is audited. |
| Priority | P1 |
| Test Type | Functional, Security, Authorization, Privacy, Audit, Performance |
| Positive/Negative | Positive and Negative |
| Automation Candidate | Partial |
| Traceability | FR-032 -> TS-FR-032 -> TC-FR-032 |

### TC-FR-033 - Enforce role-based and agency-scoped access

| Field | Details |
|---|---|
| Test Case ID | TC-FR-033 |
| Requirement ID | FR-033 |
| Test Scenario ID | TS-FR-033 |
| Module | Identity and Access Management |
| Test Case Title | Role and agency scope protect every case, document, wallet, payment, notification, and audit action |
| Objective | Verify each action is allowed only for authorized role and agency scope and denied attempts leave data unchanged. |
| Preconditions | Users exist for applicant, sub-agency, main agency, finance, support, auditor, and service roles; permission and agency scopes are configured. |
| Test Data | Valid in-scope action per role; cross-agency case; wallet from another agency; audit-only data; role revoked during session; multi-agency user; transferred case; privilege escalation attempt. |
| Test Steps | 1. Execute each permitted action within role and agency scope. 2. Attempt case, document, wallet, payment, notification, and audit actions across agency boundaries. 3. Attempt privilege escalation and role misuse. 4. Revoke a role during active session and retry action. 5. Test a user with multiple agencies and a transferred case. 6. Verify server-side denial, unchanged data, error messaging, and audit records. |
| Expected Result | Authorized in-scope actions succeed. Cross-agency access, privilege escalation, role misuse, and revoked-role attempts are denied server-side without data change. Multi-agency and transferred cases respect current scope rules. Privileged access and denied attempts are audited. |
| Priority | P1 |
| Test Type | Security, Authorization, Functional, Negative, Audit |
| Positive/Negative | Positive and Negative |
| Automation Candidate | Yes |
| Traceability | FR-033 -> TS-FR-033 -> TC-FR-033 |

### TC-FR-034 - Apply retention, deletion, anonymisation, and legal hold

| Field | Details |
|---|---|
| Test Case ID | TC-FR-034 |
| Requirement ID | FR-034 |
| Test Scenario ID | TS-FR-034 |
| Module | Privacy / Data Retention |
| Test Case Title | Personal data categories follow retention, deletion, anonymisation, and legal hold rules |
| Objective | Verify every personal data category has lifecycle handling and legal holds override deletion where required. |
| Preconditions | Data classification, lawful basis, retention periods, deletion/anonymisation paths, and legal hold rules are configured. |
| Test Data | Abandoned draft; submitted snapshot; audit record; financial record; terminal case; consent withdrawal; deletion request during processing; legal hold before scheduled deletion; retention expiry; production personal data in test environment. |
| Test Steps | 1. Abandon a draft and run configured retention action. 2. Request deletion or anonymisation for eligible and ineligible records. 3. Withdraw consent during processing. 4. Apply legal hold before scheduled deletion. 5. Reach retention expiry for terminal case. 6. Verify submitted snapshots, audit, and financial records remain according to policy. 7. Review non-production data handling controls. 8. Inspect audit and compliance records. |
| Expected Result | Eligible data is deleted or anonymised according to policy. Legal hold preserves required records and overrides deletion. Submitted snapshots, financial records, and audit records are retained where legally required. Consent withdrawal does not remove records under active processing or legal retention obligations. Production personal data is not used in test environments unless approved, minimized, and protected. |
| Priority | P1 |
| Test Type | Privacy, Compliance, Data Integrity, Security, Audit, Negative |
| Positive/Negative | Positive and Negative |
| Automation Candidate | Partial |
| Traceability | FR-034 -> TS-FR-034 -> TC-FR-034 |

### TC-FR-035 - Preserve in-progress applications through changes

| Field | Details |
|---|---|
| Test Case ID | TC-FR-035 |
| Requirement ID | FR-035 |
| Test Scenario ID | TS-FR-035 |
| Module | Change Resilience / Migration |
| Test Case Title | Rule, fee, status, and integration changes preserve in-progress applications and identify revalidation |
| Objective | Verify in-progress cases are not lost, duplicated, advanced, closed, or misrouted during configuration, rule, fee, status, or integration changes. |
| Preconditions | In-progress applications exist across draft, validation, submitted, payment, and immigration states; change events can be simulated. |
| Test Data | Visa rule change; fee increase and decrease; integration contract change during retry; routing rule change after submission; status matrix change; affected user; unaffected user. |
| Test Steps | 1. Apply visa rule change while draft and validation cases exist. 2. Apply fee change while draft, reserved, and paid cases exist. 3. Change integration contract during retry. 4. Change routing rule after submission. 5. Change status matrix while cases are in non-terminal and terminal states. 6. Verify affected users see revalidation or next action. 7. Verify no case is lost, duplicated, silently advanced, closed, or misrouted. 8. Review audit records for configuration version impact. |
| Expected Result | In-progress applications remain intact with correct status and ownership. Affected cases identify required revalidation or recovery to responsible users. No silent case advancement, closure, deletion, duplication, or misrouting occurs. Rule, fee, route, status, and integration version impacts are auditable. |
| Priority | P1 |
| Test Type | Regression, Data Integrity, Recovery, Integration, Audit |
| Positive/Negative | Positive and Negative |
| Automation Candidate | Partial |
| Traceability | FR-035 -> TS-FR-035 -> TC-FR-035 |

### TC-FR-036 - Enforce lifecycle status transition matrix

| Field | Details |
|---|---|
| Test Case ID | TC-FR-036 |
| Requirement ID | FR-036 |
| Test Scenario ID | TS-FR-036 |
| Module | Workflow Status Transitions |
| Test Case Title | Allowed status transitions succeed and invalid transitions are rejected without data change |
| Objective | Verify every lifecycle state change follows the defined status transition matrix, authority, source, precondition, recovery, and audit rules. |
| Preconditions | Cases exist in each non-terminal and terminal lifecycle status; actors and external sources are configured. |
| Test Data | Draft to documents pending; wallet verified to submitted; immigration processing to approved; draft directly to paid; paid without payment confirmation; terminal alteration by ordinary user; withdrawal from multiple stages; duplicate and late external status; concurrent transition attempts. |
| Test Steps | 1. Execute representative allowed transitions with valid actors and preconditions. 2. Attempt invalid transitions across intake, wallet, payment, GDRFA, immigration, withdrawal, closure, and terminal states. 3. Attempt transitions from unauthorized actors or sources. 4. Send duplicate, late, and contradictory external statuses. 5. Attempt concurrent transitions from two sessions. 6. Review previous status, new status, result, recovery behavior, and audit entries. |
| Expected Result | Allowed transitions succeed only when actor/source and preconditions match the matrix. Invalid, unauthorized, duplicate, late, contradictory, or concurrent losing transitions are rejected, quarantined, or recovered without unauthorized data change. Terminal statuses are protected. All attempted transitions are audited. |
| Priority | P1 |
| Test Type | Functional, Workflow, Negative, Concurrency, Integration, Audit |
| Positive/Negative | Positive and Negative |
| Automation Candidate | Yes |
| Traceability | FR-036 -> TS-FR-036 -> TC-FR-036 |

### TC-FR-037 - Classify validation finding severity

| Field | Details |
|---|---|
| Test Case ID | TC-FR-037 |
| Requirement ID | FR-037 |
| Test Scenario ID | TS-FR-037 |
| Module | Validation Severity |
| Test Case Title | Validation findings are classified and enforce behavior by severity |
| Objective | Verify informational, warning, blocking, overrideable blocking, and non-overrideable blocking classifications control display, acknowledgement, correction, override, and workflow gating. |
| Preconditions | Validation rules exist for all severity categories; supervisor override permission is configured. |
| Test Data | Informational finding; warning finding; blocking finding; overrideable blocking finding; non-overrideable blocking finding; mixed severity findings; severity policy update; sensitive duplicate-risk finding. |
| Test Steps | 1. Trigger findings in each severity category. 2. Verify display and workflow behavior for informational and warning findings. 3. Attempt progression with blocking and non-overrideable blocking findings. 4. Approve overrideable blocking finding with authorized supervisor and reason. 5. Apply severity policy update and revalidate. 6. Trigger mixed severity findings. 7. Review sensitive duplicate-risk detail exposure and audit records. |
| Expected Result | Severity classification is accurate and controls behavior. Informational findings do not block; warnings require configured acknowledgement; blocking findings stop progression; overrideable blocking requires authorized approval and reason; non-overrideable findings cannot be bypassed. Policy updates reclassify through traceable revalidation without inappropriate disclosure. |
| Priority | P1 |
| Test Type | Functional, Validation, Authorization, Security, Audit |
| Positive/Negative | Positive and Negative |
| Automation Candidate | Yes |
| Traceability | FR-037 -> TS-FR-037 -> TC-FR-037 |

### TC-FR-038 - Trace wallet financial actions

| Field | Details |
|---|---|
| Test Case ID | TC-FR-038 |
| Requirement ID | FR-038 |
| Test Scenario ID | TS-FR-038 |
| Module | Wallet Traceability / Reconciliation |
| Test Case Title | Wallet reservation, debit, release, refund, and reconciliation trace to one case, fee version, and business event |
| Objective | Verify financial actions maintain one traceable relationship to case, fee calculation version, and accepted submission or payment event. |
| Preconditions | Financial events are available across submission and payment states; finance review workflow exists. |
| Test Data | Reservation tied to snapshot; debit tied to payment event; release; refund with finance approval; reconciliation; orphan financial event; mismatched fee version; duplicate provider callback; fee recalculation after reservation; partial refund. |
| Test Steps | 1. Create reservation and verify trace to validated snapshot, case, and fee version. 2. Create debit, release, refund, and reconciliation events. 3. Attempt orphan event without case or business event. 4. Attempt event with mismatched fee version. 5. Process duplicate provider callback. 6. Recalculate fee after reservation and process partial refund. 7. Review financial references, audit, masking, and finance review routing. |
| Expected Result | Each financial action traces to exactly one case, fee version, and accepted submission or payment event. Orphan and mismatched events are rejected or routed to finance review. Duplicate callbacks are idempotent. Fee recalculation and partial refund maintain clear reconciliation history. Sensitive financial references are protected. |
| Priority | P1 |
| Test Type | Financial, Data Integrity, Audit, Integration, Security, Recovery |
| Positive/Negative | Positive and Negative |
| Automation Candidate | Partial |
| Traceability | FR-038 -> TS-FR-038 -> TC-FR-038 |

### TC-FR-039 - Enforce idempotency by business reference

| Field | Details |
|---|---|
| Test Case ID | TC-FR-039 |
| Requirement ID | FR-039 |
| Test Scenario ID | TS-FR-039 |
| Module | Idempotency / External Events |
| Test Case Title | External, financial, immigration, and notification retries do not duplicate outcomes |
| Objective | Verify repeated attempts with the same business reference preserve or return the original outcome and unauthorized references are rejected or quarantined. |
| Preconditions | Stable business references exist for GDRFA, payment, wallet, immigration, and notification operations. |
| Test Data | Duplicate GDRFA response; duplicate payment confirmation; wallet retry after timeout; immigration duplicate after terminal status; notification retry callback repeated; same payload with unauthorized different reference; out-of-order duplicate. |
| Test Steps | 1. Process an original external submission, payment confirmation, wallet action, immigration update, and notification retry. 2. Repeat each event with the same business reference. 3. Retry after timeout where first operation succeeded. 4. Send out-of-order duplicate after terminal status. 5. Send same payload with a different unauthorized reference. 6. Review case state, financial state, audit records, duplicate markers, and recovery tasks. |
| Expected Result | Repeated attempts with the same valid business reference return or preserve the original outcome without duplicate case, financial, notification, or audit business outcomes. Unauthorized or mismatched references are rejected or quarantined. Out-of-order duplicates do not alter terminal or inconsistent states. Original and duplicate handling remain traceable. |
| Priority | P1 |
| Test Type | Idempotency, Integration, Financial, Data Integrity, Security, Audit |
| Positive/Negative | Positive and Negative |
| Automation Candidate | Partial |
| Traceability | FR-039 -> TS-FR-039 -> TC-FR-039 |

### TC-FR-040 - Enforce action-level permissions

| Field | Details |
|---|---|
| Test Case ID | TC-FR-040 |
| Requirement ID | FR-040 |
| Test Scenario ID | TS-FR-040 |
| Module | Permission Matrix / Authorization |
| Test Case Title | Protected actions enforce role, agency scope, lifecycle state, and business reason |
| Objective | Verify every action in the permission matrix is allowed only for configured actors and denied when role, scope, state, or reason is invalid. |
| Preconditions | Permission matrix is configured; users exist for all roles; cases exist in relevant states; business-reason fields are available. |
| Test Data | Creation; edit; upload; OCR review; validation override; wallet action; submission; main agency processing; payment; immigration update; notification management; support recovery; audit access; export; closure; role change mid-session; supervisor temporary access; support recovery without task; missing reason. |
| Test Steps | 1. Execute each protected action as an allowed role within scope and valid lifecycle state. 2. Attempt each action with wrong role, wrong agency scope, invalid state, and missing required business reason. 3. Revoke or change a role mid-session and retry. 4. Test supervisor temporary access and support recovery without assigned task. 5. Review server-side authorization, UI availability, unchanged data on denial, and audit entries. |
| Expected Result | Authorized actions succeed only when role, agency scope, lifecycle state, and required business reason match the matrix. Denied actions leave data unchanged and return safe errors. Mid-session role changes are enforced. Temporary access and support recovery follow configured controls. Privileged and denied actions are audited. |
| Priority | P1 |
| Test Type | Security, Authorization, Functional, Negative, Audit |
| Positive/Negative | Positive and Negative |
| Automation Candidate | Yes |
| Traceability | FR-040 -> TS-FR-040 -> TC-FR-040 |

### TC-FR-041 - Require mandatory audit fields

| Field | Details |
|---|---|
| Test Case ID | TC-FR-041 |
| Requirement ID | FR-041 |
| Test Scenario ID | TS-FR-041 |
| Module | Audit Validation |
| Test Case Title | Auditable events require mandatory audit fields before acceptance |
| Objective | Verify lifecycle, access, financial, integration, and recovery events cannot be accepted without mandatory audit metadata. |
| Preconditions | Auditable actions can be triggered with complete and incomplete metadata; recovery queue exists. |
| Test Data | Complete state change audit metadata; missing actor; missing service identity; missing timestamp; missing affected case; missing correlation reference; external callback missing optional reason; recovery event for missing audit data; spoofed audit actor. |
| Test Steps | 1. Trigger a complete auditable lifecycle event and verify acceptance. 2. Trigger access, financial, integration, and recovery events with complete metadata. 3. Attempt events missing actor, service identity, timestamp, affected case, outcome, or correlation reference. 4. Process external callback missing optional reason. 5. Attempt to spoof audit actor or alter audit metadata as ordinary user. 6. Review rejection, hold-for-recovery, and audit validation behavior. |
| Expected Result | Complete auditable events are accepted with required fields. Events missing mandatory metadata are rejected or held in recovery until complete. Optional missing reason is handled according to event rules without losing required traceability. Ordinary users cannot spoof, omit, or modify audit metadata. |
| Priority | P1 |
| Test Type | Audit, Validation, Security, Integration, Recovery, Negative |
| Positive/Negative | Positive and Negative |
| Automation Candidate | Partial |
| Traceability | FR-041 -> TS-FR-041 -> TC-FR-041 |

### TC-FR-042 - Apply document and OCR acceptance thresholds

| Field | Details |
|---|---|
| Test Case ID | TC-FR-042 |
| Requirement ID | FR-042 |
| Test Scenario ID | TS-FR-042 |
| Module | Document Quality / OCR Thresholds |
| Test Case Title | Document and OCR thresholds gate progression beyond OCR and validation |
| Objective | Verify only documents and OCR results meeting configured thresholds or allowed manual recovery can proceed beyond OCR and validation. |
| Preconditions | Documents and OCR results exist at below-threshold, boundary, and above-threshold values; manual fallback and replacement flows are configured. |
| Test Data | Supported readable document; unsafe document; unreadable text; OCR critical field above 85 percent; exactly 85 percent; exactly 60 percent; below 60 percent; unresolved mismatch; replacement document after failed OCR; manual entry fallback. |
| Test Steps | 1. Process supported readable document and OCR fields above threshold. 2. Test OCR confidence exactly at 85 percent and exactly at 60 percent. 3. Process OCR confidence below 60 percent, unreadable text, unsafe document, and unresolved mismatch. 4. Replace failed document and rerun screening and OCR. 5. Use allowed manual entry fallback where automated extraction is unavailable or unusable. 6. Attempt progression beyond OCR and validation for each result. 7. Review threshold result, recovery action, audit record, unsafe document isolation, and OCR data access. |
| Expected Result | Documents and OCR results meeting thresholds proceed only after required review. Boundary values follow configured threshold rules. Unsafe documents, unreadable text, below-threshold OCR, and unresolved mismatches block progression unless manual recovery is explicitly allowed. Replacement and manual fallback recover without stale data. Threshold outcomes and recovery actions are audited, and OCR outputs are protected. |
| Priority | P1 |
| Test Type | Functional, Boundary, Validation, Security, Recovery, Audit, Accessibility |
| Positive/Negative | Positive and Negative |
| Automation Candidate | Partial |
| Traceability | FR-042 -> TS-FR-042 -> TC-FR-042 |
