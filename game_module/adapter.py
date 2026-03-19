from typing import Optional, Any
from dataclasses import dataclass

try:
    # Best-effort import of existing physics engine API in workspace
    from physics_engine import engine as pe_engine  # type: ignore
except Exception:
    pe_engine = None


class PhysicsAdapter:
    """Adapter that exposes a tiny API suitable for game loops.

    Methods are intentionally generic/stubbed so you can wire them to your
    actual physics engine objects (World, Body, etc.).
    """

    def __init__(self, engine: Optional[Any] = None):
        self.engine = engine or pe_engine
        self.world = None
        self._bodies = {}

    def init_world(self, **kwargs):
        """Initialize or reset the physics world using the engine API."""
        if self.engine is None:
            raise RuntimeError("Physics engine not available in environment")
        # Example placeholder call; adapt to your engine's constructor
        if hasattr(self.engine, "World"):
            self.world = self.engine.World(**kwargs)
        else:
            # keep a generic placeholder if engine shape is unknown
            self.world = object()
        return self.world

    def add_entity(self, entity, **body_opts):
        """Add an `Entity` to the physics world and return a body handle.

        `entity` is expected to have `x`, `y`, `mass` attributes — see
        `game_module.entity.Entity`.
        """
        if self.world is None:
            self.init_world()

        # If engine provides a body creation API, call it; otherwise store a stub
        if self.engine and hasattr(self.world, "create_body"):
            body = self.world.create_body(x=entity.x, y=entity.y, mass=entity.mass, **body_opts)  # type: ignore
        else:
            body = {"id": entity.id, "x": entity.x, "y": entity.y, "vx": getattr(entity, "vx", 0.0), "vy": getattr(entity, "vy", 0.0)}
        self._bodies[entity.id] = body
        return body

    def apply_force(self, entity_id, fx: float, fy: float):
        """Apply a force to a body identified by `entity_id`.

        Adapter will call into engine-specific API when available.
        """
        body = self._bodies.get(entity_id)
        if body is None:
            raise KeyError(entity_id)

        if self.engine and hasattr(body, "apply_force"):
            body.apply_force(fx, fy)  # type: ignore
        else:
            # simple Euler-ish velocity update for placeholder bodies
            body.setdefault("vx", 0.0)
            body.setdefault("vy", 0.0)
            body["vx"] += fx / (body.get("mass", 1.0) or 1.0)
            body["vy"] += fy / (body.get("mass", 1.0) or 1.0)

    def step(self, dt: float):
        """Advance the simulation by `dt` seconds."""
        if self.world is None:
            self.init_world()

        if self.engine and hasattr(self.world, "step"):
            return self.world.step(dt)  # type: ignore

        # fallback: integrate placeholder bodies
        for b in self._bodies.values():
            b.setdefault("x", 0.0)
            b.setdefault("y", 0.0)
            b.setdefault("vx", 0.0)
            b.setdefault("vy", 0.0)
            b["x"] += b["vx"] * dt
            b["y"] += b["vy"] * dt
        return self._bodies
