import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { MemoryRouter, Route, Routes } from "react-router-dom";
import { afterEach, describe, expect, it, vi } from "vitest";
import { PaymentQueuePage } from "../../src/finance/pages/payment_queue/PaymentQueuePage";
import { FinalOutcomePage } from "../../src/applicant/pages/final_outcome/FinalOutcomePage";

// UI test for payment states and final outcome display (T140, User Story 5,
// TS-FR-022-024 / TC-FR-022-024).

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

describe("payment queue", () => {
  it("confirms a payment and shows the resulting state", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn(() => jsonResponse({ payment_state: "paid", current_status: "paid", reason: null })),
    );
    const user = userEvent.setup();
    render(
      <MemoryRouter>
        <PaymentQueuePage />
      </MemoryRouter>,
    );

    await user.type(screen.getByLabelText(/Application ID/), "app-1");
    await user.click(screen.getByRole("button", { name: /Confirm payment/ }));

    expect(await screen.findByRole("status")).toHaveTextContent(
      "Payment state: paid. Case status: paid.",
    );
  });

  it("records a manual reconciliation", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn(() => jsonResponse({ application_id: "app-1", current_status: "paid" })),
    );
    const user = userEvent.setup();
    render(
      <MemoryRouter>
        <PaymentQueuePage />
      </MemoryRouter>,
    );

    await user.type(screen.getByLabelText(/Application ID/), "app-1");
    await user.type(screen.getByLabelText(/Receipt reference/), "manual-0001");
    await user.type(screen.getByLabelText(/Amount/), "5000");
    await user.clear(screen.getByLabelText(/Currency/));
    await user.type(screen.getByLabelText(/Currency/), "AED");
    await user.type(screen.getByLabelText(/^Reason/), "bank transfer confirmed");
    await user.click(screen.getByRole("button", { name: /Record manual reconciliation/ }));

    expect(await screen.findByText(/Reconciled/)).toBeInTheDocument();
  });
});

describe("final outcome", () => {
  it("shows the approved outcome message", async () => {
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
    render(
      <MemoryRouter initialEntries={["/applicant/draft/app-1/outcome"]}>
        <Routes>
          <Route path="/applicant/draft/:applicationId/outcome" element={<FinalOutcomePage />} />
        </Routes>
      </MemoryRouter>,
    );

    expect(await screen.findByText(/has been approved/)).toBeInTheDocument();
    expect(await screen.findByRole("list", { name: /Case status timeline/ })).toBeInTheDocument();
  });
});
