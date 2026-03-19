#!/usr/bin/env bash
set -euo pipefail

ROOT="/Volumes/USB-HDD/coding projects"
PROTO_DIR="$ROOT/physics engine/src/physics_engine/grpc"

python -m grpc_tools.protoc \
  -I "$PROTO_DIR" \
  --python_out "$PROTO_DIR" \
  --grpc_python_out "$PROTO_DIR" \
  "$PROTO_DIR/physics_room.proto"

echo "Generated gRPC Python modules in $PROTO_DIR"
