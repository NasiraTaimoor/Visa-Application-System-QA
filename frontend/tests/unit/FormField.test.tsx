import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FormField } from "@shared/components/FormField";

describe("FormField", () => {
  it("associates the label, hint, and error with the control for assistive tech", () => {
    render(
      <FormField
        label="Passport number"
        hint="As printed on the bio page"
        error="Required"
        required
      >
        {(fieldProps) => <input {...fieldProps} />}
      </FormField>,
    );

    const input = screen.getByLabelText(/Passport number/);
    expect(input).toHaveAttribute("aria-invalid", "true");
    expect(screen.getByRole("alert")).toHaveTextContent("Required");
  });
});
