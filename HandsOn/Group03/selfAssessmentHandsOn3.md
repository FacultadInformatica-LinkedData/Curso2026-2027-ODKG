# Hands-on assignment 3 – Self assessment

## Checklist

**Every resource described in the CSV file:**

- [x] Has a unique identifier in a column (not an auto-increased integer)
- [x] Is related to a class in the ontology

**Every class in the ontology:**

- [x] Is related to a resource described in the CSV file

**Every column in the CSV file:**

- [x] Is trimmed
- [x] Is properly encoded (e.g., dates, booleans)
- [x] Is related to a property in the ontology

**Every property in the ontology:**

- [x] Is related to a column in the CSV file

## Comments on the self-assessment

The histories in `openrefine/` produce the matching `csv/*-updated.csv` files:

| Dataset | Operations | Output rows |
|---|---:|---:|
| Noise | 24 | 78,230 |
| Stations | 9 | 31 |
| Terraces | 15 | 6,594 |

Reproduce with OpenRefine **3.10.0**: import the original CSVs with semicolon separator, one header row, disabled type guessing and blank cells as nulls. Use ISO-8859-1 for noise/stations and UTF-8 for terraces. Apply the matching JSON history and export comma-separated UTF-8 CSV. Complete replays reproduce the delivered files.

The chosen noise window is **2025-01-01–2026-10-04**. Cleaning normalizes identifiers, dates, whitespace and decimal notation; `N/D` becomes blank. Source measurements, including zeros, remain unchanged. The derived `percentile_order_violation` flags **213** inconsistent sequences, with 78,000 false and 17 unavailable values.

Terraces use local coordinates for street-access premises outside Baja, grouping coordinates for grouped premises, and no coordinates for other invalid or missing pairs. Conversion from EPSG:25830 to WGS84 yields **6,534 located terraces and 60 without coordinates**.

Source identifiers and composite observation keys cover the six application classes and eighteen properties. Period labels are supplied by `csv/periods.csv`.
