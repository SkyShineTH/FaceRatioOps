import type { AnalysisResponse, ReferencesResponse } from "../types";

interface ErrorBody {
  detail?: string;
}

/**
 * Submit a local image to the API for geometric analysis.
 * Mirrors the request the original vanilla workbench made to POST /analyze.
 */
export async function analyzeImage(file: File): Promise<AnalysisResponse> {
  const formData = new FormData();
  formData.append("file", file);

  const response = await fetch("/analyze", {
    method: "POST",
    body: formData,
  });

  const body: AnalysisResponse | ErrorBody = await response.json();

  if (!response.ok) {
    const detail = (body as ErrorBody).detail;
    throw new Error(detail || `Request failed with status ${response.status}`);
  }

  return body as AnalysisResponse;
}

/** Fetch the static classical-canon reference bands shown alongside measured ratios. */
export async function fetchReferences(): Promise<ReferencesResponse> {
  const response = await fetch("/references");
  if (!response.ok) {
    throw new Error(`Failed to load references (status ${response.status})`);
  }
  return (await response.json()) as ReferencesResponse;
}
