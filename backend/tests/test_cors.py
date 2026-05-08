from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_cors_preflight_accepts_frontend_origin() -> None:
    response = client.options(
        "/health",
        headers={
            "Origin": "http://127.0.0.1:5173",
            "Access-Control-Request-Method": "GET",
        },
    )

    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == "http://127.0.0.1:5173"