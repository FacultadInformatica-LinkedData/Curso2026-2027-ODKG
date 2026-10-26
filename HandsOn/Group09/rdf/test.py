
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

from rdflib import Graph, Namespace, URIRef
from rdflib.namespace import RDF


BASE_DIR = Path(__file__).resolve().parent
QUERY_FILE = BASE_DIR / "queries.sparql"

PM = Namespace("https://parking-madrid.example.org/ontology#")
BASE = "https://parking-madrid.example.org/resource/"

WARNING_ONLY = {
    "occupancy_space_mismatch",
}


def load_queries(path: Path) -> dict[str, str]:
    """Load SPARQL queries separated by '# QUERY: name' markers."""
    content = path.read_text(encoding="utf-8")
    sections = re.split(
        r"(?m)^# QUERY:\s*([a-zA-Z0-9_]+)\s*$",
        content,
    )

    queries = {}

    for index in range(1, len(sections), 2):
        name = sections[index].strip()
        query = sections[index + 1].strip()

        if query:
            queries[name] = query

    if not queries:
        raise ValueError(f"No named queries found in {path}")

    return queries


def diagnose_district(graph: Graph) -> None:
    """Diagnose whether District/10 exists and is typed correctly."""
    print("\n" + "=" * 65)
    print("DISTRICT DIAGNOSTICS")
    print("=" * 65)

    district = URIRef(f"{BASE}District/10")

    print("\n1. Exact district type triple:")
    triple_exists = (district, RDF.type, PM.District) in graph
    print(triple_exists)

    print("\n2. Types of District/10:")
    types = list(graph.objects(district, RDF.type))

    if types:
        for rdf_type in types:
            print(repr(rdf_type))
    else:
        print("No rdf:type triples found.")

    print("\n3. District references from parking facilities:")
    found = False

    for parking, referenced_district in graph.subject_objects(
        PM.locatedInDistrict
    ):
        if str(referenced_district).endswith("/District/10"):
            found = True
            print("Parking:", repr(parking))
            print("Referenced district:", repr(referenced_district))
            print(
                "Type triple exists:",
                (
                    referenced_district,
                    RDF.type,
                    PM.District,
                ) in graph,
            )
            break

    if not found:
        print("No parking facility references District/10.")

    print("\n4. District resources with code 10:")
    for subject in graph.subjects(PM.hasDistrictCode, None):
        codes = list(graph.objects(subject, PM.hasDistrictCode))

        if any(str(code) == "10" for code in codes):
            print("Resource:", repr(subject))
            print("Types:", list(graph.objects(subject, RDF.type)))

    print("=" * 65)


def main() -> int:
    rdf_path = BASE_DIR / "aparcamientos.ttl"

    if not rdf_path.is_file():
        print(f"ERROR: RDF file not found: {rdf_path}")
        return 2

    if not QUERY_FILE.is_file():
        print(f"ERROR: SPARQL query file not found: {QUERY_FILE}")
        return 2

    # 1. Load RDF.
    graph = Graph()

    try:
        graph.parse(rdf_path, format='turtle')
    except Exception as exc:
        print(f"ERROR: Failed to parse RDF: {exc}")
        return 2

    print(f"RDF file: {rdf_path}")
    print(f"Triples: {len(graph):,}")

    # 2. Count resource types.
    class_counts = {
        "District": len(set(graph.subjects(RDF.type, PM.District))),
        "Neighbourhood": len(
            set(graph.subjects(RDF.type, PM.Neighbourhood))
        ),
        "ParkingFacility": len(
            set(graph.subjects(RDF.type, PM.ParkingFacility))
        ),
        "MonthlyOccupancy": len(
            set(graph.subjects(RDF.type, PM.MonthlyOccupancy))
        ),
    }

    print("\nResource counts:")
    for class_name, count in class_counts.items():
        print(f"  {class_name}: {count:,}")

    # 3. Diagnose the reported district issue.
    diagnose_district(graph)

    # 4. Load named SPARQL queries.
    try:
        queries = load_queries(QUERY_FILE)
    except Exception as exc:
        print(f"ERROR: Failed to load SPARQL queries: {exc}")
        return 2

    errors = 0
    warnings = 0

    for class_name, count in class_counts.items():
        if count == 0:
            print(f"FAIL: No resources of type {class_name}")
            errors += 1

    # 5. Run validation queries.
    print("\nSPARQL validation results:")

    for name, query in queries.items():
        try:
            results = list(graph.query(query))
        except Exception as exc:
            print(f"ERROR: Query '{name}' failed: {exc}")
            errors += 1
            continue

        if not results:
            print(f"PASS: {name}")
            continue

        severity = (
            "WARNING" if name in WARNING_ONLY else "FAIL"
        )
        print(f"{severity}: {name} ({len(results)} result(s))")

        for result in results[:5]:
            values = ", ".join(
                f"{variable}={value}"
                for variable, value in zip(result.labels, result)
            )
            print(f"    {values}")

        if len(results) > 5:
            print(f"    ... and {len(results) - 5} more")

        if severity == "WARNING":
            warnings += len(results)
        else:
            errors += len(results)

    # 6. Summary.
    print("\nSummary:")
    print(f"  Queries executed: {len(queries)}")
    print(f"  Errors: {errors}")
    print(f"  Warnings: {warnings}")

    if errors:
        print("RESULT: FAILED")
        return 1

    print("RESULT: PASSED")

    return 0


if __name__ == "__main__":
    sys.exit(main())
