import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import { StatusTimeline, type TimelineEntry } from "@shared/components";
import { apiRequest } from "@shared/api/client";
import { getWorkspaceAuthToken, type Workspace } from "@shared/api/identity";

interface ResumeResponse {
  current_status: string;
  case_reference: string;
}

interface StatusTimelineResponse {
  timeline: TimelineEntry[];
}

const TERMINAL_MESSAGES: Record<string, string> = {
  approved: "Your visa application has been approved.",
  rejected: "Your visa application was not approved.",
  cancelled: "Your visa application has been cancelled.",
  withdrawn: "Your visa application has been withdrawn.",
  expired: "Your visa application has expired.",
  closed: "Your visa application is closed.",
};

interface FinalOutcomePageProps {
  workspace?: Workspace;
}

// Immigration processing status and final outcome screen (T139, User Story 5).
export function FinalOutcomePage({ workspace = "applicant" }: FinalOutcomePageProps) {
  const { applicationId } = useParams<{ applicationId: string }>();
  const [status, setStatus] = useState<ResumeResponse | null>(null);
  const [timeline, setTimeline] = useState<TimelineEntry[]>([]);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!applicationId) return;
    const authToken = getWorkspaceAuthToken(workspace);
    apiRequest<ResumeResponse>(`/applications/${applicationId}/resume`, { authToken })
      .then(setStatus)
      .catch((err) => setError((err as Error).message));
    apiRequest<StatusTimelineResponse>(`/applications/${applicationId}/status-timeline`, {
      authToken,
    })
      .then((response) => setTimeline(response.timeline ?? []))
      .catch(() => undefined);
  }, [applicationId, workspace]);

  const isTerminal = status ? status.current_status in TERMINAL_MESSAGES : false;

  return (
    <section aria-labelledby="final-outcome-heading">
      <h1 id="final-outcome-heading">Application outcome</h1>
      {error && <p role="alert">{error}</p>}
      {status && (
        <p role="status">
          Case {status.case_reference}: <strong>{status.current_status.replace(/_/g, " ")}</strong>.{" "}
          {isTerminal && TERMINAL_MESSAGES[status.current_status]}
          {!isTerminal && "Your application is still being processed. Check back for updates."}
        </p>
      )}
      <StatusTimeline entries={timeline} />
    </section>
  );
}
