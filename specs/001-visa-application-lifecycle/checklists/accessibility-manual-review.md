# Manual Accessibility Review Checklist: Visa Application Lifecycle

**Purpose**: Human keyboard-only and screen-reader validation of applicant-facing screens, complementing the automated `jest-axe` sweep (`frontend/tests/accessibility/`, 13 tests covering all applicant-portal screens, 0 violations as of Phase 10).

**Status**: **Not yet executed.** This is task T187 — it requires a human reviewer operating a real screen reader (NVDA, JAWS, or VoiceOver) and physical keyboard against the running app; it cannot be completed by an automated agent. Run `npm run dev` in `frontend/` and walk each row below against `http://localhost:5173`.

**Reviewer**: _______________  **Date**: _______________  **Screen reader/version**: _______________  **Browser**: _______________

## Screens to review

| Screen | Route | Keyboard-only pass | Screen-reader pass | Notes |
|---|---|---|---|---|
| Create application | `/applicant` | [ ] | [ ] | |
| Draft intake | `/applicant/draft/:id` | [ ] | [ ] | |
| Session recovery | `/applicant/resume` | [ ] | [ ] | |
| Document upload | `/applicant/draft/:id/documents` | [ ] | [ ] | |
| OCR review | `/applicant/draft/:id/ocr-review` | [ ] | [ ] | |
| OCR manual fallback | `/applicant/draft/:id/ocr-manual-fallback` | [ ] | [ ] | |
| Validation findings | `/applicant/draft/:id/validation` | [ ] | [ ] | |
| Final outcome / status timeline | `/applicant/draft/:id/outcome` | [ ] | [ ] | |
| Notification preferences | `/applicant/notifications` | [ ] | [ ] | |

## Acceptance criteria (per ui-contract.md Accessibility Acceptance + quickstart.md Accessibility Testing)

- [ ] Every control is reachable and operable using Tab/Shift+Tab/Enter/Space only — no keyboard trap.
- [ ] Focus order follows visual/reading order.
- [ ] On validation error, focus moves to the error summary automatically (`ErrorSummary` component).
- [ ] Every form control has an announced label, and hint/error text is announced when the field receives focus.
- [ ] Errors are never conveyed by color alone (confirm with the screen reader, not just visually).
- [ ] Interrupted/resumed sessions (session recovery flow) do not expose personal data to an unauthenticated or unauthorized screen-reader user.
- [ ] Long-running states (OCR "Loading…", wallet check, submission) announce their state change (e.g., via `role="status"`) rather than leaving the screen reader silent.
- [ ] The OCR manual fallback screen is fully usable without ever relying on the (unavailable) automated OCR result.
- [ ] Skip-to-content link (`AppShell`) works and is the first focusable element.

## Result

**Overall**: PASS / FAIL / PASS WITH FOLLOW-UPS _(circle one — fill in after review)_

**Follow-up items** (if any):

| # | Screen | Issue | Severity | Owner |
|---|---|---|---|---|
| | | | | |
