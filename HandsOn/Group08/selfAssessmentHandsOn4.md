# Hands-on assignment 4 - Self assessment

## Checklist

**Deliverables:**

- [x] An RML file with the mappings for every dataset under `mappings/` (`xarxa-refugis-climatics.rml`, `fonts-beure-2026.rml`, `trees.rml`) and one for the neighbourhoods and districts (`areas.rml`)
- [x] An RDF file in the Turtle syntax for every dataset under `rdf/`
- [x] A SPARQL file with queries to verify the data (`rdf/queries.sparql`)
- [x] A Markdown document with the self-assessment in the root of the group directory

**Every RDF file:**

- [x] Uses the .ttl extension
- [x] Is serialized in the Turtle format
- [x] Follows the resource naming strategy
- [x] Uses class and property URIs that are the same as those used in the ontology

**Every URI in the RDF files:**

- [x] Is "readable" and has some meaning (e.g., it is not an auto-increased integer)
- [x] Is not encoded as a string
- [x] Does not contain a double slash (i.e., "//")

**Every individual in the RDF files:**

- [x] Has a label with the name of the individual
- [x] Has a type

**Every value in the RDF files:**

- [x] Is trimmed
- [x] Is properly encoded (e.g., dates, booleans)
- [x] Includes its datatype
- [x] Uses the correct datatype (e.g., values of 0-1 may be booleans and not integers, not every string made of numbers is a number)

## Comments on the self-assessment

**Generation**

- The RDF is generated from the `csv/*-updated.csv` files with Morph-KGC 2.10.0, run from the group directory: `mappings/config.ini` applies the four mappings and `mappings/config-trees.ini` only the one for the trees. Morph-KGC does not write Turtle, so its N-Triples output is converted to Turtle with `scripts/nt2ttl.py`.
- The mappings of the shelters, the fountains and the areas, and the `StreetTree` map of `trees.rml`, use `rml:query`, an SQL view that Morph-KGC executes with DuckDB. It is used to build the street address from the street and the number, to give a fallback label to the fountains without a name, to combine the two files that describe the areas and to clean values of the source (see below). These mappings can only be run with Morph-KGC. The `TreeSpecies` map of `trees.rml` is standard RML (`rml:source`).
- No YARRRML file (optional) is provided; the mappings are written directly in RML.

| File | Individuals | Triples |
|------|-------------|---------|
| `rdf/xarxa-refugis-climatics.ttl` | 561 (550 shelters, 11 categories) | 5,956 |
| `rdf/fonts-beure-2026.ttl` | 1,760 | 14,077 |
| `rdf/areas.ttl` | 83 (73 neighbourhoods, 10 districts) | 239 |
| `rdf/trees.ttl` | 145,322 (145,034 trees, 288 species) | 1,546,115 |
| Total | 147,726 | 1,566,387 |

**URIs, labels and values**

- All 147,726 individuals have a URI of the form `resource/{Class}/{identifier}` defined in the naming strategy (`analysis.html`, section 3), with the identifier expected for their class. The identifiers are the codes of the source (tree code `0000423AR`, fountain code `01-004`) or the name of the category; no counter is used. The register id of the shelters, the id of the species and the codes of neighbourhoods and districts are numeric. The readable name of every individual is its `rdfs:label`.
- Labels: shelters and fountains use the name of the source (language tag `ca`). 353 fountains have no name in the source (349 empty cells and 4 cells with the placeholder `-`) and are labelled `Font <code>`. Trees are labelled with the scientific name and the code, species with the scientific name, shelter categories with an English label, neighbourhoods and districts with the Catalan name.
- Coordinates are `xsd:decimal`. `hr:plantingDate` is `xsd:dateTime` with the time 00:00:00 because the source gives only the day (31,568 of the 145,034 trees have a date). `hr:website` is a typed value (`xsd:anyURI`), not a plain string. Plain strings have the datatype `xsd:string`, which is implicit in RDF 1.1 and is not repeated in the Turtle files. The shelters file has two boolean columns (`addresses_main_address`, `values_outstanding`), which are not mapped, so the RDF has no boolean values. `hr:telephone` is a string because it is an identifier and not a quantity; 22 of its 26 values are made only of digits.
- Empty cells generate no triple. The tree `0345745AR` has no neighbourhood in the source and has no `hr:isLocatedInNeighbourhood` link; the other 147,343 shelters, fountains and trees point to one of the 73 neighbourhoods.
- Cleaning done in the mappings: the placeholder street numbers `0` and `9999` are treated as missing, so the address keeps the street only (2 shelters, 2 fountains and 6,825 trees: 6,256 with `0` and 569 with `9999`). In the opening hours of the shelters, the hidden character U+FEFF (9 occurrences in 7 values) is removed and the control character U+0092 (2 values) is replaced by the apostrophe it stands for (U+2019).
- Columns of the trees that are not mapped: `tipus_element` (tree or palm) and `catalogacio` have no property in the ontology, `geom` repeats the ETRS89 coordinates as WKT, and the names of neighbourhoods and districts come from `areas.ttl`.
- The links to Wikidata described in the ontology (`owl:sameAs`, `skos:broadMatch`, `hr:isHostedBy`) are not generated in this assignment.

**Verification**

- `scripts/check_rdf.py` checks the criteria above on the four files: 0 subjects without type, 0 individuals without label, 0 classes or properties that are not in the ontology, 0 URIs with a double slash or whitespace, 0 values that are not trimmed or have hidden or control characters, 0 street addresses that end with the placeholder number `0` or `9999`, and 0 subjects or values outside the domain and range of their property. With `--compare rdf/graph.nt` it shows that the Turtle files contain exactly the 1,566,387 triples generated by `mappings/config.ini`. The only plain strings that look like numbers are 22 telephone numbers, which are kept as strings on purpose.
- `rdf/queries.sparql` has 14 queries, each with its expected result computed from the CSV files: individuals per class, labels, types, placeholder labels, links to neighbourhoods and districts, datatypes, and counts per district, category, species and neighbourhood. All of them return the expected result on the generated data (`scripts/run_queries.py`).
