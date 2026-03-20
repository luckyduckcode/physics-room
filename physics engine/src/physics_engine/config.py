from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Optional, Dict

import numpy as np


@dataclass
class EngineConfig:
    N:      int   = 40
    hbar:   float = 1.0
    omega:  float = 1.0
    phi:    float = float(np.e)
    dt:     float = 0.01
    lam:    float = 0.0
    kappa:  float = 0.0
    F:      Optional[np.ndarray] = field(default=None, repr=False)
    g:      Optional[np.ndarray] = field(default=None, repr=False)
    h:      Optional[np.ndarray] = field(default=None, repr=False)
    Vcosmo: Optional[Callable[[np.ndarray], np.ndarray]] = field(default=None, repr=False)
    # Extra pluggable Hamiltonian terms: name -> callable(ops, cfg, t) -> np.ndarray
    extra_terms: Optional[Dict[str, Callable]] = field(default=None, repr=False)
    # Enable optional backends
    use_qutip: bool = False
    # Random seed for stochastic terms (None -> system default)
    random_seed: Optional[int] = None

    def __post_init__(self) -> None:
        assert self.N     >  2,  f"N must be > 2, got {self.N}"
        assert self.hbar  >  0,  f"hbar must be > 0, got {self.hbar}"
        assert self.omega >  0,  f"omega must be > 0, got {self.omega}"
        assert self.phi   >  0,  f"phi must be > 0, got {self.phi}"
        assert self.dt    >  0,  f"dt must be > 0, got {self.dt}"
        assert self.lam   >= 0,  f"lam must be >= 0, got {self.lam}"
        assert self.kappa >= 0,  f"kappa must be >= 0, got {self.kappa}"
        if self.F is None:
            self.F = np.ones(self.N + 1)
        if self.g is None:
            self.g = np.zeros(self.N)
        if self.h is None:
            self.h = np.zeros((self.N, self.N))
        assert len(self.F) >= self.N + 1
        assert len(self.g) >= self.N
        assert self.h.shape[0] >= self.N and self.h.shape[1] >= self.N


@dataclass
class CouplingConfig:
    F:     Optional[np.ndarray] = None
    g:     Optional[np.ndarray] = None
    h:     Optional[np.ndarray] = None
    lam:   float = 0.0
    kappa: float = 0.0


@dataclass
class SimulationResult:
    times:    np.ndarray
    states:   np.ndarray
    energies: np.ndarray
    norms:    np.ndarray
    logs:     list = field(default_factory=list)
 
