# AtomicSplatRenderer.gd
extends Node3D

@export var splat_data := []

var particles: GPUParticles3D

func _ready():
    setup_splats()

func setup_splats():
    particles = GPUParticles3D.new()
    add_child(particles)

    var mat = StandardMaterial3D.new()
    mat.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
    mat.albedo_color = Color(1,1,1)
    mat.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA

    var shader = Shader.new()
    shader.code = """
shader_type spatial;
render_mode unshaded, blend_mix, depth_draw_alpha_prepass;
uniform vec4 color : source_color;
void fragment() {
    // UV assumed in [0,1]^2 on a quad mesh
    float dx = UV.x - 0.5;
    float dy = UV.y - 0.5;
    float dist2 = dx*dx + dy*dy;
    float a = exp(-dist2 * 12.0);
    ALBEDO = color.rgb;
    ALPHA = a * color.a;
}
"""
    mat.shader = shader

    var mesh = QuadMesh.new()
    mesh.size = Vector2(0.2, 0.2)

    particles.amount = len(splat_data)
    particles.mesh = mesh
    particles.material_override = mat
    particles.process_material = ParticlesMaterial.new()
    particles.process_material.emission_shape = ParticlesMaterial.EMISSION_SHAPE_POINTS

    for i in range(len(splat_data)):
        var d = splat_data[i]
        var t = Transform3D()
        var scale = float(d.get("alpha", 0.1)) * 2.0
        t.basis = Basis.IDENTITY.scaled(Vector3(scale, scale, scale))
        var c = d.get("center", [0,0,0])
        t.origin = Vector3(c[0], c[1], c[2])
        particles.set_instance_transform(i, t)
        # per-instance color would require a MultiMesh or shader with per-instance attributes

func set_splats_from_json(path: String):
    var f = File.new()
    if f.open(path, File.READ) != OK:
        push_error("Could not open " + path)
        return
    var data = parse_json(f.get_as_text())
    if typeof(data) == TYPE_DICTIONARY and data.has("splats"):
        splat_data = data["splats"]
        if particles:
            particles.queue_free()
        setup_splats()
