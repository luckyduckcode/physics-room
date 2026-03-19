Godot Export for game_module

This folder contains simple, copy-paste-ready GDScript helpers to integrate
experiment-building and simple physics-driven entities into a Godot project.

How to use

1. Copy the entire `godot_export` folder into your Godot project (for example
   to `res://addons/game_module/` or `res://game_module/`).
2. In the Godot editor, create a new scene and add a `Node` as the root.
3. Add a `Node` child named `PhysicsAdapter` and attach `physics_adapter.gd`.
4. Add a `Node` child named `ExperimentController` and attach
   `experiment_controller.gd`. In the `Inspector`, point the adapter export to the
   `PhysicsAdapter` node if necessary.
5. Create an `Entity` scene using `entity.gd` or use the `add_entity` helper to
   spawn entities at runtime.

Notes

- These scripts implement a minimal, engine-agnostic placeholder integrator
  (position/velocity updates inside `_physics_process`) so you can prototype
  experiments inside Godot without hooking into an external physics engine.
- When you're ready to use the project's physics engine instead of the
  placeholder integrator, adapt `physics_adapter.gd` to create/attach
  `RigidBody2D` or engine-specific bodies and call the engine API instead of
  manual updates.

Files

- `entity.gd`: lightweight entity script (position/velocity/mass + `apply_force`).
- `physics_adapter.gd`: manager that spawns entities and exposes `add_entity`,
  `apply_force`, and `step` helpers.
- `experiment_controller.gd`: example controller exposing experiment variables
  and run/reset lifecycle hooks.
 - `entity_3d.gd`: 3D entity script (translation/velocity/mass + `apply_force`).
 - `physics_adapter_3d.gd`: 3D adapter for spawning `Node3D`-based entities.
 - `experiment_controller_3d.gd`: 3D experiment controller with example lifecycle.

Example copy command (from macOS/Linux terminal):

```bash
cp -R "game_module/godot_export" "/path/to/your/godot/project/res://game_module"
```

3D example

If you prefer 3D, copy the same folder and open `example_experiment_3d.tscn` in
Godot. The 3D scripts use `Node3D` and `Vector3` for translation and forces.

UI

An example UI scene is included: `experiment_ui.tscn` and `experiment_ui.gd`.
It provides simple `Start`/`Stop` buttons and a `Spawn Mass` slider that updates
the `ExperimentController` in the instanced 3D experiment scene. Copy the
`experiment_ui.tscn` to your project and open it in the editor to see the UI.

HTTP Integration (Python server)

A small FastAPI wrapper is provided at `game_module/http_api.py` that exposes a
`POST /simulate` endpoint. It uses `game_module.engine_adapter.PhysicsEngineAdapter`
to run simulations and returns JSON with `times`, `energies`, `norms`, `states_real`,
`states_imag`, and optional `logs`.

Run the server locally (in the project's virtualenv):

```bash
python -m game_module.run_http_api
# or directly with uvicorn:
uvicorn game_module.http_api:app --host 127.0.0.1 --port 8000
```

Godot client example: see `godot_http_client.gd` — it demonstrates using an
`HTTPRequest` node to POST simulation requests and handle JSON responses.
