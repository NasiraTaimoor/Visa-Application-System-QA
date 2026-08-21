import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { MemoryRouter } from "react-router-dom";
import { afterEach, describe, expect, it, vi } from "vitest";
import { AuditHistoryPage } from "../../src/audit/pages/audit_history/AuditHistoryPage";
import { ExportCompliancePage } from "../../src/audit/pages/export_compliance/ExportCompliancePage";
import { RecoveryTasksPage } from "../../src/support/pages/recovery_tasks/RecoveryTasksPage";

// UI test for audit history, export controls, and support recovery (T171,
// User Story 7, TS-FR-029-034 / TC-FR-029-034).

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

describe("audit history", () => {
  it("searches and lists audit events", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn(() =>
        jsonResponse({
          events: [
            {
              audit_event_id: "a-1",
              actor_or_service_id: "u-applicant-1",
              role: "applicant",
              timestamp: "2026-08-01T09:00:00Z",
              action: "application.create",
              affected_case_or_record: "app-1",
              outcome: "success",
              reason: null,
              correlation_reference: "corr-1",
            },
          ],
        }),
      ),
    );
    const user = userEvent.setup();
    render(
      <MemoryRouter>
        <AuditHistoryPage />
      </MemoryRouter>,
    );

    await user.type(screen.getByLabelText(/Application ID/), "app-1");
    await user.click(screen.getByRole("button", { name: /Search audit history/ }));

    expect(await screen.findByText("application.create")).toBeInTheDocument();
  });
});

describe("export compliance", () => {
  it("requires a business reason before exporting", async () => {
    const fetchMock = vi.fn(() => jsonResponse({ export_reference: "EXPORT-1", record_count: 3 }));
    vi.stubGlobal("fetch", fetchMock);
    const user = userEvent.setup();
    render(
      <MemoryRouter>
        <ExportCompliancePage />
      </MemoryRouter>,
    );

    await user.click(screen.getByRole("button", { name: /Export records/ }));
    expect(screen.getByRole("alert")).toHaveTextContent(/business reason is required/);
    expect(fetchMock).not.toHaveBeenCalled();

    await user.type(screen.getByLabelText(/Business reason/), "quarterly review");
    await user.click(screen.getByRole("button", { name: /Export records/ }));
    expect(await screen.findByText(/EXPORT-1/)).toBeInTheDocument();
  });
});

describe("support recovery", () => {
  it("looks up a masked case with a business reason", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn(() =>
        jsonResponse({
          application_id: "app-1",
          case_reference: "VA-000001",
          current_status: "draft_created",
          applicant_legal_name_masked: "J***",
        }),
      ),
    );
    const user = userEvent.setup();
    render(
      <MemoryRouter>
        <RecoveryTasksPage />
      </MemoryRouter>,
    );

    await user.type(screen.getByLabelText(/Application ID/), "app-1");
    await user.type(screen.getByLabelText(/Business reason/), "applicant support ticket #123");
    await user.click(screen.getByRole("button", { name: /Look up case/ }));

    expect(await screen.findByText(/VA-000001/)).toBeInTheDocument();
    expect(screen.getByText(/J\*\*\*/)).toBeInTheDocument();
  });
});
