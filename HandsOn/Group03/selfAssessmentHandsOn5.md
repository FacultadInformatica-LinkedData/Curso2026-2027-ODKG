# Hands-on assignment 5 – Self assessment

## Checklist

**Every RDF file:**

- [X] Has at least one owl:sameAs property that links to another dataset

## Comments on the self-assessment

The three `*-with-links.ttl` exports contain 17, 17, and 150 external identity
links respectively. Their union has 1,070,386 triples and 150 distinct Wikidata
links covering all 21 districts and 129 neighbourhoods represented in the data.

All OpenRefine histories and RML mappings were executed. Validation confirmed
source preservation, RDF values and datatypes, missing-value omissions, and
identity links. All five application queries use the ontology and `owl:sameAs`
and return results. Reproduction commands are in [README.md](README.md).
