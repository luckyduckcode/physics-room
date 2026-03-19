from __future__ import annotations

import time
from typing import Any

import grpc

from . import physics_room_pb2 as pb2
from . import physics_room_pb2_grpc as pb2_grpc


def call_with_retry(
    rpc_call,
    request,
    *,
    metadata: list[tuple[str, str]] | None = None,
    timeout: float | None = None,
    retries: int = 5,
    initial_backoff: float = 0.1,
    max_backoff: float = 1.0,
):
    attempt = 0
    backoff = initial_backoff
    while True:
        try:
            kwargs = {}
            if metadata is not None:
                kwargs["metadata"] = metadata
            if timeout is not None:
                kwargs["timeout"] = timeout
            return rpc_call(request, **kwargs)
        except grpc.RpcError as exc:
            code = exc.code()
            transient = code in {
                grpc.StatusCode.UNAVAILABLE,
                grpc.StatusCode.DEADLINE_EXCEEDED,
                grpc.StatusCode.RESOURCE_EXHAUSTED,
            }
            if (not transient) or attempt >= retries:
                raise
            time.sleep(backoff)
            backoff = min(max_backoff, backoff * 2.0)
            attempt += 1


class PhysicsRoomGrpcClient:
    def __init__(self, host: str = "127.0.0.1", port: int = 7005) -> None:
        self._channel = grpc.insecure_channel(f"{host}:{port}")
        self._stub = pb2_grpc.PhysicsRoomServiceStub(self._channel)

    def close(self) -> None:
        self._channel.close()

    def start_session(
        self,
        *,
        session_id: str = "grpc-demo",
        system_name: str | None = None,
        N: int = 12,
        steps: int = 3,
        metadata: list[tuple[str, str]] | None = None,
    ):
        start_req = pb2.StartSessionRequest(
            config=pb2.SessionConfig(
                session_id=session_id,
                system_name=system_name or "",
                N=N,
                dt=0.02,
                lam=0.05,
                kappa=0.01,
                phi=2.718281828,
                omega=1.0,
                hbar=1.0,
                enable_ai=False,
                use_real_modules=False,
                seed=42,
                grid_x=32,
                grid_y=32,
                grid_z=32,
            )
        )
        start = call_with_retry(self._stub.StartSession, start_req, metadata=metadata)
        run = call_with_retry(
            self._stub.TickRun,
            pb2.TickRunRequest(session_id=start.session_id, steps=steps),
            metadata=metadata,
        )
        state = call_with_retry(
            self._stub.GetSessionState,
            pb2.GetSessionStateRequest(session_id=start.session_id),
            metadata=metadata,
        )
        events = call_with_retry(
            self._stub.GetSessionEvents,
            pb2.GetSessionEventsRequest(session_id=start.session_id, after_sequence=0, limit=10),
            metadata=metadata,
        )
        return start, run, state, events


def run_demo(
    host: str = "127.0.0.1",
    port: int = 7005,
    metadata: list[tuple[str, str]] | None = None,
) -> dict[str, Any]:
    client = PhysicsRoomGrpcClient(host=host, port=port)
    try:
        start, run, state, events = client.start_session(
            session_id="grpc-demo",
            N=12,
            steps=3,
            metadata=metadata,
        )
        return {
            "session_id": start.session_id,
            "final_tick": run.final_tick,
            "active_voxels": state.state.active_voxels,
            "events": len(events.events),
        }
    finally:
        client.close()
