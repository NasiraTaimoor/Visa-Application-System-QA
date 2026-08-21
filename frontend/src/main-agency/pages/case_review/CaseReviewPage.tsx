import { FormEvent, useState } from "react";
import { useParams } from "react-router-dom";
import { ErrorSummary, FormField, type FieldError } from "@shared/components";
import { apiRequest } from "@shared/api/client";
import { getWorkspaceAuthToken } from "@shared/api/identity";

interface StatusResponse {
  current_status: string;
}

// Case review, correction request, and decision/rationale capture screen
// (T117, User Story 4).
export function CaseReviewPage() {
  const { applicationId } = useParams<{ applicationId: string }>();
  const [reason, setReason] = useState("");
  const [responsibleParty, setResponsibleParty] = useState("applicant");
  const [status, setStatus] = useState<string | null>(null);
  const [errors, setErrors] = useState<FieldError[]>([]);
  const [submitting, setSubmitting] = useState(false);

  async function handleRequestCorrection(event: FormEvent) {
    event.preventDefault();
    if (!applicationId) return;
    if (!reason.trim()) {
      setErrors([{ fieldId: "reason", message: "A reason is required to request a correction" }]);
      return;
    }
    setSubmitting(true);
    try {
      const response = await apiRequest<StatusResponse>(
        `/applications/${applicationId}/correction-request`,
        {
          method: "POST",
          authToken: getWorkspaceAuthToken("main-agency"),
          body: { reason, responsible_party: responsibleParty },
        },
      );
      setStatus(response.current_status);
      setErrors([]);
    } catch (error) {
      setErrors([{ fieldId: "reason", message: (error as Error).message }]);
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <section aria-labelledby="case-review-heading">
      <h1 id="case-review-heading">Case review: {applicationId}</h1>
      <ErrorSummary errors={errors} />
      {status && <p role="status">Status: {status.replace(/_/g, " ")}</p>}

      <form onSubmit={handleRequestCorrection} noValidate>
        <FormField label="Correction reason" required>
          {(fieldProps) => (
            <textarea {...fieldProps} value={reason} onChange={(e) => setReason(e.target.value)} />
          )}
        </FormField>
        <FormField label="Responsible party">
          {(fieldProps) => (
            <select
              {...fieldProps}
              value={responsibleParty}
              onChange={(e) => setResponsibleParty(e.target.value)}
            >
              <option value="applicant">Applicant</option>
              <option value="sub_agency_officer">Sub-agency officer</option>
            </select>
          )}
        </FormField>
        <button type="submit" disabled={submitting}>
          {submitting ? "Sending…" : "Request correction"}
        </button>
      </form>
    </section>
  );
}
