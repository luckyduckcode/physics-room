from __future__ import annotations

import json
from pathlib import Path
import sys

if str(Path(__file__).resolve().parents[1] / "src") not in sys.path:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from physics_engine.config import EngineConfig  # type: ignore[import-not-found]
from physics_engine.coordinator import PhysicsRoomCoordinator  # type: ignore[import-not-found]


def main() -> None:
    out_dir = Path(__file__).parent / "artifacts"
    out_dir.mkdir(parents=True, exist_ok=True)

    coordinator = PhysicsRoomCoordinator(
        session_id="manifest-demo",
        config=EngineConfig(N=12, dt=0.02, lam=0.05, kappa=0.01),
        use_real_modules=False,
        enable_ai=True,
        seed=42,
    )
    result = coordinator.run_steps(10)

    manifest = coordinator.manifest()
    manifest["steps_run"] = result.steps
    manifest["final_tick"] = result.final_tick

    events = [e.model_dump() for e in coordinator.events]

    manifest_path = out_dir / "manifest-demo.json"
    events_path = out_dir / "manifest-demo-events.json"
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    events_path.write_text(json.dumps(events, indent=2), encoding="utf-8")

    print(f"Wrote {manifest_path}")
    print(f"Wrote {events_path}")


if __name__ == "__main__":
    main()
