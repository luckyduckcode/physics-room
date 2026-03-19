from __future__ import annotations

import csv
from dataclasses import dataclass, field
from difflib import get_close_matches
import importlib.util
from pathlib import Path
from random import randint
from typing import Any
from uuid import uuid4

import numpy as np

from .config import EngineConfig
from .contracts import (
    EventEnvelope,
    EventType,
    RunMetadata,
    SessionState,
    TickRunResult,
    discover_code_version,
    make_config_hash,
    make_event,
    now_ns,
)
from .engine import PhysicsEngine


class _ControllerProbeAdapter:
    """Adapter exposing manifold probe interface backed by controller voxels."""

    def __init__(self, controller: Any, base_temperature: float = 4.2) -> None:
        self.controller = controller
        self.temperature = base_temperature
        self._tick = 0
        self._last_hamiltonian = 0.0

    def set_last_hamiltonian(self, value: float) -> None:
        self._last_hamiltonian = float(value)

    def get_voxel_potential(self, x: int, y: int, z: int) -> float:
        return float(self.controller.get_or_create_voxel(x, y, z).potential)

    def get_particle_density(self, x: int, y: int, z: int) -> float:
        return float(self.controller.get_or_create_voxel(x, y, z).mass_density)

    def get_current_state(self, tool_type: str) -> dict[str, Any]:
        self._tick += 1
        return {
            "tool_type": tool_type,
            "temperature": self.temperature,
            "tick": self._tick,
            "hamiltonian": self._last_hamiltonian,
        }


@dataclass
class PhysicsRoomCoordinator:
    session_id: str
    config: EngineConfig
    system_name: str | None = None
    grid_shape: tuple[int, int, int] = (32, 32, 32)
    enable_ai: bool = False
    use_real_modules: bool = True
    seed: int | None = None
    _sequence: int = 0
    _tick: int = 0
    _events: list[EventEnvelope] = field(default_factory=list)

    def __post_init__(self) -> None:
        if self.seed is None:
            self.seed = randint(1, 2_147_483_647)
        np.random.seed(self.seed)

        self.engine = PhysicsEngine(self.config)
        self.psi = np.zeros(self.config.N, dtype=complex)
        self.psi[0] = 1.0

        config_blob = {
            "N": self.config.N,
            "dt": self.config.dt,
            "hbar": self.config.hbar,
            "omega": self.config.omega,
            "phi": self.config.phi,
            "lam": self.config.lam,
            "kappa": self.config.kappa,
            "grid_shape": list(self.grid_shape),
            "enable_ai": self.enable_ai,
            "use_real_modules": self.use_real_modules,
        }
        self.metadata = RunMetadata(
            config_hash=make_config_hash(config_blob),
            code_version=discover_code_version(),
            seed=self.seed,
            created_at_ns=now_ns(),
        )
        self.dynamics_taxonomy = self._resolve_dynamics_taxonomy(self.system_name)

        self.controller_cls = None
        self.boundary_mode_enum = None
        self.stm_cls = None
        self.spec_cls = None
        self.micro_cls = None
        self.spectro_cls = None

        if self.use_real_modules:
            self._load_external_modules()

        self._init_runtime_objects()

    @staticmethod
    def new_session_id() -> str:
        return f"session-{uuid4().hex[:10]}"

    @property
    def events(self) -> list[EventEnvelope]:
        return list(self._events)

    @property
    def tick(self) -> int:
        return self._tick

    def manifest(self) -> dict[str, Any]:
        return {
            "session_id": self.session_id,
            "config": {
                "system_name": self.system_name,
                "N": self.config.N,
                "dt": self.config.dt,
                "hbar": self.config.hbar,
                "omega": self.config.omega,
                "phi": self.config.phi,
                "lam": self.config.lam,
                "kappa": self.config.kappa,
                "grid_shape": list(self.grid_shape),
                "enable_ai": self.enable_ai,
                "use_real_modules": self.use_real_modules,
            },
            "metadata": self.metadata.model_dump(),
            "dynamics_taxonomy": self.dynamics_taxonomy,
            "state": self.state().model_dump(),
        }

    def state(self) -> SessionState:
        stable = self._stable_voxels()
        return SessionState(
            session_id=self.session_id,
            tick=self._tick,
            active_voxels=self.controller.active_voxel_count,
            last_energy=float(self._last_energy),
            stable_voxels=stable,
            metadata=self.metadata,
        )

    def run_steps(self, steps: int) -> TickRunResult:
        emitted: list[EventEnvelope] = []
        for _ in range(steps):
            emitted.extend(self._run_single_tick())
        return TickRunResult(
            session_id=self.session_id,
            steps=steps,
            final_tick=self._tick,
            events=emitted,
            metadata=self.metadata,
        )

    def _run_single_tick(self) -> list[EventEnvelope]:
        self._tick += 1

        seed = self.controller.get_or_create_voxel(self._tick % self.grid_shape[0], 0, 0)
        seed.mass_density = 1.0 + (0.05 * (self._tick % 10))
        seed.frequency = self.controller.HARMONIC_CONSTANT_198_PI

        self.controller.tick_once()

        times = np.array([self._tick * self.config.dt, (self._tick + 1) * self.config.dt], dtype=float)
        sim = self.engine.simulate(psi0=self.psi, times=times)
        self.psi = sim.states[-1].copy()
        self._last_energy = float(sim.energies[-1])
        self.adapter.set_last_hamiltonian(self._last_energy)

        scan = self.stm.scan(self.adapter, x_range=(0, 8), y_range=(0, 8))
        spectrum = self.spectroscopy.probe_manifold(self.adapter, ticks=64)

        events: list[EventEnvelope] = [
            self._emit(
                source="manifold-controller",
                event_type="state.delta",
                payload={
                    "tick": self._tick,
                    "active_voxels": self.controller.active_voxel_count,
                    "stable_voxels": self._stable_voxels(),
                },
            ),
            self._emit(
                source="physics-engine",
                event_type="hamiltonian.frame",
                payload={
                    "tick": self._tick,
                    "energy": self._last_energy,
                    "norm": float(sim.norms[-1]),
                },
            ),
            self._emit(
                source="virtual-toolset",
                event_type="instrument.trace",
                payload={
                    "tick": self._tick,
                    "stm_height_shape": [len(scan["height_map"]), len(scan["height_map"][0])],
                    "spectral_peak_count": len(spectrum.get("peaks", [])),
                },
            ),
        ]

        if self.enable_ai:
            micro = self.microscopist.assess_stm_scan(scan)
            spec = self.spectroscopist.assess_spectrum(spectrum)
            events.append(
                self._emit(
                    source="ai-interpreter",
                    event_type="ai.anomaly",
                    payload={
                        "tick": self._tick,
                        "microscopist": micro,
                        "spectroscopist": spec,
                    },
                )
            )

        q_like = float(self._stable_voxels()) / max(1.0, float(self.controller.active_voxel_count))
        events.append(
            self._emit(
                source="manifold-controller",
                event_type="stability.harmonic",
                payload={"tick": self._tick, "q_factor": q_like, "drift": 1.0 - q_like},
            )
        )

        return events

    def _emit(self, *, source: str, event_type: EventType, payload: dict[str, Any]) -> EventEnvelope:
        self._sequence += 1
        event = make_event(
            session_id=self.session_id,
            source=source,
            event_type=event_type,
            sequence=self._sequence,
            payload=payload,
        )
        self._events.append(event)
        return event

    def _stable_voxels(self) -> int:
        return sum(1 for v in self.controller._grid.values() if getattr(v, "harmonically_stable", False))

    def _init_runtime_objects(self) -> None:
        if not all([self.controller_cls, self.boundary_mode_enum, self.stm_cls, self.spec_cls]):
            self._init_fallback_runtime()
            return

        assert self.boundary_mode_enum is not None
        assert self.controller_cls is not None
        assert self.stm_cls is not None
        assert self.spec_cls is not None
        boundary_mode = self.boundary_mode_enum.PERIODIC
        self.controller = self.controller_cls(grid_shape=self.grid_shape, boundary_mode=boundary_mode)
        self.adapter = _ControllerProbeAdapter(self.controller)
        self.stm = self.stm_cls(kappa=1.2, setpoint_current=0.8, z_surface=0)
        self.spectroscopy = self.spec_cls(sample_rate=198.0, instrument="raman")

        if self.enable_ai and self.micro_cls and self.spectro_cls:
            self.microscopist = self.micro_cls()
            self.spectroscopist = self.spectro_cls()

        self._last_energy = 0.0

        self._emit(
            source="coordinator",
            event_type="session.lifecycle",
            payload={
                "action": "start",
                "tick": self._tick,
                "metadata": self.metadata.model_dump(),
                "taxonomy": self.dynamics_taxonomy,
            },
        )

    def _init_fallback_runtime(self) -> None:
        class _Voxel:
            def __init__(self) -> None:
                self.potential = 0.0
                self.frequency = 0.0
                self.mass_density = 1.0
                self.harmonically_stable = False

        class _FallbackController:
            HARMONIC_CONSTANT_198_PI = 198.0 * np.pi

            def __init__(self, grid_shape: tuple[int, int, int]) -> None:
                self.grid_shape = grid_shape
                self._grid: dict[tuple[int, int, int], _Voxel] = {}
                self.tick = 0

            @property
            def active_voxel_count(self) -> int:
                return len(self._grid)

            def get_or_create_voxel(self, x: int, y: int, z: int) -> _Voxel:
                key = (x % self.grid_shape[0], y % self.grid_shape[1], z % self.grid_shape[2])
                if key not in self._grid:
                    self._grid[key] = _Voxel()
                return self._grid[key]

            def tick_once(self) -> None:
                self.tick += 1
                for voxel in self._grid.values():
                    voxel.potential += 0.01
                    voxel.frequency = voxel.frequency * 0.99 + 0.01 * self.HARMONIC_CONSTANT_198_PI
                    voxel.harmonically_stable = abs(voxel.frequency - self.HARMONIC_CONSTANT_198_PI) < 1e-3

        class _STMTool:
            def __init__(self, kappa: float, setpoint_current: float, z_surface: int) -> None:
                self.kappa = kappa
                self.setpoint_current = setpoint_current
                self.z_surface = z_surface

            def scan(self, manifold: _ControllerProbeAdapter, x_range: tuple[int, int], y_range: tuple[int, int]) -> dict[str, Any]:
                x0, x1 = x_range
                y0, y1 = y_range
                current_map = []
                height_map = []
                for x in range(x0, x1):
                    c_row = []
                    h_row = []
                    for y in range(y0, y1):
                        rho = manifold.get_particle_density(x, y, self.z_surface)
                        pot = manifold.get_voxel_potential(x, y, self.z_surface)
                        current = rho * float(np.exp(-self.kappa * (1.0 + 0.1 * pot)))
                        height = -float(np.log(max(current, 1e-12) / max(self.setpoint_current, 1e-12))) / max(self.kappa, 1e-12)
                        c_row.append(current)
                        h_row.append(height)
                    current_map.append(c_row)
                    height_map.append(h_row)
                return {"mode": "constant_current", "current_map": current_map, "height_map": height_map}

        class _SpectroscopyTool:
            def __init__(self, sample_rate: float, instrument: str) -> None:
                self.sample_rate = sample_rate
                self.instrument = instrument

            def probe_manifold(self, manifold: _ControllerProbeAdapter, ticks: int = 64) -> dict[str, Any]:
                samples = []
                for _ in range(ticks):
                    samples.append(float(manifold.get_current_state("spectroscopy").get("hamiltonian", 0.0)))
                peaks = []
                if len(samples) > 0:
                    peaks.append({"frequency": self.sample_rate / 8.0, "intensity": float(np.max(np.abs(samples)))})
                return {"instrument": self.instrument, "sample_rate": self.sample_rate, "peaks": peaks}

        class _MicroscopistExpert:
            def assess_stm_scan(self, stm_scan: dict[str, Any]) -> dict[str, Any]:
                return {"ok": True, "analysis": {"butterfly_emerging": False, "confidence": 0.5, "notes": "fallback"}}

        class _SpectroscopistExpert:
            def assess_spectrum(self, spectrum: dict[str, Any], harmonic_constant: float = 198.0 * np.pi) -> dict[str, Any]:
                return {"ok": True, "analysis": {"resonantly_pure": True, "confidence": 0.5, "matched_peaks": [], "notes": "fallback"}}

        self.controller = _FallbackController(self.grid_shape)
        self.adapter = _ControllerProbeAdapter(self.controller)
        self.stm = _STMTool(kappa=1.2, setpoint_current=0.8, z_surface=0)
        self.spectroscopy = _SpectroscopyTool(sample_rate=198.0, instrument="raman")

        if self.enable_ai:
            self.microscopist = _MicroscopistExpert()
            self.spectroscopist = _SpectroscopistExpert()

        self._last_energy = 0.0

        self._emit(
            source="coordinator",
            event_type="session.lifecycle",
            payload={
                "action": "start",
                "tick": self._tick,
                "runtime": "fallback",
                "metadata": self.metadata.model_dump(),
                "taxonomy": self.dynamics_taxonomy,
            },
        )

    def _resolve_dynamics_taxonomy(self, system_name: str | None) -> dict[str, Any] | None:
        if system_name is None or not system_name.strip():
            return None

        workspace_root = Path(__file__).resolve().parents[3]
        csv_path = workspace_root / "elements table" / "kingdom of dynamics" / "physics_dynamics_taxonomy.csv"
        if not csv_path.exists():
            return {
                "requested_system": system_name,
                "status": "taxonomy_unavailable",
            }

        try:
            with csv_path.open("r", newline="", encoding="utf-8") as f:
                reader = list(csv.DictReader(f))
        except Exception as exc:
            return {
                "requested_system": system_name,
                "status": "taxonomy_error",
                "error": str(exc),
            }

        target = system_name.strip().lower()
        for row in reader:
            system = (row.get("System") or "").strip()
            if system.lower() == target:
                return {
                    "requested_system": system_name,
                    "status": "matched",
                    "system": system,
                    "kingdom": (row.get("Kingdom") or "").strip(),
                    "phylum": (row.get("Phylum") or "").strip(),
                    "class": (row.get("Class") or "").strip(),
                    "linearity": (row.get("Linearity") or "").strip(),
                    "energy": (row.get("Energy") or "").strip(),
                    "dynamics": (row.get("Dynamics") or "").strip(),
                }

        systems = sorted((row.get("System") or "").strip() for row in reader if (row.get("System") or "").strip())
        return {
            "requested_system": system_name,
            "status": "not_found",
            "suggestions": get_close_matches(system_name.strip(), systems, n=5, cutoff=0.35),
        }

    def _load_external_modules(self) -> None:
        workspace_root = Path(__file__).resolve().parents[3]
        controller_path = workspace_root / "room:mainfold" / "manifold_controller.py"
        probes_path = workspace_root / "tools" / "physics_room" / "probes.py"
        interpreters_path = workspace_root / "tools" / "physics_room" / "interpreters.py"

        if not (controller_path.exists() and probes_path.exists() and interpreters_path.exists()):
            return

        controller_mod = self._load_module("manifold_controller_external", controller_path)
        probes_mod = self._load_module("probes_external", probes_path)
        interp_mod = self._load_module("interpreters_external", interpreters_path)

        self.controller_cls = getattr(controller_mod, "ManifoldController", None)
        self.boundary_mode_enum = getattr(controller_mod, "BoundaryMode", None)
        self.stm_cls = getattr(probes_mod, "STMTool", None)
        self.spec_cls = getattr(probes_mod, "SpectroscopyTool", None)
        self.micro_cls = getattr(interp_mod, "MicroscopistExpert", None)
        self.spectro_cls = getattr(interp_mod, "SpectroscopistExpert", None)

        if any(x is None for x in [self.controller_cls, self.boundary_mode_enum, self.stm_cls, self.spec_cls]):
            self.controller_cls = None

    @staticmethod
    def _load_module(module_name: str, module_path: Path) -> Any:
        spec = importlib.util.spec_from_file_location(module_name, module_path)
        if spec is None or spec.loader is None:
            raise RuntimeError(f"Unable to load module spec for {module_path}")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module
