from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
import os
import subprocess
import time
from typing import Any, Literal

from pydantic import BaseModel, Field


EventType = Literal[
    "state.delta",
    "hamiltonian.frame",
    "instrument.trace",
    "ai.anomaly",
    "stability.harmonic",
    "session.lifecycle",
]


class EventEnvelope(BaseModel):
    timestamp: str = Field(..., description="UTC ISO-8601 timestamp")
    session_id: str
    source: str
    event_type: EventType
    sequence: int = Field(..., ge=1)
    payload: dict[str, Any]


class RunMetadata(BaseModel):
    config_hash: str
    code_version: str
    seed: int
    created_at_ns: int


class SessionState(BaseModel):
    session_id: str
    tick: int
    active_voxels: int
    last_energy: float
    stable_voxels: int
    metadata: RunMetadata


class TickRunResult(BaseModel):
    session_id: str
    steps: int
    final_tick: int
    events: list[EventEnvelope]
    metadata: RunMetadata


class StartSessionRequest(BaseModel):
    session_id: str | None = None
    system_name: str | None = None
    N: int = Field(40, gt=2)
    dt: float = Field(0.01, gt=0)
    hbar: float = Field(1.0, gt=0)
    omega: float = Field(1.0, gt=0)
    phi: float = Field(2.718281828, gt=0)
    lam: float = Field(0.0, ge=0)
    kappa: float = Field(0.0, ge=0)
    grid_shape: tuple[int, int, int] = (32, 32, 32)
    enable_ai: bool = False
    use_real_modules: bool = False
    seed: int | None = None


class TickRunRequest(BaseModel):
    steps: int = Field(1, gt=0, le=10_000)


class StartSessionResponse(BaseModel):
    session_id: str
    state: SessionState
    metadata: RunMetadata
    taxonomy: dict[str, Any] | None = None


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def now_ns() -> int:
    return time.time_ns()


def make_config_hash(config: dict[str, Any]) -> str:
    raw = json.dumps(config, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def discover_code_version() -> str:
    env_version = os.getenv("PHYSICS_ROOM_CODE_VERSION")
    if env_version:
        return env_version
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "--short", "HEAD"],
            text=True,
            stderr=subprocess.DEVNULL,
        ).strip()
    except Exception:
        return "unknown"


def make_event(
    *,
    session_id: str,
    source: str,
    event_type: EventType,
    sequence: int,
    payload: dict[str, Any],
) -> EventEnvelope:
    return EventEnvelope(
        timestamp=utc_now_iso(),
        session_id=session_id,
        source=source,
        event_type=event_type,
        sequence=sequence,
        payload=payload,
    )
