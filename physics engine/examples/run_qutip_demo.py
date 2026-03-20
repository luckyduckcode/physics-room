"""Example: run a short simulation via QuTiP backend if available.

This script demonstrates how to enable `EngineConfig.use_qutip` and run
`PhysicsEngine.simulate`. It will fall back to the NumPy engine if QuTiP
is not installed.
"""
from physics_engine import EngineConfig, PhysicsEngine
import numpy as np

cfg = EngineConfig(N=12, use_qutip=True)
eng = PhysicsEngine(cfg)
psi0 = np.zeros(cfg.N, dtype=complex)
psi0[0] = 1.0
times = np.linspace(0.0, 0.1, 10)
res = eng.simulate(psi0, times)
print('ran simulation; states shape:', res.states.shape)
print('energies (first 5):', res.energies[:5])
