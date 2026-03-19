# Manifold Physics Engine

A reusable physics engine package designed to be embedded into future projects (rooms/manifolds/simulation services) via a stable Python API.

## Install

```bash
pip install -e .
```

## Quick usage

```python
import numpy as np
from physics_engine import EngineConfig, PhysicsEngine

cfg = EngineConfig(
  N=32,
    hbar=1.0,
    omega=1.0,
    phi=np.e,
  dt=0.01,
  lam=0.1,
  kappa=0.02,
  F=np.ones(33),
  g=np.zeros(32),
  h=np.zeros((32, 32)),
)

engine = PhysicsEngine(cfg)
psi0 = np.zeros(cfg.N, dtype=complex)
psi0[0] = 1.0

times = np.linspace(0.0, 10.0, 200)
result = engine.simulate(psi0=psi0, times=times, forcing=lambda t: np.sin(t))
print(result.states.shape)  # (200, 32)
```

## Public API

- `PhysicsEngine`: build Hamiltonians and run time evolution.
- `EngineConfig`, `CouplingConfig`, `SimulationResult`: typed config/result models.
- `EventEnvelope`, `SessionState`, `TickRunResult`: shared event/session contracts.
- `PhysicsRoomCoordinator`: coordinator adapter for manifold + probes + AI interpreter.
- `create_app()`: direct simulation FastAPI wrapper.
- `create_log_app()`: log + orchestration FastAPI wrapper.

## Optional HTTP API

Create a server:

```python
from physics_engine.api import create_app

app = create_app()
```

Run with:

```bash
uvicorn physics_engine.api:create_app --factory --reload
```

## Localhost APIs

Run localhost service:

```bash
PYTHONPATH=src .venv/bin/uvicorn physics_engine.log_api:create_log_app --factory --host 127.0.0.1 --port 8010
```

### A) Simulation log endpoints

- `GET /health`
- `POST /simulate/log` (JSON array of log lines)
- `POST /simulate/log/text` (plain text terminal-like output)
- `POST /simulate/log/stream` (streamed plain text)
- `POST /simulate/log/save` (writes a timestamped `.log` file and returns the file path)

`/simulate/log/save` accepts optional fields:

- `run_name` (string used in filename)
- `logs_dir` (default: `logs`)

Example save call:

```bash
curl -X POST "http://127.0.0.1:8010/simulate/log/save" \
  -H "Content-Type: application/json" \
  -d @examples/log_request.json
```

### B) Unified orchestration endpoints

- `POST /session/start` — create a simulation session and coordinator
- `POST /tick/run?session_id=<id>` — advance one or more ticks
- `GET /session/{session_id}/state` — current session state
- `GET /session/{session_id}/events` — event stream history
- `WS /ws/sessions/{session_id}/events` — live event feed

`POST /session/start` accepts `use_real_modules` (default `false`).
Set it to `true` to attempt dynamic loading of external manifold/tool modules.
Session metadata is versioned with `config_hash`, `code_version`, `seed`, and `created_at_ns`.

## gRPC Contract

Proto contract: [src/physics_engine/grpc/physics_room.proto](src/physics_engine/grpc/physics_room.proto)

Generate Python stubs:

```bash
chmod +x ../scripts/gen_grpc.sh
../scripts/gen_grpc.sh
```

Run gRPC server:

```bash
PYTHONPATH=src .venv/bin/python run_grpc_server.py
```

Default listener: `127.0.0.1:7005`

Enable API-key auth and namespace isolation:

```bash
export PHYSICS_GRPC_API_KEYS="alpha-secret:team-alpha,beta-secret:team-beta"
PYTHONPATH=src .venv/bin/python run_grpc_server.py
```

Client metadata headers:
- `x-api-key: <key>`
- `x-namespace: <namespace>`

Sessions are namespace-qualified and isolated (`team-alpha:<session_id>`), and cross-namespace access returns `PERMISSION_DENIED`.

## Benchmark Experiments

Known-system credibility checks are in [benchmarks/run_benchmarks.py](benchmarks/run_benchmarks.py):

- Harmonic ground-state energy stability
- Coupling/forcing energy shift sensitivity

Run benchmarks:

```bash
PYTHONPATH=src .venv/bin/python benchmarks/run_benchmarks.py
```

Generate benchmark CSV/plot artifacts:

```bash
PYTHONPATH=src .venv/bin/python benchmarks/generate_report.py
```

Artifacts are written to [benchmarks/reports](benchmarks/reports).

## Metadata Manifest + Replay

Generate a reproducible manifest and event archive:

```bash
PYTHONPATH=src .venv/bin/python examples/run_and_save_manifest.py
```

Replay from manifest:

```bash
PYTHONPATH=src .venv/bin/python examples/replay_from_manifest.py
```

Artifacts are written to [examples/artifacts](examples/artifacts).

## Result Analysis Notebook

Notebook: [../notebooks/results_analysis.ipynb](../notebooks/results_analysis.ipynb)

To produce sample event data for plotting:

```bash
PYTHONPATH=src .venv/bin/python examples/export_events_sample.py
```

Then open the notebook and run all cells.

Event envelope fields:

- `timestamp`
- `session_id`
- `source`
- `event_type`
- `sequence`
- `payload`

## Integration model

The coordinator executes one tick as:

1. Update sparse manifold voxels.
2. Run local physics step and compute energy frame.
3. Run virtual probe scan (STM + spectroscopy).
4. Optionally run AI interpretation.
5. Emit normalized event envelopes for replay and audit.
