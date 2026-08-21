import { FormEvent, useState } from "react";
import { ErrorSummary, FormField, type FieldError } from "@shared/components";
import { apiRequest } from "@shared/api/client";
import { getWorkspaceAuthToken } from "@shared/api/identity";

interface ReadinessResponse {
  current_status: string;
}

interface GdrfaSubmitResponse {
  submission_reference: string;
  response_type: string;
  current_status: string;
  response_reason: string | null;
}

// Readiness approval and GDRFA submission/response screen (T118, User Story 4).
export function GdrfaSubmissionPage() {
  const [applicationId, setApplicationId] = useState("");
  const [readinessReason, setReadinessReason] = useState("");
  const [readinessStatus, setReadinessStatus] = useState<string | null>(null);
  const [submission, setSubmission] = useState<GdrfaSubmitResponse | null>(null);
  const [errors, setErrors] = useState<FieldError[]>([]);
  const [busy, setBusy] = useState(false);

  async function handleApproveReadiness(event: FormEvent) {
    event.preventDefault();
    if (!applicationId.trim() || !readinessReason.trim()) {
      setErrors([
        {
          fieldId: "readiness-reason",
          message: "Application ID and a readiness reason are required",
        },
      ]);
      return;
    }
    setBusy(true);
    try {
      const response = await apiRequest<ReadinessResponse>(
        `/applications/${applicationId}/readiness-approve`,
        {
          method: "POST",
          authToken: getWorkspaceAuthToken("main-agency"),
          body: { reason: readinessReason },
        },
      );
      setReadinessStatus(response.current_status);
      setErrors([]);
    } catch (error) {
      setErrors([{ fieldId: "readiness-reason", message: (error as Error).message }]);
    } finally {
      setBusy(false);
    }
  }

  async function handleSubmitToGdrfa() {
    if (!applicationId.trim()) return;
    setBusy(true);
    try {
      const response = await apiRequest<GdrfaSubmitResponse>(
        `/applications/${applicationId}/gdrfa/submit`,
        {
          method: "POST",
          authToken: getWorkspaceAuthToken("main-agency"),
        },
      );
      setSubmission(response);
      setErrors([]);
    } catch (error) {
      setErrors([{ fieldId: "readiness-reason", message: (error as Error).message }]);
    } finally {
      setBusy(false);
    }
  }

  return (
    <section aria-labelledby="gdrfa-submission-heading">
      <h1 id="gdrfa-submission-heading">GDRFA readiness and submission</h1>
      <ErrorSummary errors={errors} />

      <form onSubmit={handleApproveReadiness} noValidate>
        <FormField label="Application ID" required>
          {(fieldProps) => (
            <input
              {...fieldProps}
              type="text"
              value={applicationId}
              onChange={(e) => setApplicationId(e.target.value)}
            />
          )}
        </FormField>
        <FormField label="Readiness decision reason" required>
          {(fieldProps) => (
            <input
              {...fieldProps}
              type="text"
              value={readinessReason}
              onChange={(e) => setReadinessReason(e.target.value)}
            />
          )}
        </FormField>
        <button type="submit" disabled={busy}>
          Approve readiness
        </button>
      </form>

      {readinessStatus && (
        <p role="status">Readiness recorded. Status: {readinessStatus.replace(/_/g, " ")}</p>
      )}

      <button type="button" onClick={handleSubmitToGdrfa} disabled={busy || !applicationId.trim()}>
        Submit to GDRFA
      </button>

      {submission && (
        <div role="status">
          <p>
            GDRFA response: <strong>{submission.response_type.replace(/_/g, " ")}</strong>. Status:{" "}
            {submission.current_status.replace(/_/g, " ")}.
          </p>
          {submission.response_reason && <p>Reason: {submission.response_reason}</p>}
        </div>
      )}
    </section>
  );
}
