import { useEffect, useRef } from "react";

export interface FieldError {
  fieldId: string;
  message: string;
}

interface ErrorSummaryProps {
  errors: FieldError[];
}

// Focus-managed error summary (T029): moves focus to the summary on error so
// keyboard and screen-reader users are not left without feedback.
export function ErrorSummary({ errors }: ErrorSummaryProps) {
  const ref = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (errors.length > 0) ref.current?.focus();
  }, [errors]);

  if (errors.length === 0) return null;

  return (
    <div
      ref={ref}
      tabIndex={-1}
      role="alert"
      className="error-summary"
      aria-labelledby="error-summary-heading"
    >
      <h2 id="error-summary-heading">There is a problem</h2>
      <ul>
        {errors.map((e) => (
          <li key={e.fieldId}>
            <a href={`#${e.fieldId}`}>{e.message}</a>
          </li>
        ))}
      </ul>
    </div>
  );
}
