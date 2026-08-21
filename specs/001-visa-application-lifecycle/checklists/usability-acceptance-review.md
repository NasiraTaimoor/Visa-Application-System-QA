# Usability Acceptance Review: Visa Application Lifecycle

**Purpose**: Moderated usability acceptance testing validating SC-001 and SC-008, per T192.

**Status**: **Not yet executed.** This requires a moderated session with real applicants/sub-agency officers (or representative proxies) using the running application — it cannot be simulated or fabricated by an automated agent. The automated test suite (166 backend + 37 frontend tests) validates functional correctness and accessibility conformance, but not human task-completion time or first-attempt success rate, which is what SC-001/SC-008 measure.

**Success criteria under test**:

- **SC-001**: At least 95% of applicants/sub-agency officers complete required intake fields for a standard application in 15 minutes or less, excluding external wait time.
- **SC-008**: At least 90% of representative users complete the primary application flow on first attempt (no moderator intervention required).

## Session setup

- **Participants**: ≥10 recommended (mix of applicant-role and sub-agency-officer-role testers) for a statistically meaningful 90-95% threshold read.
- **Environment**: `frontend/` dev build (`npm run dev`) against a running `backend/` instance (`uvicorn src.main:app`) with mocked integrations.
- **Task given to participant**: "Create a new tourist visa application, complete all required applicant and passport details, and get it to the point where it's ready to submit." (Applicant-role) / "Create a new application on behalf of an applicant and get it ready to submit." (Sub-agency-role)
- **Moderator role**: Observe only; do not guide unless the participant is fully stuck (an intervention counts as a first-attempt failure for SC-008).
- **Instrumentation to record per participant**:

| Participant # | Role | Start time | End time (fields complete) | Time-on-task | First-attempt success (Y/N) | Intervention notes |
|---|---|---|---|---|---|---|
| 1 | | | | | | |
| 2 | | | | | | |
| 3 | | | | | | |
| 4 | | | | | | |
| 5 | | | | | | |
| 6 | | | | | | |
| 7 | | | | | | |
| 8 | | | | | | |
| 9 | | | | | | |
| 10 | | | | | | |

## Results

- **SC-001**: ____ / ____ participants completed within 15 minutes = ____% (target ≥95%)
- **SC-008**: ____ / ____ participants succeeded on first attempt = ____% (target ≥90%)

**Overall**: PASS / FAIL _(circle one — fill in after session)_

**Notable friction points observed**:

| # | Screen/step | Observation | Suggested fix |
|---|---|---|---|
| | | | |
