import { FormEvent, useState } from "react";
import { ErrorSummary, FormField, type FieldError } from "@shared/components";
import { apiRequest } from "@shared/api/client";
import { getWorkspaceAuthToken } from "@shared/api/identity";

interface PaymentEventResponse {
  payment_state: string;
  current_status: string;
  reason: string | null;
}

interface ReconciliationResponse {
  application_id: string;
  current_status: string;
}

// Finance payment queue and reconciliation screen (T138, User Story 5).
export function PaymentQueuePage() {
  const [applicationId, setApplicationId] = useState("");
  const [confirmResult, setConfirmResult] = useState<PaymentEventResponse | null>(null);
  const [receiptReference, setReceiptReference] = useState("");
  const [amount, setAmount] = useState("");
  const [currency, setCurrency] = useState("AED");
  const [reconcileReason, setReconcileReason] = useState("");
  const [reconcileResult, setReconcileResult] = useState<ReconciliationResponse | null>(null);
  const [errors, setErrors] = useState<FieldError[]>([]);
  const [busy, setBusy] = useState(false);

  async function handleConfirm(event: FormEvent) {
    event.preventDefault();
    if (!applicationId.trim()) {
      setErrors([
        { fieldId: "application-id", message: "Enter the application to confirm payment for" },
      ]);
      return;
    }
    setBusy(true);
    try {
      const response = await apiRequest<PaymentEventResponse>(
        `/applications/${applicationId}/payment/confirm`,
        {
          method: "POST",
          authToken: getWorkspaceAuthToken("finance"),
        },
      );
      setConfirmResult(response);
      setErrors([]);
    } catch (error) {
      setErrors([{ fieldId: "application-id", message: (error as Error).message }]);
    } finally {
      setBusy(false);
    }
  }

  async function handleReconcile(event: FormEvent) {
    event.preventDefault();
    if (!applicationId.trim() || !reconcileReason.trim()) {
      setErrors([
        {
          fieldId: "reconcile-reason",
          message: "Application ID and a reconciliation reason are required",
        },
      ]);
      return;
    }
    setBusy(true);
    try {
      const response = await apiRequest<ReconciliationResponse>(
        `/applications/${applicationId}/payment/reconcile`,
        {
          method: "POST",
          authToken: getWorkspaceAuthToken("finance"),
          body: {
            receipt_reference: receiptReference,
            amount: Number(amount),
            currency,
            reason: reconcileReason,
          },
        },
      );
      setReconcileResult(response);
      setErrors([]);
    } catch (error) {
      setErrors([{ fieldId: "reconcile-reason", message: (error as Error).message }]);
    } finally {
      setBusy(false);
    }
  }

  return (
    <section aria-labelledby="payment-queue-heading">
      <h1 id="payment-queue-heading">Payment queue</h1>
      <ErrorSummary errors={errors} />

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

      <form onSubmit={handleConfirm} noValidate>
        <button type="submit" disabled={busy}>
          Confirm payment (provider callback)
        </button>
      </form>
      {confirmResult && (
        <p role="status">
          Payment state: <strong>{confirmResult.payment_state}</strong>. Case status:{" "}
          {confirmResult.current_status.replace(/_/g, " ")}.
        </p>
      )}

      <form onSubmit={handleReconcile} noValidate>
        <h2>Manual reconciliation</h2>
        <FormField label="Receipt reference" required>
          {(fieldProps) => (
            <input
              {...fieldProps}
              type="text"
              value={receiptReference}
              onChange={(e) => setReceiptReference(e.target.value)}
            />
          )}
        </FormField>
        <FormField label="Amount" required>
          {(fieldProps) => (
            <input
              {...fieldProps}
              type="number"
              value={amount}
              onChange={(e) => setAmount(e.target.value)}
            />
          )}
        </FormField>
        <FormField label="Currency" required>
          {(fieldProps) => (
            <input
              {...fieldProps}
              type="text"
              value={currency}
              onChange={(e) => setCurrency(e.target.value)}
            />
          )}
        </FormField>
        <FormField label="Reason" required>
          {(fieldProps) => (
            <input
              {...fieldProps}
              type="text"
              value={reconcileReason}
              onChange={(e) => setReconcileReason(e.target.value)}
            />
          )}
        </FormField>
        <button type="submit" disabled={busy}>
          Record manual reconciliation
        </button>
      </form>
      {reconcileResult && (
        <p role="status">
          Reconciled. Case status: {reconcileResult.current_status.replace(/_/g, " ")}.
        </p>
      )}
    </section>
  );
}
