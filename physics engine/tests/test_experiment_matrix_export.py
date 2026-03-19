from __future__ import annotations

from pathlib import Path
import csv
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from benchmarks.export_experiment_matrix import (  # noqa: E402
    ExperimentCondition,
    run_condition_matrix,
    write_condition_matrix_csv,
)


def test_run_condition_matrix_returns_expected_shape() -> None:
    rows = run_condition_matrix(
        [
            ExperimentCondition("baseline", lam=0.0, kappa=0.0),
            ExperimentCondition("variant", lam=0.05, kappa=0.01),
        ],
        steps=6,
        system_name="Double Pendulum",
    )

    assert len(rows) == 2
    assert rows[0]["condition"] == "baseline"
    assert rows[1]["condition"] == "variant"
    assert rows[0]["final_tick"] == 6
    assert rows[0]["taxonomy_status"] == "matched"


def test_write_condition_matrix_csv_creates_notebook_friendly_file(tmp_path: Path) -> None:
    out_csv = tmp_path / "experiment_condition_matrix.csv"
    rows = [
        {
            "condition": "baseline",
            "lam": 0.0,
            "kappa": 0.0,
            "steps": 6,
            "final_tick": 6,
            "event_count": 24,
            "energy_mean": 1.5,
            "energy_std": 0.0,
            "drift_mean": 1.0,
            "drift_std": 0.0,
            "config_hash": "abc",
            "taxonomy_status": "matched",
            "taxonomy_system": "Double Pendulum",
        }
    ]

    write_condition_matrix_csv(rows, out_csv)

    assert out_csv.exists()
    with out_csv.open("r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        loaded = list(reader)
    assert len(loaded) == 1
    assert loaded[0]["condition"] == "baseline"
    assert loaded[0]["taxonomy_status"] == "matched"
