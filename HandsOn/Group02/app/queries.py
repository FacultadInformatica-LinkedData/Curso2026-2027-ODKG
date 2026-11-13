"""Every SPARQL query the application runs, in one place.

The queries are written against the Group02 ontology (ontology/ontology.ttl)
and the linked RDF in rdf/*-with-links.nt. Variables listed under
"binds" are filled in per request (rdflib initBindings locally, a VALUES
clause on a remote endpoint), so user input never becomes query text.

QUERIES maps a name to (description, binds, query) and is shown on /about.
"""
from __future__ import annotations

PREFIXES = """PREFIX pe:     <http://smartcity.chicago.es/ontology/ParkExplorer#>
PREFIX schema: <http://schema.org/>
PREFIX rdf:    <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs:   <http://www.w3.org/2000/01/rdf-schema#>
PREFIX owl:    <http://www.w3.org/2002/07/owl#>
"""

QUERIES: dict[str, tuple[str, tuple[str, ...], str]] = {}


def _query(name: str, description: str, body: str, binds: tuple[str, ...] = ()) -> str:
    text = PREFIXES + body.strip() + "\n"
    QUERIES[name] = (description, binds, body.strip())
    return text


# --- Loaded once at start-up to build the in-memory catalogue ---------------

ALL_PARKS = _query(
    "ALL_PARKS",
    "Every park with its number and, when it was reconciled, its Wikidata entity.",
    """
SELECT ?park ?name ?number ?wikidata WHERE {
  ?park a pe:ChicagoPark ;
        pe:parkName ?name .
  OPTIONAL { ?park pe:parkNumber ?number }
  OPTIONAL { ?park owl:sameAs ?wikidata }
}""",
)

ALL_FACILITIES = _query(
    "ALL_FACILITIES",
    "Every facility with its name, type, hosting park and coordinates "
    "(feeds FR-02 recommendations and the map).",
    """
SELECT ?facility ?name ?type ?park ?lat ?lon WHERE {
  ?park pe:hasFacility ?facility .
  ?facility a pe:Facility ;
            pe:facilityName ?name ;
            pe:facilityType ?type ;
            schema:geo ?geo .
  ?geo schema:latitude ?lat ;
       schema:longitude ?lon .
}""",
)

ALL_ARTWORKS = _query(
    "ALL_ARTWORKS",
    "Every artwork with its hosting park and coordinates (feeds the FR-03 itinerary).",
    """
SELECT ?artwork ?name ?official ?park ?lat ?lon WHERE {
  ?park pe:hasArtwork ?artwork .
  ?artwork a pe:Artwork ;
           pe:artworkName ?name ;
           schema:geo ?geo .
  ?geo schema:latitude ?lat ;
       schema:longitude ?lon .
  OPTIONAL { ?artwork pe:officialName ?official }
}""",
)

ARTWORK_CREATORS = _query(
    "ARTWORK_CREATORS",
    "Who made each artwork, with the artist's Wikidata entity when linked.",
    """
SELECT ?artwork ?artist ?artistName ?wikidata WHERE {
  ?artwork pe:madeBy ?artist .
  ?artist pe:artistName ?artistName .
  OPTIONAL { ?artist owl:sameAs ?wikidata }
}""",
)

CLASS_COUNTS = _query(
    "CLASS_COUNTS",
    "Number of individuals per class, and how many of them are linked with owl:sameAs.",
    """
SELECT ?class (COUNT(DISTINCT ?s) AS ?individuals) (COUNT(DISTINCT ?linked) AS ?linkedIndividuals) WHERE {
  ?s a ?class .
  OPTIONAL { ?s owl:sameAs ?target . BIND(?s AS ?linked) }
}
GROUP BY ?class
ORDER BY DESC(?individuals)""",
)

# --- Run per request on the detail pages -----------------------------------

PARK_DETAIL = _query(
    "PARK_DETAIL",
    "Name, number and Wikidata link of one park.",
    """
SELECT ?name ?number ?wikidata WHERE {
  ?park a pe:ChicagoPark ;
        pe:parkName ?name .
  OPTIONAL { ?park pe:parkNumber ?number }
  OPTIONAL { ?park owl:sameAs ?wikidata }
}""",
    ("park",),
)

PARK_FACILITIES = _query(
    "PARK_FACILITIES",
    "Facilities of one park.",
    """
SELECT ?facility ?name ?type ?lat ?lon WHERE {
  ?park pe:hasFacility ?facility .
  ?facility pe:facilityName ?name ;
            pe:facilityType ?type ;
            schema:geo ?geo .
  ?geo schema:latitude ?lat ;
       schema:longitude ?lon .
}
ORDER BY ?name ?facility""",
    ("park",),
)

PARK_ARTWORKS = _query(
    "PARK_ARTWORKS",
    "Artworks of one park, with their artists (one row per artist).",
    """
SELECT ?artwork ?name ?lat ?lon ?artistName WHERE {
  ?park pe:hasArtwork ?artwork .
  ?artwork pe:artworkName ?name ;
           schema:geo ?geo .
  ?geo schema:latitude ?lat ;
       schema:longitude ?lon .
  OPTIONAL { ?artwork pe:madeBy ?artist . ?artist pe:artistName ?artistName }
}
ORDER BY ?name ?artistName""",
    ("park",),
)

FACILITY_DETAIL = _query(
    "FACILITY_DETAIL",
    "One facility, its coordinates and its park.",
    """
SELECT ?name ?type ?gis ?lat ?lon ?park ?parkName ?parkWikidata WHERE {
  ?facility a pe:Facility ;
            pe:facilityName ?name ;
            pe:facilityType ?type ;
            schema:geo ?geo .
  ?geo schema:latitude ?lat ;
       schema:longitude ?lon .
  ?park pe:hasFacility ?facility ;
        pe:parkName ?parkName .
  OPTIONAL { ?facility pe:facilityGisObjectId ?gis }
  OPTIONAL { ?park owl:sameAs ?parkWikidata }
}""",
    ("facility",),
)

ARTWORK_DETAIL = _query(
    "ARTWORK_DETAIL",
    "One artwork, its coordinates and its park.",
    """
SELECT ?name ?official ?gis ?lat ?lon ?park ?parkName ?parkWikidata WHERE {
  ?artwork a pe:Artwork ;
           pe:artworkName ?name ;
           schema:geo ?geo .
  ?geo schema:latitude ?lat ;
       schema:longitude ?lon .
  ?park pe:hasArtwork ?artwork ;
        pe:parkName ?parkName .
  OPTIONAL { ?artwork pe:officialName ?official }
  OPTIONAL { ?artwork pe:artworkGisObjectId ?gis }
  OPTIONAL { ?park owl:sameAs ?parkWikidata }
}""",
    ("artwork",),
)

ARTWORK_ARTISTS = _query(
    "ARTWORK_ARTISTS",
    "Artists of one artwork.",
    """
SELECT ?artist ?artistName ?wikidata WHERE {
  ?artwork pe:madeBy ?artist .
  ?artist pe:artistName ?artistName .
  OPTIONAL { ?artist owl:sameAs ?wikidata }
}
ORDER BY ?artistName""",
    ("artwork",),
)

ARTWORK_OWNERS = _query(
    "ARTWORK_OWNERS",
    "Owners of one artwork.",
    """
SELECT ?owner ?ownerName WHERE {
  ?artwork pe:owner ?owner .
  ?owner pe:ownerName ?ownerName .
}
ORDER BY ?ownerName""",
    ("artwork",),
)

ARTIST_DETAIL = _query(
    "ARTIST_DETAIL",
    "Name and Wikidata link of one artist.",
    """
SELECT ?name ?wikidata WHERE {
  ?artist a pe:Artist ;
          pe:artistName ?name .
  OPTIONAL { ?artist owl:sameAs ?wikidata }
}""",
    ("artist",),
)

ARTIST_WORKS = _query(
    "ARTIST_WORKS",
    "Artworks made by one artist and the parks that host them.",
    """
SELECT ?artwork ?name ?park ?parkName ?lat ?lon WHERE {
  ?artwork pe:madeBy ?artist ;
           pe:artworkName ?name ;
           schema:geo ?geo .
  ?geo schema:latitude ?lat ;
       schema:longitude ?lon .
  ?park pe:hasArtwork ?artwork ;
        pe:parkName ?parkName .
}
ORDER BY ?name""",
    ("artist",),
)

OWNER_DETAIL = _query(
    "OWNER_DETAIL",
    "Name of one artwork owner.",
    """
SELECT ?name WHERE {
  ?owner a pe:Owner ;
         pe:ownerName ?name .
}""",
    ("owner",),
)

OWNER_WORKS = _query(
    "OWNER_WORKS",
    "Artworks owned by one owner and the parks that host them.",
    """
SELECT ?artwork ?name ?park ?parkName ?lat ?lon WHERE {
  ?artwork pe:owner ?owner ;
           pe:artworkName ?name ;
           schema:geo ?geo .
  ?geo schema:latitude ?lat ;
       schema:longitude ?lon .
  ?park pe:hasArtwork ?artwork ;
        pe:parkName ?parkName .
}
ORDER BY ?name""",
    ("owner",),
)

RESOURCE_OUTGOING = _query(
    "RESOURCE_OUTGOING",
    "Every triple about a resource (the 'View RDF' panel and the Turtle export).",
    """
SELECT ?p ?o ?oLabel WHERE {
  ?s ?p ?o .
  OPTIONAL { ?o rdfs:label ?oLabel }
}
ORDER BY ?p ?o""",
    ("s",),
)

RESOURCE_INCOMING = _query(
    "RESOURCE_INCOMING",
    "Every triple that points to a resource.",
    """
SELECT ?s ?p ?sLabel WHERE {
  ?s ?p ?o .
  OPTIONAL { ?s rdfs:label ?sLabel }
}
ORDER BY ?p ?s""",
    ("o",),
)


# --- Sent to the public Wikidata endpoint (linked data enrichment) ----------

WIKIDATA_ENTITY = """
SELECT ?key ?value WHERE {
  VALUES ?item { wd:%(qid)s }
  { ?item rdfs:label ?value FILTER(LANG(?value) = "en") BIND("label" AS ?key) }
  UNION { ?item schema:description ?value FILTER(LANG(?value) = "en") BIND("description" AS ?key) }
  UNION { ?item wdt:P18 ?value BIND("image" AS ?key) }
  UNION { ?value schema:about ?item ; schema:isPartOf <https://en.wikipedia.org/> BIND("article" AS ?key) }
  UNION { ?item wdt:P569 ?value BIND("birth" AS ?key) }
  UNION { ?item wdt:P570 ?value BIND("death" AS ?key) }
  UNION { ?item wdt:P27/rdfs:label ?value FILTER(LANG(?value) = "en") BIND("citizenship" AS ?key) }
  UNION { ?item wdt:P106/rdfs:label ?value FILTER(LANG(?value) = "en") BIND("occupation" AS ?key) }
  UNION { ?item wdt:P571 ?value BIND("inception" AS ?key) }
  UNION { ?item wdt:P856 ?value BIND("website" AS ?key) }
  UNION { ?item wdt:P2046 ?value BIND("area" AS ?key) }
}
LIMIT 200
"""
QUERIES["WIKIDATA_ENTITY"] = (
    "Sent to https://query.wikidata.org/sparql for each park or artist that has an "
    "owl:sameAs link: label, description, image, Wikipedia article, life dates, "
    "nationality, occupation, inception, website and area. Each fact is a UNION branch so "
    "the answer grows with the number of facts, not with their product. "
    "%(qid)s is a validated Q-number.",
    ("qid",),
    WIKIDATA_ENTITY.strip(),
)
