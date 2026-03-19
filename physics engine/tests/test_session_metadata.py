from physics_engine.config import EngineConfig
from physics_engine.coordinator import PhysicsRoomCoordinator


def test_session_has_metadata_and_seed() -> None:
    coordinator = PhysicsRoomCoordinator(
        session_id="meta-session",
        config=EngineConfig(N=12, dt=0.02),
        use_real_modules=False,
        enable_ai=False,
        seed=123,
    )

    meta = coordinator.metadata
    assert isinstance(meta.config_hash, str) and len(meta.config_hash) == 64
    assert isinstance(meta.code_version, str) and len(meta.code_version) > 0
    assert meta.seed == 123
    assert meta.created_at_ns > 0

    state = coordinator.state()
    assert state.metadata.seed == 123


def test_tick_result_contains_metadata() -> None:
    coordinator = PhysicsRoomCoordinator(
        session_id="meta-session-2",
        config=EngineConfig(N=10, dt=0.01),
        use_real_modules=False,
        seed=42,
    )
    result = coordinator.run_steps(2)
    assert result.metadata.seed == 42
    assert result.metadata.config_hash == coordinator.metadata.config_hash
