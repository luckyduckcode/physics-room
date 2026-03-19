from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Literal, Protocol, Tuple
import math
import sqlite3


ToolType = Literal["stm", "afm", "tem", "spectroscopy", "environment"]


class ManifoldLike(Protocol):
    """Minimal interface expected by virtual probes."""

    temperature: float

    def get_voxel_potential(self, x: int, y: int, z: int) -> float:
        ...

    def get_particle_density(self, x: int, y: int, z: int) -> float:
        ...

    def get_current_state(self, tool_type: ToolType) -> Dict:
        ...


@dataclass
class DataAcquisition:
    """Captures probe snapshots and stores them in-memory + SQLite."""

    sample_rate: int = 198
    db_path: str = "data_log.db"
    buffer: List[Dict] = field(default_factory=list)

    def __post_init__(self) -> None:
        self._ensure_db()

    def _ensure_db(self) -> None:
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS probe_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    tool_type TEXT NOT NULL,
                    payload TEXT NOT NULL
                )
                """
            )

    def probe_manifold(self, manifold: ManifoldLike, tool_type: ToolType) -> Dict:
        data = manifold.get_current_state(tool_type)
        self.buffer.append(data)
        self.log_to_sqlite(tool_type, data)
        return data

    def log_to_sqlite(self, tool_type: ToolType, data: Dict) -> None:
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "INSERT INTO probe_log(tool_type, payload) VALUES (?, ?)",
                (tool_type, str(data)),
            )


@dataclass
class STMTool:
    """
    Scanning Tunneling Microscope virtual probe.

    Transfer function:
        - Tunnel current is approximated as:
            I_t \\propto rho(x,y,z_surface) * exp(-kappa * gap)
    - Height map is recovered from current by inverting the exponential.
    """

    kappa: float = 1.0
    setpoint_current: float = 1.0
    z_surface: int = 0

    def scan(
        self,
        manifold: ManifoldLike,
        x_range: Tuple[int, int],
        y_range: Tuple[int, int],
    ) -> Dict[str, Any]:
        """Return STM observables over a 2D patch."""
        current_map: List[List[float]] = []
        height_map: List[List[float]] = []

        x0, x1 = x_range
        y0, y1 = y_range

        for x in range(x0, x1):
            row_current: List[float] = []
            row_height: List[float] = []
            for y in range(y0, y1):
                phi = manifold.get_voxel_potential(x, y, self.z_surface)
                rho = manifold.get_particle_density(x, y, self.z_surface)

                gap = max(0.01, 1.0 + 0.1 * phi + 0.01 * manifold.temperature)

                current = rho * math.exp(-self.kappa * gap)
                height = self._invert_current_to_height(current)

                row_current.append(current)
                row_height.append(height)

            current_map.append(row_current)
            height_map.append(row_height)

        return {
            "mode": "constant_current",
            "current_map": current_map,
            "height_map": height_map,
            "units": {
                "current_map": "arb.",
                "height_map": "angstrom (relative)",
            },
        }

    def _invert_current_to_height(self, current: float) -> float:
        clamped = max(current, 1e-12)
        return -math.log(clamped / self.setpoint_current) / max(self.kappa, 1e-9)


@dataclass
class SpectroscopyTool:
    """
    Frequency analyzer for Raman/NMR-like virtual probes.

    Transfer function:
    - Input: time-domain Hamiltonian oscillation signal H(t)
    - Output: intensity spectrum via DFT/FFT-like transform
    """

    sample_rate: float = 198.0
    instrument: Literal["raman", "nmr", "generic"] = "generic"

    def spectrum_from_signal(
        self,
        signal: List[float],
        top_k_peaks: int = 8,
    ) -> Dict[str, Any]:
        n = len(signal)
        if n < 2:
            return {
                "instrument": self.instrument,
                "sample_rate": self.sample_rate,
                "frequencies": [],
                "intensity": [],
                "peaks": [],
            }

        freqs: List[float] = []
        intensities: List[float] = []

        half = n // 2
        for k in range(half):
            re = 0.0
            im = 0.0
            for t, value in enumerate(signal):
                angle = 2.0 * math.pi * k * t / n
                re += value * math.cos(angle)
                im -= value * math.sin(angle)

            magnitude = (re * re + im * im) ** 0.5
            frequency = (k * self.sample_rate) / n

            freqs.append(frequency)
            intensities.append(magnitude)

        peaks = self._extract_peaks(freqs, intensities, top_k=top_k_peaks)
        unit = "cm^-1" if self.instrument == "raman" else "MHz"

        return {
            "instrument": self.instrument,
            "sample_rate": self.sample_rate,
            "frequencies": freqs,
            "intensity": intensities,
            "peaks": peaks,
            "x_unit": unit,
            "y_unit": "arb.",
        }

    def probe_manifold(
        self,
        manifold: ManifoldLike,
        ticks: int = 256,
    ) -> Dict[str, Any]:
        signal: List[float] = []

        for _ in range(ticks):
            state = manifold.get_current_state("spectroscopy")
            sample = state.get("hamiltonian", 0.0)
            signal.append(float(sample))

        return self.spectrum_from_signal(signal)

    def _extract_peaks(
        self,
        frequencies: List[float],
        intensity: List[float],
        top_k: int,
    ) -> List[Dict[str, float]]:
        if len(intensity) < 3:
            return []

        local_peaks: List[Tuple[float, float]] = []
        for i in range(1, len(intensity) - 1):
            if intensity[i] > intensity[i - 1] and intensity[i] > intensity[i + 1]:
                local_peaks.append((frequencies[i], intensity[i]))

        local_peaks.sort(key=lambda item: item[1], reverse=True)
        return [
            {"frequency": freq, "intensity": amp}
            for freq, amp in local_peaks[:top_k]
        ]


class DemoManifold:
    def __init__(self, temperature: float = 4.2) -> None:
        self.temperature = temperature
        self._tick = 0

    def get_voxel_potential(self, x: int, y: int, z: int) -> float:
        return math.sin(x * 0.2) * math.cos(y * 0.2) + 0.05 * z

    def get_particle_density(self, x: int, y: int, z: int) -> float:
        return 1.5 + 0.5 * math.cos(x * 0.15 + y * 0.1) - 0.02 * z

    def get_current_state(self, tool_type: ToolType) -> Dict:
        self._tick += 1
        hamiltonian = (
            1.4 * math.sin(2.0 * math.pi * self._tick / 32.0)
            + 0.8 * math.sin(2.0 * math.pi * self._tick / 12.0)
        )
        return {
            "tool_type": tool_type,
            "temperature": self.temperature,
            "tick": self._tick,
            "hamiltonian": hamiltonian,
        }
