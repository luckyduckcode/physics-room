from __future__ import annotations

from typing import Any

import numpy as np

from .config import EngineConfig
from .engine import PhysicsEngine


def _to_array(obj: list[list[float]] | list[float]) -> np.ndarray:
    return np.asarray(obj, dtype=float)


def create_app() -> Any:
    """Factory for optional FastAPI app.

    Install extras first:
      pip install -e .[api]
    """
    from fastapi import FastAPI
    from pydantic import BaseModel, Field

    class SimulateRequest(BaseModel):
        N: int = Field(32, gt=2)
        hbar: float = 1.0
        omega: float = 1.0
        phi: float = float(np.e)
        dt: float = Field(0.01, gt=0)
        lam: float = Field(0.0, ge=0)
        kappa: float = Field(0.0, ge=0)

        F: list[float]
        g: list[float]
        h: list[list[float]]

        psi0_real: list[float]
        psi0_imag: list[float]
        times: list[float]

    app = FastAPI(title="Physics Engine API", version="0.1.0")

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok"}

    @app.post("/simulate")
    def simulate(req: SimulateRequest) -> dict[str, Any]:
        cfg = EngineConfig(
            N=req.N,
            hbar=req.hbar,
            omega=req.omega,
            phi=req.phi,
            dt=req.dt,
            lam=req.lam,
            kappa=req.kappa,
            F=_to_array(req.F),
            g=_to_array(req.g),
            h=_to_array(req.h),
        )
        engine = PhysicsEngine(cfg)

        psi0 = _to_array(req.psi0_real) + 1j * _to_array(req.psi0_imag)
        times = _to_array(req.times)

        result = engine.simulate(psi0=psi0, times=times)
        return {
            "times": result.times.tolist(),
            "norms": result.norms.tolist(),
            "energies": result.energies.tolist(),
            "states_real": result.states.real.tolist(),
            "states_imag": result.states.imag.tolist(),
        }

    return app
