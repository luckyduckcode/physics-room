from fastapi.testclient import TestClient

from physics_engine.log_api import create_log_app


def test_session_lifecycle_endpoints() -> None:
    app = create_log_app()
    client = TestClient(app)

    start_resp = client.post(
        "/session/start",
        json={"session_id": "s-api-1", "N": 10, "dt": 0.01, "enable_ai": False},
    )
    assert start_resp.status_code == 200
    body = start_resp.json()
    assert body["session_id"] == "s-api-1"
    assert "metadata" in body
    assert "config_hash" in body["metadata"]
    assert body["metadata"]["seed"] > 0

    tick_resp = client.post("/tick/run?session_id=s-api-1", json={"steps": 2})
    assert tick_resp.status_code == 200
    tick_body = tick_resp.json()
    assert tick_body["final_tick"] == 2
    assert tick_body["session_id"] == "s-api-1"
    assert "metadata" in tick_body

    state_resp = client.get("/session/s-api-1/state")
    assert state_resp.status_code == 200
    assert state_resp.json()["tick"] == 2

    events_resp = client.get("/session/s-api-1/events")
    assert events_resp.status_code == 200
    assert events_resp.json()["count"] >= 1


def test_session_start_accepts_system_name_and_emits_taxonomy() -> None:
    app = create_log_app()
    client = TestClient(app)

    start_resp = client.post(
        "/session/start",
        json={
            "session_id": "s-api-tax",
            "system_name": "Double Pendulum",
            "N": 10,
            "dt": 0.01,
            "enable_ai": False,
        },
    )
    assert start_resp.status_code == 200
    start_body = start_resp.json()
    assert start_body["taxonomy"]["status"] == "matched"
    assert start_body["taxonomy"]["system"] == "Double Pendulum"

    events_resp = client.get("/session/s-api-tax/events")
    assert events_resp.status_code == 200
    body = events_resp.json()
    assert body["count"] >= 1
    first_event = body["events"][0]
    assert first_event["event_type"] == "session.lifecycle"
    assert first_event["payload"]["taxonomy"]["status"] == "matched"
