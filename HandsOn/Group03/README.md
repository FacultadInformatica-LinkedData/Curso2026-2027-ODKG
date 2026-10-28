# Group03 Members
- Diego Aquino (@diegoaquinoh) **Leader**
- Sebastian Linares (@sebasl10)
- Noah Rose (@nsr223)
- Pedro López-Ríos (@plopezriosdc)
- Sergio Gismera Pino (@SergioGismeraPino)

## Hands-on 5: linked data

Each dataset has `*-with-links.json` operations in `lodrefine/`, a linked CSV in
`csv/`, an RML mapping in `mappings/`, and a Turtle export in `rdf/`.

| Dataset basename | Source rows | RDF triples |
| --- | ---: | ---: |
| `estaciones_acusticas` | 31 | 308 |
| `contaminacion_acustica` | 78,230 | 1,017,217 |
| `terrazas_hosteleria` | 6,594 | 53,220 |

The exports link 21 districts and 129 neighbourhoods to Wikidata. Reviewed
types, district membership, municipal codes, source URLs, and the station
district lookup are in [linking/reconciliation-evidence.json](linking/reconciliation-evidence.json).
Stations use `dcterms:spatial`; observations reach districts through
`mn:recordedAt`. Source identifiers, labels, and measurements are preserved.

To reproduce the linked CSVs, start OpenRefine 3.10.0 and run from this directory:

```sh
python3 scripts/replay_linking.py
```

For manual replay, import each `csv/*-updated.csv` as UTF-8, comma-separated
text with one header row and automatic value parsing disabled. Apply its
matching `lodrefine/*-with-links.json`, then export all rows using original
cell contents for reconciled columns, retaining unmatched values and disabling
links to entity pages. The histories use the Spanish Wikidata reconciliation
service with automatic matching disabled and explicitly reviewed identities.

Generate and validate the RDF with Python 3.12 and Morph-KGC 2.10.0:

```sh
uv venv --python 3.12 /tmp/group03-linking-venv
uv pip install --python /tmp/group03-linking-venv/bin/python -r scripts/requirements-linking.txt
/tmp/group03-linking-venv/bin/python scripts/materialize_linking.py
/tmp/group03-linking-venv/bin/python scripts/validate_linking.py
```

Skip environment creation if it already exists. Load the three linked Turtle
exports into one graph and run each query in
[rdf/queries-with-links.sparql](rdf/queries-with-links.sparql) separately.
Expected query row counts are 31, 31, 6,534, 21, and 2.

Station districts describe catalogue locations, not verified historical
locations. The terrace snapshot is dated 2026-10-04 and contains approximate
entrance coordinates for 6,534 terraces; 60 remain unlocated. Seventeen noise
observations have unavailable percentiles and flags; 213 retain source
percentile-order violations. These missing values are omitted from RDF.
