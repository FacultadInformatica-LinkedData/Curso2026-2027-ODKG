# Group 08 - Barcelona Heat Relief

Hands-on project - Open Data and Knowledge Graphs 2026-2027 (UPM, ETSI Informaticos)

## Members

| Name | GitHub user |
|------|-------------|
| Bilal Soussane | sousbila |
| Livia Scoppola | LiviaScoppola |
| Arianna Balducci | ariannabalducci |
| Valentin Blin | ValYu777 |

## Project summary

Knowledge graph and web application that bring together the public resources available in Barcelona to cope with heat: the climate shelter network, public drinking fountains and street trees. Users can explore them on a map, browse them in a catalogue with filters (category, species, neighbourhood, district) and compare neighbourhoods. Neighbourhoods and tree species are to be linked to Wikidata (data linking assignment).

## Repository contents

- `csv/` - CSV files of the selected datasets: the original files and the cleaned files (`*-updated.csv`).
- `requirements/datasetRequirements.html` - analysis of the selected datasets against requirements R1-R6.
- `requirements/applicationRequirements.html` - requirements of the application, with user interface mock-ups.
- `analysis.html` - analysis of the data, licence and resource naming strategy.
- `ontology/` - ontology (`HeatRelief.ttl`) and sample instantiation (`HeatRelief-example.ttl`).
- `openrefine/` - JSON histories of the OpenRefine operations that produce the `*-updated.csv` files.
- `mappings/` - RML mappings and Morph-KGC configuration files.
- `rdf/` - RDF data in Turtle and the verification queries (`queries.sparql`).
- `scripts/` - helper scripts to convert, check and query the RDF.
- `selfAssessmentHandsOn1.md` to `selfAssessmentHandsOn4.md` - self-assessment of each hands-on assignment.

## Data sources and attribution

All datasets are published by the Ajuntament de Barcelona through Open Data BCN under the Creative Commons Attribution 4.0 International licence (https://creativecommons.org/licenses/by/4.0/).

| Dataset | File in `csv/` | Source |
|---------|----------------|--------|
| Climate shelters network | `xarxa-refugis-climatics.csv` | https://opendata-ajuntament.barcelona.cat/data/ca/dataset/xarxa-refugis-climatics |
| Drinking fountains (2026) | `fonts-beure-2026.csv` | https://opendata-ajuntament.barcelona.cat/data/en/dataset/fonts |
| Street trees | `arbrat-viari.csv` | https://opendata-ajuntament.barcelona.cat/data/en/dataset/arbrat-viari |

Changes made to the data:

- `xarxa-refugis-climatics.csv`: the original file is encoded in UTF-16; it was converted to UTF-8 without any other change.
- `fonts-beure-2026.csv` and `arbrat-viari.csv`: unchanged.
- `*-updated.csv`: cleaned with OpenRefine in hands-on 3 (operations in `openrefine/`). They are the input of the RDF mappings.

## Generating the RDF

The RDF is generated from the `*-updated.csv` files with RML mappings and Morph-KGC. The commands are run from this directory, with Python and `pip install morph-kgc`.

```
python -m morph_kgc mappings/config-trees.ini
python scripts/nt2ttl.py rdf/trees.nt rdf/trees.ttl
python scripts/check_rdf.py ontology/HeatRelief.ttl "rdf/*.ttl"
python scripts/run_queries.py rdf/queries.sparql "rdf/*.ttl"
```

- Morph-KGC does not write Turtle, so `scripts/nt2ttl.py` converts its N-Triples output to Turtle. Morph-KGC appends to its output file, so delete the `.nt` file before running it again. The `.nt` files are not kept in the repository.
- `mappings/config.ini` applies the four mappings (shelters, fountains, areas and trees) and writes the whole graph to `rdf/graph.nt`. To check that the Turtle files in `rdf/` contain exactly those triples, run:

```
python -m morph_kgc mappings/config.ini
python scripts/check_rdf.py ontology/HeatRelief.ttl "rdf/*.ttl" --compare rdf/graph.nt
```
