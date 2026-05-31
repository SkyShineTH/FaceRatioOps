import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import SafetyBand from "../SafetyBand";

// The disclaimer copy is the project's stated brand boundary. It moved out of the
// server-rendered HTML into this component, so it must stay test-covered here.
describe("SafetyBand", () => {
  it("renders the identity-matching and attractiveness disclaimers verbatim", () => {
    render(<SafetyBand />);

    expect(
      screen.getByText(/does not perform identity matching/i),
    ).toBeInTheDocument();
    expect(screen.getByText(/attractiveness scoring/i)).toBeInTheDocument();
    expect(
      screen.getByText(/is not permanently stored by FaceRatioOps/i),
    ).toBeInTheDocument();
  });
});
