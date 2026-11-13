"""The SPARQL layer returns what the RDF contains (counts from queries-with-links.sparql)."""
import pytest
from rdflib import Literal, URIRef

import queries as Q
from kg import RESOURCE_BASE, inject_values


def test_catalog_counts(services):
    catalog = services.catalog
    assert len(catalog.parks) == 555
    assert len(catalog.facilities) == 4466
    assert len(catalog.artworks) == 346
    assert sum(1 for p in catalog.parks.values() if p.wikidata) == 322


def test_class_counts(services):
    classes = {uri.rsplit("#", 1)[-1].rsplit("/", 1)[-1]: v for uri, v in services.stats["classes"].items()}
    assert classes["ChicagoPark"] == (555, 322)
    assert classes["Artist"] == (264, 97)
    assert classes["Facility"][0] == 4466


def test_every_place_has_a_park_and_coordinates(services):
    catalog = services.catalog
    for place in list(catalog.facilities.values()) + list(catalog.artworks.values()):
        assert place.park_uri in catalog.parks
        assert 41.6 < place.lat < 42.1 and -88 < place.lon < -87.5


def test_detail_query_binds_one_resource(services):
    rows = services.kg.select(Q.ARTWORK_DETAIL, artwork=URIRef(RESOURCE_BASE + "Artwork/Indian_Boundary_River_Suite"))
    assert len(rows) == 1
    assert rows[0]["name"] == "River Suite"
    assert rows[0]["parkName"] == "INDIAN BOUNDARY"


def test_find_park(services):
    catalog = services.catalog
    assert catalog.find_park("Lincoln (Abraham)").raw_name == "LINCOLN (ABRAHAM)"
    assert catalog.find_park("lincoln (abraham)").raw_name == "LINCOLN (ABRAHAM)"
    assert catalog.find_park("no such park") is None


def test_inject_values_escapes_terms():
    query = "SELECT ?n WHERE { ?s ?p ?n }"
    sent = inject_values(query, {"n": Literal('x" } DROP ALL #')})
    assert 'VALUES (?n) { ("x\\" } DROP ALL #") }' in sent  # the quote is escaped
    with pytest.raises(Exception):
        inject_values(query, {"s": URIRef("http://example.org/a>b")})  # invalid IRIs are refused
