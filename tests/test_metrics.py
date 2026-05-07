from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_metrics_exposes_prometheus_text_for_operational_requests() -> None:
    client.get("/health")

    response = client.get("/metrics")

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/plain")
    assert "# TYPE faceratioops_http_requests_total counter" in response.text
    assert 'faceratioops_http_requests_total{method="GET",path="/health",status="200"}' in response.text
    assert "# TYPE faceratioops_http_request_duration_seconds_sum counter" in response.text
