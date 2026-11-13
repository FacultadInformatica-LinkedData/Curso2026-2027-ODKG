"""Access layer to the knowledge graph.

By default the RDF files are loaded into an in-memory rdflib graph. Setting
SPARQL_ENDPOINT (e.g. a GraphDB or Fuseki repository URL) makes the same
queries run against that endpoint instead.
"""
from __future__ import annotations

import re
import threading
from decimal import Decimal
from pathlib import Path
from typing import Any, Iterable

import requests
from rdflib import Graph, Literal, URIRef
from rdflib.term import Node

PE = "http://smartcity.chicago.es/ontology/ParkExplorer#"
RESOURCE_BASE = "http://smartcity.chicago.es/resource/"
USER_AGENT = (
    "ChicagoParkArtExplorer/1.0 (UPM Open Data and Knowledge Graphs course project; "
    "https://github.com/FacultadInformatica-LinkedData/Curso2026-2027-ODKG)"
)

_WHERE = re.compile(r"WHERE\s*\{", re.IGNORECASE)


def to_python(term: Node | None) -> Any:
    """Turn an rdflib term into a plain Python value (IRIs become str)."""
    if term is None:
        return None
    if isinstance(term, Literal):
        value = term.toPython()
        if isinstance(value, Decimal):
            return float(value)
        if isinstance(value, Literal):  # unknown datatype
            return str(value)
        return value
    return str(term)


def _from_json(binding: dict | None) -> Any:
    if binding is None:
        return None
    kind = binding["type"]
    if kind == "uri":
        return binding["value"]
    if kind == "bnode":
        return "_:" + binding["value"]
    datatype = binding.get("datatype")
    if datatype:
        return to_python(Literal(binding["value"], datatype=URIRef(datatype)))
    return binding["value"]


def inject_values(query: str, bindings: dict[str, Node]) -> str:
    """Bind variables for a remote endpoint with a VALUES clause.

    The values are serialised with rdflib's n3(), which escapes IRIs and
    literals, so the result is safe to send.
    """
    if not bindings:
        return query
    names = " ".join(f"?{name}" for name in bindings)
    values = " ".join(term.n3() for term in bindings.values())
    clause = f"\n  VALUES ({names}) {{ ({values}) }}\n"
    match = _WHERE.search(query)
    if not match:
        raise ValueError("query has no WHERE clause to bind variables into")
    return query[: match.end()] + clause + query[match.end():]


class KnowledgeGraph:
    def __init__(
        self,
        rdf_files: Iterable[Path | str] = (),
        endpoint: str | None = None,
        timeout: float = 30,
    ) -> None:
        self.endpoint = endpoint
        self.timeout = timeout
        self._lock = threading.Lock()
        self.graph: Graph | None = None
        if not endpoint:
            graph = Graph()
            for path in rdf_files:
                path = Path(path)
                fmt = "nt" if path.suffix == ".nt" else "turtle"
                graph.parse(str(path), format=fmt)
            self.graph = graph

    @property
    def source(self) -> str:
        return self.endpoint or "in-memory rdflib graph"

    def __len__(self) -> int:
        if self.graph is not None:
            return len(self.graph)
        rows = self.select("SELECT (COUNT(*) AS ?n) WHERE { ?s ?p ?o }")
        return int(rows[0]["n"])

    def select(self, query: str, **bindings: Node) -> list[dict[str, Any]]:
        """Run a SELECT query; each row is a dict of plain Python values."""
        if self.graph is not None:
            with self._lock:
                result = self.graph.query(query, initBindings=bindings or None)
                variables = list(result.vars or [])
                return [{str(v): to_python(row[v]) for v in variables} for row in result]
        response = requests.post(
            self.endpoint,
            data={"query": inject_values(query, bindings)},
            headers={"Accept": "application/sparql-results+json", "User-Agent": USER_AGENT},
            timeout=self.timeout,
        )
        response.raise_for_status()
        data = response.json()
        variables = data["head"]["vars"]
        return [{v: _from_json(b.get(v)) for v in variables} for b in data["results"]["bindings"]]


    def describe(self, uri: URIRef) -> Graph:
        """Every triple in which the resource is the subject or the object."""
        result = Graph()
        if self.graph is not None:
            with self._lock:
                for triple in self.graph.triples((uri, None, None)):
                    result.add(triple)
                for triple in self.graph.triples((None, None, uri)):
                    result.add(triple)
            return result
        query = "CONSTRUCT { ?s ?p ?o . ?x ?q ?s } WHERE { { ?s ?p ?o } UNION { ?x ?q ?s } }"
        response = requests.post(
            self.endpoint,
            data={"query": inject_values(query, {"s": uri})},
            headers={"Accept": "text/turtle", "User-Agent": USER_AGENT},
            timeout=self.timeout,
        )
        response.raise_for_status()
        result.parse(data=response.text, format="turtle")
        return result
