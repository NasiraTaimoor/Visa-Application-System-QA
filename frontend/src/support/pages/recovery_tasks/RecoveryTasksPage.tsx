import { FormEvent, useState } from "react";
import { ErrorSummary, FormField, type FieldError } from "@shared/components";
import { apiRequest } from "@shared/api/client";
import { getWorkspaceAuthToken } from "@shared/api/identity";

interface RecoveryTask {
  task_id: string;
  application_id: string;
  task_type: string;
  assigned_role: string;
  status: string;
  reason: string | null;
}

interface MaskedCaseSummary {
  application_id: string;
  case_reference: string;
  current_status: string;
  applicant_legal_name_masked: string | null;
}

// Support recovery task and masked case lookup screen (T170, User Story 7,
// BR-035).
export function RecoveryTasksPage() {
  const [tasks, setTasks] = useState<RecoveryTask[]>([]);
  const [lookupApplicationId, setLookupApplicationId] = useState("");
  const [lookupReason, setLookupReason] = useState("");
  const [caseSummary, setCaseSummary] = useState<MaskedCaseSummary | null>(null);
  const [errors, setErrors] = useState<FieldError[]>([]);
  const [busy, setBusy] = useState(false);

  async function loadTasks() {
    setBusy(true);
    try {
      const response = await apiRequest<{ tasks: RecoveryTask[] }>("/recovery/tasks", {
        authToken: getWorkspaceAuthToken("support"),
      });
      setTasks(response.tasks);
      setErrors([]);
    } catch (error) {
      setErrors([{ fieldId: "lookup-reason", message: (error as Error).message }]);
    } finally {
      setBusy(false);
    }
  }

  async function handleResolve(taskId: string) {
    const reason = window.prompt("Business reason for resolving this recovery task:");
    if (!reason) return;
    try {
      await apiRequest(`/recovery/tasks/${taskId}/resolve`, {
        method: "POST",
        authToken: getWorkspaceAuthToken("support"),
        body: { business_reason: reason },
      });
      await loadTasks();
    } catch (error) {
      setErrors([{ fieldId: "lookup-reason", message: (error as Error).message }]);
    }
  }

  async function handleLookup(event: FormEvent) {
    event.preventDefault();
    if (!lookupApplicationId.trim() || !lookupReason.trim()) {
      setErrors([
        { fieldId: "lookup-reason", message: "Application ID and a business reason are required" },
      ]);
      return;
    }
    setBusy(true);
    try {
      const response = await apiRequest<MaskedCaseSummary>(
        `/support/cases/${lookupApplicationId}/access`,
        {
          method: "POST",
          authToken: getWorkspaceAuthToken("support"),
          body: { business_reason: lookupReason },
        },
      );
      setCaseSummary(response);
      setErrors([]);
    } catch (error) {
      setErrors([{ fieldId: "lookup-reason", message: (error as Error).message }]);
    } finally {
      setBusy(false);
    }
  }

  return (
    <section aria-labelledby="recovery-tasks-heading">
      <h1 id="recovery-tasks-heading">Recovery tasks</h1>
      <ErrorSummary errors={errors} />

      <button type="button" onClick={loadTasks} disabled={busy}>
        Load open recovery tasks
      </button>
      {tasks.length > 0 && (
        <ul>
          {tasks.map((task) => (
            <li key={task.task_id}>
              {task.task_type} for {task.application_id} ({task.assigned_role})
              {task.reason && ` — ${task.reason}`}{" "}
              <button type="button" onClick={() => handleResolve(task.task_id)}>
                Resolve
              </button>
            </li>
          ))}
        </ul>
      )}

      <form onSubmit={handleLookup} noValidate>
        <h2>Masked case lookup</h2>
        <FormField label="Application ID" required>
          {(fieldProps) => (
            <input
              {...fieldProps}
              type="text"
              value={lookupApplicationId}
              onChange={(e) => setLookupApplicationId(e.target.value)}
            />
          )}
        </FormField>
        <FormField label="Business reason" required>
          {(fieldProps) => (
            <input
              {...fieldProps}
              type="text"
              value={lookupReason}
              onChange={(e) => setLookupReason(e.target.value)}
            />
          )}
        </FormField>
        <button type="submit" disabled={busy}>
          Look up case
        </button>
      </form>

      {caseSummary && (
        <p role="status">
          Case {caseSummary.case_reference} ({caseSummary.applicant_legal_name_masked}): status{" "}
          {caseSummary.current_status.replace(/_/g, " ")}.
        </p>
      )}
    </section>
  );
}
