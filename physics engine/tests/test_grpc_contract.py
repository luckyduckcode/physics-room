from pathlib import Path

import pytest


def test_proto_contract_exists() -> None:
    proto = Path(__file__).resolve().parents[1] / "src" / "physics_engine" / "grpc" / "physics_room.proto"
    assert proto.exists()
    text = proto.read_text(encoding="utf-8")
    assert "service PhysicsRoomService" in text
    assert "message StartSessionRequest" in text
    assert "system_name = 15" in text
    assert "google.protobuf.Struct taxonomy = 7" in text
    assert "google.protobuf.Struct taxonomy = 5" in text


def test_grpc_server_module_importable_after_codegen() -> None:
    pytest.importorskip("grpc")
    proto_mod = pytest.importorskip("physics_engine.grpc.physics_room_pb2")
    grpc_mod = pytest.importorskip("physics_engine.grpc.physics_room_pb2_grpc")

    assert hasattr(proto_mod, "StartSessionRequest")
    assert hasattr(grpc_mod, "PhysicsRoomServiceServicer")
