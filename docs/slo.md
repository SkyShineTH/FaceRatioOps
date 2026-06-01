# Service Level Objectives

This document defines the SLIs, SLOs, and error-budget alerting policy for the
FaceRatioOps API. It is operational-only: no SLI is derived from image content,
identity, demographic, or appearance data — only HTTP request outcomes and latency.

FaceRatioOps is a low-traffic portfolio service on a single small Droplet. The SLOs
below are deliberately modest and exist to demonstrate an SRE workflow (measure →
objective → error budget → burn-rate alerting), not to promise a commercial tier.

## Service Level Indicators (SLIs)

| SLI | Definition | Source |
| --- | --- | --- |
| Availability | Fraction of HTTP responses that are **not** `5xx`. | `faceratioops_http_requests_total{status}` |
| Latency (analyze) | Fraction of `/analyze` requests faster than the latency target. | `faceratioops_http_request_duration_seconds_bucket{path="/analyze"}` histogram |

The latency SLI relies on the request-duration **histogram** exposed at `/metrics`.
Percentiles are computed in Prometheus with `histogram_quantile()` over the bucket
counters; this is why the API exports `_bucket`, `_count`, and `_sum` series rather
than an average alone.

## Service Level Objectives (SLOs)

| SLO | Target | Window |
| --- | --- | --- |
| Availability | **99.5%** of responses are non-`5xx` | rolling 30 days |
| Analyze latency | **95%** of `/analyze` requests complete within **1.5s** | rolling 30 days |

### Error budget

A 99.5% availability target leaves a **0.5% error budget**. Over 30 days that is the
allowance of failed requests before the SLO is missed. Burn rate expresses how fast the
budget is being spent:

- burn rate `1` → budget exactly exhausted over the full 30 days.
- burn rate `14.4` → budget exhausted in ~2 days.
- burn rate `6` → budget exhausted in ~5 days.

## Alerting policy (multi-window, multi-burn-rate)

Defined in `deploy/prometheus/rules/alerts.yml`, following the Google SRE workbook. Each
alert requires the burn rate to be high over **both** a long and a short window, so a
brief spike does not page and a real regression is caught quickly.

| Alert | Condition | Severity | Meaning |
| --- | --- | --- | --- |
| `FaceRatioOpsErrorBudgetBurnFast` | 5xx ratio > 14.4×0.5% over 1h **and** 5m | page | Budget gone in ~2 days — act now. |
| `FaceRatioOpsErrorBudgetBurnSlow` | 5xx ratio > 6×0.5% over 6h **and** 30m | ticket | Slow leak — fix within working hours. |
| `FaceRatioOpsAnalyzeLatencyHigh` | `/analyze` p95 (5m) > 1.5s for 10m | ticket | Latency SLO at risk. |
| `FaceRatioOpsTargetDown` | `up{job="faceratioops-api"} == 0` for 1m | page | API unscrapeable / down. |
| `HostMemoryLow` | host MemAvailable < 10% for 5m | ticket | OOM risk on a small Droplet. |

Recording rules in `deploy/prometheus/rules/recording.yml` precompute the SLIs
(`job:faceratioops_http_error_ratio:rate*`, `path:faceratioops_analyze_duration_seconds:p95_5m`)
so alert expressions and dashboard panels stay fast and readable.

## Where to see it

- **Grafana** → *FaceRatioOps Operations Overview*: panels for analyze p95/p99 latency
  (with the 1.5s SLO threshold line), current analyze p95, and 30-day availability versus
  the 99.5% objective.
- **Prometheus** → *Alerts* tab shows rule state (inactive / pending / firing); *Rules*
  tab shows recording-rule values.
- **Alertmanager** (`deploy/alertmanager/alertmanager.yml`) routes firing alerts. The
  default receiver is a no-op so the stack runs with no secrets committed; add a
  Slack/webhook receiver on the host to actually notify.

## Validating the SLO under load

`loadtest/` contains a k6 scenario whose thresholds mirror these SLOs (p95 `/analyze`
< 1.5s, error rate < 0.5%). Running it generates the histogram traffic that makes the
latency panels and burn-rate alerts meaningful. See `docs/load-testing.md`.

## Changing the objectives

The targets are encoded in three places that must stay in sync:

1. the budget multipliers in `deploy/prometheus/rules/alerts.yml` (`* 0.005`, `> 1.5`),
2. the threshold steps in `deploy/grafana/dashboards/faceratioops-overview.json`,
3. the tables in this document.

Treat a change to any one as a change to all three.
