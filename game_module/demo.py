from .adapter import PhysicsAdapter
from .entity import Entity


def run_demo(steps: int = 10):
    adapter = PhysicsAdapter()
    e = Entity(id=1, x=0.0, y=0.0)
    adapter.add_entity(e)

    for i in range(steps):
        adapter.apply_force(e.id, 0.0, 9.8)  # small downward force (placeholder)
        state = adapter.step(0.016)
        print(f"step={i} entity_state={state.get(e.id) if isinstance(state, dict) else 'engine-step'}")


if __name__ == "__main__":
    run_demo(60)
