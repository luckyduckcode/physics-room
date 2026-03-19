from __future__ import annotations

import argparse
from typing import Iterable, Optional

from dynamics_module import load_default_taxonomy, SystemEntry
from dynamics_module.taxonomy import DynamicsTaxonomy


def _print_rows(rows: Iterable[SystemEntry]) -> None:
    rows = list(rows)
    if not rows:
        print("No results.")
        return
    for i, r in enumerate(rows, start=1):
        print(
            f"{i:>2}. {r.system} | Kingdom={r.kingdom} | Phylum={r.phylum} | "
            f"Class={r.class_type} | Linearity={r.linearity} | Energy={r.energy} | Dynamics={r.dynamics}"
        )


def _print_grouped_rows(grouped: dict[str, list[SystemEntry]]) -> None:
    for key, rows in grouped.items():
        print(f"\n## {key} ({len(rows)})")
        for r in rows:
            print(f"- {r.system}")


def _parse_fields(raw_fields: Optional[list[str]]) -> Optional[list[str]]:
    if not raw_fields:
        return None

    parsed: list[str] = []
    for item in raw_fields:
        parsed.extend(part.strip() for part in item.split(",") if part.strip())
    return parsed or None


def _interactive_mode(tax: DynamicsTaxonomy) -> None:
    print("Kingdom of Dynamics - Interactive Mode")
    print("Type 'help' for commands, 'quit' to exit.")

    while True:
        cmd = input("\nkd> ").strip().lower()

        if cmd in {"quit", "exit", "q"}:
            print("Goodbye.")
            return

        if cmd in {"help", "h", "?"}:
            print("""
Commands:
  list                     List all systems
  show                     Show one system by exact name
  search                   Search text across fields
  filter                   Filter by taxonomy fields
  group                    Group by a field
    summary                  Show taxonomy summary
    related                  Show systems related to one system
  families                 Show energy-family guide
  dna                      Show mathematical DNA guide
  quit                     Exit
""")
            continue

        if cmd == "list":
            _print_rows(tax.all())
            continue

        if cmd == "show":
            name = input("Exact system name: ").strip()
            item = tax.get(name)
            if item:
                _print_rows([item])
            else:
                print("No exact match found.")
                suggestions = tax.suggest_systems(name)
                if suggestions:
                    print("Did you mean:")
                    for s in suggestions:
                        print(f"- {s}")
            continue

        if cmd == "search":
            query = input("Search text: ").strip()
            fields = input("Fields (comma-separated, blank for all): ").strip()
            limit_raw = input("Limit (blank for all): ").strip()

            parsed_fields = _parse_fields([fields]) if fields else None
            limit = int(limit_raw) if limit_raw else None
            _print_rows(tax.search(query, fields=parsed_fields, limit=limit))
            continue

        if cmd == "filter":
            print("Leave blank to skip a field.")
            system = input("System: ").strip() or None
            kingdom = input("Kingdom: ").strip() or None
            phylum = input("Phylum: ").strip() or None
            class_type = input("Class: ").strip() or None
            linearity = input("Linearity: ").strip() or None
            energy = input("Energy: ").strip() or None
            dynamics = input("Dynamics: ").strip() or None
            contains = (input("Contains matching? [y/N]: ").strip().lower() in {"y", "yes"})
            _print_rows(
                tax.filter(
                    system=system,
                    kingdom=kingdom,
                    phylum=phylum,
                    class_type=class_type,
                    linearity=linearity,
                    energy=energy,
                    dynamics=dynamics,
                    contains=contains,
                )
            )
            continue

        if cmd == "group":
            field = input("Group field (system/kingdom/phylum/class/linearity/energy/dynamics): ").strip()
            try:
                grouped = tax.group_by(field)
            except ValueError as e:
                print(e)
                continue

            _print_grouped_rows(grouped)
            continue

        if cmd == "summary":
            data = tax.summary()
            print(f"Total systems: {data['count']}")
            print("Unique values by field:")
            for field_name, values in data["fields"].items():
                print(f"- {field_name}: {', '.join(values)}")
            continue

        if cmd == "related":
            name = input("System name: ").strip()
            by = input("Group by field (default phylum): ").strip() or "phylum"
            try:
                rows = tax.related(name, by=by)
            except ValueError as e:
                print(e)
                continue
            _print_rows(rows)
            continue

        if cmd == "families":
            for name, desc in tax.family_guide.items():
                print(f"- {name}: {desc}")
            continue

        if cmd == "dna":
            for name, desc in tax.dna_guide.items():
                print(f"- {name}: {desc}")
            continue

        print("Unknown command. Type 'help' for options.")


def main() -> None:
    parser = argparse.ArgumentParser(description="Navigate the Kingdom of Dynamics taxonomy.")
    parser.add_argument("--data", default="physics_dynamics_taxonomy.csv", help="Path to taxonomy CSV")

    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("list", help="List all systems")

    show = sub.add_parser("show", help="Show one system by exact name")
    show.add_argument("name", help="Exact system name")

    search = sub.add_parser("search", help="Text search across all fields")
    search.add_argument("query", help="Search text")
    search.add_argument(
        "--fields",
        nargs="*",
        help="Fields to search in (space/comma separated): system kingdom phylum class linearity energy dynamics",
    )
    search.add_argument("--limit", type=int, default=None, help="Max number of results")

    flt = sub.add_parser("filter", help="Filter by one or more fields")
    flt.add_argument("--system")
    flt.add_argument("--kingdom")
    flt.add_argument("--phylum")
    flt.add_argument("--class-type")
    flt.add_argument("--linearity")
    flt.add_argument("--energy")
    flt.add_argument("--dynamics")
    flt.add_argument("--contains", action="store_true", help="Use case-insensitive contains match instead of exact match")

    group = sub.add_parser("group", help="Group systems by a field")
    group.add_argument("field", choices=["system", "kingdom", "phylum", "class", "linearity", "energy", "dynamics"])

    sub.add_parser("summary", help="Show taxonomy summary and unique field values")

    related = sub.add_parser("related", help="Show systems related to a given system")
    related.add_argument("name", help="Anchor system name")
    related.add_argument("--by", default="phylum", choices=["system", "kingdom", "phylum", "class", "linearity", "energy", "dynamics"])
    related.add_argument("--limit", type=int, default=10, help="Max related systems to return")

    sub.add_parser("families", help="Show the energy-family guide")
    sub.add_parser("dna", help="Show the mathematical DNA guide")
    sub.add_parser("interactive", help="Run interactive terminal navigator")

    args = parser.parse_args()
    tax = load_default_taxonomy(".") if args.data == "physics_dynamics_taxonomy.csv" else DynamicsTaxonomy.from_csv(args.data)

    if args.command == "list":
        _print_rows(tax.all())
    elif args.command == "show":
        item = tax.get(args.name)
        if item:
            _print_rows([item])
        else:
            print("No exact match found.")
            suggestions = tax.suggest_systems(args.name)
            if suggestions:
                print("Did you mean:")
                for s in suggestions:
                    print(f"- {s}")
    elif args.command == "search":
        fields = _parse_fields(args.fields)
        _print_rows(tax.search(args.query, fields=fields, limit=args.limit))
    elif args.command == "filter":
        _print_rows(
            tax.filter(
                system=args.system,
                kingdom=args.kingdom,
                phylum=args.phylum,
                class_type=args.class_type,
                linearity=args.linearity,
                energy=args.energy,
                dynamics=args.dynamics,
                contains=args.contains,
            )
        )
    elif args.command == "group":
        grouped = tax.group_by(args.field)
        _print_grouped_rows(grouped)
    elif args.command == "summary":
        data = tax.summary()
        print(f"Total systems: {data['count']}")
        print("Unique values by field:")
        for field_name, values in data["fields"].items():
            print(f"- {field_name}: {', '.join(values)}")
    elif args.command == "related":
        _print_rows(tax.related(args.name, by=args.by, limit=args.limit))
    elif args.command == "families":
        for name, desc in tax.family_guide.items():
            print(f"- {name}: {desc}")
    elif args.command == "dna":
        for name, desc in tax.dna_guide.items():
            print(f"- {name}: {desc}")
    elif args.command == "interactive":
        _interactive_mode(tax)


if __name__ == "__main__":
    main()
