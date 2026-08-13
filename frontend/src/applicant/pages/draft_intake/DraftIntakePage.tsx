import { FormEvent, useCallback, useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { FormField, ErrorSummary, type FieldError } from "@shared/components";
import { MissingItemsSummary } from "../../components/missing_items/MissingItemsSummary";
import { apiRequest } from "@shared/api/client";
import { getWorkspaceAuthToken, type Workspace } from "@shared/api/identity";

interface ResumeResponse {
  application_id: string;
  case_reference: string;
  current_status: string;
  current_version: number;
  visa_type: string;
  applicant: {
    legal_name: string | null;
    nationality: string | null;
    date_of_birth: string | null;
  };
  missing_items: string[];
}

interface UpdateIntakeResponse {
  application_id: string;
  current_version: number;
  missing_items: string[];
}

interface DraftIntakePageProps {
  /** Which mocked identity/workspace is editing this draft (T054 reuses this page for sub-agency intake-on-behalf). */
  workspace?: Workspace;
  /** Base path used to build the "continue" links to document upload etc. */
  basePath?: string;
}

// Draft intake form (T051): applicant/contact/passport fields with save,
// resume, and missing-item guidance (User Story 1, TS-FR-001-004).
export function DraftIntakePage({
  workspace = "applicant",
  basePath = "/applicant",
}: DraftIntakePageProps) {
  const { applicationId } = useParams<{ applicationId: string }>();
  const [loading, setLoading] = useState(true);
  const [caseReference, setCaseReference] = useState("");
  const [status, setStatus] = useState("");
  const [version, setVersion] = useState(1);
  const [missingItems, setMissingItems] = useState<string[]>([]);
  const [legalName, setLegalName] = useState("");
  const [dateOfBirth, setDateOfBirth] = useState("");
  const [nationality, setNationality] = useState("");
  const [passportNumber, setPassportNumber] = useState("");
  const [issuingCountry, setIssuingCountry] = useState("");
  const [issueDate, setIssueDate] = useState("");
  const [expiryDate, setExpiryDate] = useState("");
  const [errors, setErrors] = useState<FieldError[]>([]);
  const [saving, setSaving] = useState(false);
  const [savedMessage, setSavedMessage] = useState("");

  const authToken = getWorkspaceAuthToken(workspace);

  const loadDraft = useCallback(async () => {
    if (!applicationId) return;
    setLoading(true);
    try {
      const draft = await apiRequest<ResumeResponse>(`/applications/${applicationId}/resume`, {
        authToken,
      });
      setCaseReference(draft.case_reference);
      setStatus(draft.current_status);
      setVersion(draft.current_version);
      setMissingItems(draft.missing_items);
      setLegalName(draft.applicant.legal_name ?? "");
      setNationality(draft.applicant.nationality ?? "");
      setDateOfBirth(draft.applicant.date_of_birth ?? "");
    } catch (error) {
      setErrors([{ fieldId: "legal-name", message: (error as Error).message }]);
    } finally {
      setLoading(false);
    }
  }, [applicationId, authToken]);

  useEffect(() => {
    loadDraft();
  }, [loadDraft]);

  async function handleSave(event: FormEvent) {
    event.preventDefault();
    if (!applicationId) return;
    setSaving(true);
    setSavedMessage("");
    try {
      const result = await apiRequest<UpdateIntakeResponse>(`/applications/${applicationId}`, {
        method: "PATCH",
        authToken,
        body: {
          expected_version: version,
          applicant_fields: { legal_name: legalName, date_of_birth: dateOfBirth, nationality },
          passport_fields: {
            passport_number: passportNumber,
            issuing_country: issuingCountry,
            issue_date: issueDate,
            expiry_date: expiryDate,
          },
        },
      });
      setVersion(result.current_version);
      setMissingItems(result.missing_items);
      setErrors([]);
      setSavedMessage("Progress saved.");
    } catch (error) {
      setErrors([{ fieldId: "legal-name", message: (error as Error).message }]);
      // The saved version may now be stale (concurrent edit, E-010); reload the authoritative state.
      await loadDraft();
    } finally {
      setSaving(false);
    }
  }

  if (loading) return <p role="status">Loading draft…</p>;

  return (
    <section aria-labelledby="draft-intake-heading">
      <h1 id="draft-intake-heading">Application {caseReference || applicationId}</h1>
      <p>
        Status: <strong>{status.replace(/_/g, " ")}</strong>
      </p>
      <ErrorSummary errors={errors} />
      {savedMessage && <p role="status">{savedMessage}</p>}

      <form onSubmit={handleSave} noValidate>
        <fieldset>
          <legend>Applicant details</legend>
          <FormField label="Legal name" required>
            {(fieldProps) => (
              <input
                {...fieldProps}
                type="text"
                value={legalName}
                onChange={(e) => setLegalName(e.target.value)}
              />
            )}
          </FormField>
          <FormField label="Date of birth" hint="YYYY-MM-DD" required>
            {(fieldProps) => (
              <input
                {...fieldProps}
                type="date"
                value={dateOfBirth}
                onChange={(e) => setDateOfBirth(e.target.value)}
              />
            )}
          </FormField>
          <FormField label="Nationality" required>
            {(fieldProps) => (
              <input
                {...fieldProps}
                type="text"
                value={nationality}
                onChange={(e) => setNationality(e.target.value)}
              />
            )}
          </FormField>
        </fieldset>

        <fieldset>
          <legend>Passport details</legend>
          <FormField label="Passport number" required>
            {(fieldProps) => (
              <input
                {...fieldProps}
                type="text"
                value={passportNumber}
                onChange={(e) => setPassportNumber(e.target.value)}
              />
            )}
          </FormField>
          <FormField label="Issuing country" required>
            {(fieldProps) => (
              <input
                {...fieldProps}
                type="text"
                value={issuingCountry}
                onChange={(e) => setIssuingCountry(e.target.value)}
              />
            )}
          </FormField>
          <FormField label="Issue date" hint="YYYY-MM-DD" required>
            {(fieldProps) => (
              <input
                {...fieldProps}
                type="date"
                value={issueDate}
                onChange={(e) => setIssueDate(e.target.value)}
              />
            )}
          </FormField>
          <FormField label="Expiry date" hint="YYYY-MM-DD" required>
            {(fieldProps) => (
              <input
                {...fieldProps}
                type="date"
                value={expiryDate}
                onChange={(e) => setExpiryDate(e.target.value)}
              />
            )}
          </FormField>
        </fieldset>

        <button type="submit" disabled={saving}>
          {saving ? "Saving…" : "Save progress"}
        </button>
      </form>

      <MissingItemsSummary missingItems={missingItems} />

      {applicationId && (
        <nav aria-label="Next steps">
          <Link to={`${basePath}/draft/${applicationId}/documents`}>
            Continue to document upload
          </Link>
        </nav>
      )}
    </section>
  );
}
