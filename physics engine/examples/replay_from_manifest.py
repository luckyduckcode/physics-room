from __future__ import annotations

import json
from pathlib import Path
import sys

if str(Path(__file__).resolve().parents[1] / "src") not in sys.path:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from physics_engine.config import EngineConfig  # type: ignore[import-not-found]
from physics_engine.coordinator import PhysicsRoomCoordinator  # type: ignore[import-not-found]


def main() -> None:
    manifest_path = Path(__file__).parent / "artifacts" / "manifest-demo.json"
    if not manifest_path.exists():
        raise SystemExit(f"Manifest not found: {manifest_path}")

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    cfg_data = manifest["config"]
    meta = manifest["metadata"]

    coordinator = PhysicsRoomCoordinator(
        session_id=f"{manifest['session_id']}-replay",
        config=EngineConfig(
            N=int(cfg_data["N"]),
            dt=float(cfg_data["dt"]),
            hbar=float(cfg_data["hbar"]),
            omega=float(cfg_data["omega"]),
            phi=float(cfg_data["phi"]),
            lam=float(cfg_data["lam"]),
            kappa=float(cfg_data["kappa"]),
        ),
        grid_shape=tuple(cfg_data["grid_shape"]),
        enable_ai=bool(cfg_data["enable_ai"]),
        use_real_modules=bool(cfg_data["use_real_modules"]),
        seed=int(meta["seed"]),
    )

    steps = int(manifest.get("steps_run", 10))
    result = coordinator.run_steps(steps)

    replay = coordinator.manifest()
    print(json.dumps(
        {
            "original_config_hash": meta["config_hash"],
            "replay_config_hash": replay["metadata"]["config_hash"],
            "config_match": meta["config_hash"] == replay["metadata"]["config_hash"],
            "steps": steps,
            "replay_final_tick": result.final_tick,
        },
        indent=2,
    ))


if __name__ == "__main__":
    main()
