import { FormEvent, useState } from "react";
import { Link } from "react-router-dom";
import { ErrorSummary, FormField, type FieldError } from "@shared/components";
import { apiRequest } from "@shared/api/client";
import { getWorkspaceAuthToken } from "@shared/api/identity";

interface ClaimResponse {
  application_id: string;
  current_status: string;
}

// Routed queue and assignment screen (T116, User Story 4).
export function CaseQueuePage() {
  const [applicationId, setApplicationId] = useState("");
  const [result, setResult] = useState<ClaimResponse | null>(null);
  const [errors, setErrors] = useState<FieldError[]>([]);
  const [claiming, setClaiming] = useState(false);

  async function handleClaim(event: FormEvent) {
    event.preventDefault();
    if (!applicationId.trim()) {
      setErrors([{ fieldId: "application-id", message: "Enter the routed application to claim" }]);
      return;
    }
    setClaiming(true);
    try {
      const response = await apiRequest<ClaimResponse>(`/applications/${applicationId}/claim`, {
        method: "POST",
        authToken: getWorkspaceAuthToken("main-agency"),
      });
      setResult(response);
      setErrors([]);
    } catch (error) {
      setErrors([{ fieldId: "application-id", message: (error as Error).message }]);
    } finally {
      setClaiming(false);
    }
  }

  return (
    <section aria-labelledby="case-queue-heading">
      <h1 id="case-queue-heading">Routed case queue</h1>
      <ErrorSummary errors={errors} />

      <form onSubmit={handleClaim} noValidate>
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
        <button type="submit" disabled={claiming}>
          {claiming ? "Claiming…" : "Claim for processing"}
        </button>
      </form>

      {result && (
        <div role="status">
          <p>
            Claimed. Status: <strong>{result.current_status.replace(/_/g, " ")}</strong>.
          </p>
          <Link to={`/main-agency/case/${result.application_id}`}>Review case</Link>
        </div>
      )}
    </section>
  );
}
