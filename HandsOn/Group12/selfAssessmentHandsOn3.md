# Hands-on assignment 3 – Self assessment

## Checklist

**The cleaned CSV files:**
- [X] Are in `.csv` format and UTF-8 encoded
- [X] Use the ISO 8601 standard for dates (`yyyy-MM-dd`)
- [X] Use the standard format for times (`HH:mm:ss`)
- [X] Do not contain leading or trailing whitespace in text cells
- [X] Use the correct numerical format for numbers
- [X] Do not contain empty columns
- [X] Use a standardized format for telephone numbers
- [X] Have all HTML entities decoded
- [X] Standardize text casing to Titlecase for consistency

**The OpenRefine history files:**
- [X] Are exported in JSON format
- [X] Allow reproducing the exact cleaning on the original CSV files

## Comments on the self-assessment

**Deliverables.** One operation history file in JSON format per dataset with the OpenRefine operations (under `openrefine/`) and its updated CSV file (under `csv/`):

| Dataset | Operations file | Updated CSV file |
|---|---|---|
| Open classes | `openrefine/open_classes_operations.json` | `csv/open_classes-updated.csv` |
| Closed classes | `openrefine/closed_classes_operations.json` | `csv/closed_classes-updated.csv` |
| Sports centers | `openrefine/sports_centers_operations.json` | `csv/sports_centers_info-updated.csv` |

**Main cleaning and transformation steps:**

**1. Open classes dataset (`open_classes`)**
* **Dataset filtering / Size reduction:** Row removal operation via facet filtering on the `Mes` column, retaining only month 11 (November 2025) to optimize dataset volume and execution performance for downstream RDF generation.
* **Dates:** Conversion of the `Fecha` column to the ISO 8601 format `yyyy-MM-dd`.
* **Times:** Normalization of the `Hora inicial` and `Hora final` columns to the `HH:mm:ss` format required by `xsd:time`, using the expression `with(value.trim(), v, if(v.length() == 4, "0" + v, v) + ":00")` (e.g., `9:00` → `09:00:00`). This also makes the same schedule produce identical values in the open and closed classes datasets.
* **Sports center names:** Normalization of the `Centro deportivo` column to the full facility name used in the sports centers dataset (e.g., `Alfredo Goyeneche` → `Centro Deportivo Municipal Alfredo Goyeneche`), so that classes can be linked to their facility when generating RDF.
* **Whitespace:** `trim` operation on the `Actividad`, `Centro deportivo`, `Día de la semana` and `Tipo de actividad` columns to remove leading and trailing spaces.

**2. Closed classes dataset (`closed_classes`)**
* **Schedule extraction:** Extraction of class schedule hours embedded within the text of the `Clase` column using regular expressions (`grel:value.match(...)`) to generate two new dedicated columns, `Hora inicial` and `Hora final`, in `HH:mm:ss` format.
* **Column renaming and homogenization:** Renaming capacity columns (`Nº Plazas Ofertadas` to `Plazas`, `Nº Plazas Ocupadas` to `Ocupadas`, and `Nº Plazas Libres` to `Libres`) to homogenize attribute nomenclature with the open classes dataset.
* **Numerical formats:** Conversion of text figures to numerical values using the `toNumber()` function in the `Año`, `Mes`, capacity columns (`Plazas`, `Ocupadas`, `Libres`) and gender breakdowns (`Nº Plazas Ocupadas (Masculino)` and `Nº Plazas Ocupadas (Femenino)`).
* **Character cleaning:** Mass edit in the `Actividad` and `Categoría` columns to clean placeholder dashes (`---`, `----`) into empty values.
* **Text format standardization:** Application of the `toTitlecase()` transformation in the `Clase`, `Distrito`, `Actividad` and `Categoría` columns to standardize capitalization.
* **Whitespace:** `trim` operation on the `Clase`, `Distrito` and `Centro deportivo` columns.

**3. Sports centers dataset (`sports_centers_info`)**
* **Column removal:** Deletion of the empty `PUERTA` and `ESCALERAS` columns.
* **Text format standardization:** Application of the `toTitlecase()` transformation in the `LOCALIDAD`, `PROVINCIA`, `BARRIO`, `DISTRITO`, `NOMBRE-VIA` and `CLASE-VIAL` columns to standardize capitalization. `trim` operation in `NOMBRE`, `BARRIO`, `DISTRITO`, `EMAIL` and `TELEFONO`.
* **Telephone standardization:** Replacement of line breaks, whitespaces and hyphens using regular expressions in the `TELEFONO` column, separating multiple numbers with a spaced slash.
* **HTML decoding:** Multiple `unescape('html')` operations in the `DESCRIPCION`, `EQUIPAMIENTO`, `HORARIO` and `TRANSPORTE` columns to decode special characters.
* **Whitespace and punctuation replacement:** Collapse of consecutive multiple whitespaces in the long text columns (`HORARIO`, `EQUIPAMIENTO`, `TRANSPORTE`) and removal of whitespaces prior to periods in `TRANSPORTE`.