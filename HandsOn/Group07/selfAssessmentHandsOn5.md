# Hands-on assignment 5 – Self assessment

## Deliverables

**For each dataset:**

- [X] A JSON file containing the operations performed for data linking (`lodrefine/*-with-links.json`)
- [X] An updated CSV file (`csv/*-with-links.csv`)
- [X] An updated RML mapping file (`mappings/*-with-links.rml`)
- [X] An RDF file serialized in Turtle (`rdf/*-with-links.ttl`)
- [X] A SPARQL file containing queries to verify the links (`rdf/queries-with-links.sparql`)

## Checklist

**Every RDF file:**

- [X] Contains at least one `owl:sameAs` property

**Every `owl:sameAs` property:**

- [X] Links a resource in the dataset with another resource in an external dataset

**The SPARQL file:**

- [X] Includes at least 1 query
- [X] Contains queries that retrieve the data that would be needed in the application

**Every SPARQL query:**

- [X] Makes use of the ontology
- [X] Returns a non-empty result
- [X] Makes use of the `owl:sameAs` links

## Comments on the self-assessment

_(If required)_