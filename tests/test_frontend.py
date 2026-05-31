from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_frontend_spa_shell_is_served() -> None:
    response = client.get("/")

    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    # The built React shell mounts into #root and loads the bundled assets.
    assert 'id="root"' in response.text
    assert "/static_dist/assets/" in response.text


def test_spa_fallback_serves_shell_for_client_routes() -> None:
    response = client.get("/architecture")

    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    assert 'id="root"' in response.text
