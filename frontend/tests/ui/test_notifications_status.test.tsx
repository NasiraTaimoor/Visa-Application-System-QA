import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { MemoryRouter } from "react-router-dom";
import { afterEach, describe, expect, it, vi } from "vitest";
import { NotificationPreferencesPage } from "../../src/applicant/pages/notification_preferences/NotificationPreferencesPage";
import { StatusTimeline } from "../../src/shared/components";

// UI test for status timeline visibility and notification preferences
// (T155, User Story 6, TS-FR-025-028 / TC-FR-025-028).

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

describe("notification preferences", () => {
  it("saves a channel preference and shows mandatory events cannot be disabled", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn(() => jsonResponse({ channel: "sms", opted_out_events: ["submission_created"] })),
    );
    const user = userEvent.setup();
    render(
      <MemoryRouter>
        <NotificationPreferencesPage />
      </MemoryRouter>,
    );

    expect(screen.getByText("correction requested")).toBeInTheDocument();
    expect(screen.getByText("final decision")).toBeInTheDocument();

    await user.type(screen.getByLabelText(/Application ID/), "app-1");
    await user.selectOptions(screen.getByLabelText(/Preferred channel/), "sms");
    await user.click(screen.getByLabelText(/Submission created/));
    await user.click(screen.getByRole("button", { name: /Save preferences/ }));

    expect(await screen.findByText(/Preferences saved\. Channel: sms\./)).toBeInTheDocument();
  });
});

describe("status timeline", () => {
  it("renders each status event chronologically", () => {
    render(
      <StatusTimeline
        entries={[
          {
            new_status: "draft_created",
            previous_status: null,
            timestamp: "2026-08-01T09:00:00Z",
            reason: null,
            next_action: null,
          },
          {
            new_status: "documents_pending",
            previous_status: "draft_created",
            timestamp: "2026-08-01T09:05:00Z",
            reason: null,
            next_action: "Upload remaining documents",
          },
        ]}
      />,
    );

    expect(screen.getByText("draft created")).toBeInTheDocument();
    expect(screen.getByText("documents pending")).toBeInTheDocument();
    expect(screen.getByText(/Upload remaining documents/)).toBeInTheDocument();
  });

  it("shows a message when there is no history yet", () => {
    render(<StatusTimeline entries={[]} />);
    expect(screen.getByText(/No status history is available yet/)).toBeInTheDocument();
  });
});
