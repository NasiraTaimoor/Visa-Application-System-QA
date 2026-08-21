import { FormEvent, useEffect, useState } from "react";
import { Link, useParams, useSearchParams } from "react-router-dom";
import { ErrorSummary, FormField, type FieldError } from "@shared/components";
import { apiRequest } from "@shared/api/client";
import { getWorkspaceAuthToken, type Workspace } from "@shared/api/identity";

interface OcrResultResponse {
  document_id: string;
  extraction_status: string;
  extracted_fields: Record<string, string>;
  confidence_by_field: Record<string, number>;
  overall_confidence: number | null;
  warning_flags: string[];
  reviewed_values: Record<string, string>;
  reviewer_id: string | null;
}

const WARNING_THRESHOLD = 0.85;
const BLOCKING_THRESHOLD = 0.6;

interface OcrReviewPageProps {
  workspace?: Workspace;
}

// OCR review and correction screen (T078, User Story 2). Extracted values
// remain advisory (BR-003) until the user reviews, corrects, or confirms
// them here.
export function OcrReviewPage({ workspace = "applicant" }: OcrReviewPageProps) {
  const { applicationId } = useParams<{ applicationId: string }>();
  const [searchParams] = useSearchParams();
  const documentIdFromQuery = searchParams.get("document_id") ?? "";
  const [documentId, setDocumentId] = useState(documentIdFromQuery);
  const [result, setResult] = useState<OcrResultResponse | null>(null);
  const [correctedValues, setCorrectedValues] = useState<Record<string, string>>({});
  const [errors, setErrors] = useState<FieldError[]>([]);
  const [confirming, setConfirming] = useState(false);
  const [confirmed, setConfirmed] = useState(false);

  async function loadResult(id: string) {
    if (!id) return;
    try {
      const data = await apiRequest<OcrResultResponse>(`/documents/${id}/ocr`, {
        authToken: getWorkspaceAuthToken(workspace),
      });
      setResult(data);
      setCorrectedValues(data.reviewed_values);
      setErrors([]);
    } catch (error) {
      setErrors([{ fieldId: "document-id", message: (error as Error).message }]);
    }
  }

  useEffect(() => {
    if (documentIdFromQuery) loadResult(documentIdFromQuery);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [documentIdFromQuery]);

  async function handleConfirm(event: FormEvent) {
    event.preventDefault();
    if (!applicationId || !documentId) return;
    setConfirming(true);
    try {
      await apiRequest(`/applications/${applicationId}/documents/${documentId}/ocr/confirm`, {
        method: "POST",
        authToken: getWorkspaceAuthToken(workspace),
        body: {
          reviewed_values: correctedValues,
          correction_reason: "applicant reviewed extracted values",
        },
      });
      setConfirmed(true);
      setErrors([]);
    } catch (error) {
      setErrors([{ fieldId: "document-id", message: (error as Error).message }]);
    } finally {
      setConfirming(false);
    }
  }

  const belowBlocking = (result?.overall_confidence ?? 1) < BLOCKING_THRESHOLD;
  const belowWarning = (result?.overall_confidence ?? 1) < WARNING_THRESHOLD;

  return (
    <section aria-labelledby="ocr-review-heading">
      <h1 id="ocr-review-heading">Review extracted passport details</h1>
      <ErrorSummary errors={errors} />

      {!result && (
        <form
          onSubmit={(e) => {
            e.preventDefault();
            loadResult(documentId);
          }}
          noValidate
        >
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
          <button type="submit">Load OCR result</button>
        </form>
      )}

      {result && (
        <>
          <p role="status">
            Overall confidence:{" "}
            {result.overall_confidence != null
              ? `${Math.round(result.overall_confidence * 100)}%`
              : "unavailable"}
            {belowBlocking &&
              " — confidence is too low; corrected values are required before this can be used."}
            {!belowBlocking && belowWarning && " — please review carefully before confirming."}
          </p>

          {result.extraction_status !== "completed" ? (
            <p role="alert">
              Automatic extraction was unsuccessful.{" "}
              <Link to="../ocr-manual-fallback" relative="path">
                Enter passport details manually
              </Link>
              .
            </p>
          ) : (
            <form onSubmit={handleConfirm} noValidate>
              {Object.entries(result.extracted_fields).map(([field, value]) => (
                <FormField
                  key={field}
                  label={field.replace(/_/g, " ")}
                  hint={
                    result.confidence_by_field[field] != null
                      ? `Extracted with ${Math.round(result.confidence_by_field[field] * 100)}% confidence`
                      : undefined
                  }
                >
                  {(fieldProps) => (
                    <input
                      {...fieldProps}
                      type="text"
                      defaultValue={value}
                      onChange={(e) =>
                        setCorrectedValues((prev) => ({ ...prev, [field]: e.target.value }))
                      }
                    />
                  )}
                </FormField>
              ))}

              <button
                type="submit"
                disabled={
                  confirming || (belowBlocking && Object.keys(correctedValues).length === 0)
                }
              >
                {confirming ? "Confirming…" : "Confirm values"}
              </button>
            </form>
          )}

          {confirmed && <p role="status">Values confirmed. You may continue to validation.</p>}
        </>
      )}

      {applicationId && (
        <nav aria-label="Next steps">
          <Link to="../validation" relative="path">
            Continue to validation
          </Link>
        </nav>
      )}
    </section>
  );
}
