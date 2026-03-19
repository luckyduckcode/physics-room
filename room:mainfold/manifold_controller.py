from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from math import pi, sqrt
from typing import Callable, Dict, Iterable, List, Optional, Tuple


Vec3 = Tuple[int, int, int]


class BoundaryMode(str, Enum):
    PERIODIC = "periodic"
    REFLECTIVE = "reflective"


@dataclass
class VoxelState:
    position: Vec3
    potential: float = 0.0
    frequency: float = 0.0
    mass_density: float = 1.0
    harmonically_stable: bool = False
    meta: Dict[str, float] = field(default_factory=dict)


@dataclass
class TickSnapshot:
    tick: int
    active_count: int
    stable_count: int
    avg_potential: float


class ManifoldController:
    """
    Sparse-voxel manifold controller with:
    - coordinate-to-state mapping
    - Minkowski-harmonic metric helper
    - identity interceptor around 198π
    - tick lifecycle hooks (compute/sync/react/audit/dream)
    """

    HARMONIC_CONSTANT_198_PI = 198.0 * pi
    HARMONIC_CONSTANT_100_PI_SQRT2 = 100.0 * pi * sqrt(2.0)

    def __init__(
        self,
        grid_shape: Vec3 = (64, 64, 64),
        boundary_mode: BoundaryMode = BoundaryMode.PERIODIC,
        dx: float = 1.0,
        dt: float = 1.0,
        epsilon: float = 1e-3,
        snapshot_stride: int = 10,
        dream_window: int = 100,
    ) -> None:
        self.grid_shape = grid_shape
        self.boundary_mode = boundary_mode
        self.dx = dx
        self.dt = dt
        self.epsilon = epsilon
        self.snapshot_stride = snapshot_stride
        self.dream_window = dream_window

        self.tick = 0
        self._grid: Dict[Vec3, VoxelState] = {}
        self._snapshots: List[TickSnapshot] = []

        # Optional integration hooks (can be wired to real services)
        self.grpc_sync_hook: Optional[Callable[[int, Iterable[VoxelState]], None]] = None
        self.audit_hook: Optional[Callable[[TickSnapshot], None]] = None
        self.ollama_hook: Optional[Callable[[List[TickSnapshot]], None]] = None

    # ---------------------------
    # Translation layer
    # ---------------------------
    def coordinate_to_key(self, x: int, y: int, z: int) -> Vec3:
        """Map physical coordinates to a valid sparse-grid key under boundary conditions."""
        nx, ny, nz = self.grid_shape

        if self.boundary_mode == BoundaryMode.PERIODIC:
            return (x % nx, y % ny, z % nz)

        # Reflective boundary
        return (
            self._reflect_index(x, nx),
            self._reflect_index(y, ny),
            self._reflect_index(z, nz),
        )

    def get_or_create_voxel(self, x: int, y: int, z: int) -> VoxelState:
        key = self.coordinate_to_key(x, y, z)
        if key not in self._grid:
            self._grid[key] = VoxelState(position=key)
        return self._grid[key]

    def minkowski_harmonic_distance(self, a: Vec3, b: Vec3, d_tau: float = 0.0) -> float:
        """
        Simplified Minkowski-like interval with harmonic scaling:
        s^2 = (Δx² + Δy² + Δz²) - (c_h * Δτ)²

        c_h is scaled by 198π to encode your harmonic constant.
        Returns |s|^(1/2) as a robust scalar distance proxy.
        """
        dx = (a[0] - b[0]) * self.dx
        dy = (a[1] - b[1]) * self.dx
        dz = (a[2] - b[2]) * self.dx
        c_h = self.HARMONIC_CONSTANT_198_PI

        s2 = (dx * dx + dy * dy + dz * dz) - (c_h * d_tau) ** 2
        return sqrt(abs(s2))

    # ---------------------------
    # Identity interceptor
    # ---------------------------
    def identity_interceptor(self, voxel: VoxelState) -> bool:
        """Flag voxel as harmonically stable when |f - 198π| < ε."""
        stable = abs(voxel.frequency - self.HARMONIC_CONSTANT_198_PI) < self.epsilon
        voxel.harmonically_stable = stable
        return stable

    # ---------------------------
    # Tick lifecycle
    # ---------------------------
    def tick_once(self) -> None:
        self.tick += 1

        # Step 1: Compute (local physics placeholder)
        self._compute_step()

        # Step 2: Sync (gRPC hook)
        self._sync_step()

        # Step 3: React (compound bonding placeholder)
        self._react_step()

        # Step 4: Audit (snapshot + TSDB hook)
        self._audit_step()

        # Step 5: Dream (async analysis hook)
        self._dream_step()

    def _compute_step(self) -> None:
        # Placeholder Hamiltonian integration:
        # update potential and frequency for active voxels only.
        for voxel in self._grid.values():
            voxel.potential += 0.01 * voxel.mass_density * self.dt
            voxel.frequency = voxel.frequency * 0.99 + 0.01 * self.HARMONIC_CONSTANT_198_PI
            self.identity_interceptor(voxel)

    def _sync_step(self) -> None:
        if self.grpc_sync_hook:
            self.grpc_sync_hook(self.tick, self._grid.values())

    def _react_step(self) -> None:
        # Placeholder for element table / bonding logic.
        pass

    def _audit_step(self) -> None:
        if not self._grid:
            return

        if self.tick % self.snapshot_stride != 0:
            return

        values = list(self._grid.values())
        active_count = len(values)
        stable_count = sum(1 for v in values if v.harmonically_stable)
        avg_potential = sum(v.potential for v in values) / max(active_count, 1)

        snap = TickSnapshot(
            tick=self.tick,
            active_count=active_count,
            stable_count=stable_count,
            avg_potential=avg_potential,
        )
        self._snapshots.append(snap)

        if self.audit_hook:
            self.audit_hook(snap)

    def _dream_step(self) -> None:
        if not self.ollama_hook:
            return
        if len(self._snapshots) < self.dream_window:
            return

        window = self._snapshots[-self.dream_window :]
        self.ollama_hook(window)

    # ---------------------------
    # Utility
    # ---------------------------
    @property
    def active_voxel_count(self) -> int:
        return len(self._grid)

    @property
    def snapshots(self) -> List[TickSnapshot]:
        return list(self._snapshots)

    @staticmethod
    def _reflect_index(i: int, n: int) -> int:
        if n <= 1:
            return 0
        period = 2 * (n - 1)
        j = i % period
        return j if j < n else period - j


if __name__ == "__main__":
    controller = ManifoldController(grid_shape=(32, 32, 32), boundary_mode=BoundaryMode.PERIODIC)
    controller.get_or_create_voxel(0, 0, 0).frequency = 198.0 * pi
    controller.get_or_create_voxel(1, 2, 3).frequency = 620.0

    for _ in range(30):
        controller.tick_once()

    print(f"Ticks: {controller.tick}")
    print(f"Active voxels: {controller.active_voxel_count}")
    if controller.snapshots:
        last = controller.snapshots[-1]
        print(f"Last snapshot @ tick {last.tick}: stable={last.stable_count}/{last.active_count}")
