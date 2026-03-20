# Harmonic Oscillator Benchmark Results

This file captures the local benchmark comparing `build_H` eigenvalues to analytic harmonic-oscillator energies.

Script: `physics engine/examples/benchmark_harmonic.py`

Observed (local run):

--- Full build_H lowest eigenvalues (may include extra terms) ---
[  1.5   3.5   7.5  19.5  69.5 331.5]

--- Pure build_H (configured to HO) lowest eigenvalues ---
[0.5 1.5 2.5 3.5 4.5 5.5]

--- Analytic HO energies ---
[0.5 1.5 2.5 3.5 4.5 5.5]

--- Relative differences (pure vs analytic) ---
[0. 0. 0. 0. 0. 0.]

Notes:
- The `build_H` helper may include extra configured terms by default; constructing a "pure" configuration forces the simple harmonic-oscillator Hamiltonian and reproduces analytic energies for the lowest levels.
- To reproduce these results locally, run the script from the workspace root (with your venv activated):

```bash
"/Volumes/USB-HDD/coding projects/elements table/.venv/bin/python" "physics engine/examples/benchmark_harmonic.py"
```