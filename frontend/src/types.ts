// Mirrors app/inference/schemas.py response models.

export interface FaceRatios {
  face_width_to_height: number;
  eye_distance_to_face_width: number;
  nose_width_to_face_width: number;
  mouth_width_to_face_width: number;
  symmetry_delta: number;
  upper_third_ratio: number;
  middle_third_ratio: number;
  lower_third_ratio: number;
}

export interface OverlayPoint {
  x: number;
  y: number;
}

export interface OverlayBoundingBox {
  x_min: number;
  y_min: number;
  x_max: number;
  y_max: number;
}

export interface MeasurementSegment {
  name: string;
  label: string;
  start: OverlayPoint;
  end: OverlayPoint;
}

export interface VisualizationOverlay {
  bounding_box: OverlayBoundingBox;
  measurement_segments: MeasurementSegment[];
}

export interface RatioReference {
  field: string;
  canon: string;
  expected: number;
  lower: number;
  upper: number;
  note: string;
}

export interface ReferencesResponse {
  references: RatioReference[];
  disclaimer: string;
  sources: string[];
}

export interface ModelInfo {
  name: string;
  version: string;
  task: string;
}

export interface QualityReport {
  warnings: string[];
  message: string | null;
  confidence: number | null;
}

export interface AnalysisResponse {
  face_detected: boolean;
  model: ModelInfo;
  ratios: FaceRatios | null;
  visualization: VisualizationOverlay | null;
  quality: QualityReport;
}

export type StatusState = "idle" | "running" | "ok" | "warn" | "error";

export const RATIO_LABELS: Record<keyof FaceRatios, string> = {
  face_width_to_height: "Face width to height",
  eye_distance_to_face_width: "Eye distance to face width",
  nose_width_to_face_width: "Nose width to face width",
  mouth_width_to_face_width: "Mouth width to face width",
  symmetry_delta: "Symmetry delta",
  upper_third_ratio: "Upper third (forehead–brow)",
  middle_third_ratio: "Middle third (brow–nose base)",
  lower_third_ratio: "Lower third (nose base–chin)",
};
