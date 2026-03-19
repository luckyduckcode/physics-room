# Next Steps Roadmap (Physics Room)

## Current Status Snapshot
Completed:
- Unified HTTP/WebSocket API
- gRPC contract + server/client scaffolding
- Session metadata/versioning (`config_hash`, `code_version`, `seed`, `created_at_ns`)
- Benchmark suite (2 baseline scenarios)
- CI workflow with lint/type/test/benchmark smoke
- Result analysis notebook and event export script

Recent live check:
- In-process gRPC smoke test succeeded (`session_id=grpc-demo`, `final_tick=3`, `events=10`).

---

## Priority 1: Productionize gRPC Path
1. Add integration test that boots `run_grpc_server.py` and validates all RPCs.
2. Add optional auth/interceptor layer for session namespace control.
3. Add retry/backoff behavior in gRPC client helper.
4. Add docs section with protobuf schema evolution policy.

Acceptance:
- gRPC test passes in CI reliably.
- All HTTP DTOs have one-to-one gRPC equivalents.

---

## Priority 2: Data Quality and Reproducibility
1. Persist run metadata with each saved log artifact.
2. Add deterministic seed replay command.
3. Add config snapshot exports per run (JSON manifest).

Acceptance:
- Any run can be replayed from metadata + seed + config manifest.

---

## Priority 3: Benchmark Expansion
Add known references:
1. Coherent-state packet evolution sanity check.
2. Thermal-like initial state decay profile check.
3. Parameter sweep benchmark (`lam`, `kappa`, `phi`) with trend assertions.

Acceptance:
- At least 5 benchmark scenarios with threshold assertions.

---

## Priority 4: Analysis Automation
1. Add auto-generated benchmark report (CSV + PNG plots).
2. Add notebook-to-static export (HTML artifact) in CI.
3. Add per-condition comparison plots (baseline vs variants).

Acceptance:
- Running one command produces metrics table and plots automatically.

---

## Priority 5: Release Hardening
1. Add pre-commit hooks (`ruff`, `mypy`, `pytest -q`).
2. Add semantic version tagging and changelog automation.
3. Add package health checks for macOS/Linux CI matrix.

Acceptance:
- Tagged release pipeline can produce reproducible build and test evidence.

---

## Suggested Immediate Sprint (2-3 days)
- Day 1: gRPC integration test + client retry/backoff.
- Day 2: metadata manifests + replay utility.
- Day 3: benchmark expansion + automated report generation.
