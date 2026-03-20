import numpy as np
from typing import List, Dict, Optional

try:
    from plyfile import PlyData, PlyElement
except Exception:  # plyfile may not be installed in all envs
    PlyData = None
    PlyElement = None


class SplatExporter:
    """Export molecules / wavefunction states as Gaussian-splat-friendly PLYs

    This is a compact, self-contained exporter intended to be integrated with
    the existing physics engine instance (passed as `engine`).
    """

    def __init__(self, engine):
        self.engine = engine

    def molecule_to_splats(self, formula: str, state: Optional[np.ndarray] = None) -> List[Dict]:
        atoms = self.engine.chemistry_parser.parse_formula(formula)
        splats: List[Dict] = []
        for i, (symbol, position) in enumerate(atoms):
            # position may be a 3-tuple from the chemistry parser; fall back to linear spacing
            pos = np.array(position) if position is not None else np.array([i * 1.5, 0.0, 0.0])
            alpha = {"H": 0.3, "C": 0.05, "O": 0.08}.get(symbol, 0.1)
            scale = float(alpha * (1.0 + (abs(state[i]) if state is not None and i < len(state) else 0.0)))
            splats.append({
                "x": float(pos[0]),
                "y": float(pos[1]),
                "z": float(pos[2]),
                "scale": scale,
                "color": self._element_rgb(symbol),
                "opacity": 0.9,
            })
        return splats

    def save_as_ply(self, splats: List[Dict], filename: str = "molecule_splats.ply"):
        if PlyElement is None:
            raise RuntimeError("plyfile is not installed; pip install plyfile to enable PLY export")

        vertex_dtype = [("x", "f4"), ("y", "f4"), ("z", "f4"), ("scale", "f4"),
                        ("r", "u1"), ("g", "u1"), ("b", "u1"), ("a", "u1")]
        vertex = np.empty(len(splats), dtype=vertex_dtype)
        for i, s in enumerate(splats):
            r, g, b = s["color"]
            a = int(s.get("opacity", 1.0) * 255)
            vertex[i] = (s["x"], s["y"], s["z"], s["scale"], int(r), int(g), int(b), a)

        el = PlyElement.describe(vertex, "vertex")
        PlyData([el]).write(filename)
        print(f"✅ Saved {len(splats)} atomic splats → {filename}")

    def _element_rgb(self, symbol: str):
        return {"H": (255, 255, 255), "C": (100, 100, 100), "O": (255, 0, 0)}.get(symbol, (200, 200, 200))
