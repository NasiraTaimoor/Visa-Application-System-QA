import { render } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { MemoryRouter, Route, Routes } from "react-router-dom";
import { afterEach, describe, expect, it, vi } from "vitest";
import { expectNoAxeViolations } from "../../src/accessibility/axeHelper";
import { CreateApplicationPage } from "../../src/applicant/pages/create_application/CreateApplicationPage";
import { DraftIntakePage } from "../../src/applicant/pages/draft_intake/DraftIntakePage";

// Accessibility test (keyboard + screen reader) for intake forms (T056,
// User Story 1). Automated axe sweep plus a keyboard-only interaction check.

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

describe("intake form accessibility", () => {
  it("has no axe violations on the create application screen", async () => {
    const { container } = render(
      <MemoryRouter>
        <CreateApplicationPage />
      </MemoryRouter>,
    );
    await expectNoAxeViolations(container);
  });

  it("is fully operable by keyboard, including reaching the submit control", async () => {
    const user = userEvent.setup();
    render(
      <MemoryRouter>
        <CreateApplicationPage />
      </MemoryRouter>,
    );

    await user.tab(); // visa type select
    await user.tab(); // sub-agency input
    await user.tab(); // legal name input
    await user.tab(); // consent checkbox
    expect(document.activeElement).toHaveAttribute("type", "checkbox");
    await user.keyboard(" ");
    expect(document.activeElement).toBeChecked();
    await user.tab(); // submit button
    expect(document.activeElement).toHaveTextContent(/Start application/);
  });

  it("has no axe violations on the draft intake screen with missing-item guidance shown", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn(() =>
        jsonResponse({
          application_id: "app-3",
          case_reference: "VA-000003",
          current_status: "draft_created",
          current_version: 1,
          visa_type: "tourist",
          applicant: { legal_name: "Jane Doe", nationality: null, date_of_birth: null },
          missing_items: ["applicant.nationality", "applicant.date_of_birth"],
        }),
      ),
    );

    const { container, findByText } = render(
      <MemoryRouter initialEntries={["/applicant/draft/app-3"]}>
        <Routes>
          <Route path="/applicant/draft/:applicationId" element={<DraftIntakePage />} />
        </Routes>
      </MemoryRouter>,
    );

    await findByText(/Before you can submit/);
    await expectNoAxeViolations(container);
  });
});
