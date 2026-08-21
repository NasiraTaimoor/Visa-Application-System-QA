import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { MemoryRouter, Route, Routes } from "react-router-dom";
import { afterEach, describe, expect, it, vi } from "vitest";
import { DocumentUploadPage } from "../../src/applicant/pages/document_upload/DocumentUploadPage";
import { OcrReviewPage } from "../../src/applicant/pages/ocr_review/OcrReviewPage";
import { ValidationFindingsPage } from "../../src/applicant/pages/validation_findings/ValidationFindingsPage";

// UI test for upload, OCR review, correction, and validation findings
// (T081, User Story 2, TS-FR-005-011 / TC-FR-005-011).

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

describe("document upload flow", () => {
  it("uploads a document and shows the screening outcome", async () => {
    const fetchMock = vi.fn((input: RequestInfo | URL, init?: RequestInit) => {
      const url = String(input);
      if (url.endsWith("/applications/app-1/documents") && init?.method === "POST") {
        return jsonResponse({
          document_id: "doc-1",
          document_type: "passport_bio_page",
          version: 1,
          screening_status: "accepted",
          ocr_triggered: true,
        });
      }
      throw new Error(`unexpected fetch: ${init?.method ?? "GET"} ${url}`);
    });
    vi.stubGlobal("fetch", fetchMock);

    const user = userEvent.setup();
    render(
      <MemoryRouter initialEntries={["/applicant/draft/app-1/documents"]}>
        <Routes>
          <Route
            path="/applicant/draft/:applicationId/documents"
            element={<DocumentUploadPage />}
          />
        </Routes>
      </MemoryRouter>,
    );

    const file = new File(["%PDF-1.4 bytes"], "passport.pdf", { type: "application/pdf" });
    const fileInput = screen.getByLabelText(/File/) as HTMLInputElement;
    await user.upload(fileInput, file);
    await user.click(screen.getByRole("button", { name: /Upload document/ }));

    expect(await screen.findByText(/accepted/)).toBeInTheDocument();
    expect(screen.getByText(/review OCR results/)).toBeInTheDocument();
  });
});

describe("OCR review flow", () => {
  it("loads extracted fields and confirms corrected values", async () => {
    const fetchMock = vi.fn((input: RequestInfo | URL, init?: RequestInit) => {
      const url = String(input);
      if (url.endsWith("/documents/doc-1/ocr")) {
        return jsonResponse({
          document_id: "doc-1",
          extraction_status: "completed",
          extracted_fields: { passport_number: "P1234567" },
          confidence_by_field: { passport_number: 0.97 },
          overall_confidence: 0.93,
          warning_flags: [],
          reviewed_values: {},
          reviewer_id: null,
        });
      }
      if (
        url.endsWith("/applications/app-1/documents/doc-1/ocr/confirm") &&
        init?.method === "POST"
      ) {
        return jsonResponse({
          document_id: "doc-1",
          reviewed_values: { passport_number: "P9999999" },
          reviewer_id: "u-applicant-1",
        });
      }
      throw new Error(`unexpected fetch: ${init?.method ?? "GET"} ${url}`);
    });
    vi.stubGlobal("fetch", fetchMock);

    const user = userEvent.setup();
    render(
      <MemoryRouter initialEntries={["/applicant/draft/app-1/ocr-review?document_id=doc-1"]}>
        <Routes>
          <Route path="/applicant/draft/:applicationId/ocr-review" element={<OcrReviewPage />} />
        </Routes>
      </MemoryRouter>,
    );

    expect(await screen.findByText(/Overall confidence: 93%/)).toBeInTheDocument();
    const field = screen.getByLabelText(/passport number/);
    await user.clear(field);
    await user.type(field, "P9999999");
    await user.click(screen.getByRole("button", { name: /Confirm values/ }));

    expect(await screen.findByText(/Values confirmed/)).toBeInTheDocument();
  });
});

describe("validation findings flow", () => {
  it("runs validation and shows corrective actions", async () => {
    const fetchMock = vi.fn((input: RequestInfo | URL, init?: RequestInit) => {
      const url = String(input);
      if (url.endsWith("/applications/app-1/validate") && init?.method === "POST") {
        return jsonResponse({
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
        });
      }
      throw new Error(`unexpected fetch: ${init?.method ?? "GET"} ${url}`);
    });
    vi.stubGlobal("fetch", fetchMock);

    const user = userEvent.setup();
    render(
      <MemoryRouter initialEntries={["/applicant/draft/app-1/validation"]}>
        <Routes>
          <Route
            path="/applicant/draft/:applicationId/validation"
            element={<ValidationFindingsPage />}
          />
        </Routes>
      </MemoryRouter>,
    );

    await user.click(screen.getByRole("button", { name: /Run validation/ }));

    await waitFor(() => {
      expect(screen.getByText(/action required before this case can proceed/)).toBeInTheDocument();
    });
    expect(screen.getByText(/Upload an accepted photo/)).toBeInTheDocument();
  });
});
