import { render } from "@testing-library/react";
import { MemoryRouter, Route, Routes } from "react-router-dom";
import { afterEach, describe, it, vi } from "vitest";
import { expectNoAxeViolations } from "../../src/accessibility/axeHelper";
import { DocumentUploadPage } from "../../src/applicant/pages/document_upload/DocumentUploadPage";
import { OcrReviewPage } from "../../src/applicant/pages/ocr_review/OcrReviewPage";
import { OcrManualFallbackPage } from "../../src/applicant/pages/ocr_manual_fallback/OcrManualFallbackPage";
import { ValidationFindingsPage } from "../../src/applicant/pages/validation_findings/ValidationFindingsPage";

// Accessibility test for upload controls and OCR review (T082, User Story 2).

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

describe("document/OCR/validation accessibility", () => {
  it("has no axe violations on the document upload screen", async () => {
    const { container } = render(
      <MemoryRouter initialEntries={["/applicant/draft/app-1/documents"]}>
        <Routes>
          <Route
            path="/applicant/draft/:applicationId/documents"
            element={<DocumentUploadPage />}
          />
        </Routes>
      </MemoryRouter>,
    );
    await expectNoAxeViolations(container);
  });

  it("has no axe violations on the OCR review screen with extracted fields shown", async () => {
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

    const { container, findByText } = render(
      <MemoryRouter initialEntries={["/applicant/draft/app-1/ocr-review?document_id=doc-1"]}>
        <Routes>
          <Route path="/applicant/draft/:applicationId/ocr-review" element={<OcrReviewPage />} />
        </Routes>
      </MemoryRouter>,
    );
    await findByText(/Overall confidence/);
    await expectNoAxeViolations(container);
  });

  it("has no axe violations on the manual OCR fallback screen", async () => {
    const { container } = render(
      <MemoryRouter initialEntries={["/applicant/draft/app-1/ocr-manual-fallback"]}>
        <Routes>
          <Route
            path="/applicant/draft/:applicationId/ocr-manual-fallback"
            element={<OcrManualFallbackPage />}
          />
        </Routes>
      </MemoryRouter>,
    );
    await expectNoAxeViolations(container);
  });

  it("has no axe violations on the validation findings screen", async () => {
    const { container } = render(
      <MemoryRouter initialEntries={["/applicant/draft/app-1/validation"]}>
        <Routes>
          <Route
            path="/applicant/draft/:applicationId/validation"
            element={<ValidationFindingsPage />}
          />
        </Routes>
      </MemoryRouter>,
    );
    await expectNoAxeViolations(container);
  });
});
