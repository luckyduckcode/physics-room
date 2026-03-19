from typing import Any, Optional, List
import os
import concurrent.futures

from fastapi import FastAPI, HTTPException, Request, Depends
from pydantic import BaseModel
from starlette.requests import Request as StarletteRequest
from starlette.middleware.base import BaseHTTPMiddleware

try:
    from .engine_adapter import PhysicsEngineAdapter
except Exception:
    # allow import when module is used outside package
    from game_module.engine_adapter import PhysicsEngineAdapter  # type: ignore

import logging

# configure module logger
logger = logging.getLogger("game_module.http_api")
if not logger.handlers:
    logging.basicConfig(level=logging.INFO)

app = FastAPI(title="Game Module Engine API")

# ASGI middleware to limit request body size (bytes)
MAX_REQUEST_SIZE = int(os.environ.get("GM_MAX_REQUEST_SIZE", 4 * 1024 * 1024))


class BodySizeLimiter(BaseHTTPMiddleware):
    def __init__(self, app, max_body_size: int = MAX_REQUEST_SIZE):
        super().__init__(app)
        self.max_body_size = max_body_size

    async def dispatch(self, request: StarletteRequest, call_next):
        # Quick check using Content-Length header
        cl = request.headers.get("content-length")
        if cl:
            try:
                if int(cl) > self.max_body_size:
                    raise HTTPException(status_code=413, detail="Request body too large")
            except ValueError:
                pass

        body = await request.body()
        if len(body) > self.max_body_size:
            raise HTTPException(status_code=413, detail="Request body too large")

        async def receive():
            return {"type": "http.request", "body": body, "more_body": False}

        new_req = StarletteRequest(request.scope, receive)
        return await call_next(new_req)


app.add_middleware(BodySizeLimiter, max_body_size=MAX_REQUEST_SIZE)


# Limits (configurable via env)
MAX_STATE_LEN = int(os.environ.get("GM_MAX_STATE_LEN", 4096))
MAX_TIMES_LEN = int(os.environ.get("GM_MAX_TIMES_LEN", 10000))
SIM_TIMEOUT = float(os.environ.get("GM_SIM_TIMEOUT", 60.0))


class SimulateRequest(BaseModel):
    psi0_real: List[float]
    psi0_imag: List[float]
    times: List[float]
    overrides: Optional[dict] = None
    simulate_with_logs: Optional[bool] = False


def _check_api_access(request: Request) -> None:
    api_key = os.environ.get("GAME_MODULE_API_KEY")
    client_host = request.client.host if request.client else None
    if api_key:
        header_key = request.headers.get("x-api-key")
        if header_key != api_key:
            raise HTTPException(status_code=401, detail="Invalid API key")
    else:
        if client_host not in ("127.0.0.1", "::1", "localhost"):
            raise HTTPException(status_code=403, detail="Access restricted to localhost")


@app.post("/simulate")
def simulate(req: SimulateRequest, request: Request, _acl: None = Depends(_check_api_access)) -> dict[str, Any]:
    adapter = PhysicsEngineAdapter()

    # basic validation to protect from overly large requests
    if len(req.psi0_real) > MAX_STATE_LEN or len(req.psi0_imag) > MAX_STATE_LEN:
        raise HTTPException(status_code=413, detail=f"psi0 length exceeds {MAX_STATE_LEN}")
    if len(req.times) > MAX_TIMES_LEN:
        raise HTTPException(status_code=413, detail=f"times length exceeds {MAX_TIMES_LEN}")
    if len(req.psi0_real) != len(req.psi0_imag):
        raise HTTPException(status_code=400, detail="psi0_real and psi0_imag must have same length")

    psi0 = [r + 1j * i for r, i in zip(req.psi0_real, req.psi0_imag)]
    times = req.times

    # run the simulation with a timeout to protect the server
    with concurrent.futures.ThreadPoolExecutor(max_workers=1) as ex:
        future = ex.submit(adapter.run_experiment, psi0, times, req.overrides, None, req.simulate_with_logs)
        try:
            res = future.result(timeout=SIM_TIMEOUT)
        except concurrent.futures.TimeoutError:
            future.cancel()
            logger.exception("Simulation timed out")
            raise HTTPException(status_code=504, detail="Simulation timed out")
        except Exception as e:
            logger.exception("Simulation failed")
            raise HTTPException(status_code=500, detail=f"Simulation error: {str(e)}")

    out: dict[str, Any] = {"times": list(map(float, res.times.tolist() if hasattr(res.times, 'tolist') else res.times))}
    if hasattr(res, "energies"):
        out["energies"] = list(map(float, res.energies.tolist()))
    if hasattr(res, "norms"):
        out["norms"] = list(map(float, res.norms.tolist()))
    if hasattr(res, "states"):
        out["states_real"] = res.states.real.tolist()
        out["states_imag"] = res.states.imag.tolist()
    if hasattr(res, "logs") and res.logs is not None:
        out["logs"] = list(res.logs)
    return out
