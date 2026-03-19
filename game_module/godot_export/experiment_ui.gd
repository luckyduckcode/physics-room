extends Control

@export var experiment_scene: PackedScene
var experiment_instance = null
var controller = null

func _ready() -> void:
    # Instance the 3D experiment scene if not provided
    if experiment_scene:
        experiment_instance = experiment_scene.instantiate()
        add_child(experiment_instance)
        # try find controller inside the instanced scene
        controller = experiment_instance.get_node_or_null("ExperimentController")
    else:
        # fallback: try to find an existing ExperimentController in the scene tree
        controller = get_tree().get_root().find_node("ExperimentController", true, false)

    # Wire UI signals if nodes exist
    if has_node("StartButton"):
        $StartButton.pressed.connect(_on_start_pressed)
    if has_node("StopButton"):
        $StopButton.pressed.connect(_on_stop_pressed)
    if has_node("MassSlider"):
        $MassSlider.connect("value_changed", Callable(self, "_on_mass_changed"))
        _on_mass_changed($MassSlider.value)

func _on_start_pressed() -> void:
    if controller:
        controller.start_experiment()
    else:
        push_error("ExperimentController not found")

func _on_stop_pressed() -> void:
    if controller:
        controller.stop_experiment()

func _on_mass_changed(value: float) -> void:
    if controller:
        controller.spawn_mass = value

func get_log() -> Array:
    if controller:
        return controller.get_log()
    return []
