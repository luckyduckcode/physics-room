"""Start the Physics Room gRPC server.

Usage:
    python run_grpc_server.py

Env vars:
    PHYSICS_GRPC_HOST (default: 127.0.0.1)
    PHYSICS_GRPC_PORT (default: 7005)
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

from physics_engine.grpc.server import serve_grpc


HOST = os.getenv("PHYSICS_GRPC_HOST", "127.0.0.1")
PORT = int(os.getenv("PHYSICS_GRPC_PORT", "7005"))
AUTH_KEYS = os.getenv("PHYSICS_GRPC_API_KEYS", "")


if __name__ == "__main__":
    print("Physics Room gRPC Server")
    print(f"Listening: {HOST}:{PORT}")
    print(f"Auth mode: {'api-key' if AUTH_KEYS else 'open'}")
    serve_grpc(host=HOST, port=PORT)
