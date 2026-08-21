import { useState } from "react";
import { useParams } from "react-router-dom";
import { ErrorSummary, type FieldError } from "@shared/components";
import { apiRequest } from "@shared/api/client";
import { getWorkspaceAuthToken } from "@shared/api/identity";

interface SubmitResponse {
  submission_reference: string;
  snapshot_id: string;
  current_status: string;
}

// Submission confirmation and submitted-snapshot lock screen (T099, User
// Story 3, AC-003).
export function SubmissionConfirmationPage() {
  const { applicationId } = useParams<{ applicationId: string }>();
  const [result, setResult] = useState<SubmitResponse | null>(null);
  const [errors, setErrors] = useState<FieldError[]>([]);
  const [submitting, setSubmitting] = useState(false);

  async function handleSubmit() {
    if (!applicationId) return;
    setSubmitting(true);
    try {
      const response = await apiRequest<SubmitResponse>(`/applications/${applicationId}/submit`, {
        method: "POST",
        authToken: getWorkspaceAuthToken("sub-agency"),
      });
      setResult(response);
      setErrors([]);
    } catch (error) {
      setErrors([{ fieldId: "submit", message: (error as Error).message }]);
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <section aria-labelledby="submission-confirmation-heading">
      <h1 id="submission-confirmation-heading">Submit to main agency</h1>
      <p>
        Once submitted, this application&apos;s data is locked to a snapshot and cannot be edited
        directly.
      </p>
      <ErrorSummary errors={errors} />

      {!result && (
        <button type="button" onClick={handleSubmit} disabled={submitting}>
          {submitting ? "Submitting…" : "Submit to main agency"}
        </button>
      )}

      {result && (
        <div role="status">
          <p>
            Submitted. Reference <strong>{result.submission_reference}</strong>. Status:{" "}
            {result.current_status.replace(/_/g, " ")}.
          </p>
        </div>
      )}
    </section>
  );
}
