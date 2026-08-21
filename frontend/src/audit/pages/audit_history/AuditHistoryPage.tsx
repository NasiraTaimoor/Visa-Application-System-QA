import { FormEvent, useState } from "react";
import { ErrorSummary, FormField, type FieldError } from "@shared/components";
import { apiRequest } from "@shared/api/client";
import { getWorkspaceAuthToken } from "@shared/api/identity";

interface AuditEventView {
  audit_event_id: string;
  actor_or_service_id: string;
  role: string;
  timestamp: string;
  action: string;
  affected_case_or_record: string;
  outcome: string;
  reason: string | null;
  correlation_reference: string;
}

// Audit history and lifecycle timeline screen (T168, User Story 7, FR-029/FR-032).
export function AuditHistoryPage() {
  const [applicationId, setApplicationId] = useState("");
  const [events, setEvents] = useState<AuditEventView[]>([]);
  const [errors, setErrors] = useState<FieldError[]>([]);
  const [loading, setLoading] = useState(false);

  async function handleSearch(event: FormEvent) {
    event.preventDefault();
    setLoading(true);
    try {
      const query = applicationId.trim()
        ? `?application_id=${encodeURIComponent(applicationId)}`
        : "";
      const response = await apiRequest<{ events: AuditEventView[] }>(`/audit/events${query}`, {
        authToken: getWorkspaceAuthToken("audit"),
      });
      setEvents(response.events);
      setErrors([]);
    } catch (error) {
      setErrors([{ fieldId: "application-id", message: (error as Error).message }]);
    } finally {
      setLoading(false);
    }
  }

  return (
    <section aria-labelledby="audit-history-heading">
      <h1 id="audit-history-heading">Audit history</h1>
      <ErrorSummary errors={errors} />

      <form onSubmit={handleSearch} noValidate>
        <FormField label="Application ID" hint="Leave blank to search all cases">
          {(fieldProps) => (
            <input
              {...fieldProps}
              type="text"
              value={applicationId}
              onChange={(e) => setApplicationId(e.target.value)}
            />
          )}
        </FormField>
        <button type="submit" disabled={loading}>
          {loading ? "Searching…" : "Search audit history"}
        </button>
      </form>

      {events.length > 0 && (
        <table>
          <caption>Audit events in chronological order</caption>
          <thead>
            <tr>
              <th scope="col">Timestamp</th>
              <th scope="col">Actor</th>
              <th scope="col">Action</th>
              <th scope="col">Outcome</th>
              <th scope="col">Reason</th>
            </tr>
          </thead>
          <tbody>
            {events.map((event) => (
              <tr key={event.audit_event_id}>
                <td>{new Date(event.timestamp).toLocaleString()}</td>
                <td>
                  {event.actor_or_service_id} ({event.role})
                </td>
                <td>{event.action}</td>
                <td>{event.outcome}</td>
                <td>{event.reason ?? "—"}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </section>
  );
}
