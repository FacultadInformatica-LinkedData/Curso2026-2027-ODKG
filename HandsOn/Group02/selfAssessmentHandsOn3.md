# Hands-on assignment 3 – Self assessment

## Checklist

**Every resource described in the CSV file:**

- [X] Has a unique identifier in a column (not an auto-increased integer)
- [X] Is related to a class in the ontology

**Every class in the ontology:**

- [X] Is related to a resource described in the CSV file

**Every column in the CSV file:**

- [X] Is trimmed
- [X] Is properly encoded (e.g., dates, booleans)
- [X] Is related to a property in the ontology

**Every property in the ontology:**

- [X] Is related to a column in the CSV file

## Comments on the self-assessment
**Resources**
- Parks are identified by `PARK_NO`, the official Chicago Park District park number shared by both datasets. Artists and owners have slugs derived from their names (`ARTIST_ID`, `OWNER_ID`).
- Facilities and artworks use `FACILITY_ID` / `ARTWORK_ID`, the publisher's own record identifiers (`OBJECTID` in the source), not numbers we generated.

**Classes**
- Our five classes and `schema:GeoCoordinates` have direct instances. `schema:Place`, `schema:Park`, `schema:Person` and `schema:Organization` are included for alignment with schema.org: the first two are superclasses of our classes, and the last two define artists and owners as persons or organizations.
