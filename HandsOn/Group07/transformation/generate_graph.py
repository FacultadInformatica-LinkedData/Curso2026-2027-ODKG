import argparse
import os
from pathlib import Path

import morph_kgc


def parse_args():
    parser = argparse.ArgumentParser(
        description="Generate the RDF graph in Turtle format."
    )
    parser.add_argument(
        "--with-links",
        action="store_true",
        help="Use the Wikidata-linked CSV and mapping.",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    group_dir = Path(__file__).resolve().parent.parent
    rdf_dir = group_dir / "rdf"

    if args.with_links:
        config_path = "transformation/config-with-links.ini"
        output_path = rdf_dir / "knowledge-graph-with-links.ttl"
    else:
        config_path = "transformation/config.ini"
        output_path = rdf_dir / "knowledge-graph.ttl"

    # Paths in the configuration files are relative to Group07.
    os.chdir(group_dir)

    graph = morph_kgc.materialize(config_path)

    rdf_dir.mkdir(exist_ok=True)

    graph.serialize(
        destination=str(output_path),
        format="turtle",
    )

    print(f"Generated {len(graph)} triples in {output_path.name}")


if __name__ == "__main__":
    main()
