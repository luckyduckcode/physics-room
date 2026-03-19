from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any

@dataclass
class Element:
    atomic_number: int
    symbol: str
    name: str
    atomic_mass: float
    state: Optional[str] = None
    melting_point: Optional[float] = None
    boiling_point: Optional[float] = None
    hardness: Optional[float] = None
    durability: Optional[str] = None
    stability: Optional[str] = None
    # Extend as needed

@dataclass
class Material:
    name: str
    elements: List[Element]
    composition: Dict[str, float]  # e.g., {'Fe': 0.7, 'C': 0.3}
    density: Optional[float] = None
    # Extend as needed

@dataclass
class Room:
    name: str
    materials: List[Material]
    temperature: Optional[float] = None
    pressure: Optional[float] = None
    # Extend as needed

@dataclass
class Environment:
    name: str
    rooms: List[Room]
    global_conditions: Dict[str, Any] = field(default_factory=dict)

@dataclass
class Universe:
    environments: List[Environment]
    metadata: Dict[str, Any] = field(default_factory=dict)
