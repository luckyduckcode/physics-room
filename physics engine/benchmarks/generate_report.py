from __future__ import annotations

from dataclasses import asdict
import csv
from pathlib import Path

try:
    import matplotlib.pyplot as plt
except Exception:  # pragma: no cover
    plt = None

from run_benchmarks import run_all_benchmarks


def main() -> None:
    out_dir = Path(__file__).parent / "reports"
    out_dir.mkdir(parents=True, exist_ok=True)

    results = [asdict(r) for r in run_all_benchmarks()]

    csv_path = out_dir / "benchmark_results.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["name", "passed", "observed", "expected"])
        for r in results:
            writer.writerow([r["name"], r["passed"], r["observed"], r["expected"]])

    print(f"Wrote {csv_path}")
    if plt is not None:
        names = [r["name"] for r in results]
        scores = [1 if r["passed"] else 0 for r in results]

        plt.figure(figsize=(10, 4))
        plt.bar(names, scores)
        plt.ylim(0, 1.1)
        plt.ylabel("Pass (1) / Fail (0)")
        plt.title("Physics Room Benchmark Status")
        plt.xticks(rotation=30, ha="right")
        plt.tight_layout()
        plot_path = out_dir / "benchmark_status.png"
        plt.savefig(plot_path, dpi=160)
        plt.close()
        print(f"Wrote {plot_path}")
    else:
        print("Skipped PNG plot (matplotlib not installed)")


if __name__ == "__main__":
    main()
