import { FormEvent, useState } from "react";
import { ErrorSummary, FormField, type FieldError } from "@shared/components";
import { apiRequest } from "@shared/api/client";
import { getWorkspaceAuthToken } from "@shared/api/identity";

interface ExportResponse {
  export_reference: string;
  record_count: number;
}

// Export filters and retention/legal-hold view (T169, User Story 7, FR-032).
export function ExportCompliancePage() {
  const [applicationId, setApplicationId] = useState("");
  const [businessReason, setBusinessReason] = useState("");
  const [result, setResult] = useState<ExportResponse | null>(null);
  const [errors, setErrors] = useState<FieldError[]>([]);
  const [exporting, setExporting] = useState(false);

  async function handleExport(event: FormEvent) {
    event.preventDefault();
    if (!businessReason.trim()) {
      setErrors([
        {
          fieldId: "business-reason",
          message: "A business reason is required for compliance export",
        },
      ]);
      return;
    }
    setExporting(true);
    try {
      const response = await apiRequest<ExportResponse>("/audit/export", {
        method: "POST",
        authToken: getWorkspaceAuthToken("audit"),
        body: { application_id: applicationId || undefined, business_reason: businessReason },
      });
      setResult(response);
      setErrors([]);
    } catch (error) {
      setErrors([{ fieldId: "business-reason", message: (error as Error).message }]);
    } finally {
      setExporting(false);
    }
  }

  return (
    <section aria-labelledby="export-compliance-heading">
      <h1 id="export-compliance-heading">Export and compliance</h1>
      <p>Exports are audited and scoped to your authorized business need.</p>
      <ErrorSummary errors={errors} />

      <form onSubmit={handleExport} noValidate>
        <FormField label="Application ID" hint="Leave blank to export across all authorized cases">
          {(fieldProps) => (
            <input
              {...fieldProps}
              type="text"
              value={applicationId}
              onChange={(e) => setApplicationId(e.target.value)}
            />
          )}
        </FormField>
        <FormField label="Business reason" required>
          {(fieldProps) => (
            <input
              {...fieldProps}
              type="text"
              value={businessReason}
              onChange={(e) => setBusinessReason(e.target.value)}
            />
          )}
        </FormField>
        <button type="submit" disabled={exporting}>
          {exporting ? "Exporting…" : "Export records"}
        </button>
      </form>

      {result && (
        <p role="status">
          Export <strong>{result.export_reference}</strong> created with {result.record_count}{" "}
          record(s).
        </p>
      )}
    </section>
  );
}
