extends Node

@export var splat_json_path: String = "res://splats_received.json"
@export var renderer_path: NodePath = NodePath("../AtomicSplatMultimeshRenderer")
@export var poll_interval: float = 0.5

var _last_text: String = ""
var _timer: Timer

func _ready():
    _timer = Timer.new()
    _timer.wait_time = poll_interval
    _timer.one_shot = false
    _timer.autostart = true
    add_child(_timer)
    _timer.connect("timeout", Callable(self, "_on_poll"))

func _on_poll():
    var f = File.new()
    var path = splat_json_path
    if not f.file_exists(path):
        return
    if f.open(path, File.READ) != OK:
        return
    var text = f.get_as_text()
    f.close()
    if text == _last_text:
        return
    _last_text = text
    var data = parse_json(text)
    if typeof(data) != TYPE_DICTIONARY:
        return
    # Find renderer and call its loader
    var renderer = get_node_or_null(renderer_path)
    if renderer and renderer.has_method("set_splats_from_json"):
        # write a temporary file in project path and call loader
        # the renderer expects a res:// path; the JSON file should be inside the project
        renderer.set_splats_from_json(splat_json_path.replace("res://", ""))
