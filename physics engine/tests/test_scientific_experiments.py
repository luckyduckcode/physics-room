from __future__ import annotations

import math
from statistics import mean

from physics_engine.config import EngineConfig
from physics_engine.coordinator import PhysicsRoomCoordinator


def _run_condition(*, session_id: str, lam: float, kappa: float, system_name: str | None = None) -> dict[str, float | int | str]:
    coordinator = PhysicsRoomCoordinator(
        session_id=session_id,
        config=EngineConfig(N=12, dt=0.02, lam=lam, kappa=kappa),
        use_real_modules=False,
        enable_ai=False,
        seed=42,
        system_name=system_name,
    )

    result = coordinator.run_steps(steps=12)

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

    return {
        "session_id": coordinator.session_id,
        "final_tick": result.final_tick,
        "config_hash": coordinator.metadata.config_hash,
        "energy_mean": mean(energy),
        "drift_mean": mean(drift),
        "taxonomy_status": (coordinator.dynamics_taxonomy or {}).get("status", "none"),
    }


def test_condition_matrix_produces_measurable_outputs() -> None:
    baseline = _run_condition(session_id="exp-baseline", lam=0.00, kappa=0.00, system_name="Double Pendulum")
    variant = _run_condition(session_id="exp-variant", lam=0.08, kappa=0.02, system_name="Double Pendulum")

    assert baseline["final_tick"] == 12
    assert variant["final_tick"] == 12

    assert math.isfinite(float(baseline["energy_mean"]))
    assert math.isfinite(float(variant["energy_mean"]))
    assert math.isfinite(float(baseline["drift_mean"]))
    assert math.isfinite(float(variant["drift_mean"]))

    # Scientific condition matrix should encode distinct setup signatures.
    assert baseline["config_hash"] != variant["config_hash"]


def test_experiment_context_keeps_taxonomy_signal() -> None:
    matched = _run_condition(session_id="exp-tax-matched", lam=0.02, kappa=0.01, system_name="Double Pendulum")
    unknown = _run_condition(session_id="exp-tax-unknown", lam=0.02, kappa=0.01, system_name="Unknown XYZ")

    assert matched["taxonomy_status"] == "matched"
    assert unknown["taxonomy_status"] == "not_found"
