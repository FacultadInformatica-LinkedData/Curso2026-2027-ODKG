"""Convert an N-Triples file (Morph-KGC output) to Turtle.

Usage: python scripts/nt2ttl.py rdf/trees.nt rdf/trees.ttl

Uses only the standard library. Subjects are sorted by IRI, prefixes are declared
for the namespaces that appear in the file, and decimals are written as bare numbers.
"""
import re
import sys

XSD = "http://www.w3.org/2001/XMLSchema#"
RDF_TYPE = "http://www.w3.org/1999/02/22-rdf-syntax-ns#type"

PREFIXES = {
    "hr": "https://w3id.org/barcelona-heat-relief/ontology/HeatRelief#",
    "shelter": "https://w3id.org/barcelona-heat-relief/resource/ClimateShelter/",
    "shelterCat": "https://w3id.org/barcelona-heat-relief/resource/ShelterCategory/",
    "fountain": "https://w3id.org/barcelona-heat-relief/resource/DrinkingFountain/",
    "tree": "https://w3id.org/barcelona-heat-relief/resource/StreetTree/",
    "species": "https://w3id.org/barcelona-heat-relief/resource/TreeSpecies/",
    "neighbourhood": "https://w3id.org/barcelona-heat-relief/resource/Neighbourhood/",
    "district": "https://w3id.org/barcelona-heat-relief/resource/District/",
    "geo": "http://www.w3.org/2003/01/geo/wgs84_pos#",
    "rdfs": "http://www.w3.org/2000/01/rdf-schema#",
    "owl": "http://www.w3.org/2002/07/owl#",
    "skos": "http://www.w3.org/2004/02/skos/core#",
    "xsd": XSD,
}

LINE = re.compile(
    r'^(<[^>]*>) (<[^>]*>) (<[^>]*>|"(?:[^"\\]|\\.)*"(?:\^\^<[^>]*>|@[A-Za-z]+(?:-[A-Za-z0-9]+)*)?) \.$'
)
LITERAL = re.compile(r'^"((?:[^"\\]|\\.)*)"(?:\^\^<([^>]*)>|@(.+))?$')
DECIMAL = re.compile(r"^[+-]?[0-9]*\.[0-9]+$")
LOCAL = re.compile(r"^[A-Za-z0-9_][A-Za-z0-9_-]*$")
BY_LENGTH = sorted(PREFIXES.items(), key=lambda kv: -len(kv[1]))


def shorten(iri, used):
    for prefix, namespace in BY_LENGTH:
        if iri.startswith(namespace) and LOCAL.match(iri[len(namespace):]):
            used.add(prefix)
            return prefix + ":" + iri[len(namespace):]
    return "<" + iri + ">"


def term(token, used):
    if token.startswith("<"):
        return shorten(token[1:-1], used)
    lexical, datatype, language = LITERAL.match(token).groups()
    if language:
        return '"' + lexical + '"@' + language
    if datatype is None or datatype == XSD + "string":
        return '"' + lexical + '"'
    if datatype == XSD + "decimal" and DECIMAL.match(lexical):
        return lexical
    return '"' + lexical + '"^^' + shorten(datatype, used)


def convert(source, target):
    used = set()
    graph = {}
    with open(source, encoding="utf-8") as handle:
        for number, line in enumerate(handle, 1):
            line = line.rstrip("\r\n")
            if not line:
                continue
            match = LINE.match(line)
            if not match:
                sys.exit(f"{source}, line {number}: unsupported N-Triples line")
            s, p, o = match.groups()
            predicate = "a" if p[1:-1] == RDF_TYPE else shorten(p[1:-1], used)
            graph.setdefault(s[1:-1], set()).add((p[1:-1], predicate, term(o, used)))
    blocks = []
    count = 0
    for subject in sorted(graph):
        by_predicate = {}
        for p_iri, predicate, obj in graph[subject]:
            by_predicate.setdefault((p_iri != RDF_TYPE, p_iri, predicate), []).append(obj)
            count += 1
        entries = [(key[2], ", ".join(sorted(objects))) for key, objects in sorted(by_predicate.items())]
        text = shorten(subject, used)
        for index, (predicate, objects) in enumerate(entries):
            separator = " " if index == 0 else "\n    "
            end = " ." if index == len(entries) - 1 else " ;"
            text += f"{separator}{predicate} {objects}{end}"
        blocks.append(text)
    with open(target, "w", encoding="utf-8", newline="\n") as out:
        for prefix in sorted(used):
            out.write(f"@prefix {prefix}: <{PREFIXES[prefix]}> .\n")
        for text in blocks:
            out.write("\n" + text + "\n")
    return count


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit("Usage: python scripts/nt2ttl.py input.nt output.ttl")
    print(f"{convert(sys.argv[1], sys.argv[2])} triples written to {sys.argv[2]}")
