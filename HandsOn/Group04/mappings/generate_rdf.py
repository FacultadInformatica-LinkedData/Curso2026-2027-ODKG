"""Group04 - Breathe & Play Madrid - Hands-on 4

Runs the RML mappings with Morph-KGC and writes one Turtle file per dataset.
Morph-KGC only serialises N-Triples/N-Quads, so the graph is materialised in
memory and serialised as Turtle with rdflib.

Usage (from the HandsOn/Group04 directory):
    pip install morph-kgc rdflib
    python mappings/generate_rdf.py
"""
from pathlib import Path

import morph_kgc
from rdflib import XSD, Literal, Namespace

BASE = "https://w3id.org/breatheplay-madrid/resource/"
PREFIXES = {
    "bpm": "https://w3id.org/breatheplay-madrid/ontology#",
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
mappings: mappings/{name}.rml
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
        graph.bind(prefix, Namespace(uri))
    out = Path("rdf", f"{name}.ttl")
    graph.serialize(destination=out, format="turtle", encoding="utf-8")
    print(f"{out}: {len(graph)} triples")
