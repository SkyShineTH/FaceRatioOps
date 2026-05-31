import type { AnalysisResponse, FaceRatios, StatusState } from "../types";
import { RATIO_LABELS } from "../types";
import DefinitionList, { type DefinitionEntry } from "./DefinitionList";

interface ResultPanelProps {
  status: { message: string; state: StatusState };
  result: AnalysisResponse | null;
}

function ratioEntries(result: AnalysisResponse | null): DefinitionEntry[] {
  const ratios = result?.ratios;
  if (!ratios) {
    return result ? [["Ratios", "Unavailable"]] : [["Awaiting analysis", "-"]];
  }
  return (Object.entries(ratios) as [keyof FaceRatios, number][]).map(([key, value]) => [
    RATIO_LABELS[key] ?? key,
    Number(value).toFixed(3),
  ]);
}

function qualityEntries(result: AnalysisResponse | null): DefinitionEntry[] {
  if (!result) return [["Warnings", "None yet"]];
  const warnings = result.quality?.warnings ?? [];
  return [
    ["Warnings", warnings.length ? warnings.join(", ") : "None"],
    ["Message", result.quality?.message || "None"],
    ["Confidence", result.quality?.confidence != null ? String(result.quality.confidence) : "Unavailable"],
  ];
}

function modelEntries(result: AnalysisResponse | null): DefinitionEntry[] {
  const model = result?.model;
  return [
    ["Name", model?.name || "-"],
    ["Version", model?.version || "-"],
    ["Task", model?.task || "-"],
  ];
}

function overlayEntries(result: AnalysisResponse | null): DefinitionEntry[] {
  const overlay = result?.visualization ?? null;
  if (!overlay) {
    return [
      ["Detected face area", result ? "Unavailable" : "-"],
      ["Measurement segments", result ? "0" : "-"],
    ];
  }
  return [
    ["Detected face area", "Available"],
    ["Measurement segments", String(overlay.measurement_segments?.length ?? 0)],
  ];
}

export default function ResultPanel({ status, result }: ResultPanelProps) {
  return (
    <div className="result-panel">
      <div className="panel-heading">
        <span className="step">02</span>
        <div>
          <h2>Geometry analysis result</h2>
          <p>Geometry measurements, model metadata, and technical warnings only.</p>
        </div>
      </div>

      <div className={`status-banner ${status.state}`} role="status">
        {status.message}
      </div>

      <div className="result-grid">
        <section className="result-section" aria-labelledby="ratios-title">
          <h3 id="ratios-title">Geometric ratios</h3>
          <DefinitionList className="ratio-list" entries={ratioEntries(result)} />
        </section>

        <section className="result-section" aria-labelledby="quality-title">
          <h3 id="quality-title">Quality warnings</h3>
          <DefinitionList className="quality-list" entries={qualityEntries(result)} />
        </section>
      </div>

      <section className="result-section model-section" aria-labelledby="model-title">
        <h3 id="model-title">Model metadata</h3>
        <DefinitionList className="model-list" entries={modelEntries(result)} />
      </section>

      <section className="result-section model-section" aria-labelledby="overlay-title">
        <h3 id="overlay-title">Explainability overlay</h3>
        <DefinitionList className="model-list" entries={overlayEntries(result)} />
      </section>
    </div>
  );
}
