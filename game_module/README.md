# game_module

Scaffold module to integrate the project's physics engine with a simple game-style
entity loop.

- `adapter.py` — small adapter class (`PhysicsAdapter`) that provides `init_world`,
  `add_entity`, `apply_force`, and `step` methods. Stubs fall back to a simple
  placeholder integrator when an engine is not present.
- `entity.py` — lightweight `Entity` dataclass for position/velocity/mass.
- `demo.py` — runnable demo showing how to create an adapter, add an entity,
  apply a force, and step the simulation.

Usage:

```bash
python -m game_module.demo
```

Adapt the adapter methods to match the real physics engine API in
`physics engine/src/physics_engine` when ready.
