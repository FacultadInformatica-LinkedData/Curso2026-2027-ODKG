# Hands-on assignment 5 – Self assessment

## Checklist

**Data linking:**

- [X] The entities that can be linked with external datasets have been identified
- [X] Wikidata has been selected as the external dataset for reconciliation
- [X] Data reconciliation has been performed using OpenRefine
- [X] External Wikidata URIs have been incorporated into the dataset

**The "lodrefine" directory:**

- [X] Contains a JSON file with the operations performed in OpenRefine for data linking

**The "csv" directory:**

- [X] Contains the updated CSV dataset with Wikidata links
- [X] The original and previously cleaned CSV datasets have been preserved

**The "mappings" directory:**

- [X] Contains an updated RML file incorporating external links
- [X] Reuses the ontology and resource naming strategy defined in previous assignments
- [X] Represents streets, cities, states and countries as RDF resources
- [X] Uses `owl:sameAs` to link RDF resources to their corresponding Wikidata entities

**The "rdf" directory:**

- [X] Contains the updated RDF dataset serialized in Turtle format
- [X] Contains a SPARQL file with queries to verify the generated links
- [X] The generated RDF data have been successfully validated using SPARQL queries

## Comments on the self-assessment

- The New York City traffic accidents dataset was reconciled with Wikidata using OpenRefine, linking streets, New York City, New York State and the United States to external entities.
- The RML mappings were extended to incorporate `owl:sameAs` links and represent geographical resources using Schema.org.
- The resulting RDF graph contains 21,699 traffic accidents and 218,041 RDF triples, including 60 distinct streets linked to Wikidata.
- SPARQL queries confirmed the geographical links, the relationships between accidents and streets, and the preservation of the original accident records.
