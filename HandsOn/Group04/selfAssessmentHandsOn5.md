# Hands-on assignment 5 – Self assessment
Group 04
## Checklist

**Every RDF file:**

- [x] Has at least one owl:sameAs property that links to another dataset

## Comments on the self-assessment

All links point to Wikidata. They were created with OpenRefine reconciliation
(`lodrefine/*-with-links.json`), stored as new columns in `csv/*-with-links.csv`
and turned into `owl:sameAs` triples by the mappings `mappings/*-with-links.rml`
(run with `python mappings/generate_rdf-with-links.py`).

| RDF file | Linked resources | owl:sameAs |
|---|---|---|
| `rdf/calidad-aire-diario-2024-with-links.ttl` | 11 pollutants (e.g. NO2 → wd:Q207895, O3 → wd:Q36933) | 11 |
| `rdf/estaciones-control-aire-with-links.ttl` | 16 districts and 5 neighbourhoods of the stations | 21 |
| `rdf/instalaciones-deportivas-with-links.ttl` | 21 districts and 111 neighbourhoods | 132 |

- **Stations dataset.** The monitoring stations themselves are not in Wikidata
  (reconciling their names only returns metro stations with the same name, which
  are different entities, so they are not `owl:sameAs`). Instead, we added the
  district and neighbourhood of each station, taken from the station pages of 
  the Portal web of the Madrid City Council (Ayuntamiento de Madrid), and linked them to Wikidata.
  The stations now have `bpm:locatedInDistrict` (24 stations) and `bpm:locatedInNeighbourhood` (5
  stations; the official pages only give the neighbourhood for these). The
  districts and neighbourhoods use the same IRIs as in the sports facilities
  dataset, so both datasets share them.
- **Plaza de España (28079004).** The official page gives "Sol / MONCLOA-ARAVACA",
  but Sol belongs to the Centro district, so we only kept the district
  (Moncloa-Aravaca).
- **San Andrés and Ambroz.** In the sports facilities dataset, six rows have a
  neighbourhood without a code: three "SAN ANDRES" (the old name of Villaverde Alto, Casco Histórico de Villaverde,
  code 171, wd:Q390435) and three with “AMBROZ” (wd:Q11905294). The row keeps the Wikidata link in the CSV, 
  but no neighbourhood resource is generated for it because it has no code (same as in Hands-on 4).
- **Pollutants.** Some pollutants were matched manually because the automatic
  match was not right: PM2.5 → wd:Q48035814, PM10 → wd:Q1056863 and
  NOx → wd:Q424418.
- **Queries.** `rdf/queries-with-links.sparql` keeps the Hands-on 4 queries
  (Q12 now uses the district of the stations, Q14 returns the Wikidata entity of
  the pollutant) and adds Q15-Q17, which use the `owl:sameAs` links. All of them
  return results except the control queries Q2-Q4, which must return 0 rows.
