from physics_engine.contracts import make_event


def test_event_envelope_shape() -> None:
    event = make_event(
        session_id="s1",
        source="unit-test",
        event_type="state.delta",
        sequence=1,
        payload={"tick": 1},
    )

    dumped = event.model_dump()
    assert dumped["session_id"] == "s1"
    assert dumped["event_type"] == "state.delta"
    assert dumped["sequence"] == 1
    assert dumped["payload"]["tick"] == 1
    assert "timestamp" in dumped
