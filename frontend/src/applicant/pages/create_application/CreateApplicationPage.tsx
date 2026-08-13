import { FormEvent, useState } from "react";
import { useNavigate } from "react-router-dom";
import { FormField, ErrorSummary, type FieldError } from "@shared/components";
import { apiRequest } from "@shared/api/client";
import { getWorkspaceAuthToken } from "@shared/api/identity";

// Visa types mirror backend/src/config/policy.py PolicyConfig.visa_types.
const VISA_TYPES = ["tourist", "work", "student", "family_sponsorship", "transit"] as const;

interface CreateApplicationResponse {
  application_id: string;
  case_reference: string;
  current_status: string;
}

// Application creation screen (T050): authorized user starts a new draft
// (User Story 1, TS-FR-001/TC-FR-001).
export function CreateApplicationPage() {
  const navigate = useNavigate();
  const [visaType, setVisaType] = useState<string>(VISA_TYPES[0]);
  const [owningSubAgencyId, setOwningSubAgencyId] = useState("sub-agency-001");
  const [legalName, setLegalName] = useState("");
  const [consentGiven, setConsentGiven] = useState(false);
  const [errors, setErrors] = useState<FieldError[]>([]);
  const [submitting, setSubmitting] = useState(false);

  async function handleSubmit(event: FormEvent) {
    event.preventDefault();
    const fieldErrors: FieldError[] = [];
    if (!owningSubAgencyId.trim())
      fieldErrors.push({ fieldId: "owning-sub-agency-id", message: "Sub-agency is required" });
    if (!consentGiven)
      fieldErrors.push({
        fieldId: "consent-given",
        message: "Consent is required to create an application",
      });
    if (fieldErrors.length > 0) {
      setErrors(fieldErrors);
      return;
    }

    setSubmitting(true);
    try {
      const result = await apiRequest<CreateApplicationResponse>("/applications", {
        method: "POST",
        authToken: getWorkspaceAuthToken("applicant"),
        body: {
          visa_type: visaType,
          owning_sub_agency_id: owningSubAgencyId,
          consent_given: consentGiven,
          legal_name: legalName || undefined,
        },
      });
      navigate(`/applicant/draft/${result.application_id}`);
    } catch (error) {
      setErrors([{ fieldId: "owning-sub-agency-id", message: (error as Error).message }]);
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <section aria-labelledby="create-application-heading">
      <h1 id="create-application-heading">Start a new visa application</h1>
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

        <FormField
          label="Sub-agency"
          hint="The sub-agency responsible for reviewing and submitting this application"
          required
        >
          {(fieldProps) => (
            <input
              {...fieldProps}
              type="text"
              value={owningSubAgencyId}
              onChange={(e) => setOwningSubAgencyId(e.target.value)}
            />
          )}
        </FormField>

        <FormField label="Legal name" hint="As printed on your passport">
          {(fieldProps) => (
            <input
              {...fieldProps}
              type="text"
              value={legalName}
              onChange={(e) => setLegalName(e.target.value)}
            />
          )}
        </FormField>

        <FormField
          label="I consent to processing of my identity data for this application"
          required
        >
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
          {submitting ? "Creating…" : "Start application"}
        </button>
      </form>
    </section>
  );
}
