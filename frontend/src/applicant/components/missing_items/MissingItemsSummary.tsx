const LABELS: Record<string, string> = {
  "applicant.legal_name": "Legal name",
  "applicant.date_of_birth": "Date of birth",
  "applicant.nationality": "Nationality",
  "passport.passport_number": "Passport number",
  "passport.issuing_country": "Passport issuing country",
  "passport.issue_date": "Passport issue date",
  "passport.expiry_date": "Passport expiry date",
  "consent.applicant_identity_data": "Consent to process applicant identity data",
};

function describe(item: string): string {
  if (LABELS[item]) return LABELS[item];
  if (item.startsWith("document.")) {
    return `Upload required document: ${item.slice("document.".length).replace(/_/g, " ")}`;
  }
  return item;
}

interface MissingItemsSummaryProps {
  missingItems: string[];
}

// Missing-items summary (T052): tells the applicant what remains before the
// application can be considered complete, per FR-004 / AC-001.
export function MissingItemsSummary({ missingItems }: MissingItemsSummaryProps) {
  if (missingItems.length === 0) {
    return (
      <p role="status" className="missing-items-complete">
        All required information is complete. You may continue to document upload.
      </p>
    );
  }

  return (
    <section aria-labelledby="missing-items-heading" className="missing-items-summary">
      <h2 id="missing-items-heading">Before you can submit ({missingItems.length} remaining)</h2>
      <ul>
        {missingItems.map((item) => (
          <li key={item}>{describe(item)}</li>
        ))}
      </ul>
    </section>
  );
}
