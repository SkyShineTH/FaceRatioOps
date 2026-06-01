// k6 load test for the FaceRatioOps API.
//
// Exercises the two cost classes of the service:
//   - cheap, fast GET /health (liveness / scrape-style traffic)
//   - expensive POST /analyze (MediaPipe landmark detection + ratio + overlay)
//
// Thresholds mirror the SLOs in docs/slo.md so the test passes/fails on the same
// objectives the burn-rate alerts watch:
//   - /analyze p95 < 1.5s
//   - request error rate < 0.5%
//
// Run:
//   k6 run loadtest/k6/analyze-load.js                       # default ramping load
//   k6 run -e SCENARIO=smoke loadtest/k6/analyze-load.js     # quick 1-VU smoke
//   k6 run -e BASE_URL=https://faceratioops.skyshine.online loadtest/k6/analyze-load.js
//
// The upload is a committed synthetic (non-real) image; it is not a real person.

import http from "k6/http";
import { check } from "k6";
import { Rate } from "k6/metrics";

const BASE_URL = (__ENV.BASE_URL || "http://127.0.0.1:8000").replace(/\/$/, "");
const SCENARIO = __ENV.SCENARIO || "load";

// Loaded once per VU at init time; k6 requires open() at init scope.
const FACE_IMAGE = open("../assets/synthetic-face.png", "b");

const errorRate = new Rate("faceratioops_errors");

const SCENARIOS = {
  smoke: {
    executor: "constant-vus",
    vus: 1,
    duration: "30s",
  },
  load: {
    executor: "ramping-vus",
    startVUs: 0,
    stages: [
      { duration: "30s", target: 5 },
      { duration: "1m", target: 5 },
      { duration: "30s", target: 10 },
      { duration: "1m", target: 10 },
      { duration: "30s", target: 0 },
    ],
    gracefulRampDown: "10s",
  },
};

export const options = {
  scenarios: { [SCENARIO]: SCENARIOS[SCENARIO] },
  thresholds: {
    "http_req_duration{endpoint:analyze}": ["p(95)<1500"],
    "http_req_duration{endpoint:health}": ["p(95)<200"],
    faceratioops_errors: ["rate<0.005"],
  },
};

export default function () {
  // Liveness-style traffic.
  const health = http.get(`${BASE_URL}/health`, { tags: { endpoint: "health" } });
  check(health, { "health 200": (r) => r.status === 200 });
  errorRate.add(health.status >= 500);

  // Heavy inference path.
  const res = http.post(
    `${BASE_URL}/analyze`,
    { file: http.file(FACE_IMAGE, "synthetic-face.png", "image/png") },
    { tags: { endpoint: "analyze" } },
  );
  check(res, {
    "analyze 200": (r) => r.status === 200,
    "analyze returns json": (r) => (r.headers["Content-Type"] || "").includes("application/json"),
  });
  // 5xx counts against the budget; a clean 4xx (e.g. validation) does not.
  errorRate.add(res.status >= 500);
}
