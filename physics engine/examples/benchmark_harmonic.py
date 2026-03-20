"""Run a quick benchmark comparing `build_H` eigenvalues to analytic harmonic oscillator energies."""
import numpy as np
from physics_engine.config import EngineConfig
from physics_engine.hamiltonian import build_H
cfg = EngineConfig(N=30, hbar=1.0, omega=1.0)

# Default build_H (may include extra terms from config defaults)
H_full = build_H(N=cfg.N, hbar=cfg.hbar, omega=cfg.omega, phi=cfg.phi, F=cfg.F, g=cfg.g, h=cfg.h)
evals_full = np.linalg.eigvalsh(H_full)

# Pure harmonic construction using build_H by setting F such that
# H = hbar*omega*(0.5 * I + Ad A)
F_pure = np.zeros(cfg.N + 1)
F_pure[1] = 0.5
F_pure[2] = 1.0
H_pure = build_H(N=cfg.N, hbar=cfg.hbar, omega=cfg.omega, phi=1.0, F=F_pure, g=np.zeros(cfg.N), h=np.zeros((cfg.N, cfg.N)))
evals_pure = np.linalg.eigvalsh(H_pure)

n = np.arange(min(6, len(evals_pure)))
analytic = cfg.hbar * cfg.omega * (n + 0.5)

print('--- Full build_H lowest eigenvalues (may include extra terms) ---')
print(np.round(evals_full[:6], 8))
print('\n--- Pure build_H (configured to HO) lowest eigenvalues ---')
print(np.round(evals_pure[:6], 8))
print('\n--- Analytic HO energies ---')
print(np.round(analytic[:6], 8))
print('\n--- Relative differences (pure vs analytic) ---')
print(np.round(np.abs(evals_pure[:6] - analytic[:6]) / (np.abs(analytic[:6]) + 1e-12), 8))
