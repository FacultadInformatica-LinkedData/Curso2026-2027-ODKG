#!/usr/bin/env python3
"""
Generate the RDF with Morph-KGC, as N-Triples and as Turtle.

For every config-*.ini in this folder (or the configs given as arguments):
  - rdf/<name>.nt  is written by Morph-KGC itself, as set in the config's output_file
  - rdf/<name>.ttl is the same graph: Morph-KGC materializes it as an RDFLib graph
                   (morph_kgc.materialize) and RDFLib saves it as Turtle

Morph-KGC's output_format only offers N-Triples, N-Quads and Jelly, so the Turtle file
comes from its RDFLib integration.
"""

import configparser
import os
import subprocess
import sys
from pathlib import Path

import morph_kgc

GROUP_DIR = Path(__file__).resolve().parent
os.chdir(GROUP_DIR)  # the paths in the configs and mappings are relative to this folder

configs = sys.argv[1:] or sorted(path.name for path in GROUP_DIR.glob("config-*.ini"))

for config in configs:
    # N-Triples, written by Morph-KGC exactly as the config says
    if subprocess.run([sys.executable, "-m", "morph_kgc", config]).returncode != 0:
        sys.exit(f"Morph-KGC failed for {config}")

    # Turtle: the same graph, materialized by Morph-KGC as an RDFLib graph
    graph = morph_kgc.materialize(config)

    # Morph-KGC doesn't pass the mappings' prefixes on, so RDFLib would name these two
    # namespaces ns1: and ns2:, in a different order on every run.
    graph.bind("pe", "http://smartcity.chicago.es/ontology/ParkExplorer#")
    graph.bind("schema", "http://schema.org/", replace=True)  # RDFLib's default schema: is https

    ini = configparser.ConfigParser(interpolation=configparser.ExtendedInterpolation())
    ini.read(config)
    ttl_file = Path(ini.get("CONFIGURATION", "output_file", fallback="knowledge-graph")).with_suffix(".ttl")
    graph.serialize(destination=ttl_file, format="turtle")
    print(f"{config}: wrote {ttl_file.with_suffix('.nt')} and {ttl_file} ({len(graph)} triples)")