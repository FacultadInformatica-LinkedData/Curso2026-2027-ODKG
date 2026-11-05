"""Pre-fetch Wikidata facts for every linked park and artist.

    python warm_wikidata.py

Writes wikidata_seed.json next to this file. The app reads it at start-up, so
the deployed site works even when Wikidata is slow or unreachable (e.g. from
a PythonAnywhere free account). Re-run it after the RDF changes.
"""
from __future__ import annotations

import sys
import time
from pathlib import Path


from kg import KnowledgeGraph
from wikidata import WikidataClient, qid_of

APP_DIR = Path(__file__).resolve().parent
RDF_FILES = ("facilities-with-links-fixed.nt", "park-art-with-links-fixed.nt")
TARGETS = """
PREFIX owl: <http://www.w3.org/2002/07/owl#>
SELECT DISTINCT ?target WHERE { ?s owl:sameAs ?target }
"""


def main() -> int:
    kg = KnowledgeGraph([APP_DIR.parent / "rdf" / name for name in RDF_FILES])
    targets = sorted({row["target"] for row in kg.select(TARGETS) if qid_of(row["target"])})
    client = WikidataClient(APP_DIR / "wikidata_seed.json", timeout=30)
    missing = []
    for i, uri in enumerate(targets, start=1):
        if client.entity(uri) is None:
            client._offline_until = 0  # retry the next one instead of backing off
            missing.append(uri)
        print(f"\r{i}/{len(targets)} fetched, {len(missing)} failed", end="", flush=True)
        time.sleep(0.5)  # be polite to the public endpoint
    print()
    for uri in missing:
        print("not fetched:", uri)
    return 0


if __name__ == "__main__":
    sys.exit(main())
