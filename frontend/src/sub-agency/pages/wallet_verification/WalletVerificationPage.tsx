import { FormEvent, useState } from "react";
import { useNavigate } from "react-router-dom";
import { ErrorSummary, FormField, type FieldError } from "@shared/components";
import { apiRequest } from "@shared/api/client";
import { getWorkspaceAuthToken } from "@shared/api/identity";

interface VerifyWalletResponse {
  sufficient: boolean;
  amount: number;
  currency: string;
  reservation_reference: string | null;
  shortfall_amount: number | null;
}

// Wallet verification and shortfall screen (T098, User Story 3, AC-003, E-004).
export function WalletVerificationPage() {
  const navigate = useNavigate();
  const [applicationId, setApplicationId] = useState("");
  const [result, setResult] = useState<VerifyWalletResponse | null>(null);
  const [errors, setErrors] = useState<FieldError[]>([]);
  const [checking, setChecking] = useState(false);

  async function handleVerify(event: FormEvent) {
    event.preventDefault();
    if (!applicationId.trim()) {
      setErrors([{ fieldId: "application-id", message: "Enter the application to verify" }]);
      return;
    }
    setChecking(true);
    try {
      const response = await apiRequest<VerifyWalletResponse>(
        `/applications/${applicationId}/wallet/verify`,
        {
          method: "POST",
          authToken: getWorkspaceAuthToken("sub-agency"),
        },
      );
      setResult(response);
      setErrors([]);
    } catch (error) {
      setErrors([{ fieldId: "application-id", message: (error as Error).message }]);
    } finally {
      setChecking(false);
    }
  }

  return (
    <section aria-labelledby="wallet-verification-heading">
      <h1 id="wallet-verification-heading">Verify wallet and reserve funds</h1>
      <ErrorSummary errors={errors} />

      <form onSubmit={handleVerify} noValidate>
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
        <button type="submit" disabled={checking}>
          {checking ? "Checking…" : "Verify wallet"}
        </button>
      </form>

      {result && result.sufficient && (
        <div role="status">
          <p>
            Sufficient balance. Reserved {result.amount} {result.currency} (reference{" "}
            {result.reservation_reference}).
          </p>
          <button type="button" onClick={() => navigate(`/sub-agency/submission/${applicationId}`)}>
            Continue to submission
          </button>
        </div>
      )}

      {result && !result.sufficient && (
        <div role="alert">
          <p>
            Insufficient available balance. Short by {result.shortfall_amount} {result.currency}. No
            funds were reserved; top up the agency wallet before trying again.
          </p>
        </div>
      )}
    </section>
  );
}
