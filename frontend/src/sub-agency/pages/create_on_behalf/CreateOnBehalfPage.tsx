import { FormEvent, useState } from "react";
import { useNavigate } from "react-router-dom";
import { FormField, ErrorSummary, type FieldError } from "@shared/components";
import { apiRequest } from "@shared/api/client";
import { getWorkspaceAuthToken } from "@shared/api/identity";

const VISA_TYPES = ["tourist", "work", "student", "family_sponsorship", "transit"] as const;

interface CreateApplicationResponse {
  application_id: string;
  case_reference: string;
}

// Sub-agency intake-on-behalf entry point (T054): a sub-agency officer
// creates a draft for an applicant within their own agency scope. Reuses the
// same Create application command as T050; the officer's agency is fixed
// (not user-editable) since cross-agency creation is denied server-side.
export function CreateOnBehalfPage() {
  const navigate = useNavigate();
  const owningSubAgencyId = "sub-agency-001"; // matches u-subagency-1's agency_id fixture
  const [visaType, setVisaType] = useState<string>(VISA_TYPES[0]);
  const [applicantLegalName, setApplicantLegalName] = useState("");
  const [consentGiven, setConsentGiven] = useState(false);
  const [errors, setErrors] = useState<FieldError[]>([]);
  const [submitting, setSubmitting] = useState(false);

  async function handleSubmit(event: FormEvent) {
    event.preventDefault();
    if (!consentGiven) {
      setErrors([
        {
          fieldId: "consent-given",
          message: "Applicant consent must be recorded before creating a case",
        },
      ]);
      return;
    }
    setSubmitting(true);
    try {
      const result = await apiRequest<CreateApplicationResponse>("/applications", {
        method: "POST",
        authToken: getWorkspaceAuthToken("sub-agency"),
        body: {
          visa_type: visaType,
          owning_sub_agency_id: owningSubAgencyId,
          consent_given: consentGiven,
          legal_name: applicantLegalName || undefined,
        },
      });
      navigate(`/sub-agency/draft/${result.application_id}`);
    } catch (error) {
      setErrors([{ fieldId: "consent-given", message: (error as Error).message }]);
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <section aria-labelledby="create-on-behalf-heading">
      <h1 id="create-on-behalf-heading">Create application on behalf of an applicant</h1>
      <p>Agency scope: {owningSubAgencyId}</p>
      <ErrorSummary errors={errors} />
      <form onSubmit={handleSubmit} noValidate>
        <FormField label="Visa type" required>
          {(fieldProps) => (
            <select {...fieldProps} value={visaType} onChange={(e) => setVisaType(e.target.value)}>
              {VISA_TYPES.map((type) => (
                <option key={type} value={type}>
                  {type.replace(/_/g, " ")}
                </option>
              ))}
            </select>
          )}
        </FormField>

        <FormField label="Applicant legal name" hint="As printed on the applicant's passport">
          {(fieldProps) => (
            <input
              {...fieldProps}
              type="text"
              value={applicantLegalName}
              onChange={(e) => setApplicantLegalName(e.target.value)}
            />
          )}
        </FormField>

        <FormField label="Applicant consent to process identity data has been obtained" required>
          {(fieldProps) => (
            <input
              {...fieldProps}
              type="checkbox"
              checked={consentGiven}
              onChange={(e) => setConsentGiven(e.target.checked)}
            />
          )}
        </FormField>

        <button type="submit" disabled={submitting}>
          {submitting ? "Creating…" : "Create case"}
        </button>
      </form>
    </section>
  );
}
