"""Group04 - Breathe & Play Madrid - Hands-on 5 (linking)

Runs the RML mappings with links (mappings/*-with-links.rml) with Morph-KGC and
writes, for each dataset, one N-Triples file (rdf/*-with-links.nt) and one Turtle
file (rdf/*-with-links.ttl) with the same triples. The mappings read the CSV files
enriched with Wikidata links in OpenRefine (csv/*-with-links.csv) and add the
owl:sameAs triples.

Usage (from the HandsOn/Group04 directory):
    pip install morph-kgc rdflib
    python mappings/generate_rdf-with-links.py

Important: On Windows, set PYTHONUTF8=1 first (cmd/Anaconda Prompt: set PYTHONUTF8=1;
PowerShell: $env:PYTHONUTF8 = "1") so that the mappings are read as UTF-8.
"""
from pathlib import Path

import morph_kgc
from rdflib import XSD, Literal, Namespace

BASE = "https://w3id.org/breatheplay-madrid/resource/"
PREFIXES = {
    "bpm": "https://w3id.org/breatheplay-madrid/ontology#",
    "sosa": "http://www.w3.org/ns/sosa/",
    "geo": "http://www.w3.org/2003/01/geo/wgs84_pos#",
    "schema": "http://schema.org/",
    "owl": "http://www.w3.org/2002/07/owl#",
    "wd": "http://www.wikidata.org/entity/",
    "obs": BASE + "observation/",
    "sp": BASE + "sampling-point/",
    "pol": BASE + "pollutant/",
    "tech": BASE + "technique/",
    "station": BASE + "station/",
    "sttype": BASE + "station-type/",
    "fac": BASE + "sports-facility/",
    "factype": BASE + "facility-type/",
    "access": BASE + "accessibility-level/",
    "district": BASE + "district/",
    "nbh": BASE + "neighbourhood/",
}

DATASETS = [
    "calidad-aire-diario-2024",
    "estaciones-control-aire",
    "instalaciones-deportivas",
]

Path("rdf").mkdir(exist_ok=True)
for name in DATASETS:
    config = f"""
[CONFIGURATION]
na_values=,#N/A,N/A,NULL,null,NaN,nan,None

[{name}]
mappings: mappings/{name}-with-links.rml
"""
    graph = morph_kgc.materialize(config)
    # The mappings declare rr:datatype xsd:string, but plain literals lose it
    # on the way out; make it explicit (self-assessment: "includes its datatype").
    plain = [(s, p, o) for s, p, o in graph
             if isinstance(o, Literal) and o.datatype is None and o.language is None]
    for s, p, o in plain:
        graph.remove((s, p, o))
        graph.add((s, p, Literal(str(o), datatype=XSD.string)))
    for prefix, uri in PREFIXES.items():
        graph.bind(prefix, Namespace(uri), override=True, replace=True)
    for ext, fmt in (("nt", "nt"), ("ttl", "turtle")):
        out = Path("rdf", f"{name}-with-links.{ext}")
        graph.serialize(destination=out, format=fmt, encoding="utf-8")
        print(f"{out}: {len(graph)} triples")
