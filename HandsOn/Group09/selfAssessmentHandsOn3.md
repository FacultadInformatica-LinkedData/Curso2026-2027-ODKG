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
- [ ] Is related to a property in the ontology

**Every property in the ontology:**

- [X] Is related to a column in the CSV file

## Comments on the self-assessment
We cleaned two datasets with OpenRefine: historical monthly car park occupancy (4,754 rows) and the car park inventory (301 rows). We normalized column names, removed unnecessary whitespace, standardized parking types and district/neighbourhood names, and converted relevant numerical fields. We also checked identifiers and duplicates. Invalid negative occupancy percentages and average daily vehicle counts were replaced with blank values.

The ontology provides classes for parking facilities, districts, neighbourhoods and monthly occupancy observations, with properties linked to fields in the datasets. However, not every source column is currently represented by an ontology property (for example, some auxiliary identifiers, URLs and dissuasive-parking fields), and the CSVs still contain textual YES/NO-style values rather than typed booleans. Therefore, we have left the corresponding all-columns checklist items unchecked pending further transformations or mapping decisions.
