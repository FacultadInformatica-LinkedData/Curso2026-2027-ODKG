# Hands-on assignment 2 – Self assessment

## Checklist

**The “analysis.html” file:**

- [x] Includes the potential license of the dataset to be generated
- [x] Includes the resource naming strategy

**The resource naming strategy:**

- [x] Uses a domain that is not the one given by default in Protégé
- [x] Uses different paths for ontology resources (i.e., classes and properties) and individuals
- [x] Ensures that the paths for individuals of different classes are not the same
- [x] Defines individual URIs independently of class URIs

**The ontology file:**

- [x] Uses the .ttl extension
- [x] Is serialized in the Turtle format
- [x] Follows the resource naming strategy
- [x] Contains at least one class
- [x] Contains at least one object property (where the value of the property is a resource)
- [x] Contains at least one datatype property (where the value of the property is a string literal, usually typed)
- [x] Defines the domain of all the properties (the origin of the property)
- [x] Defines the range of all the properties (the destination of the property)
- [x] Defines all class names starting with a capital letter
- [x] Defines all property names starting with a non-capital letter
- [x] Does not mix labels in different languages (e.g., Spanish and English)
- [x] Does not define multiple domains or multiple ranges in properties
- [x] Contains at least one class that will be used to link to other entities

**The sample instantiation file:**

- [x] Uses the .ttl extension
- [x] Is serialized in the Turtle format
- [x] Follows the resource naming strategy
- [x] Does not include the definition of ontology terms

## Comments on the self-assessment

- The ontology was conceptualised as a diagram in the Chowlk notation (`ontology/HeatRelief-diagram.xml`), which Chowlk converts with no errors, and developed by adding English labels and comments. The OWL API profile checker reports OWL 2 DL, for the ontology alone and together with the example. HermiT finds the ontology consistent, both alone and with the example. OOPS! reports a single pitfall, P13 (inverse relationships not explicitly declared, 5 cases, minor), which we accept because the application does not need inverse properties.
- `hr:plantingDate` uses `xsd:dateTime` with the time 00:00:00, because `xsd:date` is not in the OWL 2 datatype map and HermiT rejects it.
- `geo:lat` and `geo:long` are reused from the W3C Basic Geo vocabulary with their own domain, `geo:SpatialThing`, which is the superclass of `hr:UrbanElement`.
- Links to other entities: neighbourhoods, districts and species-level taxa use `owl:sameAs` towards Wikidata; cultivars, varieties and forms use `skos:broadMatch`; shelters use `hr:isHostedBy` towards the Wikidata item of the place that hosts them (`hr:Facility`).
- The example (`ontology/HeatRelief-example.ttl`) contains 24 real individuals from the three datasets and uses every property of the ontology. It imports the ontology; until the w3id IRI is registered, `ontology/catalog-v001.xml` lets Protégé load the import from the local file.
- Known limitation: the 14 records that have a district but no neighbourhood get no area link (analysis, section 1.4).
