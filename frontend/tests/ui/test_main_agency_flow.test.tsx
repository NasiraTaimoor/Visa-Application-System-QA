import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { MemoryRouter, Route, Routes } from "react-router-dom";
import { afterEach, describe, expect, it, vi } from "vitest";
import { CaseQueuePage } from "../../src/main-agency/pages/case_queue/CaseQueuePage";
import { CaseReviewPage } from "../../src/main-agency/pages/case_review/CaseReviewPage";
import { GdrfaSubmissionPage } from "../../src/main-agency/pages/gdrfa_submission/GdrfaSubmissionPage";

// UI test for main agency queue, correction request, readiness approval, and
// GDRFA response handling (T119, User Story 4, TS-FR-017-021 / TC-FR-017-021).

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

describe("main agency case queue", () => {
  it("claims a routed case and links to the review screen", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn(() =>
        jsonResponse({ application_id: "app-1", current_status: "main_agency_processing" }),
      ),
    );
    const user = userEvent.setup();
    render(
      <MemoryRouter>
        <CaseQueuePage />
      </MemoryRouter>,
    );

    await user.type(screen.getByLabelText(/Application ID/), "app-1");
    await user.click(screen.getByRole("button", { name: /Claim for processing/ }));

    expect(await screen.findByText(/main agency processing/)).toBeInTheDocument();
    expect(screen.getByRole("link", { name: /Review case/ })).toBeInTheDocument();
  });
});

describe("case review", () => {
  it("requires a reason before requesting a correction", async () => {
    const fetchMock = vi.fn(() => jsonResponse({ current_status: "correction_requested" }));
    vi.stubGlobal("fetch", fetchMock);
    const user = userEvent.setup();
    render(
      <MemoryRouter initialEntries={["/main-agency/case/app-1"]}>
        <Routes>
          <Route path="/main-agency/case/:applicationId" element={<CaseReviewPage />} />
        </Routes>
      </MemoryRouter>,
    );

    await user.click(screen.getByRole("button", { name: /Request correction/ }));
    expect(screen.getByRole("alert")).toHaveTextContent(/reason is required/);
    expect(fetchMock).not.toHaveBeenCalled();

    await user.type(screen.getByLabelText(/Correction reason/), "missing signature");
    await user.click(screen.getByRole("button", { name: /Request correction/ }));
    expect(await screen.findByText(/correction requested/)).toBeInTheDocument();
  });
});

describe("GDRFA submission", () => {
  it("approves readiness then submits and shows the response", async () => {
    const fetchMock = vi.fn((input: RequestInfo | URL) => {
      const url = String(input);
      if (url.endsWith("/readiness-approve"))
        return jsonResponse({ current_status: "main_agency_processing" });
      if (url.endsWith("/gdrfa/submit"))
        return jsonResponse({
          submission_reference: "GDRFA-SUB-1",
          response_type: "acknowledged",
          current_status: "payment_pending",
          response_reason: null,
        });
      throw new Error(`unexpected fetch: ${url}`);
    });
    vi.stubGlobal("fetch", fetchMock);
    const user = userEvent.setup();
    render(
      <MemoryRouter>
        <GdrfaSubmissionPage />
      </MemoryRouter>,
    );

    await user.type(screen.getByLabelText(/Application ID/), "app-1");
    await user.type(screen.getByLabelText(/Readiness decision reason/), "verified");
    await user.click(screen.getByRole("button", { name: /Approve readiness/ }));
    expect(await screen.findByText(/Readiness recorded/)).toBeInTheDocument();

    await user.click(screen.getByRole("button", { name: /Submit to GDRFA/ }));
    expect(await screen.findByText(/GDRFA response:/)).toBeInTheDocument();
    expect(screen.getByText("acknowledged")).toBeInTheDocument();
  });
});
