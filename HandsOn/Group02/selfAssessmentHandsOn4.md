# Hands-on assignment 4 – Self assessment

## Checklist

**Every RDF file:**

- [X] Uses the .nt extension
- [X] Is serialized in the NTriples format
- [X] Follows the resource naming strategy
- [X] Uses class and property URIs that are the same as those used in the ontology

**Every URI in the RDF files:**

- [X] Is "readable" and has some meaning (e.g., it is not an auto-increased integer) 
- [X] Is not encoded as a string
- [X] Does not contain a double slash (i.e., “//”)

**Every individual in the RDF files:**

- [X] Has a label with the name of the individual
- [X] Has a type

**Every value in the RDF files:**

- [X] Is trimmed
- [X] Is properly encoded (e.g., dates, booleans)
- [X] Includes its datatype
- [X] Uses the correct datatype (e.g., values of 0-1 may be booleans and not integers, not every string made of numbers is a number)

## Comments on the self-assessment
Artists and owners have name slugs (`Artist/Phil_Schuster`), and parks use the official park number (`ChicagoPark/165`). Facilities and artworks use the publisher's record identifiers, so every URI leads back to its record in the City of Chicago data. Coordinate URIs say which facility or artwork they belong to (`GeoCoordinates/Facility_1`).