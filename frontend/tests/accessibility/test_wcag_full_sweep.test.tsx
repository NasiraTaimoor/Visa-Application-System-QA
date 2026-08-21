import { render } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import type { ReactElement } from "react";
import { MemoryRouter, Route, Routes } from "react-router-dom";
import { afterEach, describe, it, vi } from "vitest";
import { expectNoAxeViolations } from "../../src/accessibility/axeHelper";
import { CreateApplicationPage } from "../../src/applicant/pages/create_application/CreateApplicationPage";
import { DraftIntakePage } from "../../src/applicant/pages/draft_intake/DraftIntakePage";
import { SessionRecoveryPage } from "../../src/applicant/pages/session_recovery/SessionRecoveryPage";
import { DocumentUploadPage } from "../../src/applicant/pages/document_upload/DocumentUploadPage";
import { OcrReviewPage } from "../../src/applicant/pages/ocr_review/OcrReviewPage";
import { OcrManualFallbackPage } from "../../src/applicant/pages/ocr_manual_fallback/OcrManualFallbackPage";
import { ValidationFindingsPage } from "../../src/applicant/pages/validation_findings/ValidationFindingsPage";
import { NotificationPreferencesPage } from "../../src/applicant/pages/notification_preferences/NotificationPreferencesPage";
import { FinalOutcomePage } from "../../src/applicant/pages/final_outcome/FinalOutcomePage";

// Full WCAG 2.1 AA automated accessibility sweep across applicant-facing
// screens (T186), per ui-contract.md's Applicant Portal screen list and
// Accessibility Acceptance criteria. Screens with data-dependent content
// (draft intake, OCR review, final outcome) are rendered with mocked fetch
// so their populated states are swept too, not just the empty shell.

function jsonResponse(body: unknown) {
  return Promise.resolve({
    ok: true,
    status: 200,
    json: () => Promise.resolve(body),
    statusText: "",
  } as Response);
}

afterEach(() => {
  vi.unstubAllGlobals();
});

function renderAt(path: string, routePath: string, element: ReactElement) {
  return render(
    <MemoryRouter initialEntries={[path]}>
      <Routes>
        <Route path={routePath} element={element} />
      </Routes>
    </MemoryRouter>,
  );
}

describe("WCAG 2.1 AA sweep: applicant portal", () => {
  it("create application screen", async () => {
    const { container } = render(
      <MemoryRouter>
        <CreateApplicationPage />
      </MemoryRouter>,
    );
    await expectNoAxeViolations(container);
  });

  it("session recovery screen", async () => {
    const { container } = render(
      <MemoryRouter>
        <SessionRecoveryPage />
      </MemoryRouter>,
    );
    await expectNoAxeViolations(container);
  });

  it("draft intake screen (populated)", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn(() =>
        jsonResponse({
          application_id: "app-1",
          case_reference: "VA-000001",
          current_status: "draft_created",
          current_version: 1,
          visa_type: "tourist",
          applicant: { legal_name: "Jane Doe", nationality: "GBR", date_of_birth: null },
          missing_items: ["applicant.date_of_birth"],
        }),
      ),
    );
    const { container, findByText } = renderAt(
      "/applicant/draft/app-1",
      "/applicant/draft/:applicationId",
      <DraftIntakePage />,
    );
    await findByText(/Before you can submit/);
    await expectNoAxeViolations(container);
  });

  it("document upload screen", async () => {
    const { container } = renderAt(
      "/applicant/draft/app-1/documents",
      "/applicant/draft/:applicationId/documents",
      <DocumentUploadPage />,
    );
    await expectNoAxeViolations(container);
  });

  it("OCR review screen (populated)", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn(() =>
        jsonResponse({
          document_id: "doc-1",
          extraction_status: "completed",
          extracted_fields: { passport_number: "P1234567" },
          confidence_by_field: { passport_number: 0.97 },
          overall_confidence: 0.93,
          warning_flags: [],
          reviewed_values: {},
          reviewer_id: null,
        }),
      ),
    );
    const { container, findByText } = renderAt(
      "/applicant/draft/app-1/ocr-review?document_id=doc-1",
      "/applicant/draft/:applicationId/ocr-review",
      <OcrReviewPage />,
    );
    await findByText(/Overall confidence/);
    await expectNoAxeViolations(container);
  });

  it("OCR manual fallback screen", async () => {
    const { container } = renderAt(
      "/applicant/draft/app-1/ocr-manual-fallback",
      "/applicant/draft/:applicationId/ocr-manual-fallback",
      <OcrManualFallbackPage />,
    );
    await expectNoAxeViolations(container);
  });

  it("validation findings screen (populated)", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn(() =>
        jsonResponse({
          current_status: "ocr_and_validation",
          is_ready: false,
          findings: [
            {
              finding_id: "f-1",
              rule_id: "document_presence",
              severity: "overrideable_blocking",
              affected_field_or_document: "document.photo",
              corrective_action: "Upload an accepted photo",
              override_status: null,
            },
          ],
        }),
      ),
    );
    const user = userEvent.setup();
    const { container, findByRole } = renderAt(
      "/applicant/draft/app-1/validation",
      "/applicant/draft/:applicationId/validation",
      <ValidationFindingsPage />,
    );
    await user.click(await findByRole("button", { name: /Run validation/ }));
    await expectNoAxeViolations(container);
  });

  it("notification preferences screen", async () => {
    const { container } = render(
      <MemoryRouter>
        <NotificationPreferencesPage />
      </MemoryRouter>,
    );
    await expectNoAxeViolations(container);
  });

  it("final outcome screen (populated)", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn((input: RequestInfo | URL) => {
        const url = String(input);
        if (url.endsWith("/status-timeline")) {
          return jsonResponse({
            timeline: [
              {
                new_status: "approved",
                previous_status: "immigration_processing",
                timestamp: "2026-08-13T10:00:00Z",
                reason: null,
                next_action: null,
              },
            ],
          });
        }
        return jsonResponse({ current_status: "approved", case_reference: "VA-000001" });
      }),
    );
    const { container, findByText } = renderAt(
      "/applicant/draft/app-1/outcome",
      "/applicant/draft/:applicationId/outcome",
      <FinalOutcomePage />,
    );
    await findByText(/has been approved/);
    await expectNoAxeViolations(container);
  });
});
