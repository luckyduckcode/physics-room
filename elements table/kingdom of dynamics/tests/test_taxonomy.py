from __future__ import annotations

from pathlib import Path
import sys

import pytest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from dynamics_module.taxonomy import DynamicsTaxonomy, load_default_taxonomy  # noqa: E402


def _write_csv(tmp_path: Path, content: str) -> Path:
    p = tmp_path / "taxonomy.csv"
    p.write_text(content, encoding="utf-8")
    return p


def test_from_csv_validates_required_columns(tmp_path: Path) -> None:
    path = _write_csv(
        tmp_path,
        "System,Kingdom,Phylum,Class,Linearity,Energy\n"
        "A,Classical,Deterministic,Continuous,Linear,Conservative\n",
    )

    with pytest.raises(ValueError):
        DynamicsTaxonomy.from_csv(path)


def test_search_fields_and_limit(tmp_path: Path) -> None:
    path = _write_csv(
        tmp_path,
        "System,Kingdom,Phylum,Class,Linearity,Energy,Dynamics\n"
        "Double Pendulum,Classical,Deterministic,Continuous,Non-linear,Conservative,Chaotic\n"
        "Lorenz Weather Model,Classical,Deterministic,Continuous,Non-linear,Dissipative,Strange Attractor\n",
    )
    tax = DynamicsTaxonomy.from_csv(path)

    rows = tax.search("chaotic", fields=["dynamics"], limit=1)
    assert len(rows) == 1
    assert rows[0].system == "Double Pendulum"


def test_filter_contains_matching(tmp_path: Path) -> None:
    path = _write_csv(
        tmp_path,
        "System,Kingdom,Phylum,Class,Linearity,Energy,Dynamics\n"
        "Van der Pol Oscillator,Classical,Deterministic,Continuous,Non-linear,Dissipative,Limit Cycle\n",
    )
    tax = DynamicsTaxonomy.from_csv(path)

    exact_none = tax.filter(energy="diss", contains=False)
    partial_hit = tax.filter(energy="diss", contains=True)

    assert exact_none == []
    assert len(partial_hit) == 1


def test_related_respects_grouping_and_limit(tmp_path: Path) -> None:
    path = _write_csv(
        tmp_path,
        "System,Kingdom,Phylum,Class,Linearity,Energy,Dynamics\n"
        "A,Classical,P1,C,Linear,Conservative,Periodic\n"
        "B,Classical,P1,C,Non-linear,Dissipative,Chaotic\n"
        "C,Classical,P1,C,Non-linear,Dissipative,Chaotic\n",
    )
    tax = DynamicsTaxonomy.from_csv(path)

    rows = tax.related("A", by="phylum", limit=1)
    assert len(rows) == 1
    assert rows[0].system in {"B", "C"}


def test_load_default_taxonomy_fallback_works() -> None:
    tax = load_default_taxonomy("/definitely/not/real")
    assert len(tax) > 0
