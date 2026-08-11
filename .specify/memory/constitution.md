<!--
Sync Impact Report
- Version change: template/unversioned -> 1.0.0
- Modified principles: template placeholders -> I. Privacy and Security by Design;
  II. Accurate, Traceable Case Records; III. Applicant-Centred Accessibility;
  IV. Testable, Reliable Workflows; V. Minimal, Maintainable Change
- Added sections: Data Protection and Compliance; Delivery and Quality Gates
- Removed sections: none
- Follow-up TODOs: none
-->
# Visa Application System Constitution

## Core Principles

### I. Privacy and Security by Design
The system MUST collect, store, display, and transmit only applicant data necessary for a defined
business purpose. Sensitive data MUST be encrypted in transit and at rest where platform support
exists, access MUST use least privilege, and secrets MUST never enter source control, logs, or
client-side bundles. Security-sensitive changes require a documented threat and privacy impact
review before release. Rationale: visa applications contain identity, travel, and eligibility data
whose disclosure can cause material harm.

### II. Accurate, Traceable Case Records
Every application state change, document action, eligibility decision, and privileged access event
MUST produce a durable audit record that identifies the actor, time, action, and affected case.
The system MUST preserve submitted information and decision rationale according to applicable
retention rules, and MUST prevent unauthorized alteration of completed decisions. Rationale:
staff, applicants, and auditors need an accountable record of how each case was handled.

### III. Applicant-Centred Accessibility
Applicant-facing journeys MUST be understandable, usable with keyboard and assistive technology,
and meet WCAG 2.1 AA or the stricter applicable accessibility standard. Forms MUST provide clear
field requirements, actionable errors, confirmation of submission, and a way to recover from
interrupted sessions without exposing personal data. Rationale: access to an immigration process
must not depend on ability, device, or familiarity with government systems.

### IV. Testable, Reliable Workflows
Changes to application intake, validation, payment, document handling, notifications, integrations,
or decision status MUST include automated tests for expected paths, authorization boundaries, and
meaningful failure handling. Releases MUST not knowingly break an in-progress application or
silently lose, duplicate, or misroute case data. Rationale: workflow failures can delay or
incorrectly affect high-impact immigration outcomes.

### V. Minimal, Maintainable Change
Teams MUST choose the simplest design that satisfies validated requirements, avoid speculative
features, and document any material architectural, data-model, or integration trade-off. Public
and internal interfaces MUST be versioned or migrated safely when contracts change. Rationale:
clear, constrained designs reduce security defects and make a regulated service supportable.

## Data Protection and Compliance

Data classification, retention periods, deletion or anonymisation procedures, and lawful processing
bases MUST be documented before a data category is introduced. Production data MUST NOT be used in
development or test environments unless it has been formally approved, minimized, and protected.
Third-party processors and integrations MUST have documented data flows, security responsibilities,
and failure procedures. Legal, regulatory, or policy requirements that conflict with this
constitution take precedence and MUST be recorded in the relevant specification.

## Delivery and Quality Gates

Each change MUST have a written specification proportionate to its risk, peer review, and evidence
that applicable automated checks pass before merge. High-risk changes affecting authentication,
authorization, personal data, payments, eligibility rules, or external case-system interfaces MUST
include a rollback or mitigation plan and receive security or domain-owner review. Production
incidents involving confidentiality, integrity, availability, or incorrect decisions MUST be
recorded, remediated, and used to improve safeguards without assigning blame.

## Governance

This constitution supersedes conflicting project conventions. Feature specifications, plans, task
lists, pull requests, and release reviews MUST explicitly verify applicable principles and document
any approved exception, its owner, expiry, and mitigation. Amendments require a written rationale,
review by the project owner and affected security or domain owners, and an update to this document.

Versioning follows semantic versioning: MAJOR for incompatible principle or governance changes,
MINOR for a new principle or material expansion, and PATCH for clarifications that do not alter
required behaviour. Compliance is reviewed during planning, code review, release approval, and
post-incident analysis; unresolved violations block release unless a time-bound exception is
approved and recorded.

**Version**: 1.0.0 | **Ratified**: 2026-08-11 | **Last Amended**: 2026-08-11
