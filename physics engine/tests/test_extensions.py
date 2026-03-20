import numpy as np
from physics_engine import EngineConfig, PhysicsEngine


def test_add_collapse_and_operator():
    cfg = EngineConfig(N=6)
    eng = PhysicsEngine(cfg)

    A, Ad = __import__('physics_engine').operators.ladder_ops(cfg.N)
    # add as collapse operator
    eng.add_collapse_operator(A)
    assert len(eng.collapse_operators) == 1

    # add as non-unitary operator
    eng.add_non_unitary_operator(A, strength=0.1)
    assert any((mat.shape == (cfg.N, cfg.N)) for (mat, _) in eng.non_unitary_ops)


def test_try_promote_callable_to_operator():
    cfg = EngineConfig(N=5)
    eng = PhysicsEngine(cfg)

    # operator-style callable
    def sample_op(ops, cfg, t):
        x = ops['x']
        return 0.5 * (x @ x)

    promoted = eng.try_promote_callable_to_operator(sample_op)
    assert promoted
    assert len(eng.non_unitary_ops) >= 1


def test_simulate_shapes_with_ops():
    cfg = EngineConfig(N=8)
    eng = PhysicsEngine(cfg)
    A, _ = __import__('physics_engine').operators.ladder_ops(cfg.N)
    eng.add_non_unitary_operator(A, strength=0.02)

    psi0 = np.zeros(cfg.N, dtype=complex)
    psi0[0] = 1.0
    times = np.linspace(0, 0.02, 4)
    res = eng.simulate(psi0, times)
    assert res.states.shape == (len(times), cfg.N)
    assert res.energies.shape == (len(times),)
