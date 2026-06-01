from fastapi.testclient import TestClient

from app.core.metrics import MetricsRegistry
from app.main import app

client = TestClient(app)


def test_metrics_exposes_prometheus_text_for_operational_requests() -> None:
    client.get("/health")

    response = client.get("/metrics")

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/plain")
    assert "# TYPE faceratioops_http_requests_total counter" in response.text
    assert 'faceratioops_http_requests_total{method="GET",path="/health",status="200"}' in response.text


def test_metrics_exposes_latency_histogram() -> None:
    client.get("/health")

    body = client.get("/metrics").text

    assert "# TYPE faceratioops_http_request_duration_seconds histogram" in body
    assert "faceratioops_http_request_duration_seconds_bucket{" in body
    assert 'le="+Inf"' in body
    assert "faceratioops_http_request_duration_seconds_count{" in body
    assert "faceratioops_http_request_duration_seconds_sum{" in body


def test_histogram_buckets_are_cumulative_and_match_count() -> None:
    registry = MetricsRegistry()
    # 0.003s -> bucket le=0.005; 0.2s -> bucket le=0.25; 30s -> +Inf overflow.
    registry.record_request("GET", "/analyze", 200, 0.003)
    registry.record_request("GET", "/analyze", 200, 0.2)
    registry.record_request("GET", "/analyze", 200, 30.0)

    rendered = registry.render_prometheus()
    buckets = {
        line.split('le="')[1].split('"')[0]: int(line.rsplit(" ", 1)[1])
        for line in rendered.splitlines()
        if line.startswith("faceratioops_http_request_duration_seconds_bucket")
    }

    # Cumulative: le=0.005 has 1, le=0.25 has 2, +Inf has all 3.
    assert buckets["0.005"] == 1
    assert buckets["0.25"] == 2
    assert buckets["+Inf"] == 3
    # Buckets are monotonically non-decreasing.
    le_order = ("0.005", "0.01", "0.025", "0.05", "0.1", "0.25", "0.5", "1", "2.5", "5", "10", "+Inf")
    ordered = [buckets[le] for le in le_order]
    assert ordered == sorted(ordered)
