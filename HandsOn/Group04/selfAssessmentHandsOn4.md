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

**Deliverables (one per dataset):**

| Dataset | Mapping | RDF | Triples |
|---|---|---|---|
| D1 `calidad-aire-diario-2024-csv-updated.csv` | `mappings/calidad-aire-diario-2024.rml` | `rdf/calidad-aire-diario-2024.ttl` | 258,734 |
| D2 `212629-0-estaciones-control-aire-csv-updated.csv` | `mappings/estaciones-control-aire.rml` | `rdf/estaciones-control-aire.ttl` | 222 |
| D3 `200215-0-instalaciones-deportivas-csv-csv-updated.csv` | `mappings/instalaciones-deportivas.rml` | `rdf/instalaciones-deportivas.ttl` | 10,304 |

The RDF was generated with Morph-KGC 2.10 and serialized as Turtle with rdflib (Morph-KGC only writes N-Triples/N-Quads). To regenerate it, run `python mappings/generate_rdf.py` from the `Group04` directory. Verification queries are in `rdf/queries.sparql`: Q1–Q4 check the RDF, Q5–Q8 explore the data across the 3 datasets, and Q9–Q14 answer the competency questions of the application defined in Hands-on 1 (`requirements/applicationRequirements.html`).

**How the checklist was verified** (on the merged graph of the three files, 269,164 triples):

- All 12 classes and 32 properties of `ontology/breatheplay.ttl` are used, and no class or property outside the ontology is used (`bpm:Place` is used through its subclasses `bpm:MonitoringStation` and `bpm:SportsFacility`).
- Individuals: 42,973 daily observations, 131 sampling points, 11 pollutants, 6 measurement techniques, 24 monitoring stations, 3 station types, 607 sports facilities, 24 facility types, 4 accessibility levels, 21 districts and 111 neighbourhoods. All of them have `rdf:type` and `rdfs:label` (query Q2 returns no results).
- URIs follow the naming strategy of `analysis.html` and `ontology/breatheplay-example.ttl` (`https://w3id.org/breatheplay-madrid/resource/{class-path}/{code}`). Observations are named `observation/{samplingPoint}/{date}`, which identifies them uniquely (one value per sampling point and day). No URI contains "//".
- Links between datasets use `rr:parentTriplesMap` with an `rr:joinCondition`: sampling points (D1, `ESTACION_CODIGO`) and sports facilities (D3, `ESTACION_CERCANA`) are joined with the stations of D2 (`CODIGO`). The stations triples map is repeated in the D1 and D3 mappings with the same URI template and label, so the resources merge with those generated from D2. Within each dataset, links to code lists (pollutants, techniques, station types, facility types, accessibility levels, districts and neighbourhoods) use the same URI template as the subject map of the target class. Query Q3 checks that every object property points to an existing individual (no results).
- Datatypes follow the ranges of the ontology: `xsd:date` (dates), `xsd:decimal` (values, coordinates, distances), `xsd:integer` (altitude), `xsd:boolean` (validity), `xsd:anyURI` (content URL) and `xsd:string`. Codes made of digits (station, district, neighbourhood, pollutant, technique, postal code, facility id) are kept as `xsd:string`. Query Q4 checks the datatypes (no results).
- Labels are taken from the data and tagged `@es`; observation and sampling point labels are built with a template (e.g., "Observación diaria de Monóxido de carbono en el punto de muestreo 28079004_6_48 el 2024-01-01"@es).

**Known limitations:**

- Empty cells produce no triples: 8 sports facilities have no neighbourhood code, 2 have no postal code, 6 have no address and 3 have no transport information. All facilities have a district.
- Monitoring stations have no district in D2, so `bpm:locatedInDistrict` is only used for sports facilities.
- Two PM2.5 observations have negative values (-1 and -0); both are flagged as not valid (`bpm:isValid false`) and are kept as published.
- District and neighbourhood labels are kept in upper case, as published in D3.
