import { Navigate, Route, Routes } from "react-router-dom";
import { AppShell } from "@shared/layout/AppShell";

import { CreateApplicationPage } from "./applicant/pages/create_application/CreateApplicationPage";
import { DraftIntakePage } from "./applicant/pages/draft_intake/DraftIntakePage";
import { SessionRecoveryPage } from "./applicant/pages/session_recovery/SessionRecoveryPage";
import { DocumentUploadPage } from "./applicant/pages/document_upload/DocumentUploadPage";
import { OcrReviewPage } from "./applicant/pages/ocr_review/OcrReviewPage";
import { OcrManualFallbackPage } from "./applicant/pages/ocr_manual_fallback/OcrManualFallbackPage";
import { ValidationFindingsPage } from "./applicant/pages/validation_findings/ValidationFindingsPage";
import { FinalOutcomePage } from "./applicant/pages/final_outcome/FinalOutcomePage";
import { NotificationPreferencesPage } from "./applicant/pages/notification_preferences/NotificationPreferencesPage";

import { CreateOnBehalfPage } from "./sub-agency/pages/create_on_behalf/CreateOnBehalfPage";
import { WalletVerificationPage } from "./sub-agency/pages/wallet_verification/WalletVerificationPage";
import { SubmissionConfirmationPage } from "./sub-agency/pages/submission_confirmation/SubmissionConfirmationPage";

import { CaseQueuePage } from "./main-agency/pages/case_queue/CaseQueuePage";
import { CaseReviewPage } from "./main-agency/pages/case_review/CaseReviewPage";
import { GdrfaSubmissionPage } from "./main-agency/pages/gdrfa_submission/GdrfaSubmissionPage";

import { PaymentQueuePage } from "./finance/pages/payment_queue/PaymentQueuePage";

import { RecoveryTasksPage } from "./support/pages/recovery_tasks/RecoveryTasksPage";

import { AuditHistoryPage } from "./audit/pages/audit_history/AuditHistoryPage";
import { ExportCompliancePage } from "./audit/pages/export_compliance/ExportCompliancePage";

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<Navigate to="/applicant" replace />} />

      <Route
        path="/applicant"
        element={
          <AppShell
            workspaceName="Applicant"
            navItems={[
              { to: "/applicant", label: "New Application" },
              { to: "/applicant/notifications", label: "Notification Preferences" },
            ]}
          />
        }
      >
        <Route index element={<CreateApplicationPage />} />
        <Route path="draft/:applicationId" element={<DraftIntakePage />} />
        <Route path="resume" element={<SessionRecoveryPage />} />
        <Route path="draft/:applicationId/documents" element={<DocumentUploadPage />} />
        <Route path="draft/:applicationId/ocr-review" element={<OcrReviewPage />} />
        <Route
          path="draft/:applicationId/ocr-manual-fallback"
          element={<OcrManualFallbackPage />}
        />
        <Route path="draft/:applicationId/validation" element={<ValidationFindingsPage />} />
        <Route path="draft/:applicationId/outcome" element={<FinalOutcomePage />} />
        <Route path="notifications" element={<NotificationPreferencesPage />} />
      </Route>

      <Route
        path="/sub-agency"
        element={
          <AppShell
            workspaceName="Sub-Agency"
            navItems={[
              { to: "/sub-agency", label: "Create on Behalf" },
              { to: "/sub-agency/wallet", label: "Wallet Verification" },
            ]}
          />
        }
      >
        <Route index element={<CreateOnBehalfPage />} />
        <Route
          path="draft/:applicationId"
          element={<DraftIntakePage workspace="sub-agency" basePath="/sub-agency" />}
        />
        <Route path="wallet" element={<WalletVerificationPage />} />
        <Route path="submission/:applicationId" element={<SubmissionConfirmationPage />} />
      </Route>

      <Route
        path="/main-agency"
        element={
          <AppShell
            workspaceName="Main Agency"
            navItems={[
              { to: "/main-agency", label: "Case Queue" },
              { to: "/main-agency/gdrfa", label: "GDRFA Submission" },
            ]}
          />
        }
      >
        <Route index element={<CaseQueuePage />} />
        <Route path="case/:applicationId" element={<CaseReviewPage />} />
        <Route path="gdrfa" element={<GdrfaSubmissionPage />} />
      </Route>

      <Route
        path="/finance"
        element={
          <AppShell
            workspaceName="Finance"
            navItems={[{ to: "/finance", label: "Payment Queue" }]}
          />
        }
      >
        <Route index element={<PaymentQueuePage />} />
      </Route>

      <Route
        path="/support"
        element={
          <AppShell
            workspaceName="Support"
            navItems={[{ to: "/support", label: "Recovery Tasks" }]}
          />
        }
      >
        <Route index element={<RecoveryTasksPage />} />
      </Route>

      <Route
        path="/audit"
        element={
          <AppShell
            workspaceName="Audit"
            navItems={[
              { to: "/audit", label: "Audit History" },
              { to: "/audit/export", label: "Export & Compliance" },
            ]}
          />
        }
      >
        <Route index element={<AuditHistoryPage />} />
        <Route path="export" element={<ExportCompliancePage />} />
      </Route>
    </Routes>
  );
}
