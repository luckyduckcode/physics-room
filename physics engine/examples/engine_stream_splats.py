"""Example: Stream splat coeff updates from an engine by computing per-vertex values.

This script demonstrates using the mapping helpers and writing per-tick JSON updates
that Godot can load. It uses a mock vertex_values callable if the engine does not
provide one.
"""
from __future__ import annotations
import time
import argparse
import numpy as np

from physics_engine.chem_visualizer import (
    build_molecule_splats,
    assign_nearest_vertices,
    update_splat_coeffs_from_vertex_values,
    write_splats_json,
)


def demo_vertex_values_from_coords(vertices: np.ndarray, t: float) -> np.ndarray:
    # Example: a traveling Gaussian on X axis to modulate coeffs
    x = vertices[:, 0]
    vals = np.exp(-((x - (t % 5)) ** 2) / 0.5)
    # normalize to 0..1
    vals = vals - vals.min()
    if vals.max() > 0:
        vals = vals / vals.max()
    return vals


def run_stream(formula: str, outpath: str = 'godot_scene_bundle/splats_received.json', interval: float = 0.5):
    # Build initial splats and a mock vertex array
    splats = build_molecule_splats(formula)
    # For demo, create a fake vertex grid near splat centers
    vertices = np.array([s.center for s in splats])
    if len(vertices) == 0:
        raise SystemExit('No splats generated')

    mapping = assign_nearest_vertices(splats, vertices)

    t = 0.0
    try:
        while True:
            vertex_values = demo_vertex_values_from_coords(vertices, t)
            update_splat_coeffs_from_vertex_values(splats, vertex_values, mapping=mapping)
            write_splats_json(outpath, splats, mapping=mapping)
            print(f'Wrote {len(splats)} splats to {outpath} (t={t:.2f})')
            time.sleep(interval)
            t += interval
    except KeyboardInterrupt:
        print('Stopped')


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('formula')
    p.add_argument('--interval', type=float, default=0.5)
    p.add_argument('--out', default='godot_scene_bundle/splats_received.json')
    args = p.parse_args()
    run_stream(args.formula, outpath=args.out, interval=args.interval)
