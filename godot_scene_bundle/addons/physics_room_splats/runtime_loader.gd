extends Node
class_name RuntimeSplatLoader

@export var ply_path: String = "res://example_splats.ply"
@export var point_size: float = 0.06

var multimesh_instance: MultiMeshInstance3D

func _ready() -> void:
    if not ply_path:
        return
    var pts, cols, alphas, coeffs = _parse_ply(ply_path)
    if pts.size() == 0:
        return
    _create_multimesh(pts, cols)

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

func _create_multimesh(pts: Array, cols: Array) -> void:
    if multimesh_instance and is_instance_valid(multimesh_instance):
        multimesh_instance.queue_free()

    var mm = MultiMesh.new()
    mm.transform_format = MultiMesh.TRANSFORM_3D
    mm.color_format = MultiMesh.COLOR_8BIT
    mm.instance_count = pts.size()

    for i in pts.size():
        var t = Transform3D()
        t.origin = pts[i]
        mm.set_instance_transform(i, t)
        mm.set_instance_color(i, cols[i])

    var mmi = MultiMeshInstance3D.new()
    mmi.multimesh = mm
    var mat = StandardMaterial3D.new()
    mat.flags_unshaded = true
    mat.next_pass = null
    mat.point_size = point_size
    mmi.material_override = mat
    add_child(mmi)
    multimesh_instance = mmi
