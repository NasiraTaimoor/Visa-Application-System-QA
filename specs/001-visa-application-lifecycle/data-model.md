# Data Model: Visa Application Lifecycle

## Entity: Applicant

**Fields**: applicant_id, legal_name, date_of_birth, nationality, contact_details, identity_references, sponsor_details, consent_records, agency_relationships, data_classification, retention_policy_id.

**Relationships**: Has many Visa Applications; has many Consent and Retention Policy records.

**Validation rules**: Required fields vary by visa type and applicant context. Personal data must be minimized, classified, masked where appropriate, and retained or anonymised by policy.

## Entity: Visa Application

**Fields**: application_id, case_reference, applicant_id, visa_type, owning_sub_agency_id, routed_main_agency_id, current_status, current_version, validated_snapshot_id, fee_version, created_at, updated_at, terminal_outcome, terminal_locked_at.

**Relationships**: Belongs to Applicant; has Passport, Documents, OCR Results, Validation Findings, Wallet Ledger Events, Submissions, Payments, Status Events, Notifications, Audit Events, Error Records, Processing Tasks.

**State transitions**: No case -> Draft created -> Documents pending -> OCR and validation -> Ready for sub-agency review -> Wallet verified -> Submitted to main agency -> Main agency processing -> GDRFA submitted -> Payment pending/Paid/Payment failed -> Immigration processing -> Approved/Rejected/Cancelled/Withdrawn/Expired/Closed. Correction and recovery loops return to responsible editable states under the transition matrix.

## Entity: Passport

**Fields**: passport_id, application_id, passport_number, issuing_country, issue_date, expiry_date, machine_readable_details, document_id, confirmed_source, confirmed_at, confirmed_by.

**Relationships**: Belongs to Visa Application; references Document and OCR Result.

**Validation rules**: Expiry must satisfy configured passport-validity policy at workflow gates; issue and expiry dates must be coherent; duplicate active passport risk must be flagged without exposing unrelated applicant data.

## Entity: Document

**Fields**: document_id, application_id, document_type, file_reference, file_metadata, upload_actor_id, upload_time, upload_status, screening_status, verification_status, version, replaced_document_id, retention_classification.

**Relationships**: Belongs to Visa Application; has OCR Results and Audit Events.

**Validation rules**: Type, size, page count, integrity, quality, password protection, security screening, and visa-type document requirements must pass before downstream processing.

## Entity: OCR Result

**Fields**: ocr_result_id, document_id, extraction_status, extracted_fields, confidence_by_field, overall_confidence, warning_flags, reviewed_values, reviewer_id, reviewed_at, correction_reason, source_payload_reference.

**Relationships**: Belongs to Document; may confirm Passport or application data.

**Validation rules**: Advisory until authorized review; critical fields below configured threshold block or require manual fallback; mismatches require correction or approved override.

## Entity: Validation Finding

**Fields**: finding_id, application_id, rule_id, rule_version, result, severity, affected_field_or_document, responsible_party, corrective_action, override_status, override_actor_id, override_reason, resolved_at.

**Relationships**: Belongs to Visa Application; linked to Audit Events.

**Validation rules**: Severity must be informational, warning, blocking, overrideable blocking, or non-overrideable blocking. Blocking findings prevent progression unless corrected or authorized override is allowed.

## Entity: Agency

**Fields**: agency_id, agency_type, parent_agency_id, name, status, wallet_account_reference, routing_rules, permitted_roles.

**Relationships**: Has users, applications, wallet ledger events, queues, and processing tasks.

**Validation rules**: Agency scope must be enforced for case, document, wallet, payment, audit, export, and processing actions.

## Entity: Wallet Ledger Event

**Fields**: wallet_event_id, agency_id, application_id, event_type, amount, currency, fee_version, available_balance_result, reservation_reference, debit_reference, release_reference, refund_reference, reconciliation_reference, status, reason, idempotency_key, created_at.

**Relationships**: Belongs to Agency and Visa Application; linked to Payment and Audit Events where applicable.

**Validation rules**: Events must trace to one case, fee version, and accepted business event. Duplicate accepted submissions must not duplicate reservations or debits.

## Entity: Submission

**Fields**: submission_id, application_id, submission_type, source_agency_id, target_agency_or_system, snapshot_id, submission_reference, external_reference, status, attempt_count, last_response, response_reason, idempotency_key, submitted_at.

**Relationships**: Belongs to Visa Application; linked to Status Events, External Case Responses, and Audit Events.

**Validation rules**: Sub-agency submission requires validated snapshot and wallet reservation. GDRFA submission requires main agency readiness approval and prerequisites.

## Entity: Processing Task

**Fields**: task_id, application_id, task_type, assigned_role, assigned_user_id, owning_agency_id, status, due_at, reason, recovery_context, created_at, completed_at.

**Relationships**: Belongs to Visa Application; created by workflow, validation, integration, finance, support, or compliance actions.

**Validation rules**: Task actions must match role, scope, lifecycle state, and business reason.

## Entity: External Case Response

**Fields**: response_id, application_id, source_system, external_reference, response_type, status_value, reason, payload_reference, received_at, matched_status, quarantine_reason, idempotency_key.

**Relationships**: Belongs to Visa Application; may update Submission, Payment, Status Event, or Processing Task.

**Validation rules**: Source and business reference must be trusted and matched before mutation. Unmatched or contradictory events are quarantined.

## Entity: Payment

**Fields**: payment_id, application_id, payment_state, amount, currency, fee_version, provider_reference, receipt_reference, confirmation_source, reconciliation_status, dispute_status, refund_status, finance_actor_id, reason, idempotency_key.

**Relationships**: Belongs to Visa Application; linked to Wallet Ledger Events and Audit Events.

**Validation rules**: Paid requires authorized provider confirmation or finance reconciliation. Invalid transitions and unauthorized actors are denied without state change.

## Entity: Status Event

**Fields**: status_event_id, application_id, previous_status, new_status, source, actor_or_service_id, timestamp, responsible_party, external_reference, reason, next_action, visibility_classification, correlation_reference.

**Relationships**: Belongs to Visa Application and Audit Event.

**Validation rules**: Must follow transition matrix; terminal statuses are immutable to ordinary users.

## Entity: Notification

**Fields**: notification_id, application_id, event_type, recipient_category, channel, preference_source, message_classification, delivery_status, attempt_count, last_attempt_at, failure_reason, retry_status.

**Relationships**: Belongs to Visa Application; linked to Status Event and Audit Event.

**Validation rules**: Content must be minimal and role-appropriate. Mandatory operational/legal notices cannot be disabled.

## Entity: Audit Event

**Fields**: audit_event_id, actor_or_service_id, role, agency_scope, timestamp, action, affected_case_or_record, outcome, reason, source, correlation_reference, metadata_reference, tamper_evidence_marker.

**Relationships**: Linked from all auditable domain entities.

**Validation rules**: Mandatory audit fields are required before accepting auditable lifecycle, access, financial, integration, or recovery events. Ordinary users cannot modify or delete audit records.

## Entity: Error Record

**Fields**: error_record_id, application_id, source_component, error_type, severity, user_safe_message, protected_diagnostic_reference, recovery_owner, recovery_status, correlation_reference, created_at, resolved_at.

**Relationships**: Belongs to Visa Application or integration operation; may create Processing Task and Audit Event.

**Validation rules**: User-facing errors must be actionable and must not expose secrets, stack traces, tokens, internal endpoints, or unnecessary personal data.

## Entity: Consent and Retention Policy

**Fields**: policy_id, data_category, lawful_basis, consent_required, retention_period, deletion_path, anonymisation_path, legal_hold_behavior, production_test_data_rules, effective_from, effective_to.

**Relationships**: Applies to Applicant, Visa Application, Document, Audit Event, Payment, and export records.

**Validation rules**: Data category cannot be introduced for production use without classification, lawful basis, retention, deletion/anonymisation path, and legal hold behavior.
