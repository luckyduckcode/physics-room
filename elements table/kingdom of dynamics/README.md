# Kingdom of Dynamics

A lightweight Python toolkit for exploring a dynamics taxonomy from CSV data.

It includes:
- a reusable Python API (`dynamics_module`)
- a command-line interface (`cli.py`)
- a curated dataset (`physics_dynamics_taxonomy.csv`)

## Project structure

- `physics_dynamics_taxonomy.csv` — source taxonomy data
- `dynamics_module/taxonomy.py` — core data model and query API
- `dynamics_module/__init__.py` — package exports
- `cli.py` — command-line navigator

## Requirements

- Python 3.9+
- No third-party dependencies (standard library only)

## Quick start

From the project root:

```bash
python cli.py list
python cli.py interactive
python cli.py search "chaos"
python cli.py search "chaos" --fields dynamics --limit 5
python cli.py show "Double Pendulum"
python cli.py filter --energy Dissipative --linearity Non-linear
python cli.py filter --energy diss --contains
python cli.py group energy
python cli.py summary
python cli.py related "Double Pendulum" --by phylum --limit 5
python cli.py families
python cli.py dna
```

## CLI commands

- `list` — list all systems
- `show <name>` — show a system by exact name
- `search <query> [--fields ...] [--limit N]` — substring search across selected fields
- `filter [--system ... --kingdom ... --phylum ... --class-type ... --linearity ... --energy ... --dynamics ...] [--contains]`
- `group <field>` — group systems by: `system`, `kingdom`, `phylum`, `class`, `linearity`, `energy`, `dynamics`
- `summary` — show counts and unique values by taxonomy field
- `related <name> [--by field] [--limit N]` — show related systems by a shared field
- `families` — show energy-family guide
- `dna` — show mathematical DNA guide
- `interactive` — launch menu-driven terminal mode

Optional global argument:

```bash
python cli.py --data /path/to/your.csv list
```

## Python API example

```python
from dynamics_module import load_default_taxonomy

tax = load_default_taxonomy(".")

print(tax.systems())
print(tax.family_guide)
print(tax.dna_guide)

results = tax.filter(energy="Dissipative", linearity="Non-linear")
for row in results:
    print(row.system)

print(tax.summary())
print(tax.suggest_systems("double"))
print(tax.related("Double Pendulum", by="phylum", limit=3))
```

## Notes

- Filtering is exact-match and case-insensitive by default; add `contains=True` for partial match.
- `search` is case-insensitive substring matching and can be restricted to selected fields.
- If the CSV path is invalid, loading will raise `FileNotFoundError`.
