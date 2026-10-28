# SHACL validation with Astrea

## Files

| File | Purpose |
| --- | --- |
| `shapes.ttl` | Required deliverable: the complete, standalone shapes graph. |
| `report.ttl` | Required deliverable: the final RDF validation report. |
| `shapes_ideas.md` | Our selected validation ideas. |
| `report-before.ttl` | Evidence of the twelve issues detected before correction. |
| `postal-code-corrections.csv` | The twelve corrections, with station identifiers and official source URLs. |
| `README.md` | Explanation of the method, constraints and results. |

The final report validates **`../rdf/knowledge-graph-with-links.ttl`**.
The corrections are persisted in `../csv/DBtrainrides-with-links.csv`, and the
main linked graph has been regenerated from that corrected source.

## Astrea generation

Astrea takes `../ontology/db-delays.ttl` as input. The course illustrates this
workflow in printed slide 83 (PDF page 76) and lists pySHACL among validators in
printed slide 84 (PDF page 77).

The public Astrea website was unavailable during generation, so the official
Astrea 1.2.1 library was executed locally with its released mapping catalogue.
The run loaded 80 mapping queries, read 121 ontology triples, and produced 181
shape triples: four node shapes and twenty property shapes.

The official downloads were:

- [Astrea web distribution containing the library and dependencies](https://github.com/oeg-upm/astrea-web/blob/master/Dockerfile/astrea-service-2.2.1.jar).
- [Astrea 1.2.1 release containing the mapping catalogue, Astrea-KG.zip](https://github.com/oeg-upm/astrea/releases/tag/%231.2.1).

The library was called through `OwlGenerator(File)` and `fromModel`, using the
installed JetBrains Runtime 25.0.4. Generation took place on 23 October 2026.
The bundled library's SHA-256 was
`a1151c3c39619e9d296a75b5188bd2131b5644a0188f86ddf19cf9af6a1f28aa`.

`shapes.ttl` contains three labelled sections:

1. The unmodified Astrea output. This section preserves the generated material
   directly, making a separate copy unnecessary.
2. Forty explicit structural repairs: the released generator/catalogue omitted
   twenty `sh:path` declarations and twenty `sh:property` associations. They were
   recovered from the original ontology's property labels and domains.
3. The selected dataset-specific constraints added manually.

Datatype checks and object ranges come from the ontology through Astrea.
The additional requirements below are manual additions, not automatically
inferred from English ontology comments. All constraints use SHACL Core.

## Selected constraints

| Idea | Implementation |
| --- | --- |
| Datatypes | Dates use `xsd:dateTime`; delays and categories use integers; coordinates use decimals; identifiers and postal codes use strings. |
| Planned arrival before departure | `plannedArrival <= plannedDeparture` when both timestamps exist. |
| Updated arrival before departure | `updatedArrival <= updatedDeparture` when both timestamps exist. |
| One label per resource | Exactly one non-blank string label for each train stop, station, city and state. Different resources may share a label. |
| Coordinates | Longitude is within [-180, 180]; latitude within [-90, 90]. |
| Postal code | Each present value is a string matching `^[0-9]{5}$`. |
| Missing arrival implies missing path | If `plannedArrival` is absent, `previousStations` must also be absent. This is a warning. |

`sh:targetClass` selects resources to check, and `sh:path` selects a property.
`sh:datatype` checks literal types. `sh:minCount 1` and `sh:maxCount 1` together
require exactly one value. `sh:pattern` checks text formats, while numerical
bounds check coordinates.

For time ordering, `sh:lessThanOrEquals` permits equal timestamps because the
source records time at minute precision. Missing timestamps are allowed; no pair
is compared when either side is absent.

The arrival/path implication is expressed as: arrival is present **OR** path is
absent. It uses `sh:or` and cardinalities. It is a warning because a missing
arrival does not prove that an observation is the first station. In this sample,
932 records have both fields and 68 have neither, so this rule finds no warnings.

No global label uniqueness, source-ID uniqueness or delay/status consistency
constraint is imposed. Status properties retain only their ontology-derived
datatype checks. The shapes remain open to additional properties.

## Validation and correction

Validation used pySHACL 0.40.1 with inference disabled and meta-SHACL enabled
to check the well-formedness of the shapes graph.

| Data graph | Conforms | Violations | Warnings |
| --- | --- | --- | --- |
| Linked graph before correcting the source CSV | false | 12 | 0 |
| Regenerated `knowledge-graph-with-links.ttl` after correcting the CSV | true | 0 | 0 |

The twelve findings were four-digit station postal codes. Each replacement was
checked against the individual official DB station page recorded in
`postal-code-corrections.csv`. For example, Altenburg's `"4600"` was corrected to
`"04600"`, matching [DB's station address](https://www.bahnhof.de/altenburg).
The sources are current station pages, not archived proof of the 2024 addresses.

The twelve station-specific corrections were also applied to all matching rows
of `DBtrainrides-with-links.csv`: 23 `zip` cells changed across 12 stations. Other
columns, row order and the 1,000-row count were preserved. The source correction
is repeatable: a second run makes no changes. The main TTL was then regenerated
with Morph-KGC from this CSV and validated; it contains 16,527 triples.
`report-before.ttl` preserves the initial findings, while `report.ttl` records
`sh:conforms true` for the corrected graph. In a failing report, `sh:focusNode`
identifies the resource, `sh:resultPath` the property, and `sh:value` the offending
value.

## Revalidate

From the repository root, the source-to-report workflow is:

```powershell
python HandsOn/Group07/transformation/validate_shacl.py --fix-source-csv
python HandsOn/Group07/transformation/generate_graph.py --with-links
python HandsOn/Group07/transformation/validate_shacl.py
```

The first command applies only the reviewed station-specific old/new matches
from `postal-code-corrections.csv` to the linked CSV. Leading zeros remain part
of the string value. Already correct values are left alone; an unexpected value
requires investigation. It does not automatically pad arbitrary postal codes.
The second command regenerates the main linked TTL, and the third validates it
and writes `report.ttl`. `report-before.ttl` remains the historical report of the
twelve initial violations; it is not overwritten when validating the clean source.

To regenerate the shapes with an actual Astrea run and validate the main TTL:

```powershell
python HandsOn/Group07/transformation/validate_shacl.py --regenerate-shapes --java "C:/Program Files/JetBrains/PyCharm 2026.2.3/jbr/bin/java.exe"
```

Adjust `--java` to the installed Java executable, or omit it if `java` is on PATH.
This command uses the official library/dependencies in
`tmp/astrea/extracted/BOOT-INF/lib/` and the released catalogue in
`tmp/astrea/catalog/dataset.ttl`. The script creates its temporary Java launcher,
runs Astrea again on the current ontology, checks the assembled shapes with
meta-SHACL, and replaces `shapes.ttl`. It then validates the main linked TTL and
regenerates `report.ttl`. Astrea's raw output and execution log
stay under `tmp/astrea/`, outside the deliverables directory.

The correction CSV retains the reviewed values and source evidence. Newly
discovered validation problems require their own review before a replacement
is added. Use `--data` to specify a different input TTL.

If the ontology or requirements change, review or regenerate the shapes as well.
Updating only the instance data does not by itself require another Astrea run.

From the repository root, with pySHACL installed:

```powershell
python -m pip install pyshacl==0.40.1
python -m pyshacl -s HandsOn/Group07/shacl/shapes.ttl -m -i none -f turtle -o HandsOn/Group07/shacl/report.ttl HandsOn/Group07/rdf/knowledge-graph-with-links.ttl
```

No second corrected TTL is needed: the main linked CSV and its generated TTL now
contain the corrected values. The unlinked source `DBtrainrides.csv` and the
unlinked `knowledge-graph.ttl` are outside this correction workflow.

The assignment deliverables are `shapes.ttl` and `report.ttl`. A passing report
establishes conformance to these explicit rules, not factual correctness of every
value or identity link.
