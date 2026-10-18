# Self-assessment Hands-On 3 (OpenRefine) - Group08

## Checklist

- [x] Data imported into OpenRefine (D1, D2, D3)
- [x] Data analysed and errors from the previous hands-on fixed
- [x] Data transformed to facilitate RDF generation
- [x] JSON operation history for every dataset under `openrefine/`
- [x] Updated CSV for every dataset under `csv/` (`*-updated.csv`)
- [x] JSON histories reproduce the CSVs (single-cell edits replaced by GREL transforms)
- [x] Self-assessment file in the root of the group directory

## Comments

**D1 - Climate shelters (`xarxa-refugis-climatics`, 550 rows)**
- Trimmed whitespace and collapsed double spaces; converted numbers. `created`/`modified` keep the source's local time as `YYYY-MM-DDTHH:MM:SS` (no UTC shift).
- Fixed name typos via clustering.
- `register_id` contains digits only and is unique.
- HTML timetable converted to plain text; HTML tags stripped from `values_value`.
- Abbreviated street names (C, Av, Pl, Pg) expanded to the full official form.
- Category derived from the name and mapped to English (Library, SwimmingPool, SportsCentre, Park, School, Museum, HealthCentre, Market, CivicCentre, WaterPlayArea, Other).
- Canonical district names.
- Extracted `email`, `website` and `telephone` columns; non-URL notes removed from `website`.

**D2 - Drinking fountains (`fonts-beure-2026`, 1760 rows)**
- Whitespace trimmed in every column; `LATITUD` and `LONGITUD` converted to numbers.
- Filled the missing neighbourhood (code and name) of 10 fountains with rules on the fountain code (see the JSON).
- Corrected the district code of 5 fountains so that it matches their neighbourhood code (neighbourhoods 18, 19, 29 and 37 belong to districts 03, 04, 06 and 07).
- District names set from the district code (canonical form).
- `CARRER` normalised to ALL CAPS with undotted prefixes (C, AV, PL, PG, ...); typos fixed; `NOM` case variants unified; `SN` placeholders in `NUMERO_CARRER` blanked.

**D3 - Street trees (`arbrat_viari`, 145,034 rows)**
- Whitespace trimmed in every column; the placeholder `SENSE INFORMAR` in `tipus_reg` blanked.
- Columns holding several values split into numbered columns: `tipus_aigua` (separator `/`), `cat_nom_castella` and `cat_nom_catala` (separator `;`).
- `data_plantacio` values before 1950 blanked.
- The two ids of Ulmus minor 'Umbraculifera' (589 and 2764) unified as 589; the hybrid sign in scientific names normalised to `×`.
- District and neighbourhood names aligned with the official codes, so they match D1 and D2.
- `-` placeholders blanked in the four common-name columns; repeated spaces collapsed and a few case and spelling variants unified in `espai_verd` and `cat_nom_catala 1`.
- Missing neighbourhood (7 trees) and district (3 trees) filled from the nearest tree by coordinates (7 to 18 m away); one tree (`0345745AR`, no street) remains without area.
- The JSON history was validated by re-applying it to the original CSV.

**Reproducibility:** all manual single-cell edits were replaced by GREL transforms, so applying each `openrefine/*.json` to the original data reproduces the corresponding `csv/*-updated.csv`.
