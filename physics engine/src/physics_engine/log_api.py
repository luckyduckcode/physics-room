from __future__ import annotations

import asyncio
import datetime
import math
import os
from typing import Any

import numpy as np
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.responses import PlainTextResponse, StreamingResponse
from pydantic import BaseModel, Field

from .config import EngineConfig
from .contracts import StartSessionRequest, StartSessionResponse, TickRunRequest
from .coordinator import PhysicsRoomCoordinator
from .engine import PhysicsEngine


class SimulateRequest(BaseModel):
    N:         int   = Field(40,  gt=2)
    hbar:      float = Field(1.0, gt=0)
    omega:     float = Field(1.0, gt=0)
    phi:       float = Field(2.718281828, gt=0)
    dt:        float = Field(0.01, gt=0)
    lam:       float = Field(0.0, ge=0)
    kappa:     float = Field(0.0, ge=0)
    t_start:   float = 0.0
    t_end:     float = 10.0
    n_steps:   int   = Field(100, gt=0)
    log_every: int   = Field(10,  gt=0)
    run_name:  str   = "run"
    logs_dir:  str   = "logs"
    psi0_mode: str   = "ground"


def _make_psi0(mode: str, N: int) -> np.ndarray:
    psi = np.zeros(N, dtype=complex)
    if mode == "coherent":
        alpha = 1.0
        for n in range(N):
            psi[n] = (alpha ** n) / math.sqrt(math.factorial(n))
        psi *= math.exp(-0.5 * abs(alpha) ** 2)
    elif mode == "thermal":
        beta    = 1.0
        weights = np.array([math.exp(-beta * n) for n in range(N)])
        psi     = np.sqrt(weights / weights.sum()).astype(complex)
    else:
        psi[0] = 1.0
    return psi / np.linalg.norm(psi)


def _build_engine(req: SimulateRequest) -> tuple[PhysicsEngine, np.ndarray, np.ndarray]:
    cfg    = EngineConfig(N=req.N, hbar=req.hbar, omega=req.omega,
                          phi=req.phi, dt=req.dt, lam=req.lam, kappa=req.kappa)
    engine = PhysicsEngine(cfg)
    psi0   = _make_psi0(req.psi0_mode, req.N)
    times  = np.linspace(req.t_start, req.t_end, req.n_steps)
    return engine, psi0, times


def _save_log(lines: list[str], logs_dir: str, run_name: str) -> str:
    os.makedirs(logs_dir, exist_ok=True)
    ts   = datetime.datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    safe = run_name.strip().replace(" ", "_")
    path = os.path.join(logs_dir, f"{ts}_{safe}.log")
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    return path


def create_log_app() -> FastAPI:
    app = FastAPI(
        title="Physics Engine - Log API",
        description="Localhost data-log server. Terminal-style simulation output.",
        version="1.0.0",
    )
    sessions: dict[str, PhysicsRoomCoordinator] = {}

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok", "service": "physics-engine-log-api"}

    @app.get("/logs")
    def list_logs(logs_dir: str = "logs") -> dict[str, Any]:
        if not os.path.isdir(logs_dir):
            return {"files": [], "count": 0}
        files = sorted(f for f in os.listdir(logs_dir) if f.endswith(".log"))
        return {"files": files, "count": len(files)}

    @app.get("/logs/{filename}", response_class=PlainTextResponse)
    def read_log(filename: str, logs_dir: str = "logs") -> str:
        path = os.path.join(logs_dir, filename)
        if not os.path.isfile(path):
            raise HTTPException(status_code=404, detail="Log file not found")
        return open(path, encoding="utf-8").read()

    @app.post("/simulate/log")
    def simulate_log(req: SimulateRequest) -> dict[str, Any]:
        try:
            engine, psi0, times = _build_engine(req)
            result = engine.simulate_with_logs(psi0, times, log_every=req.log_every)
            return {
                "logs":         result.logs,
                "final_energy": float(result.energies[-1]),
                "final_norm":   float(result.norms[-1]),
                "n_steps":      len(times),
            }
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @app.post("/simulate/log/text", response_class=PlainTextResponse)
    def simulate_log_text(req: SimulateRequest) -> str:
        try:
            engine, psi0, times = _build_engine(req)
            result = engine.simulate_with_logs(psi0, times, log_every=req.log_every)
            return "\n".join(result.logs)
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @app.post("/simulate/log/stream")
    def simulate_log_stream(req: SimulateRequest) -> StreamingResponse:
        try:
            engine, psi0, times = _build_engine(req)
            result = engine.simulate_with_logs(psi0, times, log_every=req.log_every)
            def _gen():
                for line in result.logs:
                    yield line + "\n"
            return StreamingResponse(_gen(), media_type="text/plain")
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @app.post("/simulate/log/save")
    def simulate_log_save(req: SimulateRequest) -> dict[str, Any]:
        try:
            engine, psi0, times = _build_engine(req)
            result = engine.simulate_with_logs(psi0, times, log_every=req.log_every)
            path   = _save_log(result.logs, req.logs_dir, req.run_name)
            return {
                "saved_to":     path,
                "final_energy": float(result.energies[-1]),
                "final_norm":   float(result.norms[-1]),
                "n_steps":      len(times),
                "log_lines":    len(result.logs),
            }
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @app.post("/session/start", response_model=StartSessionResponse)
    def start_session(req: StartSessionRequest) -> StartSessionResponse:
        try:
            session_id = req.session_id or PhysicsRoomCoordinator.new_session_id()
            cfg = EngineConfig(
                N=req.N,
                dt=req.dt,
                hbar=req.hbar,
                omega=req.omega,
                phi=req.phi,
                lam=req.lam,
                kappa=req.kappa,
            )
            coordinator = PhysicsRoomCoordinator(
                session_id=session_id,
                config=cfg,
                system_name=req.system_name,
                grid_shape=req.grid_shape,
                enable_ai=req.enable_ai,
                use_real_modules=req.use_real_modules,
                seed=req.seed,
            )
            sessions[session_id] = coordinator
            return StartSessionResponse(
                session_id=session_id,
                state=coordinator.state(),
                metadata=coordinator.metadata,
                taxonomy=coordinator.dynamics_taxonomy,
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @app.post("/tick/run")
    def run_tick(session_id: str, req: TickRunRequest) -> dict[str, Any]:
        coordinator = sessions.get(session_id)
        if coordinator is None:
            raise HTTPException(status_code=404, detail="Session not found")
        try:
            result = coordinator.run_steps(req.steps)
            return result.model_dump()
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @app.get("/session/{session_id}/state")
    def get_session_state(session_id: str) -> dict[str, Any]:
        coordinator = sessions.get(session_id)
        if coordinator is None:
            raise HTTPException(status_code=404, detail="Session not found")
        return coordinator.state().model_dump()

    @app.get("/session/{session_id}/events")
    def get_session_events(session_id: str, after_sequence: int = 0, limit: int = 500) -> dict[str, Any]:
        coordinator = sessions.get(session_id)
        if coordinator is None:
            raise HTTPException(status_code=404, detail="Session not found")
        selected = [
            e.model_dump() for e in coordinator.events
            if e.sequence > after_sequence
        ][: max(1, min(limit, 5000))]
        return {
            "session_id": session_id,
            "count": len(selected),
            "events": selected,
        }

    @app.websocket("/ws/sessions/{session_id}/events")
    async def stream_session_events(websocket: WebSocket, session_id: str) -> None:
        coordinator = sessions.get(session_id)
        if coordinator is None:
            await websocket.close(code=4404)
            return

        await websocket.accept()
        last_seq = 0
        try:
            while True:
                pending = [e for e in coordinator.events if e.sequence > last_seq]
                for event in pending:
                    await websocket.send_json(event.model_dump())
                    last_seq = event.sequence
                await asyncio.sleep(0.2)
        except WebSocketDisconnect:
            return

    return app
