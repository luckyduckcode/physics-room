from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path
import sys

import numpy as np

if str(Path(__file__).resolve().parents[1] / "src") not in sys.path:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from physics_engine import EngineConfig, PhysicsEngine  # type: ignore[import-not-found]


@dataclass
class BenchmarkResult:
    name: str
    expected: dict[str, float]
    observed: dict[str, float]
    passed: bool


def benchmark_harmonic_ground_state() -> BenchmarkResult:
    cfg = EngineConfig(N=16, dt=0.01, hbar=1.0, omega=1.0, lam=0.0, kappa=0.0)
    engine = PhysicsEngine(cfg)
    psi0 = np.zeros(cfg.N, dtype=complex)
    psi0[0] = 1.0
    times = np.linspace(0.0, 2.0, 100)
    out = engine.simulate(psi0=psi0, times=times)

    mean_energy = float(np.mean(out.energies))
    energy_std = float(np.std(out.energies))
    expected_energy = 1.5

    return BenchmarkResult(
        name="harmonic_ground_state_energy_stability",
        expected={"mean_energy": expected_energy, "energy_std_max": 1e-8},
        observed={"mean_energy": mean_energy, "energy_std": energy_std},
        passed=abs(mean_energy - expected_energy) < 1e-8 and energy_std < 1e-8,
    )


def benchmark_coupling_shift() -> BenchmarkResult:
    N = 16
    psi0 = np.zeros(N, dtype=complex)
    psi0[0] = 1.0
    times = np.linspace(0.0, 2.0, 100)

    baseline = PhysicsEngine(EngineConfig(N=N, dt=0.01, lam=0.0, kappa=0.0)).simulate(psi0=psi0, times=times)
    variant_cfg = EngineConfig(
        N=N,
        dt=0.01,
        lam=0.1,
        kappa=0.02,
        g=np.ones(N),
        h=np.eye(N),
    )
    variant = PhysicsEngine(variant_cfg).simulate(psi0=psi0, times=times, forcing=lambda t: np.sin(t))

    baseline_mean = float(np.mean(baseline.energies))
    variant_mean = float(np.mean(variant.energies))
    delta = variant_mean - baseline_mean

    return BenchmarkResult(
        name="coupling_and_forcing_energy_shift",
        expected={"delta_energy_min": 0.05},
        observed={
            "baseline_mean_energy": baseline_mean,
            "variant_mean_energy": variant_mean,
            "delta_energy": delta,
        },
        passed=delta > 0.05,
    )


def benchmark_norm_conservation() -> BenchmarkResult:
    cfg = EngineConfig(N=20, dt=0.005, lam=0.02, kappa=0.01)
    engine = PhysicsEngine(cfg)
    psi0 = np.zeros(cfg.N, dtype=complex)
    psi0[0] = 1.0
    times = np.linspace(0.0, 3.0, 150)
    out = engine.simulate(psi0=psi0, times=times, forcing=lambda t: 0.2 * np.sin(t))

    max_norm_error = float(np.max(np.abs(out.norms - 1.0)))
    return BenchmarkResult(
        name="norm_conservation_under_forcing",
        expected={"max_norm_error": 1e-10},
        observed={"max_norm_error": max_norm_error},
        passed=max_norm_error < 1e-10,
    )


def benchmark_phi_sensitivity() -> BenchmarkResult:
    N = 16
    psi0 = np.zeros(N, dtype=complex)
    psi0[0] = 1.0
    times = np.linspace(0.0, 2.0, 100)

    e_low = PhysicsEngine(EngineConfig(N=N, dt=0.01, phi=1.2)).simulate(psi0=psi0, times=times).energies
    e_high = PhysicsEngine(EngineConfig(N=N, dt=0.01, phi=3.0)).simulate(psi0=psi0, times=times).energies

    mean_delta = float(abs(np.mean(e_high) - np.mean(e_low)))
    return BenchmarkResult(
        name="phi_parameter_sensitivity",
        expected={"mean_energy_delta_min": 0.01},
        observed={"mean_energy_delta": mean_delta},
        passed=mean_delta > 0.01,
    )


def benchmark_temporal_step_consistency() -> BenchmarkResult:
    N = 14
    psi0 = np.zeros(N, dtype=complex)
    psi0[0] = 1.0

    coarse = PhysicsEngine(EngineConfig(N=N, dt=0.02)).simulate(
        psi0=psi0,
        times=np.linspace(0.0, 2.0, 100),
    )
    fine = PhysicsEngine(EngineConfig(N=N, dt=0.01)).simulate(
        psi0=psi0,
        times=np.linspace(0.0, 2.0, 100),
    )

    delta = float(abs(np.mean(coarse.energies) - np.mean(fine.energies)))
    return BenchmarkResult(
        name="temporal_step_consistency",
        expected={"mean_energy_delta_max": 0.2},
        observed={"mean_energy_delta": delta},
        passed=delta < 0.2,
    )


def run_all_benchmarks() -> list[BenchmarkResult]:
    return [
        benchmark_harmonic_ground_state(),
        benchmark_coupling_shift(),
        benchmark_norm_conservation(),
        benchmark_phi_sensitivity(),
        benchmark_temporal_step_consistency(),
    ]


if __name__ == "__main__":
    results = [asdict(r) for r in run_all_benchmarks()]
    payload = {
        "benchmark_count": len(results),
        "passed_count": sum(1 for r in results if r["passed"]),
        "results": results,
    }
    print(json.dumps(payload, indent=2))
