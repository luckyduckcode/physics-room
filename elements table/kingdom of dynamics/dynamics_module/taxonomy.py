from __future__ import annotations

from dataclasses import dataclass
from difflib import get_close_matches
from pathlib import Path

import logging
from typing import Any, Dict, Iterable, List, Optional
import csv


@dataclass(frozen=True)
class SystemEntry:
    system: str
    kingdom: str
    phylum: str
    class_type: str
    linearity: str
    energy: str
    dynamics: str

    def to_dict(self) -> Dict[str, str]:
        return {
            "System": self.system,
            "Kingdom": self.kingdom,
            "Phylum": self.phylum,
            "Class": self.class_type,
            "Linearity": self.linearity,
            "Energy": self.energy,
            "Dynamics": self.dynamics,
        }


class DynamicsTaxonomy:
    """Navigation-first wrapper around a dynamics taxonomy CSV."""

    FIELD_ALIASES = {
        "system": "system",
        "kingdom": "kingdom",
        "phylum": "phylum",
        "class": "class_type",
        "class_type": "class_type",
        "linearity": "linearity",
        "energy": "energy",
        "dynamics": "dynamics",
    }

    REQUIRED_COLUMNS = ["System", "Kingdom", "Phylum", "Class", "Linearity", "Energy", "Dynamics"]

    def __init__(self, entries: Iterable[SystemEntry], source: Optional[Path] = None) -> None:
        self._entries: List[SystemEntry] = list(entries)
        self._by_system: Dict[str, SystemEntry] = {
            e.system.strip().lower(): e
            for e in self._entries
            if e.system.strip()
        }
        self.source = source

    @classmethod
    def from_csv(cls, csv_path: str | Path) -> "DynamicsTaxonomy":
        path = Path(csv_path)
        with path.open("r", newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            if reader.fieldnames is None:
                raise ValueError(f"CSV has no header row: {path}")

            missing = [col for col in cls.REQUIRED_COLUMNS if col not in reader.fieldnames]
            if missing:
                raise ValueError(f"CSV is missing required columns {missing}: {path}")

            entries = [
                SystemEntry(
                    system=row["System"].strip(),
                    kingdom=row["Kingdom"].strip(),
                    phylum=row["Phylum"].strip(),
                    class_type=row["Class"].strip(),
                    linearity=row["Linearity"].strip(),
                    energy=row["Energy"].strip(),
                    dynamics=row["Dynamics"].strip(),
                )
                for row in reader
                if any((row.get(k) or "").strip() for k in cls.REQUIRED_COLUMNS)
            ]
        return cls(entries, source=path)

    def __len__(self) -> int:
        return len(self._entries)

    def __iter__(self):
        return iter(self._entries)

    @classmethod
    def fields(cls) -> List[str]:
        return ["system", "kingdom", "phylum", "class", "linearity", "energy", "dynamics"]

    def all(self) -> List[SystemEntry]:
        return list(self._entries)

    def systems(self) -> List[str]:
        return sorted(e.system for e in self._entries)

    def get(self, system_name: str) -> Optional[SystemEntry]:
        return self._by_system.get(system_name.strip().lower())

    def suggest_systems(self, text: str, limit: int = 5) -> List[str]:
        if limit <= 0:
            return []

        names = sorted(e.system for e in self._entries)
        if not text.strip():
            return names[:limit]

        matched = get_close_matches(text.strip(), names, n=limit, cutoff=0.35)
        if len(matched) < limit:
            q = text.strip().lower()
            prefix = [name for name in names if q in name.lower() and name not in matched]
            matched.extend(prefix[: max(0, limit - len(matched))])
        return matched[:limit]

    def search(
        self,
        text: str,
        *,
        fields: Optional[Iterable[str]] = None,
        limit: Optional[int] = None,
    ) -> List[SystemEntry]:
        q = text.strip().lower()
        selected_fields = self._resolve_fields(fields)
        if not q:
            rows = self.all()
            return rows if limit is None else rows[: max(0, limit)]

        rows = [
            e
            for e in self._entries
            if any(q in str(getattr(e, attr)).lower() for attr in selected_fields)
        ]
        if rows:
            logging.info(f"[DynamicsTaxonomy] Search threshold passed: text='{text}', fields={selected_fields}, matched={len(rows)} row(s)")
        return rows if limit is None else rows[: max(0, limit)]

    def filter(
        self,
        *,
        system: Optional[str] = None,
        kingdom: Optional[str] = None,
        phylum: Optional[str] = None,
        class_type: Optional[str] = None,
        linearity: Optional[str] = None,
        energy: Optional[str] = None,
        dynamics: Optional[str] = None,
        contains: bool = False,
    ) -> List[SystemEntry]:
        def matches(value: str, expected: Optional[str]) -> bool:
            if expected is None:
                return True
            left = value.lower()
            right = expected.strip().lower()
            return right in left if contains else left == right

        filtered = [
            e
            for e in self._entries
            if matches(e.system, system)
            and matches(e.kingdom, kingdom)
            and matches(e.phylum, phylum)
            and matches(e.class_type, class_type)
            and matches(e.linearity, linearity)
            and matches(e.energy, energy)
            and matches(e.dynamics, dynamics)
        ]
        if any([system, kingdom, phylum, class_type, linearity, energy, dynamics]):
            logging.info(f"[DynamicsTaxonomy] Filter threshold passed: system={system}, kingdom={kingdom}, phylum={phylum}, class_type={class_type}, linearity={linearity}, energy={energy}, dynamics={dynamics}, contains={contains}, matched={len(filtered)} row(s)")
        return filtered

    def group_by(self, field: str) -> Dict[str, List[SystemEntry]]:
        key_attr = self.FIELD_ALIASES.get(field.strip().lower())
        if key_attr is None:
            raise ValueError(f"Unsupported field '{field}'. Valid values: {', '.join(self.fields())}")

        grouped: Dict[str, List[SystemEntry]] = {}
        for entry in self._entries:
            key = getattr(entry, key_attr)
            grouped.setdefault(key, []).append(entry)
        return dict(sorted(grouped.items(), key=lambda kv: kv[0].lower()))

    def unique(self, field: str) -> List[str]:
        grouped = self.group_by(field)
        return list(grouped.keys())

    def summary(self) -> Dict[str, Any]:
        return {
            "count": len(self._entries),
            "systems": self.systems(),
            "fields": {
                "kingdom": self.unique("kingdom"),
                "phylum": self.unique("phylum"),
                "class": self.unique("class"),
                "linearity": self.unique("linearity"),
                "energy": self.unique("energy"),
                "dynamics": self.unique("dynamics"),
            },
        }

    def related(self, system_name: str, *, by: str = "phylum", limit: int = 10) -> List[SystemEntry]:
        if limit <= 0:
            return []

        base = self.get(system_name)
        if base is None:
            return []

        attr = self.FIELD_ALIASES.get(by.strip().lower())
        if attr is None:
            raise ValueError(f"Unsupported related-group field '{by}'. Valid values: {', '.join(self.fields())}")

        anchor = getattr(base, attr)
        rows = [e for e in self._entries if getattr(e, attr) == anchor and e.system != base.system]
        if rows:
            logging.info(f"[DynamicsTaxonomy] Related threshold passed: system_name={system_name}, by={by}, anchor={anchor}, matched={len(rows)} row(s), limit={limit}")
        return rows[:limit]

    def _resolve_fields(self, fields: Optional[Iterable[str]]) -> List[str]:
        if fields is None:
            return [
                "system",
                "kingdom",
                "phylum",
                "class_type",
                "linearity",
                "energy",
                "dynamics",
            ]

        resolved: List[str] = []
        for name in fields:
            key = self.FIELD_ALIASES.get(name.strip().lower())
            if key is None:
                raise ValueError(f"Unsupported search field '{name}'. Valid values: {', '.join(self.fields())}")
            resolved.append(key)

        if not resolved:
            return [
                "system",
                "kingdom",
                "phylum",
                "class_type",
                "linearity",
                "energy",
                "dynamics",
            ]
        return resolved

    @property
    def family_guide(self) -> Dict[str, str]:
        return {
            "Conservative": (
                "dH/dt = 0: idealized no-loss systems. Energy trades between forms "
                "without net loss, so trajectories typically persist (orbits/oscillations)."
            ),
            "Dissipative": (
                "dE/dt < 0: systems with friction, damping, resistance, or coupling to an "
                "environment. Trajectories approach attractors (equilibria, limit cycles, etc.)."
            ),
        }

    @property
    def dna_guide(self) -> Dict[str, str]:
        return {
            "Linear": "x_dot = A x (or A x + B u): superposition applies; mode/eigenvalue analysis works.",
            "Non-linear": "x_dot = f(x): interactions and feedback produce richer behavior (bifurcation, chaos).",
        }


def load_default_taxonomy(base_dir: str | Path = ".") -> DynamicsTaxonomy:
    candidate = Path(base_dir) / "physics_dynamics_taxonomy.csv"
    if candidate.exists():
        return DynamicsTaxonomy.from_csv(candidate)

    module_default = Path(__file__).resolve().parents[1] / "physics_dynamics_taxonomy.csv"
    if module_default.exists():
        return DynamicsTaxonomy.from_csv(module_default)

    raise FileNotFoundError(
        f"Could not find CSV at either: {candidate} or {module_default}"
    )
