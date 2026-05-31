from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_references_endpoint_returns_canon_bands() -> None:
    response = client.get("/references")

    assert response.status_code == 200
    body = response.json()
    assert body["disclaimer"]
    assert len(body["sources"]) >= 1

    fields = {ref["field"] for ref in body["references"]}
    assert {"upper_third_ratio", "middle_third_ratio", "lower_third_ratio"} <= fields

    for ref in body["references"]:
        assert ref["lower"] <= ref["expected"] <= ref["upper"]
        assert ref["canon"]
        assert ref["note"]


def test_references_disclaimer_keeps_neutral_framing() -> None:
    body = client.get("/references").json()
    text = body["disclaimer"].lower()
    assert "not ideals" in text or "not an ideal" in text
