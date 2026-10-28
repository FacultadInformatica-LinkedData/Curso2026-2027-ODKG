# Hands-on assignment 4 – Self assessment

## Checklist

**Every RDF file:**

- [X] Uses the .ttl extension
- [X] Is serialized in the Turtle format
- [X] Follows the resource naming strategy
- [X] Uses class and property URIs that are the same as those used in the ontology

**Every URI in the RDF files:**

- [X] Is "readable" and has some meaning (e.g., it is not an auto-increased integer)
- [X] Is not encoded as a string
- [X] Does not contain a double slash (i.e., "//")

**Every individual in the RDF files:**

- [X] Has a label with the name of the individual
- [X] Has a type

**Every value in the RDF files:**

- [X] Is trimmed
- [X] Is properly encoded (e.g., dates, booleans)
- [X] Includes its datatype
- [X] Uses the correct datatype (e.g., values of 0-1 may be booleans and not integers, not every string made of numbers is a number)

## Comments on the self-assessment
The RML mappings in `mappings/` (`mapping-sports-centers.rml`, `mapping-open-classes.rml` and `mapping-closed-classes.rml`, with their equivalent YARRRML rules in `.yml` files) were executed with Morph-KGC. Each mapping produces one Turtle file in `rdf/` (`sports-centers.ttl`, `open-classes.ttl` and `closed-classes.ttl`).

- **Generated data:** The three files contain **1,101,209 triples**, modelling 137,692 sports classes (56,012 open and 81,680 closed), 82 sports facilities with their 82 postal addresses, 64 neighborhoods, 21 districts, 379 sports activities and 606 time intervals.
- **Links between datasets:** Classes are linked to their sports facility through `am:takesPlaceAt`, by joining the class's `Centro deportivo` column with the facility's `NOMBRE` column. This produces **126,137 `am:takesPlaceAt` assertions**, all pointing to existing facilities. Both open and closed classes are linked to their schedule through `time:hasTime`.
- **URIs and types:** All URIs follow the resource naming strategy (`https://w3id.org/active-madrid/resource/...`). There are no URIs with duplicate slashes, no untyped individuals and no untrimmed literals.
- **Datatypes:** Capacity values (`am:offeredPlaces`, `am:occupiedPlaces`, `am:availablePlaces`) are typed as `xsd:nonNegativeInteger`, coordinates (`geo:lat`, `geo:long`) as `xsd:decimal`, URLs as `xsd:anyURI`, and interval bounds (`time:hasBeginning`, `time:hasEnd`) as `xsd:time`. No literal is ill-typed.
- **SPARQL verification:** `rdf/queries.sparql` contains 13 queries that were executed over the three RDF files loaded together. All of them are syntactically valid and return the expected results.