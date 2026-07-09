# Load Testing

> **Status — decommissioned 2026-07-09.** The live DigitalOcean demo that
> these load tests targeted is torn down. The k6 scripts and thresholds
> below remain valid for any redeployed instance.

FaceRatioOps is load-tested with [k6](https://k6.io). The goal is capacity awareness on
a small Droplet and validating the latency/availability SLOs in [`docs/slo.md`](slo.md)
under realistic traffic — not synthetic vanity numbers.

The `/analyze` path is the expensive one: it runs MediaPipe landmark detection, ratio
calculation, and overlay geometry. `/health` is the cheap baseline. The script drives both.

## Files

| File | Purpose |
| --- | --- |
| `loadtest/k6/analyze-load.js` | k6 scenarios + SLO-aligned thresholds. |
| `loadtest/assets/synthetic-face.png` | Committed synthetic (non-real) upload. Not a real person. |

## Prerequisites

- A running API: `uvicorn app.main:app` (with the `inference` extra installed so
  `/analyze` actually runs MediaPipe), or the Docker image, or the public URL.
- k6 installed: <https://grafana.com/docs/k6/latest/set-up/install-k6/>.

## Run

```bash
# Quick 1-VU smoke (30s)
k6 run -e SCENARIO=smoke loadtest/k6/analyze-load.js

# Ramping load (0→10 VUs, ~3.5 min) against a local API
k6 run loadtest/k6/analyze-load.js

# Against the deployed service
k6 run -e BASE_URL=https://faceratioops.skyshine.online loadtest/k6/analyze-load.js
```

## Thresholds (mirror the SLOs)

The run fails (non-zero exit, so it can gate CI) if any threshold is breached:

| Threshold | Value | Maps to |
| --- | --- | --- |
| `http_req_duration{endpoint:analyze}` p95 | < 1500 ms | Analyze latency SLO |
| `http_req_duration{endpoint:health}` p95 | < 200 ms | Liveness responsiveness |
| `faceratioops_errors` rate | < 0.5% | Availability error budget |

## Reading the results

- `http_req_duration` p95/p99 for `endpoint:analyze` is the latency capacity signal.
  Compare it against the 1.5s SLO and watch where it degrades as VUs climb.
- If p95 rises sharply at a given VU count, that is the practical concurrency ceiling
  for the current Droplet size — the number to cite for capacity planning.
- Run with the monitoring stack up to watch the same traffic flow through the Grafana
  SLO panels and (if pushed hard enough) trip the burn-rate alerts in Prometheus.

## Capacity notes

- `max_inference_dimension` (default 1024) downscales large uploads before detection,
  which caps per-request CPU and memory and keeps `/analyze` latency bounded regardless
  of upload resolution. Lowering it trades landmark precision for throughput.
- MediaPipe inference is CPU-bound and largely single-threaded per request; throughput
  scales with cores/workers, not with raising the per-request pixel budget.
- Do not point this script at infrastructure you do not own. Load testing third-party
  endpoints can look like a denial-of-service attack.
