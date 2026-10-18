# Hands-on assignment 4 – Self assessment

## Checklist

**The "mappings" directory:**

- [X] Contains an RML file with the mappings
- [X] Uses the cleaned CSV dataset from Hands-On 3
- [X] Follows the resource naming strategy defined in Hands-On 2
- [X] Reuses the classes and properties defined in the ontology
- [X] Defines relationships between traffic accidents and streets

**The "rdf" directory:**

- [X] Contains an RDF file serialized in Turtle format
- [X] Contains a SPARQL file with queries to verify the generated data
- [X] The generated RDF data have been successfully validated using SPARQL queries

## Comments on the self-assessment

- The cleaned New York City traffic accidents dataset was transformed into RDF using RML mappings and RMLMapper.
- The mappings reuse the ontology and resource naming strategy defined in Hands-On 2.
- Traffic accidents and streets are represented as RDF resources and linked through the `ao:locatedOn` property.