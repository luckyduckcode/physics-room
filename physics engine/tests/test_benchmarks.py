from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from benchmarks.run_benchmarks import run_all_benchmarks


def test_benchmarks_pass() -> None:
    results = run_all_benchmarks()
    assert len(results) >= 5
    assert all(r.passed for r in results)
