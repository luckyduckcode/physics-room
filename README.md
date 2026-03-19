# The Physics Room Workspace

This workspace contains a complete local simulation stack for quantum-classical experiments.

## Workspace Contents
- elements table/
- physics engine/
- room:mainfold/
- tools/

## Core Capabilities
- Hamiltonian-based quantum simulation.
- Chemical formula parsing and molar mass computation.
- Virtual STM and spectroscopy probing.
- AI anomaly event generation.
- Unified session/tick/event API.
- gRPC contract and service implementation.
- Benchmark scenarios for model credibility.
- Notebook-based post-run analysis.

## Start Here
1. Read [physics engine/README.md](physics%20engine/README.md)
2. Read [HOW_TO_USE.md](HOW_TO_USE.md)
3. Review [WHITE_PAPER_PHYSICS_ROOM.md](WHITE_PAPER_PHYSICS_ROOM.md)

## Quick Validation
From [physics engine](physics%20engine):
- Run tests with `PYTHONPATH=src <python> -m pytest`

## Unified API Endpoints
- `POST /session/start`
- `POST /tick/run?session_id=<id>`
- `GET /session/{session_id}/state`
- `GET /session/{session_id}/events`
- `WS /ws/sessions/{session_id}/events`

## Additional Runtime Interfaces
- gRPC proto: [physics engine/src/physics_engine/grpc/physics_room.proto](physics%20engine/src/physics_engine/grpc/physics_room.proto)
- gRPC server launcher: [physics engine/run_grpc_server.py](physics%20engine/run_grpc_server.py)
- Benchmarks: [physics engine/benchmarks/run_benchmarks.py](physics%20engine/benchmarks/run_benchmarks.py)
- Notebook analysis: [notebooks/results_analysis.ipynb](notebooks/results_analysis.ipynb)

## Notes
- `use_real_modules=false` gives stable local fallback behavior.
- `enable_ai=true` enables `ai.anomaly` event emission.
