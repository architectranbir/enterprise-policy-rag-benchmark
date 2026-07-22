from fastapi.testclient import TestClient

from policy_rag.api.app import create_app


def test_health_reports_unconfigured_without_claiming_readiness() -> None:
    client = TestClient(create_app())
    assert client.get("/health").json() == {"status": "ok", "backend": "unconfigured"}
    assert client.get("/ready").status_code == 503


def test_ask_rejects_unconfigured_service() -> None:
    response = TestClient(create_app()).post(
        "/ask",
        json={
            "question": "What is the policy?",
            "as_of": "2026-01-01",
        },
        headers={
            "X-Authenticated-User-ID": "u1",
            "X-Authenticated-User-Groups": "employees",
        },
    )
    assert response.status_code == 503
