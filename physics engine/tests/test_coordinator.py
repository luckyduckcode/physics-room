from physics_engine.config import EngineConfig
from physics_engine.coordinator import PhysicsRoomCoordinator


def test_coordinator_runs_ticks() -> None:
    coordinator = PhysicsRoomCoordinator(
        session_id="test-session",
        config=EngineConfig(N=12, dt=0.01),
        use_real_modules=False,
        enable_ai=False,
    )

    out = coordinator.run_steps(3)
    assert out.final_tick == 3
    assert len(out.events) >= 3

    state = coordinator.state()
    assert state.tick == 3
    assert state.active_voxels >= 1


def test_coordinator_emits_lifecycle_event() -> None:
    coordinator = PhysicsRoomCoordinator(
        session_id="test-session-2",
        config=EngineConfig(N=8, dt=0.01),
        use_real_modules=False,
    )
    assert len(coordinator.events) >= 1
    assert coordinator.events[0].event_type == "session.lifecycle"


def test_coordinator_attaches_dynamics_taxonomy_when_system_name_given() -> None:
    coordinator = PhysicsRoomCoordinator(
        session_id="test-session-taxonomy",
        config=EngineConfig(N=8, dt=0.01),
        use_real_modules=False,
        system_name="Double Pendulum",
    )

    manifest = coordinator.manifest()
    taxonomy = manifest.get("dynamics_taxonomy")
    assert taxonomy is not None
    assert taxonomy["status"] == "matched"
    assert taxonomy["system"] == "Double Pendulum"

    lifecycle = coordinator.events[0]
    assert lifecycle.payload.get("taxonomy", {}).get("status") == "matched"
