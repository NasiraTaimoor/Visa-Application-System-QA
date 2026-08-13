import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { MemoryRouter, Route, Routes } from "react-router-dom";
import { afterEach, describe, expect, it, vi } from "vitest";
import { WalletVerificationPage } from "../../src/sub-agency/pages/wallet_verification/WalletVerificationPage";
import { SubmissionConfirmationPage } from "../../src/sub-agency/pages/submission_confirmation/SubmissionConfirmationPage";

// UI test for wallet verification, shortfall display, and submission (T100,
// User Story 3, TS-FR-012-016 / TC-FR-012-016).

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

describe("wallet verification", () => {
  it("shows the reservation reference when the balance is sufficient", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn(() =>
        jsonResponse({
          sufficient: true,
          amount: 5000,
          currency: "AED",
          reservation_reference: "wal-res-1",
          shortfall_amount: null,
        }),
      ),
    );
    const user = userEvent.setup();
    render(
      <MemoryRouter>
        <WalletVerificationPage />
      </MemoryRouter>,
    );

    await user.type(screen.getByLabelText(/Application ID/), "app-1");
    await user.click(screen.getByRole("button", { name: /Verify wallet/ }));

    expect(await screen.findByText(/Reserved 5000 AED/)).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /Continue to submission/ })).toBeInTheDocument();
  });

  it("shows the shortfall amount and does not offer to continue when insufficient", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn(() =>
        jsonResponse({
          sufficient: false,
          amount: 5000,
          currency: "AED",
          reservation_reference: null,
          shortfall_amount: 4500,
        }),
      ),
    );
    const user = userEvent.setup();
    render(
      <MemoryRouter>
        <WalletVerificationPage />
      </MemoryRouter>,
    );

    await user.type(screen.getByLabelText(/Application ID/), "app-2");
    await user.click(screen.getByRole("button", { name: /Verify wallet/ }));

    expect(await screen.findByText(/Short by 4500 AED/)).toBeInTheDocument();
    expect(
      screen.queryByRole("button", { name: /Continue to submission/ }),
    ).not.toBeInTheDocument();
  });
});

describe("submission confirmation", () => {
  it("submits and shows the submission reference", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn(() =>
        jsonResponse({
          submission_reference: "SUB-ABC123",
          snapshot_id: "snapshot-app-3-v2",
          current_status: "submitted_to_main_agency",
        }),
      ),
    );
    const user = userEvent.setup();
    render(
      <MemoryRouter initialEntries={["/sub-agency/submission/app-3"]}>
        <Routes>
          <Route
            path="/sub-agency/submission/:applicationId"
            element={<SubmissionConfirmationPage />}
          />
        </Routes>
      </MemoryRouter>,
    );

    await user.click(screen.getByRole("button", { name: /Submit to main agency/ }));
    expect(await screen.findByText(/SUB-ABC123/)).toBeInTheDocument();
  });
});
