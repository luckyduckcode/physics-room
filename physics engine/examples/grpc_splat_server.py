"""Simple gRPC server that accepts SplatCloud messages and prints a short summary.

Run after generating protos:

  cd "physics engine/scripts"
  ./generate_protos.sh
  cd ../examples
  python grpc_splat_server.py

The server listens on localhost:50051 by default.
"""
import time

try:
    from physics_engine.grpc._generated import splats_pb2, splats_pb2_grpc
    import grpc
    from concurrent import futures
except Exception:
    print("Protobuf bindings not generated. Run physics engine/scripts/generate_protos.sh first.")
    raise


class VisualizerServicer(splats_pb2_grpc.VisualizerServicer):
    def SendSplatCloud(self, request, context):
        n = len(request.splats)
        print(f'Received SplatCloud from {request.source_id} with {n} splats')
        # Example: print first splat
        if n:
            s = request.splats[0]
            print('First splat:', s.atom, s.center, s.alpha)
        return splats_pb2.Ack(ok=True, message='Received')


def serve(addr='[::]:50051'):
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=4))
    splats_pb2_grpc.add_VisualizerServicer_to_server(VisualizerServicer(), server)
    server.add_insecure_port(addr)
    server.start()
    print('gRPC server listening on', addr)
    try:
        while True:
            time.sleep(60)
    except KeyboardInterrupt:
        server.stop(0)


if __name__ == '__main__':
    serve()
