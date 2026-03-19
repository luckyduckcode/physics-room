# How To Use: The Physics Room

## 1) Environment Setup
Use your current virtual environment and install dependencies for the physics engine project.

Recommended project root for commands:
- [physics engine](physics%20engine)

## 2) Run Test Suite
Run the full tests before usage:
- `PYTHONPATH=src <python> -m pytest -q`

## 3) Start the API Server
Start unified API from [physics engine](physics%20engine):
- `PYTHONPATH=src <python> -m uvicorn physics_engine.log_api:create_log_app --factory --host 127.0.0.1 --port 8010`

Optional gRPC stack:
- Generate stubs: `./scripts/gen_grpc.sh`
- Start gRPC server: `PYTHONPATH=src <python> run_grpc_server.py`

Authenticated gRPC mode:
- `export PHYSICS_GRPC_API_KEYS="alpha-secret:team-alpha,beta-secret:team-beta"`
- Start server as above
- Send metadata headers per RPC: `x-api-key`, `x-namespace`

## 4) Create a Session
Call:
- `POST /session/start`

Example payload fields:
- `session_id`
- `N`, `dt`, `hbar`, `omega`, `phi`, `lam`, `kappa`
- `enable_ai`
- `use_real_modules`

## 5) Run Experiment Ticks
Call:
- `POST /tick/run?session_id=<id>`

Payload:
- `steps`

## 6) Inspect State and Events
Call:
- `GET /session/{session_id}/state`
- `GET /session/{session_id}/events`

For live stream:
- `WS /ws/sessions/{session_id}/events`

## 7) Simple Chemistry + Physics Experiment
Suggested baseline:
- Formula: `H2O`
- Parse with [elements table/element_resources.py](elements%20table/element_resources.py)
- Use molar mass and atom counts as metadata in your experiment report.
- Run 3 to 10 ticks and inspect:
  - `hamiltonian.frame` energy trend
  - `stability.harmonic` drift
  - `instrument.trace` peak count
  - `ai.anomaly` (if enabled)

## 8) Common Modes
- Stable local mode:
  - `use_real_modules=false`
- External module mode:
  - `use_real_modules=true`
- AI-enabled mode:
  - `enable_ai=true`

## 9) Troubleshooting
- If imports fail, ensure `PYTHONPATH=src` from [physics engine](physics%20engine).
- If API calls fail, verify server is running on `127.0.0.1:8010`.
- If AI events are missing, confirm `enable_ai=true` and check session events.

## 10) Credibility + Analysis
- Run benchmark checks: `PYTHONPATH=src <python> benchmarks/run_benchmarks.py`
- Export condition matrix CSV/JSON for notebook ingestion: `PYTHONPATH=src <python> benchmarks/export_experiment_matrix.py`
- Export sample events: `PYTHONPATH=src <python> examples/export_events_sample.py`
- Open notebook: [notebooks/results_analysis.ipynb](notebooks/results_analysis.ipynb)

## 11) Immediate Execution Order
1. gRPC smoke (integration):
  - Start server: `PYTHONPATH=src <python> run_grpc_server.py`
  - Run client demo: `PYTHONPATH=src <python> -c "from physics_engine.grpc.client import run_demo; print(run_demo())"`
2. Metadata manifest + replay:
  - `PYTHONPATH=src <python> examples/run_and_save_manifest.py`
  - `PYTHONPATH=src <python> examples/replay_from_manifest.py`
3. Expanded benchmarks + report:
  - `PYTHONPATH=src <python> benchmarks/run_benchmarks.py`
  - `PYTHONPATH=src <python> benchmarks/generate_report.py`
4. Notebook workflow:
  - `PYTHONPATH=src <python> examples/export_events_sample.py`
  - Open [notebooks/results_analysis.ipynb](notebooks/results_analysis.ipynb)
