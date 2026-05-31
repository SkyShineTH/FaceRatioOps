import { useEffect, useRef, useState } from "react";

import type { AnalysisResponse, StatusState } from "../types";
import { analyzeImage } from "../api/client";
import OverlayCanvas from "./OverlayCanvas";
import ResultPanel from "./ResultPanel";

const DEFAULT_STATUS = "Select an image to start the workflow.";
const DEFAULT_CAPTION = "Overlay appears after a detected face returns landmark-derived measurement geometry.";

function formatBytes(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / 1024 / 1024).toFixed(2)} MB`;
}

interface ImageDimensions {
  naturalWidth: number;
  naturalHeight: number;
}

export default function Workbench() {
  const [file, setFile] = useState<File | null>(null);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const [fileMeta, setFileMeta] = useState("No file selected");
  const [status, setStatus] = useState<{ message: string; state: StatusState }>({
    message: DEFAULT_STATUS,
    state: "idle",
  });
  const [result, setResult] = useState<AnalysisResponse | null>(null);
  const [imageDims, setImageDims] = useState<ImageDimensions>({ naturalWidth: 0, naturalHeight: 0 });
  const [caption, setCaption] = useState(DEFAULT_CAPTION);
  const [analyzing, setAnalyzing] = useState(false);
  const previewUrlRef = useRef<string | null>(null);

  // Revoke the last object URL when it changes or the component unmounts.
  useEffect(() => {
    previewUrlRef.current = previewUrl;
    return () => {
      if (previewUrlRef.current) URL.revokeObjectURL(previewUrlRef.current);
    };
  }, [previewUrl]);

  function handleFileChange(event: React.ChangeEvent<HTMLInputElement>) {
    const nextFile = event.target.files?.[0] ?? null;
    setFile(nextFile);
    setResult(null);
    setCaption(DEFAULT_CAPTION);
    setImageDims({ naturalWidth: 0, naturalHeight: 0 });

    if (previewUrl) URL.revokeObjectURL(previewUrl);

    if (!nextFile) {
      setPreviewUrl(null);
      setFileMeta("No file selected");
      setStatus({ message: DEFAULT_STATUS, state: "idle" });
      return;
    }

    setFileMeta(`${nextFile.name} - ${formatBytes(nextFile.size)}`);
    setPreviewUrl(URL.createObjectURL(nextFile));
    setStatus({
      message: "Image ready. Submit it to the API when you want to analyze geometry.",
      state: "idle",
    });
  }

  async function handleAnalyze() {
    if (!file) return;
    setAnalyzing(true);
    setStatus({ message: "Detecting landmarks and calculating ratios...", state: "running" });

    try {
      const body = await analyzeImage(file);
      setResult(body);

      const hasRatios = !!body.ratios && Object.keys(body.ratios).length > 0;
      if (body.face_detected && hasRatios) {
        setStatus({
          message: "Analysis complete. Technical geometry measurements are available.",
          state: "ok",
        });
      } else {
        setStatus({
          message: body.quality?.message || "Analysis complete with technical quality warnings.",
          state: "warn",
        });
      }
      setCaption(
        body.visualization
          ? "Overlay shows detected landmark measurements on the local preview."
          : "No overlay geometry was returned for this analysis.",
      );
    } catch (error) {
      const message = error instanceof Error ? error.message : "Analysis failed.";
      setStatus({ message, state: "error" });
    } finally {
      setAnalyzing(false);
    }
  }

  return (
    <section className="workspace" aria-label="Analysis workflow">
      <div className="upload-panel">
        <div className="panel-heading">
          <span className="step">01</span>
          <div>
            <h2>Input</h2>
            <p>JPEG, PNG, or WebP. Processed in memory by the API.</p>
          </div>
        </div>

        <label className="dropzone" htmlFor="image-input">
          <input
            id="image-input"
            type="file"
            accept="image/jpeg,image/png,image/webp"
            onChange={handleFileChange}
          />
          <span className="dropzone-title">Choose local image</span>
          <span className="dropzone-meta">{fileMeta}</span>
        </label>

        <div className="preview-frame" aria-live="polite">
          {previewUrl ? (
            <>
              <img
                src={previewUrl}
                alt=""
                onLoad={(event) =>
                  setImageDims({
                    naturalWidth: event.currentTarget.naturalWidth,
                    naturalHeight: event.currentTarget.naturalHeight,
                  })
                }
              />
              <OverlayCanvas
                overlay={result?.visualization ?? null}
                naturalWidth={imageDims.naturalWidth}
                naturalHeight={imageDims.naturalHeight}
              />
            </>
          ) : (
            <div className="preview-empty">
              <span>Local preview appears here</span>
            </div>
          )}
        </div>
        <p className="overlay-caption">{caption}</p>

        <button
          type="button"
          className="analyze-button"
          disabled={!file || analyzing}
          onClick={handleAnalyze}
        >
          Analyze geometry
        </button>
      </div>

      <ResultPanel status={status} result={result} />
    </section>
  );
}
