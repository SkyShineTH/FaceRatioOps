import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import ResultPanel from "../ResultPanel";
import type { AnalysisResponse } from "../../types";

const sampleResult: AnalysisResponse = {
  face_detected: true,
  model: { name: "MediaPipe Face Mesh", version: "0.10.21", task: "face_landmark" },
  ratios: {
    face_width_to_height: 0.812,
    eye_distance_to_face_width: 0.421,
    nose_width_to_face_width: 0.255,
    mouth_width_to_face_width: 0.38,
    symmetry_delta: 0.014,
    upper_third_ratio: 0.3,
    middle_third_ratio: 0.35,
    lower_third_ratio: 0.35,
  },
  visualization: {
    bounding_box: { x_min: 0.1, y_min: 0.1, x_max: 0.9, y_max: 0.9 },
    measurement_segments: [
      { name: "face_width", label: "Face width", start: { x: 0, y: 0 }, end: { x: 1, y: 0 } },
    ],
  },
  quality: { warnings: [], message: null, confidence: 0.97 },
};

describe("ResultPanel", () => {
  it("shows placeholder content before any analysis", () => {
    render(<ResultPanel status={{ message: "Select an image", state: "idle" }} result={null} />);
    expect(screen.getByText("Awaiting analysis")).toBeInTheDocument();
    expect(screen.getByText("None yet")).toBeInTheDocument();
  });

  it("renders ratios, model metadata, and overlay summary from a response", () => {
    render(
      <ResultPanel status={{ message: "Analysis complete.", state: "ok" }} result={sampleResult} />,
    );

    expect(screen.getByText("Eye distance to face width")).toBeInTheDocument();
    expect(screen.getByText("0.421")).toBeInTheDocument();
    expect(screen.getByText("MediaPipe Face Mesh")).toBeInTheDocument();
    expect(screen.getByText("Available")).toBeInTheDocument();
    expect(screen.getByRole("status")).toHaveTextContent("Analysis complete.");
  });
});
