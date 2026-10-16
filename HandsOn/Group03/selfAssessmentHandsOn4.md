# Hands-on assignment 4 – Self assessment

## Checklist

**Every RDF file:**

- [x] Uses the .ttl extension
- [x] Is serialized in the Turtle format
- [x] Follows the resource naming strategy
- [x] Uses class and property URIs that are the same as those used in the ontology

**Every URI in the RDF files:**

- [x] Is "readable" and has some meaning (e.g., it is not an auto-increased integer)
- [x] Is not encoded as a string
- [x] Does not contain a double slash (i.e., “//”)

**Every individual in the RDF files:**

- [x] Has a label with the name of the individual
- [x] Has a type

**Every value in the RDF files:**

- [x] Is trimmed
- [x] Is properly encoded (e.g., dates, booleans)
- [x] Includes its datatype
- [x] Uses the correct datatype (e.g., values of 0-1 may be booleans and not integers, not every string made of numbers is a number)

## Comments on the self-assessment

The deliverables are [`madridnoise.rml`](mappings/madridnoise.rml) (**9 triples maps**), optional [`madridnoise.yml`](mappings/madridnoise.yml), [`madridnoise.ttl`](rdf/madridnoise.ttl) (**1,070,055 triples**) and [`queries.sparql`](rdf/queries.sparql) (**14 queries**).

Use the updated CSVs exported by the OpenRefine **3.10.0** histories and `csv/periods.csv`. Run from `Group03` with RMLMapper **7.3.3**:

```sh
java -jar rmlmapper.jar -m mappings/madridnoise.rml -s turtle -o rdf/madridnoise.ttl
```

The graph covers **78,230 observations (2025-01-01–2026-10-04)**, 31 stations and 6,594 terraces: **6,534 located and 60 without coordinates**. Three dataset resources have types and labels. The [ontology example](ontology/ontology-example.ttl) contains **63 triples over 13 resources**, all present in the generated graph.

Readable source keys determine IRIs. Resources have types and labels; dates, integers, decimals and booleans use their appropriate datatypes. Unavailable measurements are omitted. The percentile-order flag marks **213** inconsistent sequences while preserving the published measurements.

The Turtle, mappings and all fourteen queries were validated against the cleaned CSVs. The terrace data is a **4 October 2026 snapshot**; it cannot establish historical terrace activity for each noise date.
