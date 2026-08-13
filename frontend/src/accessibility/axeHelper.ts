import { axe, toHaveNoViolations } from "jest-axe";
import { expect } from "vitest";

// Automated WCAG 2.1 AA accessibility testing tooling (T033). Import this
// module once per test file (side-effect registers the matcher), then call
// `expectNoAxeViolations(container)` after rendering a component.
expect.extend(toHaveNoViolations);

export async function expectNoAxeViolations(container: Element): Promise<void> {
  const results = await axe(container);
  expect(results).toHaveNoViolations();
}
