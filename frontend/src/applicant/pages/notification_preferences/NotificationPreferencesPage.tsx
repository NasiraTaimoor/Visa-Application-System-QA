import { FormEvent, useState } from "react";
import { ErrorSummary, FormField, type FieldError } from "@shared/components";
import { apiRequest } from "@shared/api/client";
import { getWorkspaceAuthToken } from "@shared/api/identity";

const OPTIONAL_EVENTS = [
  { value: "submission_created", label: "Submission created" },
  { value: "validation_failed", label: "Validation issue found" },
  { value: "gdrfa_response", label: "GDRFA response received" },
  { value: "immigration_event", label: "Immigration processing update" },
] as const;

const MANDATORY_EVENTS = ["correction_requested", "wallet_shortfall", "final_decision"];

interface PreferenceResponse {
  channel: string;
  opted_out_events: string[];
}

// Notification preferences screen (T153, User Story 6, FR-027). Mandatory
// operational/legal notices cannot be opted out of.
export function NotificationPreferencesPage() {
  const [applicationId, setApplicationId] = useState("");
  const [channel, setChannel] = useState("email");
  const [optedOut, setOptedOut] = useState<string[]>([]);
  const [saved, setSaved] = useState<PreferenceResponse | null>(null);
  const [errors, setErrors] = useState<FieldError[]>([]);
  const [saving, setSaving] = useState(false);

  function toggleEvent(event: string) {
    setOptedOut((prev) =>
      prev.includes(event) ? prev.filter((e) => e !== event) : [...prev, event],
    );
  }

  async function handleSave(event: FormEvent) {
    event.preventDefault();
    if (!applicationId.trim()) {
      setErrors([{ fieldId: "application-id", message: "Enter your application ID" }]);
      return;
    }
    setSaving(true);
    try {
      const response = await apiRequest<PreferenceResponse>(
        `/applications/${applicationId}/notification-preferences`,
        {
          method: "POST",
          authToken: getWorkspaceAuthToken("applicant"),
          body: { channel, opted_out_events: optedOut },
        },
      );
      setSaved(response);
      setErrors([]);
    } catch (error) {
      setErrors([{ fieldId: "application-id", message: (error as Error).message }]);
    } finally {
      setSaving(false);
    }
  }

  return (
    <section aria-labelledby="notification-preferences-heading">
      <h1 id="notification-preferences-heading">Notification preferences</h1>
      <p>Optional channel preferences; mandatory notices always continue.</p>
      <ErrorSummary errors={errors} />

      <form onSubmit={handleSave} noValidate>
        <FormField label="Application ID" required>
          {(fieldProps) => (
            <input
              {...fieldProps}
              type="text"
              value={applicationId}
              onChange={(e) => setApplicationId(e.target.value)}
            />
          )}
        </FormField>

        <FormField label="Preferred channel">
          {(fieldProps) => (
            <select {...fieldProps} value={channel} onChange={(e) => setChannel(e.target.value)}>
              <option value="email">Email</option>
              <option value="sms">SMS</option>
            </select>
          )}
        </FormField>

        <fieldset>
          <legend>Optional notifications (uncheck to opt out)</legend>
          {OPTIONAL_EVENTS.map((event) => (
            <label key={event.value}>
              <input
                type="checkbox"
                checked={!optedOut.includes(event.value)}
                onChange={() => toggleEvent(event.value)}
              />
              {event.label}
            </label>
          ))}
        </fieldset>

        <fieldset>
          <legend>Mandatory notifications (always sent)</legend>
          <ul>
            {MANDATORY_EVENTS.map((event) => (
              <li key={event}>{event.replace(/_/g, " ")}</li>
            ))}
          </ul>
        </fieldset>

        <button type="submit" disabled={saving}>
          {saving ? "Saving…" : "Save preferences"}
        </button>
      </form>

      {saved && <p role="status">Preferences saved. Channel: {saved.channel}.</p>}
    </section>
  );
}
