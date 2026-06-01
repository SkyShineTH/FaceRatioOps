import type { AnalysisResponse, FaceRatios, RatioReference, StatusState } from "../types";
import { RATIO_LABELS } from "../types";
import DefinitionList, { type DefinitionEntry } from "./DefinitionList";

interface ResultPanelProps {
  status: { message: string; state: StatusState };
  result: AnalysisResponse | null;
  references: RatioReference[];
  referenceDisclaimer?: string;
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

function RatioReadings({
  ratios,
  references,
}: {
  ratios: FaceRatios;
  references: RatioReference[];
}) {
  const refByField = new Map(references.map((ref) => [ref.field, ref]));
  const rows = (Object.entries(ratios) as [keyof FaceRatios, number][]).map(([key, value]) => {
    const ref = refByField.get(key);
    const within = ref ? value >= ref.lower && value <= ref.upper : null;
    return (
      <div className="ratio-reading" key={key}>
        <div className="ratio-reading-head">
          <dt>{RATIO_LABELS[key] ?? key}</dt>
          <dd>{Number(value).toFixed(3)}</dd>
        </div>
        {ref ? (
          <p className={`ratio-ref ${within ? "within" : "outside"}`}>
            <span className="ref-canon">{ref.canon}</span>
            <span className="ref-band">
              ref ~{ref.expected.toFixed(2)} ({ref.lower.toFixed(2)}–{ref.upper.toFixed(2)})
            </span>
            <span className="ref-state">{within ? "within reference band" : "outside reference band"}</span>
          </p>
        ) : null}
      </div>
    );
  });
  return <dl className="ratio-readings">{rows}</dl>;
}

export default function ResultPanel({ status, result, references, referenceDisclaimer }: ResultPanelProps) {
  const ratios = result?.ratios ?? null;
  const showReferences = !!ratios && references.length > 0;

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

      {result ? (
        <>
          <div className="result-grid">
            <section className="result-section" aria-labelledby="ratios-title">
              <h3 id="ratios-title">Geometric ratios</h3>
              {ratios ? (
                <RatioReadings ratios={ratios} references={references} />
              ) : (
                <DefinitionList className="ratio-list" entries={[["Ratios", "Unavailable"]]} />
              )}
              {showReferences && referenceDisclaimer ? (
                <p className="ratio-ref-note">{referenceDisclaimer}</p>
              ) : null}
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
        </>
      ) : (
        <div className="result-empty">
          <svg viewBox="0 0 48 48" fill="none" stroke="currentColor" strokeWidth="2" aria-hidden="true">
            <circle cx="24" cy="22" r="13" />
            <circle cx="19" cy="19" r="1.6" fill="currentColor" stroke="none" />
            <circle cx="29" cy="19" r="1.6" fill="currentColor" stroke="none" />
            <path d="M24 20v6" />
            <path d="M19 29c1.6 1.6 8.4 1.6 10 0" />
            <path d="M24 35v9M15 44h18" strokeLinecap="round" />
          </svg>
          <span className="empty-title">Awaiting analysis</span>
          <p>
            Upload a local image and run <strong>Analyze geometry</strong> to see landmark-derived
            ratios, classical-canon comparisons, quality warnings, and model metadata here.
          </p>
          <div className="empty-tags">
            <span>Ratios</span>
            <span>Canon bands</span>
            <span>Quality</span>
            <span>Model</span>
          </div>
        </div>
      )}
    </div>
  );
}
