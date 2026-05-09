"""End-to-end runner test against a local mock HTTP server.

Avoids touching real LLM endpoints by only exercising the microservice
node path. The runner's persistence (node_runs table) is checked via
the API.
"""

import json
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

import pytest


class _Handler(BaseHTTPRequestHandler):
    def _send(self, body: dict):
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(body).encode())

    def do_GET(self):
        self._send({"path": self.path, "user_id": 7, "name": "Ana"})

    def do_POST(self):
        n = int(self.headers.get("Content-Length", 0))
        raw = self.rfile.read(n).decode() if n else ""
        try:
            payload = json.loads(raw) if raw else None
        except json.JSONDecodeError:
            payload = raw
        self._send({"received": payload})

    def log_message(self, *a, **k):  # silence test noise
        pass


@pytest.fixture(scope="module")
def mock_server():
    server = HTTPServer(("127.0.0.1", 0), _Handler)
    port = server.server_port
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    yield f"http://127.0.0.1:{port}"
    server.shutdown()


@pytest.fixture()
def client():
    from fastapi.testclient import TestClient

    from app.main import app

    return TestClient(app)


def test_run_two_node_cascade_with_templating(client, mock_server):
    payload = {
        "graph": {
            "nodes": [
                {
                    "id": "ms1",
                    "type": "microservice",
                    "data": {
                        "config": {
                            "method": "GET",
                            "url": f"{mock_server}/users/me",
                            "headers": [],
                            "body": "",
                            "timeout_seconds": 5,
                        }
                    },
                },
                {
                    "id": "ms2",
                    "type": "microservice",
                    "data": {
                        "config": {
                            "method": "POST",
                            "url": f"{mock_server}/echo",
                            "headers": [{"key": "Content-Type", "value": "application/json"}],
                            "body": '{"upstream": {{ms1.user_id}}, "name": "{{ms1.name}}"}',
                            "timeout_seconds": 5,
                        }
                    },
                },
            ],
            "edges": [{"source": "ms1", "target": "ms2"}],
        }
    }

    resp = client.post("/api/run", json=payload)
    assert resp.status_code == 200
    results = resp.json()["results"]
    assert [r["node_id"] for r in results] == ["ms1", "ms2"]
    assert all(r["status"] == "ok" for r in results)
    received = results[1]["output"]["received"]
    assert received == {"upstream": 7, "name": "Ana"}


def test_runs_endpoint_persists_and_lists(client, mock_server):
    # Run a single node to produce a log entry
    payload = {
        "graph": {
            "nodes": [
                {
                    "id": "ms-log-test",
                    "type": "microservice",
                    "data": {
                        "config": {
                            "method": "GET",
                            "url": f"{mock_server}/log",
                            "headers": [],
                            "body": "",
                            "timeout_seconds": 5,
                        }
                    },
                }
            ],
            "edges": [],
        }
    }
    client.post("/api/run", json=payload)

    listed = client.get("/api/runs?node_id=ms-log-test&limit=5")
    assert listed.status_code == 200
    rows = listed.json()
    assert len(rows) >= 1
    row = rows[0]
    assert row["node_id"] == "ms-log-test"
    assert row["status"] == "ok"
    assert row["duration_ms"] >= 0
    assert row["output"]["path"] == "/log"


def test_unknown_node_type_returns_clean_error(client):
    payload = {
        "graph": {
            "nodes": [{"id": "x", "type": "bogus", "data": {"config": {}}}],
            "edges": [],
        }
    }
    resp = client.post("/api/run", json=payload)
    assert resp.status_code == 200
    results = resp.json()["results"]
    assert results[0]["status"] == "error"
    assert "bogus" in (results[0]["error"] or "")
