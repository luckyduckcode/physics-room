# physics-room-game-plugins

Physics Room + 3D Gaussian Splatting plugins for Godot, Unity, and Unreal — turn quantum simulations into real-time game visuals.

This repository is a plugin-family scaffold that reuses the existing `physics-room` simulation core to export and stream 3D Gaussian splats (atomic/psi visualizations) consumable by game engines.

Structure
```
physics-room-game-plugins/
├── core/
├── plugins/
│   ├── godot/
│   ├── unity/
│   └── unreal/
└── docs/
```

See `core/physics_engine/src/export/splat_exporter.py` for an exporter example and `plugins/godot/addons/physics-room-splats` for a minimal Godot bridge.
