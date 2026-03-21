extends Node
class_name RuntimeSplatLoader

@export var ply_path: String = "res://example_splats.ply"
@export var point_size: float = 0.06
@export var max_splats: int = 20000
@export var auto_update_lod: bool = true
@export var lod_update_interval: float = 0.5
@export var shader_path: String = "res://addons/physics_room_splats/shaders/gaussian_splat.shader"

const CHUNK_SIZE := 65535

var _pts = []
var _cols = []
var _alphas = []
var _coeffs = []
var _multimesh_instances: Array = []
var _time_accum: float = 0.0

func _ready() -> void:
    if not ply_path:
        return
    var pts, cols, alphas, coeffs = _parse_ply(ply_path)
    if pts.size() == 0:
        return
    _pts = pts
    _cols = cols
    _alphas = alphas
    _coeffs = coeffs
    refresh_lod()

func _process(delta: float) -> void:
    if not auto_update_lod:
        return
    _time_accum += delta
    if _time_accum >= lod_update_interval:
        _time_accum = 0.0
        refresh_lod()

func _parse_ply(path: String) -> Array:
    var pts = []
    var cols = []
    var alphas = []
    var coeffs = []
    var f = File.new()
    var err = f.open(path, File.READ)
    if err != OK:
        push_error("RuntimeSplatLoader: failed to open %s" % path)
        return [pts, cols, alphas, coeffs]

    var in_header = true
    while not f.eof_reached():
        var line = f.get_line()
        if in_header:
            if line.strip_edges().to_lower() == "end_header":
                in_header = false
            continue
        if line.strip_edges() == "":
            continue
        var parts = line.strip_edges().split(" ")
        if parts.size() < 8:
            continue
        var x = float(parts[0])
        var y = float(parts[1])
        var z = float(parts[2])
        var r = int(parts[3]) / 255.0
        var g = int(parts[4]) / 255.0
        var b = int(parts[5]) / 255.0
        var a = float(parts[6])
        var coeff = float(parts[7])
        pts.append(Vector3(x, y, z))
        cols.append(Color(r, g, b, a))
        alphas.append(a)
        coeffs.append(coeff)

    f.close()
    return [pts, cols, alphas, coeffs]

func refresh_lod() -> void:
    # Select nearest `max_splats` to the current camera (if available)
    var count = _pts.size()
    if count == 0:
        return

    var cam = get_viewport().get_camera_3d()
    var idxs = []
    for i in count:
        idxs.append(i)

    if cam != null:
        var cam_pos = cam.global_transform.origin
        idxs.sort_custom(funcref(self, "_sort_by_distance"), cam_pos)
    # else leave original order

    var use_n = min(max_splats, count)
    var selected = idxs.slice(0, use_n)

    # clear previous multimesh instances
    for m in _multimesh_instances:
        if is_instance_valid(m):
            m.queue_free()
    _multimesh_instances.clear()

    # build chunks
    var i = 0
    while i < selected.size():
        var chunk = selected.slice(i, i + CHUNK_SIZE)
        _build_multimesh_chunk(chunk)
        i += CHUNK_SIZE

func _sort_by_distance(a, b, cam_pos):
    var pa = _pts[a]
    var pb = _pts[b]
    var da = pa.distance_to(cam_pos)
    var db = pb.distance_to(cam_pos)
    return int(sign(da - db))

func _build_multimesh_chunk(indices: Array) -> void:
    var mm = MultiMesh.new()
    mm.transform_format = MultiMesh.TRANSFORM_3D
    mm.color_format = MultiMesh.COLOR_8BIT
    mm.instance_count = indices.size()

    for j in indices.size():
        var idx = indices[j]
        var t = Transform3D()
        t.origin = _pts[idx]
        mm.set_instance_transform(j, t)
        mm.set_instance_color(j, _cols[idx])

    var mmi = MultiMeshInstance3D.new()
    mmi.multimesh = mm

    # prefer shader if available
    var mat_res = null
    if shader_path != "":
        var sh = ResourceLoader.load(shader_path)
        if sh and sh is Shader:
            var sm = ShaderMaterial.new()
            sm.shader = sh
            mat_res = sm

    if mat_res == null:
        var mat = StandardMaterial3D.new()
        mat.flags_unshaded = true
        mat.point_size = point_size
        mat_res = mat

    mmi.material_override = mat_res
    add_child(mmi)
    _multimesh_instances.append(mmi)
