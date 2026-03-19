# Experiment Design Guide (Physics Room)

## Purpose
This guide defines a repeatable method to design a simulation experiment in The Physics Room.

## 1) Define the Research Question
State one primary question in measurable terms.

Examples:
- How does increasing `lam` change harmonic drift over 20 ticks?
- Does a higher `kappa` alter spectroscopy peak count stability?

## 2) Set a Testable Hypothesis
Write a directional hypothesis with expected signal behavior.

Template:
- If parameter `X` increases, metric `Y` will increase/decrease under condition `C`.

## 3) Choose Independent and Dependent Variables
Independent variables (controls you change):
- `N`, `dt`, `lam`, `kappa`, `phi`, `omega`, `hbar`
- chemistry input (formula, e.g., `H2O`, `Al2(SO4)3`)
- `enable_ai`, `use_real_modules`

Dependent variables (outcomes you measure):
- `hamiltonian.frame.payload.energy`
- `stability.harmonic.payload.q_factor`
- `stability.harmonic.payload.drift`
- `instrument.trace.payload.spectral_peak_count`
- AI assessments from `ai.anomaly`

## 4) Define Experimental Conditions
Use at least:
- Baseline condition (reference)
- One or more perturbed conditions

Example matrix:
- Baseline: `lam=0.00`, `kappa=0.00`
- Condition A: `lam=0.05`, `kappa=0.00`
- Condition B: `lam=0.05`, `kappa=0.01`
- Condition C: `lam=0.10`, `kappa=0.01`

## 5) Standardize Runtime Protocol
For each condition:
1. Create session via `POST /session/start`.
2. Run fixed steps via `POST /tick/run`.
3. Pull events via `GET /session/{id}/events`.
4. Store raw event envelopes unchanged.

Keep constant across conditions:
- same `steps`
- same initial state assumptions
- same probe geometry (if applicable)

## 6) Add Chemistry Metadata
Use [elements table/element_resources.py](elements%20table/element_resources.py) to derive:
- atom counts
- molar mass
- mass percentages

Attach this metadata to your run report so each simulation condition is chemistry-contextualized.

## 7) Plan Replicates
Run each condition multiple times (recommended: $n \ge 3$) and record:
- mean and standard deviation of key metrics
- confidence intervals when possible

## 8) Define Acceptance Criteria
Specify what counts as support for the hypothesis.

Example:
- Mean drift reduction of at least 10% relative to baseline and non-overlapping confidence intervals.

## 9) Analyze and Compare
Minimum analysis outputs:
- Energy vs tick
- Drift vs tick
- Peak count vs tick
- AI anomaly count and confidence distribution

Recommended summary table columns:
- Condition
- Mean energy
- Mean drift
- Mean q-factor
- Mean spectral peaks
- AI anomaly rate

## 10) Report Template
Include:
1. Objective
2. Hypothesis
3. Configuration matrix
4. Procedure
5. Raw and aggregated results
6. Interpretation
7. Limitations
8. Next experiment

---

## Quick Starter Experiment
- Formula: `H2O`
- Session: `N=12`, `dt=0.02`
- Compare:
  - Baseline: `lam=0.00`, `kappa=0.00`
  - Variant: `lam=0.05`, `kappa=0.01`
- Run `steps=20`
- Evaluate:
  - final and average `energy`
  - average `drift`
  - `spectral_peak_count` trend
  - AI anomaly frequency (if `enable_ai=true`)

This provides a compact baseline-to-perturbation experiment structure suitable for extension.
