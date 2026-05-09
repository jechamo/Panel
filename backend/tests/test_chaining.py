"""Verifies that:
- An agent's output_fields drive a strict JSON output validation (without
  calling any real LLM — we monkeypatch the call_llm).
- An agent → microservice chain resolves placeholders against the agent's
  structured output.
"""

import json
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

import pytest


class _Handler(BaseHTTPRequestHandler):
    def do_POST(self):
        n = int(self.headers.get("Content-Length", 0))
        raw = self.rfile.read(n).decode() if n else ""
        try:
            payload = json.loads(raw) if raw else None
        except json.JSONDecodeError:
            payload = raw
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps({"echo": payload}).encode())

    def log_message(self, *a, **k):
        pass


@pytest.fixture(scope="module")
def mock_server():
    server = HTTPServer(("127.0.0.1", 0), _Handler)
    port = server.server_port
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    yield f"http://127.0.0.1:{port}"
    server.shutdown()


def test_agent_to_microservice_chain(monkeypatch, mock_server):
    """The agent returns a hard-coded JSON; the microservice node must
    receive the agent's fields rendered into its body."""
    from app.llm import base as llm_base

    def fake_call_llm(**kwargs):
        # Simulate a provider that returned a perfect JSON matching the schema
        return llm_base.LLMResponse(
            text='{"pais": "Espana", "capital": "Madrid"}',
            provider="anthropic",
            model="claude-sonnet-4-6",
        )

    monkeypatch.setattr("app.runners.agent.call_llm", fake_call_llm)

    from fastapi.testclient import TestClient

    from app.main import app

    client = TestClient(app)
    payload = {
        "graph": {
            "nodes": [
                {
                    "id": "agent1",
                    "type": "agent",
                    "data": {
                        "config": {
                            "provider": "anthropic",
                            "model": "claude-sonnet-4-6",
                            "system_prompt": "x",
                            "user_prompt": "y",
                            "output_fields": [
                                {"name": "pais", "description": "nombre del pais"},
                                {"name": "capital", "description": "capital"},
                            ],
                            "attachments": [],
                        }
                    },
                },
                {
                    "id": "ms1",
                    "type": "microservice",
                    "data": {
                        "config": {
                            "method": "POST",
                            "url": f"{mock_server}/use",
                            "headers": [{"key": "Content-Type", "value": "application/json"}],
                            "body": '{"p": "{{agent1.pais}}", "c": "{{agent1.capital}}"}',
                            "timeout_seconds": 5,
                        }
                    },
                },
            ],
            "edges": [{"source": "agent1", "target": "ms1"}],
        }
    }
    resp = client.post("/api/run", json=payload)
    assert resp.status_code == 200
    results = resp.json()["results"]
    by_id = {r["node_id"]: r for r in results}
    assert by_id["agent1"]["status"] == "ok"
    assert by_id["agent1"]["output"] == {"pais": "Espana", "capital": "Madrid"}
    assert by_id["ms1"]["status"] == "ok"
    assert by_id["ms1"]["output"]["echo"] == {"p": "Espana", "c": "Madrid"}


def test_agent_output_validates_against_schema(monkeypatch):
    """If the model returns an invalid JSON, the agent run reports the error."""
    from app.llm import base as llm_base

    def fake_call_llm(**kwargs):
        return llm_base.LLMResponse(text="this is not JSON", provider="x", model="y")

    monkeypatch.setattr("app.runners.agent.call_llm", fake_call_llm)

    from fastapi.testclient import TestClient

    from app.main import app

    client = TestClient(app)
    resp = client.post(
        "/api/run",
        json={
            "graph": {
                "nodes": [
                    {
                        "id": "a",
                        "type": "agent",
                        "data": {
                            "config": {
                                "provider": "anthropic",
                                "model": "x",
                                "system_prompt": "",
                                "user_prompt": "",
                                "output_fields": [{"name": "k", "description": ""}],
                                "attachments": [],
                            }
                        },
                    }
                ],
                "edges": [],
            }
        },
    )
    out = resp.json()["results"][0]
    # The runner returns a dict with an `_error` key when the model output
    # cannot be parsed/validated, but status stays "ok" because the node
    # itself executed without exceptions.
    assert "_error" in out["output"]
