import numpy as np

from physics_engine import EngineConfig, PhysicsEngine


def main() -> None:
    N = 24
    cfg = EngineConfig(
        N=N,
        lam=0.1,
        kappa=0.01,
        F=np.ones(N + 1),
        g=np.zeros(N),
        h=np.zeros((N, N)),
    )

    engine = PhysicsEngine(cfg)
    psi0 = np.zeros(N, dtype=complex)
    psi0[0] = 1.0

    times = np.linspace(0.0, 5.0, 100)
    out = engine.simulate(psi0=psi0, times=times, forcing=lambda t: np.sin(t))

    print("final norm:", out.norms[-1])
    print("final energy:", out.energies[-1])


if __name__ == "__main__":
    main()
