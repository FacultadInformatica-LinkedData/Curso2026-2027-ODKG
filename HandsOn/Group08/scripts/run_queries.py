"""Run the queries of a .sparql file on one or more RDF files and print the results.

Usage: python scripts/run_queries.py rdf/queries.sparql "rdf/*.ttl"

The queries in the file are separated by comment lines that start with "# Q".
"""
import glob
import re
import sys
import time

from pyoxigraph import Literal, NamedNode, Store

BASE = "https://w3id.org/barcelona-heat-relief/"
MAX_ROWS = 25


def show(term):
    if term is None:
        return ""
    if isinstance(term, NamedNode):
        return term.value.replace(BASE, "")
    if isinstance(term, Literal):
        return term.value
    return str(term)


def split_queries(text):
    parts = re.split(r"(?m)^# (Q\d+\..*)$", text)
    return [(parts[i], parts[i + 1]) for i in range(1, len(parts), 2)]


def main(query_file, data_files):
    sys.stdout.reconfigure(encoding="utf-8")
    store = Store()
    for path in data_files:
        with open(path, "rb") as handle:
            store.bulk_load(handle, "text/turtle")
    with open(query_file, encoding="utf-8") as handle:
        queries = split_queries(handle.read())
    for title, body in queries:
        started = time.time()
        solutions = store.query(body)
        names = [v.value for v in solutions.variables]
        rows = [[show(t) for t in row] for row in solutions]
        print(f"\n{title}")
        print("  " + " | ".join(names))
        for row in rows[:MAX_ROWS]:
            print("  " + " | ".join(row))
        more = f", first {MAX_ROWS} shown" if len(rows) > MAX_ROWS else ""
        print(f"  ({len(rows)} rows{more}, {time.time() - started:.1f} s)")


if __name__ == "__main__":
    if len(sys.argv) < 3:
        sys.exit('Usage: python scripts/run_queries.py rdf/queries.sparql "rdf/*.ttl"')
    files = [p for arg in sys.argv[2:] for p in sorted(glob.glob(arg))]
    main(sys.argv[1], files)
