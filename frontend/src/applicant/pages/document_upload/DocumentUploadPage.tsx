import { FormEvent, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { ErrorSummary, FormField, type FieldError } from "@shared/components";
import { apiRequest } from "@shared/api/client";
import { getWorkspaceAuthToken, type Workspace } from "@shared/api/identity";

// Document types mirror backend/src/config/policy.py PolicyConfig.document_requirements.
const DOCUMENT_TYPES = [
  { value: "passport_bio_page", label: "Passport bio page" },
  { value: "photo", label: "Photo" },
  { value: "sponsor_letter", label: "Sponsor letter" },
  { value: "enrollment_letter", label: "Enrollment letter" },
  { value: "employment_offer", label: "Employment offer" },
] as const;

interface UploadedDocument {
  document_id: string;
  document_type: string;
  version: number;
  screening_status: string;
  ocr_triggered: boolean;
}

interface DocumentUploadPageProps {
  workspace?: Workspace;
}

// Document upload screen with boundary guidance (T077, User Story 2).
export function DocumentUploadPage({ workspace = "applicant" }: DocumentUploadPageProps) {
  const { applicationId } = useParams<{ applicationId: string }>();
  const [documentType, setDocumentType] = useState<string>(DOCUMENT_TYPES[0].value);
  const [file, setFile] = useState<File | null>(null);
  const [uploads, setUploads] = useState<UploadedDocument[]>([]);
  const [errors, setErrors] = useState<FieldError[]>([]);
  const [uploading, setUploading] = useState(false);

  async function handleUpload(event: FormEvent) {
    event.preventDefault();
    if (!applicationId) return;
    if (!file) {
      setErrors([{ fieldId: "document-file", message: "Choose a file to upload" }]);
      return;
    }
    setUploading(true);
    setErrors([]);
    try {
      const formData = new FormData();
      formData.append("document_type", documentType);
      formData.append("file", file);
      const result = await apiRequest<UploadedDocument>(
        `/applications/${applicationId}/documents`,
        {
          method: "POST",
          authToken: getWorkspaceAuthToken(workspace),
          body: formData,
        },
      );
      setUploads((prev) => [...prev, result]);
      if (result.screening_status === "rejected") {
        setErrors([
          {
            fieldId: "document-file",
            message:
              "This file did not pass document screening. Choose a replacement file to try again.",
          },
        ]);
      }
      setFile(null);
    } catch (error) {
      setErrors([{ fieldId: "document-file", message: (error as Error).message }]);
    } finally {
      setUploading(false);
    }
  }

  return (
    <section aria-labelledby="document-upload-heading">
      <h1 id="document-upload-heading">Upload documents</h1>
      <p>
        Accepted formats: PDF, JPG, PNG. Maximum size 10 MB, maximum 20 pages. Files are screened
        for security and quality before they are used.
      </p>
      <ErrorSummary errors={errors} />

      <form onSubmit={handleUpload} noValidate>
        <FormField label="Document type" required>
          {(fieldProps) => (
            <select
              {...fieldProps}
              value={documentType}
              onChange={(e) => setDocumentType(e.target.value)}
            >
              {DOCUMENT_TYPES.map((type) => (
                <option key={type.value} value={type.value}>
                  {type.label}
                </option>
              ))}
            </select>
          )}
        </FormField>

        <FormField label="File" required>
          {(fieldProps) => (
            <input
              {...fieldProps}
              type="file"
              accept=".pdf,.jpg,.jpeg,.png"
              onChange={(e) => setFile(e.target.files?.[0] ?? null)}
            />
          )}
        </FormField>

        <button type="submit" disabled={uploading}>
          {uploading ? "Uploading…" : "Upload document"}
        </button>
      </form>

      {uploads.length > 0 && (
        <section aria-labelledby="uploaded-documents-heading">
          <h2 id="uploaded-documents-heading">Uploaded documents</h2>
          <ul>
            {uploads.map((doc) => (
              <li key={doc.document_id}>
                {DOCUMENT_TYPES.find((t) => t.value === doc.document_type)?.label ??
                  doc.document_type}{" "}
                — v{doc.version} — <strong>{doc.screening_status}</strong>
                {doc.ocr_triggered && (
                  <>
                    {" "}
                    (
                    <Link to={`../ocr-review?document_id=${doc.document_id}`} relative="path">
                      review OCR results
                    </Link>
                    )
                  </>
                )}
              </li>
            ))}
          </ul>
        </section>
      )}

      {applicationId && (
        <nav aria-label="Next steps">
          <Link to={`../validation`} relative="path">
            Continue to validation
          </Link>
        </nav>
      )}
    </section>
  );
}
