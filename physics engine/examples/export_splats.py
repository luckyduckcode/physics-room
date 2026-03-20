"""Example exporter: build splats for a molecule and write JSON or send via gRPC.

This script demonstrates using `chem_visualizer.build_molecule_splats` and
exporting the result to a JSON file that can be imported by Godot or a visualizer.
"""
from __future__ import annotations
import json
import argparse
from physics_engine.chem_visualizer import build_molecule_splats


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("formula", help="chemical formula (e.g., H2O)")
    parser.add_argument("--out", default="splats.json")
    args = parser.parse_args()

    splats = build_molecule_splats(args.formula)
    data = [s.to_dict() for s in splats]
    with open(args.out, "w") as f:
        json.dump({"splats": data, "source": "export_splats.py"}, f, indent=2)
    print(f"Wrote {len(data)} splats to {args.out}")


if __name__ == "__main__":
    main()
