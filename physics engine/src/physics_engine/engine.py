from __future__ import annotations

from typing import Callable, Optional

import numpy as np
from scipy.linalg import expm

from .config import EngineConfig, SimulationResult
from .hamiltonian import build_H


class PhysicsEngine:
    def __init__(self, config: EngineConfig) -> None:
        self.config = config

    def _build_H(self, t: float, forcing: Optional[Callable] = None) -> np.ndarray:
        f_t = float(forcing(t)) if forcing else 0.0
        c = self.config
        return build_H(
            N=c.N, hbar=c.hbar, omega=c.omega, phi=c.phi,
            F=c.F, g=c.g, h=c.h,
            lam=c.lam, kappa=c.kappa, Vcosmo=c.Vcosmo, f_t=f_t,
        )

    def simulate(
        self,
        psi0: np.ndarray,
        times: np.ndarray,
        forcing: Optional[Callable] = None,
    ) -> SimulationResult:
        N = self.config.N
        assert psi0.shape == (N,), f"psi0 must have shape ({N},)"
        psi = psi0.astype(complex).copy()
        psi /= np.linalg.norm(psi)

        states   = np.zeros((len(times), N), dtype=complex)
        energies = np.zeros(len(times))
        norms    = np.zeros(len(times))

        for i, t in enumerate(times):
            H = self._build_H(t, forcing)
            psi = expm(-1j * H * self.config.dt / self.config.hbar) @ psi
            psi /= np.linalg.norm(psi)
            states[i]   = psi
            energies[i] = float(np.real(psi.conj() @ H @ psi))
            norms[i]    = float(np.linalg.norm(psi))

        return SimulationResult(times=times, states=states, energies=energies, norms=norms)

    def simulate_with_logs(
        self,
        psi0: np.ndarray,
        times: np.ndarray,
        forcing: Optional[Callable] = None,
        log_every: int = 1,
        energy_threshold: float = None,
        norm_threshold: float = None,
    ) -> SimulationResult:
        N  = self.config.N
        c  = self.config
        assert psi0.shape == (N,), f"psi0 must have shape ({N},)"
        psi = psi0.astype(complex).copy()
        psi /= np.linalg.norm(psi)

        states   = np.zeros((len(times), N), dtype=complex)
        energies = np.zeros(len(times))
        norms    = np.zeros(len(times))
        logs: list[str] = []

        logs.append("=" * 64)
        logs.append("  PHYSICS ENGINE  -  SIMULATION START")
        logs.append("=" * 64)
        logs.append(f"  dim N     : {c.N}")
        logs.append(f"  dt        : {c.dt}")
        logs.append(f"  hbar      : {c.hbar}   omega : {c.omega}   phi : {c.phi:.6f}")
        logs.append(f"  lambda    : {c.lam}   kappa : {c.kappa}")
        logs.append(f"  steps     : {len(times)}")
        logs.append("=" * 64)
        logs.append(f"  {'step':>6}  {'t':>10}  {'energy':>14}  {'norm':>10}  {'peak |n>':>8}")
        logs.append("-" * 64)

        for i, t in enumerate(times):
            H   = self._build_H(t, forcing)
            psi = expm(-1j * H * c.dt / c.hbar) @ psi
            psi /= np.linalg.norm(psi)
            energy = float(np.real(psi.conj() @ H @ psi))
            norm   = float(np.linalg.norm(psi))

            states[i]   = psi
            energies[i] = energy
            norms[i]    = norm

            threshold_msgs = []
            if energy_threshold is not None and abs(energy) > energy_threshold:
                threshold_msgs.append(f"[THRESHOLD PASSED] step={i} t={t:.4f} energy={energy:.8f} > {energy_threshold}")
            if norm_threshold is not None and abs(norm) > norm_threshold:
                threshold_msgs.append(f"[THRESHOLD PASSED] step={i} t={t:.4f} norm={norm:.8f} > {norm_threshold}")

            if i % log_every == 0:
                peak_n = int(np.argmax(np.abs(psi) ** 2))
                logs.append(
                    f"  {i:>6}  {t:>10.4f}  {energy:>14.8f}  {norm:>10.8f}  {peak_n:>8}"
                )
                logs.extend(threshold_msgs)
            elif threshold_msgs:
                logs.extend(threshold_msgs)

        logs.append("=" * 64)
        logs.append("  SIMULATION COMPLETE")
        logs.append(f"  final energy : {energies[-1]:.8f}")
        logs.append(f"  final norm   : {norms[-1]:.8f}")
        logs.append("=" * 64)

        return SimulationResult(
            times=times, states=states, energies=energies, norms=norms, logs=logs
        )

    @staticmethod
    def expectation(states: np.ndarray, operator: np.ndarray) -> np.ndarray:
        return np.real(np.einsum("bi,ij,bj->b", states.conj(), operator, states))
