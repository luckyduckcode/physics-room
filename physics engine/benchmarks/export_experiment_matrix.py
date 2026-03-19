from __future__ import annotations

from dataclasses import dataclass
import csv
import json
from pathlib import Path
from statistics import mean, pstdev
import sys
from typing import Any

if str(Path(__file__).resolve().parents[1] / "src") not in sys.path:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from physics_engine.config import EngineConfig  # type: ignore[import-not-found]
from physics_engine.coordinator import PhysicsRoomCoordinator  # type: ignore[import-not-found]


@dataclass(frozen=True)
class ExperimentCondition:
    name: str
    lam: float
    kappa: float


def run_condition_matrix(
    conditions: list[ExperimentCondition],
    *,
    steps: int = 20,
    system_name: str | None = "Double Pendulum",
    seed: int = 42,
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []

    for cond in conditions:
        coordinator = PhysicsRoomCoordinator(
            session_id=f"matrix-{cond.name}",
            config=EngineConfig(N=12, dt=0.02, lam=cond.lam, kappa=cond.kappa),
            use_real_modules=False,
            enable_ai=False,
            seed=seed,
            system_name=system_name,
        )
        result = coordinator.run_steps(steps)

        energy = [
            float(e.payload["energy"])
            for e in result.events
            if e.event_type == "hamiltonian.frame"
        ]
        drift = [
            float(e.payload["drift"])
            for e in result.events
            if e.event_type == "stability.harmonic"
        ]

        rows.append(
            {
                "condition": cond.name,
                "lam": cond.lam,
                "kappa": cond.kappa,
                "steps": result.steps,
                "final_tick": result.final_tick,
                "event_count": len(result.events),
                "energy_mean": mean(energy) if energy else 0.0,
                "energy_std": pstdev(energy) if len(energy) > 1 else 0.0,
                "drift_mean": mean(drift) if drift else 0.0,
                "drift_std": pstdev(drift) if len(drift) > 1 else 0.0,
                "config_hash": coordinator.metadata.config_hash,
                "taxonomy_status": (coordinator.dynamics_taxonomy or {}).get("status", "none"),
                "taxonomy_system": (coordinator.dynamics_taxonomy or {}).get("system", ""),
            }
        )

    return rows


def write_condition_matrix_csv(rows: list[dict[str, Any]], out_path: Path) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        out_path.write_text("", encoding="utf-8")
        return

    fieldnames = list(rows[0].keys())
    with out_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def write_condition_matrix_json(rows: list[dict[str, Any]], out_path: Path) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(rows, indent=2), encoding="utf-8")


def main() -> None:
    conditions = [
        ExperimentCondition("baseline", lam=0.00, kappa=0.00),
        ExperimentCondition("condition_a", lam=0.05, kappa=0.00),
        ExperimentCondition("condition_b", lam=0.05, kappa=0.01),
        ExperimentCondition("condition_c", lam=0.10, kappa=0.01),
    ]

    rows = run_condition_matrix(conditions, steps=20)

    out_dir = Path(__file__).parent / "reports"
    csv_path = out_dir / "experiment_condition_matrix.csv"
    json_path = out_dir / "experiment_condition_matrix.json"

    write_condition_matrix_csv(rows, csv_path)
    write_condition_matrix_json(rows, json_path)

    print(f"Wrote {csv_path}")
    print(f"Wrote {json_path}")


if __name__ == "__main__":
    main()
