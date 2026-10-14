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

**Deliverables.** One operation history file in JSON format per dataset with the OpenRefine operations and its updated CSV file:

| Dataset | Operations file | Updated CSV file |
|---|---|---|
| Open classes | `open_classes_operations.json` | `open_classes_updated.csv` |
| Closed classes | `closed_classes_operations.json` | `closed_classes_updated.csv` |
| Sports centers | `sports_centers_operations.json` | `sports_centers_info_updated.csv` |

**Main cleaning and transformation steps:**

**1. Open classes dataset (`open_classes`)**
* **Dates and times:** Conversion of the `Fecha` column to the ISO format `yyyy-MM-dd`. Transformation of the `Hora inicial` and `Hora final` columns to the `HH:mm:ss` format.
* **Whitespace:** `trim` operation on the `Actividad`, `Centro deportivo`, `Día de la semana` and `Tipo de actividad` columns to remove leading and trailing spaces.

**2. Closed classes dataset (`closed_classes`)**
* **Numerical formats:** Conversion of text figures to numerical values using the `toNumber()` function in the `Año`, `Mes`, `Nº Plazas Ofertadas`, `Nº Plazas Ocupadas`, `Nº Plazas Libres`, `Nº Plazas Ocupadas (Masculino)` and `Nº Plazas Ocupadas (Femenino)` columns.
* **Character cleaning:** Mass edit in the `Actividad` and `Categoría` columns to remove fields filled with dashes.
* **Text format standardization:** Application of the `toTitlecase()` transformation in the `Clase`, `Distrito`, `Actividad` and `Categoría` columns to standardize capitalization.
* **Whitespace:** `trim` operation on the `Clase`, `Distrito` and `Centro deportivo` columns.

**3. Sports centers dataset (`sports_centers_info`)**
* **Column removal:** Deletion of the empty `PUERTA` and `ESCALERAS` columns.
* **Text format standardization:** Application of the `toTitlecase()` transformation in the `LOCALIDAD`, `PROVINCIA`, `BARRIO`, `DISTRITO`, `NOMBRE-VIA` and `CLASE-VIAL` columns to standardize capitalization. `trim` operation in `NOMBRE`, `BARRIO`, `DISTRITO`, `EMAIL` and `TELEFONO`.
* **Telephone standardization:** Replacement of line breaks, whitespaces and hyphens using regular expressions in the `TELEFONO` column, separating multiple numbers with a spaced slash.
* **HTML decoding:** Multiple `unescape('html')` operations in the `DESCRIPCION`, `EQUIPAMIENTO`, `HORARIO` and `TRANSPORTE` columns to decode special characters.
* **Whitespace and punctuation replacement:** Collapse of consecutive multiple whitespaces in the long text columns (`HORARIO`, `EQUIPAMIENTO`, `TRANSPORTE`) and removal of whitespaces prior to periods in `TRANSPORTE`.