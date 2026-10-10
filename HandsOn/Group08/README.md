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

Knowledge graph and web application that bring together the public resources available in Barcelona to cope with heat: the climate shelter network, public drinking fountains and street trees. Users can explore them on a map, browse them in a catalogue with filters (category, species, neighbourhood, district) and compare neighbourhoods. Neighbourhoods and tree species are linked to Wikidata.

## Repository contents

- `csv/` - CSV files of the selected datasets.
- `requirements/datasetRequirements.html` - analysis of the selected datasets against requirements R1-R6.
- `requirements/applicationRequirements.html` - requirements of the application, with user interface mock-ups.
- `selfAssessmentHandsOn1.md` - self-assessment of hands-on assignment 1.

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
- The data will be transformed into RDF in later assignments.
