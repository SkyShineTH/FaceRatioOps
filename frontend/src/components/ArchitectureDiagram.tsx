import { useMemo, useState } from "react";

interface ArchNode {
  id: string;
  label: string;
  kind: string;
  description: string;
  tech: string[];
  x: number;
  y: number;
}

interface ArchEdge {
  from: string;
  to: string;
  monitoring?: boolean;
  label?: string;
}

const NODE_W = 220;
const NODE_H = 54;

const NODES: ArchNode[] = [
  {
    id: "client",
    label: "Client / Postman / curl",
    kind: "Entry point",
    description:
      "Any HTTP client that uploads a single local image and reads back the JSON geometry analysis.",
    tech: ["HTTPS", "multipart/form-data"],
    x: 30,
    y: 20,
  },
  {
    id: "cloudflare",
    label: "Cloudflare",
    kind: "DNS / TLS edge",
    description:
      "Public DNS and HTTPS termination in front of the origin. Provides the public hostname and TLS.",
    tech: ["DNS", "TLS"],
    x: 30,
    y: 110,
  },
  {
    id: "caddy",
    label: "Caddy reverse proxy",
    kind: "Droplet edge",
    description:
      "Runs on the DigitalOcean droplet and reverse-proxies inbound requests to the API container.",
    tech: ["Caddy", "DigitalOcean"],
    x: 30,
    y: 200,
  },
  {
    id: "api",
    label: "FastAPI Inference API",
    kind: "Application",
    description:
      "Docker Compose service. Validates uploads, orchestrates inference, exposes /health, /model-info, and /metrics, and serves this frontend.",
    tech: ["FastAPI", "Docker Compose", "Uvicorn"],
    x: 30,
    y: 290,
  },
  {
    id: "mediapipe",
    label: "MediaPipe Face Mesh",
    kind: "Inference",
    description:
      "Landmark detection adapter. Produces normalized face landmarks consumed by the ratio calculator.",
    tech: ["MediaPipe", "NumPy", "Pillow"],
    x: 30,
    y: 380,
  },
  {
    id: "calculator",
    label: "Ratio Calculator",
    kind: "Compute",
    description:
      "Derives technical geometric ratios and a symmetry proxy from selected landmark pairs.",
    tech: ["Python"],
    x: 30,
    y: 470,
  },
  {
    id: "response",
    label: "JSON + Logs + Health",
    kind: "Output",
    description:
      "Structured JSON response plus structured logs and container health checks for operations.",
    tech: ["JSON", "structured logs"],
    x: 30,
    y: 560,
  },
  {
    id: "node_exporter",
    label: "Node Exporter",
    kind: "Monitoring",
    description: "Exposes DigitalOcean droplet host metrics (CPU, memory, disk, network).",
    tech: ["Node Exporter"],
    x: 470,
    y: 290,
  },
  {
    id: "prometheus",
    label: "Prometheus",
    kind: "Monitoring",
    description:
      "Scrapes the API /metrics endpoint and Node Exporter, storing time-series for dashboards.",
    tech: ["Prometheus"],
    x: 470,
    y: 390,
  },
  {
    id: "grafana",
    label: "Grafana",
    kind: "Monitoring",
    description:
      "Dashboards for request rate, latency, status/error rate, scrape health, and host usage.",
    tech: ["Grafana"],
    x: 470,
    y: 490,
  },
];

const EDGES: ArchEdge[] = [
  { from: "client", to: "cloudflare" },
  { from: "cloudflare", to: "caddy" },
  { from: "caddy", to: "api" },
  { from: "api", to: "mediapipe" },
  { from: "mediapipe", to: "calculator" },
  { from: "calculator", to: "response" },
  { from: "api", to: "prometheus", monitoring: true, label: "/metrics" },
  { from: "node_exporter", to: "prometheus", monitoring: true },
  { from: "prometheus", to: "grafana", monitoring: true },
];

const VIEWBOX_W = 720;
const VIEWBOX_H = 634;

const nodeById = new Map(NODES.map((node) => [node.id, node]));

function center(node: ArchNode) {
  return { x: node.x + NODE_W / 2, y: node.y + NODE_H / 2 };
}

// Point on a node's border along the line toward another point.
function borderPoint(node: ArchNode, toward: { x: number; y: number }) {
  const c = center(node);
  const dx = toward.x - c.x;
  const dy = toward.y - c.y;
  const hw = NODE_W / 2;
  const hh = NODE_H / 2;
  const scale = 1 / Math.max(Math.abs(dx) / hw, Math.abs(dy) / hh || Number.EPSILON);
  return { x: c.x + dx * scale, y: c.y + dy * scale };
}

export default function ArchitectureDiagram() {
  const [activeId, setActiveId] = useState<string | null>(null);

  const adjacency = useMemo(() => {
    const map = new Map<string, Set<string>>();
    for (const edge of EDGES) {
      if (!map.has(edge.from)) map.set(edge.from, new Set());
      if (!map.has(edge.to)) map.set(edge.to, new Set());
      map.get(edge.from)!.add(edge.to);
      map.get(edge.to)!.add(edge.from);
    }
    return map;
  }, []);

  function isNodeLit(id: string): boolean {
    if (!activeId) return false;
    return id === activeId || (adjacency.get(activeId)?.has(id) ?? false);
  }

  function isEdgeLit(edge: ArchEdge): boolean {
    return activeId != null && (edge.from === activeId || edge.to === activeId);
  }

  const activeNode = activeId ? nodeById.get(activeId) : null;

  return (
    <div className="architecture-layout">
      <div className="architecture-stage">
        <svg
          className={`architecture-svg${activeId ? " has-active" : ""}`}
          viewBox={`0 0 ${VIEWBOX_W} ${VIEWBOX_H}`}
          role="group"
          aria-label="FaceRatioOps deployment architecture. Hover or focus a service to inspect it."
        >
          <defs>
            <marker
              id="arrow"
              viewBox="0 0 10 10"
              refX="9"
              refY="5"
              markerWidth="7"
              markerHeight="7"
              orient="auto-start-reverse"
            >
              <path d="M 0 0 L 10 5 L 0 10 z" fill="oklch(47% 0.04 238)" />
            </marker>
          </defs>

          <g className="arch-edges">
            {EDGES.map((edge) => {
              const source = nodeById.get(edge.from)!;
              const target = nodeById.get(edge.to)!;
              const start = borderPoint(source, center(target));
              const end = borderPoint(target, center(source));
              const lit = isEdgeLit(edge);
              const midX = (start.x + end.x) / 2;
              const midY = (start.y + end.y) / 2;
              return (
                <g key={`${edge.from}-${edge.to}`}>
                  <line
                    className={`arch-edge${edge.monitoring ? " monitoring" : ""}${lit ? " active" : ""}`}
                    x1={start.x}
                    y1={start.y}
                    x2={end.x}
                    y2={end.y}
                    markerEnd="url(#arrow)"
                  />
                  {edge.label ? (
                    <text className="arch-node-kind" x={midX + 6} y={midY - 6}>
                      {edge.label}
                    </text>
                  ) : null}
                </g>
              );
            })}
          </g>

          <g className="arch-nodes">
            {NODES.map((node) => {
              const lit = isNodeLit(node.id);
              return (
                <g
                  key={node.id}
                  className={`arch-node${lit ? " active" : ""}`}
                  tabIndex={0}
                  role="button"
                  aria-pressed={activeId === node.id}
                  aria-label={`${node.label}, ${node.kind}`}
                  onMouseEnter={() => setActiveId(node.id)}
                  onMouseLeave={() => setActiveId(null)}
                  onFocus={() => setActiveId(node.id)}
                  onBlur={() => setActiveId(null)}
                >
                  <rect
                    className="arch-node-box"
                    x={node.x}
                    y={node.y}
                    width={NODE_W}
                    height={NODE_H}
                    rx={6}
                  />
                  <text className="arch-node-kind" x={node.x + 14} y={node.y + 20}>
                    {node.kind}
                  </text>
                  <text className="arch-node-label" x={node.x + 14} y={node.y + 40}>
                    {node.label}
                  </text>
                </g>
              );
            })}
          </g>
        </svg>
      </div>

      <aside className="architecture-detail" aria-live="polite">
        {activeNode ? (
          <>
            <p className="detail-kind">{activeNode.kind}</p>
            <h2>{activeNode.label}</h2>
            <p>{activeNode.description}</p>
            <div className="detail-tech">
              {activeNode.tech.map((item) => (
                <span key={item}>{item}</span>
              ))}
            </div>
          </>
        ) : (
          <>
            <p className="detail-kind">Architecture</p>
            <h2>Deployment overview</h2>
            <p>
              Hover or focus any service to highlight its connections and read what it does. Solid
              lines follow the request path; dashed lines show the monitoring pipeline.
            </p>
          </>
        )}
      </aside>
    </div>
  );
}
