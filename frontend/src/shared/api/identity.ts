// Mock bearer tokens matching backend/tests/fixtures/integrations/identity_provider.json
// (T013 mock identity provider). Real environments replace this with an
// authenticated session/token from the IdP; workspaces stay unaware of the
// difference because apiRequest only needs a bearer string.
export type Workspace =
  "applicant" | "sub-agency" | "main-agency" | "finance" | "support" | "audit";

const WORKSPACE_TOKENS: Record<Workspace, string> = {
  applicant: "u-applicant-1",
  "sub-agency": "u-subagency-1",
  "main-agency": "u-mainagency-1",
  finance: "u-finance-1",
  support: "u-support-1",
  audit: "u-audit-1",
};

export function getWorkspaceAuthToken(workspace: Workspace): string {
  return WORKSPACE_TOKENS[workspace];
}
