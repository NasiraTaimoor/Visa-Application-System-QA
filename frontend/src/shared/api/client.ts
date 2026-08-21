// Thin fetch wrapper shared by every workspace. Adds correlation reference,
// idempotency key (when supplied), and the mocked bearer identity token.
const API_BASE = import.meta.env.VITE_API_BASE_URL ?? "/api/v1";

export interface ApiOptions {
  method?: "GET" | "POST" | "PATCH" | "DELETE";
  body?: unknown;
  idempotencyKey?: string;
  authToken?: string;
}

export async function apiRequest<T>(path: string, options: ApiOptions = {}): Promise<T> {
  const isFormData = options.body instanceof FormData;
  const headers: Record<string, string> = isFormData ? {} : { "Content-Type": "application/json" };
  if (options.authToken) headers["Authorization"] = `Bearer ${options.authToken}`;
  if (options.idempotencyKey) headers["Idempotency-Key"] = options.idempotencyKey;

  const response = await fetch(`${API_BASE}${path}`, {
    method: options.method ?? "GET",
    headers,
    body: isFormData
      ? (options.body as FormData)
      : options.body
        ? JSON.stringify(options.body)
        : undefined,
  });

  if (!response.ok) {
    const problem = await response.json().catch(() => ({ message: response.statusText }));
    throw new Error(problem.message ?? "Request failed");
  }
  return (await response.json()) as T;
}
