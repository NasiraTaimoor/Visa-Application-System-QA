import { FormEvent, useState } from "react";
import { useParams } from "react-router-dom";
import { ErrorSummary, FormField, type FieldError } from "@shared/components";
import { apiRequest } from "@shared/api/client";
import { getWorkspaceAuthToken, type Workspace } from "@shared/api/identity";

interface ValidationFinding {
  finding_id: string;
  rule_id: string;
  severity: string;
  affected_field_or_document: string | null;
  corrective_action: string | null;
  override_status: string | null;
}

interface ValidateResponse {
  current_status: string;
  is_ready: boolean;
  findings: ValidationFinding[];
}

const SEVERITY_LABELS: Record<string, string> = {
  informational: "Informational",
  warning: "Warning",
  blocking: "Blocking — must be corrected",
  overrideable_blocking: "Blocking — correction or supervisor override required",
  non_overrideable_blocking: "Blocking — cannot be overridden",
};

interface ValidationFindingsPageProps {
  workspace?: Workspace;
}

// Validation findings screen with corrective action guidance (T079, User
// Story 2).
export function ValidationFindingsPage({ workspace = "applicant" }: ValidationFindingsPageProps) {
  const { applicationId } = useParams<{ applicationId: string }>();
  const [outcome, setOutcome] = useState<ValidateResponse | null>(null);
  const [errors, setErrors] = useState<FieldError[]>([]);
  const [running, setRunning] = useState(false);
  const [overrideReason, setOverrideReason] = useState<Record<string, string>>({});

  async function runValidation() {
    if (!applicationId) return;
    setRunning(true);
    try {
      const result = await apiRequest<ValidateResponse>(`/applications/${applicationId}/validate`, {
        method: "POST",
        authToken: getWorkspaceAuthToken(workspace),
      });
      setOutcome(result);
      setErrors([]);
    } catch (error) {
      setErrors([{ fieldId: "validate", message: (error as Error).message }]);
    } finally {
      setRunning(false);
    }
  }

  async function handleOverride(findingId: string, event: FormEvent) {
    event.preventDefault();
    try {
      await apiRequest(`/validation/findings/${findingId}/override`, {
        method: "POST",
        authToken: getWorkspaceAuthToken(workspace),
        body: { reason: overrideReason[findingId] ?? "" },
      });
      await runValidation();
    } catch (error) {
      setErrors([{ fieldId: "validate", message: (error as Error).message }]);
    }
  }

  return (
    <section aria-labelledby="validation-findings-heading">
      <h1 id="validation-findings-heading">Validation findings</h1>
      <ErrorSummary errors={errors} />

      <button type="button" onClick={runValidation} disabled={running}>
        {running ? "Checking…" : "Run validation"}
      </button>

      {outcome && (
        <>
          <p role="status">
            Status: <strong>{outcome.current_status.replace(/_/g, " ")}</strong> —{" "}
            {outcome.is_ready ? "ready to proceed" : "action required before this case can proceed"}
          </p>

          {outcome.findings.length === 0 ? (
            <p>No outstanding findings.</p>
          ) : (
            <ul>
              {outcome.findings.map((finding) => (
                <li key={finding.finding_id}>
                  <strong>{SEVERITY_LABELS[finding.severity] ?? finding.severity}</strong>
                  {finding.affected_field_or_document && ` — ${finding.affected_field_or_document}`}
                  {finding.corrective_action && <p>{finding.corrective_action}</p>}
                  {finding.override_status === "approved" && (
                    <p role="status">Override approved.</p>
                  )}
                  {finding.severity === "overrideable_blocking" &&
                    finding.override_status !== "approved" && (
                      <form onSubmit={(e) => handleOverride(finding.finding_id, e)} noValidate>
                        <FormField label="Override reason (supervisor approval required)">
                          {(fieldProps) => (
                            <input
                              {...fieldProps}
                              type="text"
                              value={overrideReason[finding.finding_id] ?? ""}
                              onChange={(e) =>
                                setOverrideReason((prev) => ({
                                  ...prev,
                                  [finding.finding_id]: e.target.value,
                                }))
                              }
                            />
                          )}
                        </FormField>
                        <button type="submit">Request override</button>
                      </form>
                    )}
                </li>
              ))}
            </ul>
          )}
        </>
      )}
    </section>
  );
}
