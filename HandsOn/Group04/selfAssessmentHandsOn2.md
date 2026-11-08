# Hands-on assignment 2 – Self assessment
Group 04

## Checklist

**The "analysis.html" file:**

- [X] Includes the potential license of the dataset to be generated
- [X] Includes the resource naming strategy

**The resource naming strategy:**

- [X] Uses a domain that is not the one given by default in Protégé
- [X] Uses different paths for ontology resources (i.e., classes and properties) and individuals
- [X] Ensures that the paths for individuals of different classes are not the same
- [X] Defines individual URIs independently of class URIs

**The ontology file:**

- [X] Uses the .ttl extension
- [X] Is serialized in the Turtle format
- [X] Follows the resource naming strategy
- [X] Contains at least one class
- [X] Contains at least one object property (where the value of the property is a resource)
- [X] Contains at least one datatype property (where the value of the property is a string literal, usually typed)
- [X] Defines the domain of all the properties (the origin of the property)
- [X] Defines the range of all the properties (the destination of the property)
- [X] Defines all class names starting with a capital letter
- [X] Defines all property names starting with a non-capital letter
- [X] Does not mix labels in different languages (e.g., Spanish and English)
- [X] Does not define multiple domains or multiple ranges in properties
- [X] Contains at least one class that will be used to link to other entities

**The sample instantiation file:**

- [X] Uses the .ttl extension
- [X] Is serialized in the Turtle format
- [X] Follows the resource naming strategy
- [X] Does not include the definition of ontology terms

## Comments on the self-assessment

- Domain: `https://w3id.org/breatheplay-madrid/` (w3id.org persistent identifiers). Ontology terms use hash URIs under `/ontology#` (prefix `bpm:`), and individuals use slash URIs under `/resource/{type}/{id}`, with a different path for each type (`station/`, `sampling-point/`, `observation/`, `pollutant/`, `technique/`, `sports-facility/`, `facility-type/`, `accessibility-level/`, `district/`, `neighbourhood/`…).
- The ontology (`ontology/breatheplay.ttl`, version 1.1.0) has 12 classes, 8 object properties and 17 datatype properties of its own. Each of them has exactly one domain and one range. `bpm:MonitoringStation` and `bpm:SportsFacility` are subclasses of `bpm:Place`, which holds the shared location properties. All labels are in English.
- Standard vocabularies are reused where they cover the model (see *Reused vocabularies* in `analysis.html`): SOSA for the observations (`bpm:DailyObservation`, `bpm:SamplingPoint`, `bpm:MonitoringStation`, `bpm:Pollutant` and `bpm:MeasurementTechnique` are subclasses of `sosa:Observation`, `sosa:Sensor`, `sosa:Platform`, `sosa:ObservableProperty` and `sosa:Procedure`), WGS84 Geo Positioning for coordinates (`bpm:Place` ⊑ `geo:SpatialThing`) and schema.org for the facilities (`bpm:SportsFacility` ⊑ `schema:SportsActivityLocation`). Eight standard properties are used directly instead of our own (`sosa:madeBySensor`, `sosa:observedProperty`, `sosa:hasSimpleResult`, `sosa:isHostedBy`, `sosa:observes`, `geo:lat`, `geo:long`, `geo:alt`); their domains and ranges are those of their vocabularies, so the ontology only declares them (no `owl:imports`).
- `bpm:District`, `bpm:Neighbourhood` and `bpm:Pollutant` are the classes used to link to other entities (Wikidata, via `owl:sameAs`). `bpm:MonitoringStation` links the three datasets with each other (`sosa:isHostedBy`, `bpm:hasNearestStation`).
- `ontology/breatheplay-example.ttl` instantiates the 1st row of each CSV, plus the nearest station of the first facility and one observation flagged as not valid. Names of real places keep their official Spanish names (`@es`); code lists also have English labels.
- `ontology/breatheplay.drawio.xml` is the Chowlk conceptualization (diagrams.net), including the reused classes and properties and the subclass axioms towards them.
- Both Turtle files were validated with RDFLib.
- Generated dataset license: CC BY 4.0, the same as the source data (Ayuntamiento de Madrid).
