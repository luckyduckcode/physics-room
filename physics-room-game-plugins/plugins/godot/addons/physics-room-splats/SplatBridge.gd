extends Node3D

@export var ply_file: String = "res://examples/molecule_splats.ply"

func _ready():
    print("Physics Room Splats: ready — ply_file=", ply_file)
    # A minimal placeholder: real implementation should parse the PLY and
    # create a GPUParticles3D + shader to render Gaussian splats.
    _load_placeholder()

func _load_placeholder():
    var label = Label3D.new()
    label.text = "Physics Room Splats: placeholder"
    add_child(label)
