import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { MemoryRouter, Route, Routes } from "react-router-dom";
import { afterEach, describe, expect, it, vi } from "vitest";
import { CreateApplicationPage } from "../../src/applicant/pages/create_application/CreateApplicationPage";
import { DraftIntakePage } from "../../src/applicant/pages/draft_intake/DraftIntakePage";

// UI test for intake creation, save, resume, and missing-item guidance
// (T055, User Story 1, TS-FR-001-004 / TC-FR-001-004).

function jsonResponse(body: unknown, ok = true) {
  return Promise.resolve({
    ok,
    status: ok ? 200 : 400,
    json: () => Promise.resolve(body),
    statusText: "",
  } as Response);
}

afterEach(() => {
  vi.unstubAllGlobals();
});

describe("intake creation flow", () => {
  it("creates a draft application and navigates to the draft intake screen", async () => {
    const fetchMock = vi.fn((input: RequestInfo | URL, init?: RequestInit) => {
      const url = String(input);
      if (url.endsWith("/applications") && init?.method === "POST") {
        return jsonResponse({
          application_id: "app-1",
          case_reference: "VA-000001",
          current_status: "draft_created",
        });
      }
      if (url.endsWith("/applications/app-1/resume")) {
        return jsonResponse({
          application_id: "app-1",
          case_reference: "VA-000001",
          current_status: "draft_created",
          current_version: 1,
          visa_type: "tourist",
          applicant: { legal_name: null, nationality: null, date_of_birth: null },
          missing_items: ["applicant.legal_name"],
        });
      }
      throw new Error(`unexpected fetch: ${init?.method ?? "GET"} ${url}`);
    });
    vi.stubGlobal("fetch", fetchMock);

    const user = userEvent.setup();
    render(
      <MemoryRouter initialEntries={["/applicant"]}>
        <Routes>
          <Route path="/applicant" element={<CreateApplicationPage />} />
          <Route path="/applicant/draft/:applicationId" element={<DraftIntakePage />} />
        </Routes>
      </MemoryRouter>,
    );

    await user.type(screen.getByLabelText(/Legal name/), "Jane Doe");
    await user.click(screen.getByLabelText(/I consent/));
    await user.click(screen.getByRole("button", { name: /Start application/ }));

    expect(await screen.findByRole("heading", { name: /VA-000001/ })).toBeInTheDocument();
    expect(screen.getByText(/Before you can submit/)).toBeInTheDocument();
  });
});

describe("draft intake save and missing-item guidance", () => {
  it("saves progress, updates the version, and reports missing items", async () => {
    const fetchMock = vi.fn((input: RequestInfo | URL, init?: RequestInit) => {
      const url = String(input);
      if (url.endsWith("/applications/app-2/resume")) {
        return jsonResponse({
          application_id: "app-2",
          case_reference: "VA-000002",
          current_status: "draft_created",
          current_version: 1,
          visa_type: "tourist",
          applicant: { legal_name: null, nationality: null, date_of_birth: null },
          missing_items: ["applicant.legal_name", "applicant.date_of_birth"],
        });
      }
      if (url.endsWith("/applications/app-2") && init?.method === "PATCH") {
        return jsonResponse({ application_id: "app-2", current_version: 2, missing_items: [] });
      }
      throw new Error(`unexpected fetch: ${init?.method ?? "GET"} ${url}`);
    });
    vi.stubGlobal("fetch", fetchMock);

    const user = userEvent.setup();
    render(
      <MemoryRouter initialEntries={["/applicant/draft/app-2"]}>
        <Routes>
          <Route path="/applicant/draft/:applicationId" element={<DraftIntakePage />} />
        </Routes>
      </MemoryRouter>,
    );

    expect(await screen.findByText(/Before you can submit \(2 remaining\)/)).toBeInTheDocument();

    await user.type(screen.getByLabelText(/Legal name/), "Jane Doe");
    await user.type(screen.getByLabelText(/Date of birth/), "1990-01-01");
    await user.click(screen.getByRole("button", { name: /Save progress/ }));

    await waitFor(() => {
      expect(screen.getByText(/All required information is complete/)).toBeInTheDocument();
    });
    expect(screen.getByText(/Progress saved\./)).toBeInTheDocument();
  });
});
