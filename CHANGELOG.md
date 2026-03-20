# Changelog

All notable changes to this repository will be documented in this file.

## [0.2.0] - 2026-03-20
### Added
- Pluggable Hamiltonian registry and runtime APIs for adding extra Hamiltonian terms.
- Optional QuTiP backend support and SymPy symbolic-check hooks.
- Simple open-system helpers: thermal noise, Lindblad-like damping, and collapse operator plumbing.
- `chem_visualizer` utilities: `AtomicGaussianSplat`, STO-3G effective-alpha support, mesh-to-splats sampler, KDTree vertex mapping, and helpers to update splat coefficients.
- gRPC proto for SplatCloud messages and example client/server/streaming scripts.
- Godot MultiMesh splat renderer and auto-reload script for live visualization.
- Benchmark and example scripts demonstrating harmonic convergence and splat export/streaming.

### Changed
- Bumped package version to `0.2.0`.

### Fixed
- Cleaned duplicate imports and adjusted optional-dependency fallbacks.

### Notes
- Some optional features (QuTiP, SymPy, trimesh, matplotlib) are gated behind optional dependencies; see `pyproject.toml` optional-dependencies for details.
