#!/usr/bin/env bash
# Generate Python gRPC bindings from .proto files
# Requires: python -m pip install grpcio-tools

set -euo pipefail
PROTO_DIR="../src/physics_engine/grpc"
OUT_DIR="../src/physics_engine/grpc/_generated"

mkdir -p "$OUT_DIR"
python -m grpc_tools.protoc -I "$PROTO_DIR" --python_out="$OUT_DIR" --grpc_python_out="$OUT_DIR" "$PROTO_DIR"/splats.proto

echo "Generated proto bindings in $OUT_DIR"
