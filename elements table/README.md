# Elements Table Resources

This workspace now includes:

- A complete 118-element table with atomic number, symbol, name, and atomic mass.
- Element quantity extraction from a compound formula.
- A compound resource builder (atom counts, molar mass, mass percentages).
- Core chemistry math explanations.

## Files

- `elements_table.csv` — all elements in table form.
- `element_resources.py` — CLI utility for element lookup, formula quantity parsing, and report generation.

## Quick usage

```bash
python element_resources.py list
python element_resources.py element Fe
python element_resources.py element 26
python element_resources.py quantity C6H12O6
python element_resources.py build Al2(SO4)3
python element_resources.py build CuSO4·5H2O
python element_resources.py math
```

## Math model used

For each element and compound:

- Atomic identity: $Z$ = number of protons.
- Nucleon count: $A = Z + N$.
- Ion charge: $q = p - e$.
- Compound atom total: $n_{\text{total}} = \sum_i n_i$.
- Molar mass: $M = \sum_i n_i m_i$.
- Mass fraction: $w_i = \frac{n_i m_i}{M}$.
- Percent composition: $\%_i = 100\,w_i$.

These relations connect atomic structure to measurable compound behavior.

## Integration role in Physics Room

The element resource module is the chemistry-side lookup layer used by the manifold workflow:

- `parse_formula()` supplies atom counts for compound assembly.
- `molar_mass()` and `mass_percentages()` provide derived material priors.
- These priors can be attached to session events as structured payload fields for audit/replay.
