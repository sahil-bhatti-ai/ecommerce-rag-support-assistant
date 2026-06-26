from fastapi.testclient import TestClient

from app.main import create_app


def test_openapi_contract_exposes_core_endpoints() -> None:
    client = TestClient(create_app())
    schema = client.get("/openapi.json").json()
    paths = schema["paths"]

    assert "/upload" in paths
    assert "/chat" in paths
    assert "/sessions" in paths
    assert "/health" in paths
    assert "/admin/documents" in paths
