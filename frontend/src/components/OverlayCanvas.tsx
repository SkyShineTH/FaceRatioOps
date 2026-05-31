import { useEffect, useRef } from "react";

import type { MeasurementSegment, OverlayBoundingBox, OverlayPoint, VisualizationOverlay } from "../types";

interface Rect {
  x: number;
  y: number;
  width: number;
  height: number;
}

interface OverlayCanvasProps {
  overlay: VisualizationOverlay | null;
  naturalWidth: number;
  naturalHeight: number;
}

const SEGMENT_COLORS = ["#b83f35", "#2d7b48", "#147f78", "#9a6a1d", "#5d5797"];

// Map normalized [0,1] overlay coordinates onto the rendered (object-fit: contain) image rect.
function renderedImageRect(frame: Rect, naturalWidth: number, naturalHeight: number): Rect {
  const frameRatio = frame.width / frame.height;
  const imageRatio = naturalWidth / naturalHeight;

  if (imageRatio > frameRatio) {
    const width = frame.width;
    const height = width / imageRatio;
    return { x: 0, y: (frame.height - height) / 2, width, height };
  }
  const height = frame.height;
  const width = height * imageRatio;
  return { x: (frame.width - width) / 2, y: 0, width, height };
}

function toCanvasPoint(imageRect: Rect, point: OverlayPoint) {
  return {
    x: imageRect.x + point.x * imageRect.width,
    y: imageRect.y + point.y * imageRect.height,
  };
}

function drawBoundingBox(context: CanvasRenderingContext2D, imageRect: Rect, box: OverlayBoundingBox) {
  const start = toCanvasPoint(imageRect, { x: box.x_min, y: box.y_min });
  const end = toCanvasPoint(imageRect, { x: box.x_max, y: box.y_max });
  context.save();
  context.strokeStyle = "#147f78";
  context.lineWidth = 2;
  context.setLineDash([8, 6]);
  context.strokeRect(start.x, start.y, end.x - start.x, end.y - start.y);
  context.restore();
}

function drawSegment(context: CanvasRenderingContext2D, imageRect: Rect, segment: MeasurementSegment, index: number) {
  const start = toCanvasPoint(imageRect, segment.start);
  const end = toCanvasPoint(imageRect, segment.end);
  const color = SEGMENT_COLORS[index % SEGMENT_COLORS.length];

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

export default function OverlayCanvas({ overlay, naturalWidth, naturalHeight }: OverlayCanvasProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    function draw() {
      if (!canvas) return;
      const context = canvas.getContext("2d");
      if (!context) return;

      const rect = canvas.getBoundingClientRect();
      const pixelRatio = window.devicePixelRatio || 1;
      canvas.width = Math.max(Math.floor(rect.width * pixelRatio), 1);
      canvas.height = Math.max(Math.floor(rect.height * pixelRatio), 1);
      context.setTransform(pixelRatio, 0, 0, pixelRatio, 0, 0);
      context.clearRect(0, 0, rect.width, rect.height);

      if (!overlay || !naturalWidth || !naturalHeight) return;

      const imageRect = renderedImageRect(rect, naturalWidth, naturalHeight);
      drawBoundingBox(context, imageRect, overlay.bounding_box);
      overlay.measurement_segments.forEach((segment, index) => {
        drawSegment(context, imageRect, segment, index);
      });
    }

    draw();
    window.addEventListener("resize", draw);
    return () => window.removeEventListener("resize", draw);
  }, [overlay, naturalWidth, naturalHeight]);

  return <canvas ref={canvasRef} className="overlay-canvas" aria-hidden="true" />;
}
