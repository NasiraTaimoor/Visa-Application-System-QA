import { FormEvent, useState } from "react";
import { useParams, useSearchParams } from "react-router-dom";
import { ErrorSummary, FormField, type FieldError } from "@shared/components";
import { apiRequest } from "@shared/api/client";
import { getWorkspaceAuthToken, type Workspace } from "@shared/api/identity";

interface OcrManualFallbackPageProps {
  workspace?: Workspace;
}

// Accessible manual fallback for unavailable/unusable OCR (T080, User Story
// 2, E-018). Lets the user enter passport values by hand when automatic
// extraction fails, keeping the case editable rather than blocked.
export function OcrManualFallbackPage({ workspace = "applicant" }: OcrManualFallbackPageProps) {
  const { applicationId } = useParams<{ applicationId: string }>();
  const [searchParams] = useSearchParams();
  const [documentId, setDocumentId] = useState(searchParams.get("document_id") ?? "");
  const [passportNumber, setPassportNumber] = useState("");
  const [dateOfBirth, setDateOfBirth] = useState("");
  const [nationality, setNationality] = useState("");
  const [expiryDate, setExpiryDate] = useState("");
  const [errors, setErrors] = useState<FieldError[]>([]);
  const [submitting, setSubmitting] = useState(false);
  const [submitted, setSubmitted] = useState(false);

  async function handleSubmit(event: FormEvent) {
    event.preventDefault();
    if (!applicationId || !documentId) {
      setErrors([{ fieldId: "document-id", message: "Document ID is required" }]);
      return;
    }
    setSubmitting(true);
    try {
      await apiRequest(`/applications/${applicationId}/documents/${documentId}/ocr/confirm`, {
        method: "POST",
        authToken: getWorkspaceAuthToken(workspace),
        body: {
          reviewed_values: {
            passport_number: passportNumber,
            date_of_birth: dateOfBirth,
            nationality,
            expiry_date: expiryDate,
          },
          correction_reason: "manual entry: automatic extraction was unavailable or unusable",
        },
      });
      setSubmitted(true);
      setErrors([]);
    } catch (error) {
      setErrors([{ fieldId: "document-id", message: (error as Error).message }]);
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <section aria-labelledby="ocr-manual-fallback-heading">
      <h1 id="ocr-manual-fallback-heading">Enter passport details manually</h1>
      <p>
        Automatic extraction was unavailable or could not read this document. Enter the details by
        hand instead.
      </p>
      <ErrorSummary errors={errors} />

      <form onSubmit={handleSubmit} noValidate>
        <FormField label="Document ID" required>
          {(fieldProps) => (
            <input
              {...fieldProps}
              type="text"
              value={documentId}
              onChange={(e) => setDocumentId(e.target.value)}
            />
          )}
        </FormField>
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
        <FormField label="Passport expiry date" hint="YYYY-MM-DD" required>
          {(fieldProps) => (
            <input
              {...fieldProps}
              type="date"
              value={expiryDate}
              onChange={(e) => setExpiryDate(e.target.value)}
            />
          )}
        </FormField>

        <button type="submit" disabled={submitting}>
          {submitting ? "Saving…" : "Save manual entry"}
        </button>
      </form>

      {submitted && (
        <p role="status">Manually entered values saved. You may continue to validation.</p>
      )}
    </section>
  );
}
