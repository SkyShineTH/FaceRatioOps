const input = document.querySelector("#image-input");
const fileMeta = document.querySelector("#file-meta");
const previewImage = document.querySelector("#preview-image");
const previewEmpty = document.querySelector("#preview-empty");
const analyzeButton = document.querySelector("#analyze-button");
const statusBanner = document.querySelector("#status-banner");
const ratioList = document.querySelector("#ratio-list");
const qualityList = document.querySelector("#quality-list");
const modelList = document.querySelector("#model-list");
const overlayList = document.querySelector("#overlay-list");
const overlayCanvas = document.querySelector("#overlay-canvas");
const overlayCaption = document.querySelector("#overlay-caption");

let selectedFile = null;
let previewUrl = null;
let activeOverlay = null;

const ratioLabels = {
  face_width_to_height: "Face width to height",
  eye_distance_to_face_width: "Eye distance to face width",
  nose_width_to_face_width: "Nose width to face width",
  mouth_width_to_face_width: "Mouth width to face width",
  symmetry_delta: "Symmetry delta",
};

function setStatus(message, state = "idle") {
  statusBanner.textContent = message;
  statusBanner.className = `status-banner ${state}`;
}

function formatBytes(bytes) {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / 1024 / 1024).toFixed(2)} MB`;
}

function renderDefinitionList(target, entries) {
  target.replaceChildren(
    ...entries.map(([term, description]) => {
      const row = document.createElement("div");
      const dt = document.createElement("dt");
      const dd = document.createElement("dd");
      dt.textContent = term;
      dd.textContent = description;
      row.append(dt, dd);
      return row;
    }),
  );
}

function resetResults() {
  activeOverlay = null;
  drawOverlay();
  renderDefinitionList(ratioList, [["Awaiting analysis", "-"]]);
  renderDefinitionList(qualityList, [["Warnings", "None yet"]]);
  renderDefinitionList(modelList, [
    ["Name", "-"],
    ["Version", "-"],
    ["Task", "-"],
  ]);
  renderDefinitionList(overlayList, [
    ["Detected face area", "-"],
    ["Measurement segments", "-"],
  ]);
  overlayCaption.textContent = "Overlay appears after a detected face returns landmark-derived measurement geometry.";
}

input.addEventListener("change", () => {
  const [file] = input.files;
  selectedFile = file ?? null;
  analyzeButton.disabled = !selectedFile;
  resetResults();

  if (previewUrl) {
    URL.revokeObjectURL(previewUrl);
    previewUrl = null;
  }

  if (!selectedFile) {
    fileMeta.textContent = "No file selected";
    previewImage.hidden = true;
    previewImage.removeAttribute("src");
    previewEmpty.hidden = false;
    setStatus("Select an image to start the workflow.");
    return;
  }

  fileMeta.textContent = `${selectedFile.name} - ${formatBytes(selectedFile.size)}`;
  previewUrl = URL.createObjectURL(selectedFile);
  previewImage.src = previewUrl;
  previewImage.hidden = false;
  previewEmpty.hidden = true;
  setStatus("Image ready. Submit it to the API when you want to analyze geometry.");
});

analyzeButton.addEventListener("click", async () => {
  if (!selectedFile) return;

  const formData = new FormData();
  formData.append("file", selectedFile);
  analyzeButton.disabled = true;
  setStatus("Detecting landmarks and calculating ratios...", "running");

  try {
    const response = await fetch("/analyze", {
      method: "POST",
      body: formData,
    });
    const body = await response.json();

    if (!response.ok) {
      throw new Error(body.detail || `Request failed with status ${response.status}`);
    }

    renderResult(body);
  } catch (error) {
    setStatus(error.message || "Analysis failed.", "error");
  } finally {
    analyzeButton.disabled = false;
  }
});

function renderResult(body) {
  const warnings = body.quality?.warnings ?? [];
  const hasRatios = body.ratios && Object.keys(body.ratios).length > 0;
  activeOverlay = body.visualization ?? null;
  drawOverlay();

  if (body.face_detected && hasRatios) {
    setStatus("Analysis complete. Technical geometry measurements are available.", "ok");
  } else {
    setStatus(body.quality?.message || "Analysis complete with technical quality warnings.", "warn");
  }

  const ratioEntries = hasRatios
    ? Object.entries(body.ratios).map(([key, value]) => [ratioLabels[key] || key, Number(value).toFixed(3)])
    : [["Ratios", "Unavailable"]];

  const qualityEntries = [
    ["Warnings", warnings.length ? warnings.join(", ") : "None"],
    ["Message", body.quality?.message || "None"],
    ["Confidence", body.quality?.confidence ?? "Unavailable"],
  ];

  const model = body.model ?? {};
  const modelEntries = [
    ["Name", model.name || "-"],
    ["Version", model.version || "-"],
    ["Task", model.task || "-"],
  ];
  const overlayEntries = activeOverlay
    ? [
        ["Detected face area", "Available"],
        ["Measurement segments", `${activeOverlay.measurement_segments?.length ?? 0}`],
      ]
    : [
        ["Detected face area", "Unavailable"],
        ["Measurement segments", "0"],
      ];

  renderDefinitionList(ratioList, ratioEntries);
  renderDefinitionList(qualityList, qualityEntries);
  renderDefinitionList(modelList, modelEntries);
  renderDefinitionList(overlayList, overlayEntries);
  overlayCaption.textContent = activeOverlay
    ? "Overlay shows detected landmark measurements on the local preview."
    : "No overlay geometry was returned for this analysis.";
}

function drawOverlay() {
  const context = overlayCanvas.getContext("2d");
  const rect = overlayCanvas.getBoundingClientRect();
  const pixelRatio = window.devicePixelRatio || 1;
  overlayCanvas.width = Math.max(Math.floor(rect.width * pixelRatio), 1);
  overlayCanvas.height = Math.max(Math.floor(rect.height * pixelRatio), 1);
  context.setTransform(pixelRatio, 0, 0, pixelRatio, 0, 0);
  context.clearRect(0, 0, rect.width, rect.height);

  if (!activeOverlay || previewImage.hidden || !previewImage.naturalWidth || !previewImage.naturalHeight) {
    return;
  }

  const imageRect = renderedImageRect(rect, previewImage.naturalWidth, previewImage.naturalHeight);
  drawBoundingBox(context, imageRect, activeOverlay.bounding_box);
  (activeOverlay.measurement_segments || []).forEach((segment, index) => {
    drawSegment(context, imageRect, segment, index);
  });
}

function renderedImageRect(frameRect, naturalWidth, naturalHeight) {
  const frameRatio = frameRect.width / frameRect.height;
  const imageRatio = naturalWidth / naturalHeight;

  if (imageRatio > frameRatio) {
    const width = frameRect.width;
    const height = width / imageRatio;
    return { x: 0, y: (frameRect.height - height) / 2, width, height };
  }

  const height = frameRect.height;
  const width = height * imageRatio;
  return { x: (frameRect.width - width) / 2, y: 0, width, height };
}

function toCanvasPoint(imageRect, point) {
  return {
    x: imageRect.x + point.x * imageRect.width,
    y: imageRect.y + point.y * imageRect.height,
  };
}

function drawBoundingBox(context, imageRect, box) {
  const start = toCanvasPoint(imageRect, { x: box.x_min, y: box.y_min });
  const end = toCanvasPoint(imageRect, { x: box.x_max, y: box.y_max });
  context.save();
  context.strokeStyle = "#147f78";
  context.lineWidth = 2;
  context.setLineDash([8, 6]);
  context.strokeRect(start.x, start.y, end.x - start.x, end.y - start.y);
  context.restore();
}

function drawSegment(context, imageRect, segment, index) {
  const start = toCanvasPoint(imageRect, segment.start);
  const end = toCanvasPoint(imageRect, segment.end);
  const color = segmentColor(index);

  context.save();
  context.strokeStyle = color;
  context.fillStyle = color;
  context.lineWidth = 3;
  context.beginPath();
  context.moveTo(start.x, start.y);
  context.lineTo(end.x, end.y);
  context.stroke();

  context.beginPath();
  context.arc(start.x, start.y, 4, 0, Math.PI * 2);
  context.arc(end.x, end.y, 4, 0, Math.PI * 2);
  context.fill();
  context.restore();
}

function segmentColor(index) {
  const colors = [
    "#b83f35",
    "#2d7b48",
    "#147f78",
    "#9a6a1d",
    "#5d5797",
  ];
  return colors[index % colors.length];
}

resetResults();

previewImage.addEventListener("load", drawOverlay);
window.addEventListener("resize", drawOverlay);
