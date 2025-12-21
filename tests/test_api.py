import pytest
from fastapi.testclient import TestClient

import src.api.main as main_mod


def test_health_endpoint():
    client = TestClient(main_mod.app)
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"


@pytest.mark.asyncio
async def test_analyze_endpoint_mocked_pipeline(monkeypatch):
    async def fake_analyze(content_id: str, text: str):
        return {
            "content_id": content_id,
            "decision": {
                "label": "flag",
                "confidence": 0.77,
                "reasons": ["Mocked pipeline decision for tests."],
            },
        }

    # Patch the pipeline used by FastAPI module
    monkeypatch.setattr(main_mod.pipeline, "analyze", fake_analyze)

    client = TestClient(main_mod.app)
    payload = {"id": "t1", "text": "some text"}
    resp = client.post("/analyze", json=payload)

    assert resp.status_code == 200
    data = resp.json()
    assert data["content_id"] == "t1"
    assert data["decision"]["label"] == "flag"
    assert 0.0 <= data["decision"]["confidence"] <= 1.0
    assert isinstance(data["decision"]["reasons"], list)
