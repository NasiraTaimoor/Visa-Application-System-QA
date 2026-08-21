import { FormEvent, useState } from "react";
import { useNavigate } from "react-router-dom";
import { FormField, ErrorSummary, type FieldError } from "@shared/components";
import { apiRequest } from "@shared/api/client";
import { getWorkspaceAuthToken } from "@shared/api/identity";

// Session recovery / resume flow (T053): restores an interrupted draft after
// re-authentication without exposing personal data to unauthorized users
// (masking is enforced server-side by resume_draft; see AC-001, E-010).
export function SessionRecoveryPage() {
  const navigate = useNavigate();
  const [applicationId, setApplicationId] = useState("");
  const [errors, setErrors] = useState<FieldError[]>([]);
  const [checking, setChecking] = useState(false);

  async function handleResume(event: FormEvent) {
    event.preventDefault();
    if (!applicationId.trim()) {
      setErrors([
        { fieldId: "application-id", message: "Enter your application reference to resume" },
      ]);
      return;
    }
    setChecking(true);
    try {
      await apiRequest(`/applications/${applicationId}/resume`, {
        authToken: getWorkspaceAuthToken("applicant"),
      });
      navigate(`/applicant/draft/${applicationId}`);
    } catch (error) {
      setErrors([{ fieldId: "application-id", message: (error as Error).message }]);
    } finally {
      setChecking(false);
    }
  }

  return (
    <section aria-labelledby="session-recovery-heading">
      <h1 id="session-recovery-heading">Resume a saved application</h1>
      <p>
        Your session was interrupted. Sign back in and enter your application reference to continue
        safely.
      </p>
      <ErrorSummary errors={errors} />
      <form onSubmit={handleResume} noValidate>
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
        <button type="submit" disabled={checking}>
          {checking ? "Checking…" : "Resume application"}
        </button>
      </form>
    </section>
  );
}
