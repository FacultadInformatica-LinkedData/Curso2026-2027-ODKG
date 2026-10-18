"""Check RDF files against the self-assessment criteria of hands-on 4.

Usage: python scripts/check_rdf.py ontology/HeatRelief.ttl "rdf/*.ttl" [--compare rdf/graph.nt]

The first file is the ontology; the others are the data files (wildcards are expanded).
With --compare, the data files are also compared with the N-Triples file produced by
Morph-KGC from mappings/config.ini.
"""
import glob
import re
import sys
import unicodedata
from collections import Counter

from pyoxigraph import BlankNode, Literal, NamedNode, Store, parse

RDF = "http://www.w3.org/1999/02/22-rdf-syntax-ns#"
RDFS = "http://www.w3.org/2000/01/rdf-schema#"
OWL = "http://www.w3.org/2002/07/owl#"
XSD = "http://www.w3.org/2001/XMLSchema#"
LINKING = {OWL + "sameAs", "http://www.w3.org/2004/02/skos/core#broadMatch"}
NUMBER = re.compile(r"^[+-]?[0-9]+([.,][0-9]+)?$")
DATE = re.compile(r"^[0-9]{4}-[0-9]{2}-[0-9]{2}")
BOOLEAN = re.compile(r"^(true|false)$", re.IGNORECASE)
PLACEHOLDER_NUMBER = re.compile(r", (0|9999)$")


def has_hidden_character(text):
    """True if the text has a control or format character (such as U+FEFF), apart from tab and line breaks."""
    return any(unicodedata.category(c) in ("Cc", "Cf") and c not in "\t\n\r" for c in text)


def triples(path):
    mime = "application/n-triples" if path.endswith(".nt") else "text/turtle"
    with open(path, "rb") as handle:
        for quad in parse(handle, mime):
            yield quad.subject, quad.predicate.value, quad.object


def read_ontology(path):
    classes, properties, parents = set(), {}, {}
    domain, range_ = {}, {}
    for s, p, o in triples(path):
        if isinstance(s, BlankNode):
            continue
        if p == RDF + "type" and o.value == OWL + "Class":
            classes.add(s.value)
        elif p == RDF + "type" and o.value in (OWL + "ObjectProperty", OWL + "DatatypeProperty"):
            properties[s.value] = o.value
        elif p == RDFS + "subClassOf":
            parents.setdefault(s.value, set()).add(o.value)
        elif p == RDFS + "domain":
            domain[s.value] = o.value
        elif p == RDFS + "range":
            range_[s.value] = o.value
    return classes, properties, parents, domain, range_


def ancestors(cls, parents):
    found, pending = {cls}, [cls]
    while pending:
        for parent in parents.get(pending.pop(), ()):
            if parent not in found:
                found.add(parent)
                pending.append(parent)
    return found


def main(ontology, files):
    classes, properties, parents, domain, range_ = read_ontology(ontology)
    types, labels, subjects = {}, set(), set()
    for f in files:
        for s, p, o in triples(f):
            if isinstance(s, BlankNode):
                continue
            subjects.add(s.value)
            if p == RDF + "type":
                types.setdefault(s.value, set()).add(o.value)
            elif p == RDFS + "label":
                labels.add(s.value)
    individuals = {s for s, t in types.items() if t & classes}

    unknown_class, unknown_property = Counter(), Counter()
    bad_iri, untrimmed, placeholder, hidden = set(), Counter(), Counter(), Counter()
    placeholder_number = 0
    bad_domain, bad_range, looks_typed = Counter(), Counter(), Counter()
    total = 0
    for f in files:
        for s, p, o in triples(f):
            if isinstance(s, BlankNode):
                continue
            total += 1
            if p == RDF + "type":
                if o.value not in classes:
                    unknown_class[o.value] += 1
            elif p != RDFS + "label" and p not in properties and p not in LINKING:
                unknown_property[p] += 1
            for term in (s, o):
                if isinstance(term, NamedNode) and (re.search(r"\s", term.value) or re.match(r"^[a-z]+://[^/]+/.*//", term.value)):
                    bad_iri.add(term.value)
            if p in domain and not any(domain[p] in ancestors(t, parents) for t in types.get(s.value, ())):
                bad_domain[p] += 1
            if isinstance(o, Literal):
                if o.value != o.value.strip() or o.value == "":
                    untrimmed[p] += 1
                if has_hidden_character(o.value):
                    hidden[p] += 1
                if p.endswith("#streetAddress") and PLACEHOLDER_NUMBER.search(o.value):
                    placeholder_number += 1
                if p == RDFS + "label" and re.match(r"^[-\s]*$", o.value):
                    placeholder[p] += 1
                if p in range_ and o.datatype.value != range_[p]:
                    bad_range[p] += 1
                if o.datatype.value == XSD + "string" and p != RDFS + "label" and (
                    NUMBER.match(o.value) or DATE.match(o.value) or BOOLEAN.match(o.value)
                ):
                    looks_typed[p] += 1
            elif isinstance(o, NamedNode) and p in range_ and p in properties and p != RDF + "type":
                if not any(range_[p] in ancestors(t, parents) for t in types.get(o.value, ())):
                    bad_range[p] += 1

    def short(counter):
        return {k.split("#")[-1].split("/")[-1]: v for k, v in counter.items()} or 0

    print(f"triples {total}, subjects {len(subjects)}, individuals {len(individuals)}")
    print(f"subjects without type: {len(subjects - set(types))}")
    print(f"individuals without label: {len(individuals - labels)}")
    print(f"classes not in ontology: {short(unknown_class)}; properties not in ontology: {short(unknown_property)}")
    print(f"IRIs with double slash or whitespace: {len(bad_iri)}")
    print(f"literals not trimmed or empty: {short(untrimmed)}; placeholder labels: {short(placeholder)}")
    print(f"literals with hidden or control characters: {short(hidden)}")
    print(f"street addresses ending with the placeholder number 0 or 9999: {placeholder_number}")
    print(f"subjects outside the property domain: {short(bad_domain)}")
    print(f"values outside the property range (datatype or class): {short(bad_range)}")
    print(f"plain strings that look like numbers, dates or booleans: {short(looks_typed)}")


def compare(reference_path, files):
    reference, produced = Store(), Store()
    with open(reference_path, "rb") as handle:
        reference.bulk_load(handle, "application/n-triples")
    for f in files:
        with open(f, "rb") as handle:
            produced.bulk_load(handle, "text/turtle")
    only_files = sum(1 for quad in produced if quad not in reference)
    only_graph = len(reference) - (len(produced) - only_files)
    print(f"comparison with {reference_path}: {len(reference)} triples generated, {len(produced)} in the files, "
          f"only in the files {only_files}, only in the generated graph {only_graph}")


if __name__ == "__main__":
    args = sys.argv[1:]
    reference = None
    if "--compare" in args:
        position = args.index("--compare")
        reference = args[position + 1]
        del args[position:position + 2]
    paths = [p for arg in args for p in sorted(glob.glob(arg))]
    if len(paths) < 2:
        sys.exit('Usage: python scripts/check_rdf.py ontology/HeatRelief.ttl "rdf/*.ttl" [--compare rdf/graph.nt]')
    main(paths[0], paths[1:])
    if reference:
        compare(reference, paths[1:])
