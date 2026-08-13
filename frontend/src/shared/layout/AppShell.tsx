import { NavLink, Outlet } from "react-router-dom";
import { ReactNode } from "react";

export interface WorkspaceNavItem {
  to: string;
  label: string;
}

interface AppShellProps {
  workspaceName: string;
  navItems: WorkspaceNavItem[];
  children?: ReactNode;
}

// Role-based layout shell (T030) shared by applicant, sub-agency, main
// agency, finance, support, and audit workspaces. Keyboard-operable skip
// link + landmark regions per WCAG 2.1 AA.
export function AppShell({ workspaceName, navItems, children }: AppShellProps) {
  return (
    <div className="app-shell">
      <a href="#main-content" className="skip-link">
        Skip to main content
      </a>
      <header>
        <strong>Visa Application System</strong>
        <span className="workspace-name">{workspaceName}</span>
      </header>
      <nav aria-label={`${workspaceName} navigation`}>
        <ul>
          {navItems.map((item) => (
            <li key={item.to}>
              <NavLink to={item.to} end>
                {item.label}
              </NavLink>
            </li>
          ))}
        </ul>
      </nav>
      <main id="main-content">{children ?? <Outlet />}</main>
    </div>
  );
}
