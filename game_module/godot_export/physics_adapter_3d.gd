extends Node3D

@export var entity_scene: PackedScene
var entities := {}
var next_id := 1

func add_entity(position := Vector3.ZERO, mass := 1.0) -> int:
    var ent
    if entity_scene:
        ent = entity_scene.instantiate()
        # assume PackedScene author will set translation/mass
        ent.translation = position
        if ent.has_variable("mass"):
            ent.mass = mass
        add_child(ent)
    else:
        # Create a RigidBody3D for real physics when no PackedScene provided
        var rb := null
        if Engine.has_singleton("RigidBody3D") or true:
            # best-effort creation; Godot will ignore unknown types if running elsewhere
            rb = RigidBody3D.new()
            rb.translation = position
            # set mass if property exists (Godot 4 uses mass via PhysicsBody3D properties)
            if rb.has_variable("mass"):
                rb.mass = mass
            # add a simple visual so entity is visible in editor/runtime
            var mesh = MeshInstance3D.new()
            var sphere = SphereMesh.new()
            sphere.radius = 0.5
            mesh.mesh = sphere
            rb.add_child(mesh)
            add_child(rb)
            ent = rb
        else:
            ent = Node3D.new()
            ent.translation = position
            add_child(ent)
    var id = next_id
    entities[id] = ent
    next_id += 1
    return id

func apply_force(id: int, fx: float, fy: float, fz: float) -> void:
    var ent = entities.get(id, null)
    if ent == null:
        return
    if ent.has_method("apply_force"):
        ent.apply_force(fx, fy, fz)
        return
    # If this is a RigidBody3D, use physics impulses/forces
    if ent is RigidBody3D:
        # Prefer apply_central_impulse if available (impulse-like)
        if ent.has_method("apply_central_impulse"):
            ent.apply_central_impulse(Vector3(fx, fy, fz))
        elif ent.has_method("apply_impulse"):
            ent.apply_impulse(Vector3.ZERO, Vector3(fx, fy, fz))
        elif ent.has_method("add_force"):
            ent.add_force(Vector3(fx, fy, fz), Vector3.ZERO)
        else:
            # last-resort: modify a velocity property if present
            if ent.has_variable("velocity"):
                ent.velocity = ent.velocity + Vector3(fx, fy, fz) / (ent.mass if ent.has_variable("mass") and ent.mass != 0 else 1.0)
        return
    # Generic Node3D fallback
    if ent.has_variable("velocity"):
        ent.velocity = ent.velocity + Vector3(fx, fy, fz) / (ent.mass if ent.has_variable("mass") and ent.mass != 0 else 1.0)

func step(delta: float) -> Dictionary:
    var snap = {}
    for id in entities.keys():
        var e = entities[id]
        var vel = Vector3.ZERO
        if e.has_variable("velocity"):
            vel = e.velocity
        snap[id] = {"position": e.translation, "velocity": vel}
    return snap
