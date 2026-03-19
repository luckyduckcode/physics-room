from __future__ import annotations

import json
from pathlib import Path

from fastapi.testclient import TestClient

from physics_engine.log_api import create_log_app


def main() -> None:
    app = create_log_app()
    client = TestClient(app)

    session_id = "notebook-sample"
    client.post(
        "/session/start",
        json={
            "session_id": session_id,
            "N": 12,
            "dt": 0.02,
            "lam": 0.05,
            "kappa": 0.01,
            "enable_ai": True,
            "use_real_modules": False,
            "seed": 42,
        },
    )
    client.post(f"/tick/run?session_id={session_id}", json={"steps": 10})
    data = client.get(f"/session/{session_id}/events?after_sequence=0&limit=500").json()

    out_path = Path(__file__).parent / "events_sample.json"
    out_path.write_text(json.dumps(data.get("events", []), indent=2), encoding="utf-8")
    print(f"Wrote {out_path}")


if __name__ == "__main__":
    main()
