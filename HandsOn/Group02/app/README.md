# Personalized Chicago Park & Art Explorer

The Group02 application for *Open Data and Knowledge Graphs* (UPM, 2026-27). It is a web app that
plans walking routes through Chicago's public art and park facilities. All of its park, facility
and artwork data comes from the knowledge graph built in the hands-on (`../rdf/*-with-links-fixed.nt`),
queried with SPARQL. The `owl:sameAs` links are followed to Wikidata.

Spec: [`../requirements/applicationRequirements.html`](../requirements/applicationRequirements.html).

## Requirements → implementation

| Requirement | Where |
|---|---|
| FR-01 Location & preferences | `/` form (`templates/index.html`, `static/js/app.js`): park name, map click or GPS; 30–180 min budget; 5 interests. Validated in `parse_explore()` (`app.py`); points outside Chicago are rejected with a message. |
| FR-02 Facility recommendation | `recommend_facilities()` in `recommender.py`; table at the bottom of `/explore`. |
| FR-03 Art itinerary | `build_itinerary()` in `recommender.py` (greedy value-per-minute + 2-opt); never exceeds the budget. |
| FR-04 Interactive map | Leaflet + OpenStreetMap (`static/js/maps.js`): numbered route, start, recommended facilities; `★ Save route` stores the route in the browser (localStorage) and lists it on `/`. `/map` loads places for the visible area only (`/api/places?bbox=`). |
| FR-05 Reviews, ratings, tags, photos | Form on every facility/artwork page (`templates/place.html`); stored by `reviews.py` in SQLite (`data/reviews.db`), photos in `data/uploads/` (JPEG/PNG checked by content, ≤ 5 MB, random file names). |
| FR-06 Reviews in the ranking | `review_boost()` in `recommender.py` (formula below). |
| Disclaimer | Footer of every page (`templates/base.html`), text from the requirements. |
| Linked data | Resource pages mirror the URIs: `http://smartcity.chicago.es/resource/Artwork/X` → `/resource/Artwork/X`. Each page has a "Linked data" panel with its triples and a Turtle export (`?format=ttl`). Parks and artists with `owl:sameAs` show Wikidata facts and a Commons image (`wikidata.py`). |

## Architecture

```
Browser (Leaflet map, forms)
   │ HTTP
   ▼
app.py (Flask) ──► recommender.py   ranking, route, review boost
   │               reviews.py       SQLite + uploaded photos (app-generated data)
   │ SPARQL (queries.py)
   ▼
kg.py ── rdflib in-memory graph (default) or any SPARQL endpoint (SPARQL_ENDPOINT)
   │ owl:sameAs
   ▼
wikidata.py ── https://query.wikidata.org/sparql, cached in wikidata_seed.json + data/
```

* **`queries.py`**: every SPARQL query, with a description. They are also shown on `/about`. Per-request
  values (the resource URI) are passed as bindings (`initBindings`, or an escaped `VALUES` clause on a
  remote endpoint). User text is never pasted into a query.
* **`catalog.py`**: at start-up, `ALL_PARKS`, `ALL_FACILITIES`, `ALL_ARTWORKS` and `ARTWORK_CREATORS`
  are run once and kept in memory. The route search compares every candidate with every other one,
  so this avoids running thousands of queries per request. Detail pages query the graph live.
* **Reviews are kept out of the RDF** on purpose. They are app-generated, change constantly and are
  not the City of Chicago's data. They are keyed by the resource URI, so they join the graph cleanly.

| Query | Answers |
|---|---|
| `ALL_PARKS`, `ALL_FACILITIES`, `ALL_ARTWORKS`, `ARTWORK_CREATORS` | the catalogue used for routing and recommendations |
| `CLASS_COUNTS` | individuals per class and how many have `owl:sameAs` (home and about pages) |
| `PARK_DETAIL`, `PARK_FACILITIES`, `PARK_ARTWORKS` | park page |
| `FACILITY_DETAIL`, `ARTWORK_DETAIL`, `ARTWORK_ARTISTS`, `ARTWORK_OWNERS` | facility / artwork page |
| `ARTIST_DETAIL`, `ARTIST_WORKS`, `OWNER_DETAIL`, `OWNER_WORKS` | artist / owner page |
| `RESOURCE_OUTGOING`, `RESOURCE_INCOMING` | the "Linked data" panel |
| `WIKIDATA_ENTITY` | sent to Wikidata for each linked park or artist |

## Scoring

* **Interest match**: a facility scores 1 for each selected interest that its `pe:facilityName`
  serves (mapping in `INTEREST_FACILITIES`). Artworks have no type in the data, so they score 1.0 for
  Sculpture, 0.8 for Culture and 0.4 for Walking.
* **Recommendation score (FR-02)** = match − 0.5 × distance_km + review boost. Candidates must be
  within the search radius: half the budget spent walking, between 1 and 5 km.
* **Review boost (FR-06)** = 0.6 × (avg − 3) × n/(n+2)
  \+ 0.3 × (share of reviews carrying a tag that suits the interests)
  − 0.3 × (share tagged *crowded*).
  The n/(n+2) factor means one 5-star review counts for a third of its weight.
* **Route (FR-03)**: walking at 5 km/h on streets 1.25× longer than straight lines; visits take 10 min
  (artwork) or 15 min (facility). Starting at the start point, the route repeatedly adds the candidate
  with the best `value / (walk + visit minutes)` that still fits the budget. 2-opt then shortens the
  path, and the freed time is refilled. There is at most one stop per facility type.

## Run locally

```bash
cd HandsOn/Group02/app
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements-dev.txt
python app.py          # http://127.0.0.1:5050
pytest                 # 35 tests: counts from the graph, routing, reviews, pages
```

Environment variables (all optional):

| Variable | Default | Meaning |
|---|---|---|
| `SECRET_KEY` | random per start | signs the flash messages; set it in production |
| `DATA_DIR` | `app/data` | reviews database, uploaded photos, runtime Wikidata cache |
| `RDF_DIR` | `../rdf` | where the `.nt` files are |
| `SPARQL_ENDPOINT` | unset | query a GraphDB/Fuseki repository instead of loading the files |
| `WIKIDATA_ENABLED` | `1` | `0` = use only the cached Wikidata answers |
| `PORT` | `5050` | local port (5000 is taken by AirPlay on macOS) |

`python warm_wikidata.py` fetches Wikidata facts for all 322 linked parks and 97 linked artists into
`wikidata_seed.json`. Commit that file with the app: the site shows Wikidata data instantly, even if
Wikidata is slow. Re-run the script when the RDF links change.

## Deploy on PythonAnywhere (free account)

1. Sign up for a free *Beginner* account at <https://www.pythonanywhere.com>. The site will be
   `https://<username>.pythonanywhere.com`.
2. **Get the code.** The full course repository (every group, all history) is larger than the free
   512 MB disk, so fetch only the latest version of the two folders the app needs. Open
   *Consoles → Bash* and run:
   ```bash
   git clone --depth 1 --filter=blob:none --sparse -b app https://github.com/ZhengJinFa168/Curso2026-2027-ODKG.git
   cd Curso2026-2027-ODKG && git sparse-checkout set HandsOn/Group02/app HandsOn/Group02/rdf
   ```
3. **Create a virtualenv** (pick a Python version that the *Web* tab offers; 3.10 or newer):
   ```bash
   mkvirtualenv --python=/usr/bin/python3.12 explorer
   pip install -r ~/Curso2026-2027-ODKG/HandsOn/Group02/app/requirements.txt
   ```
4. **Create the web app.** In the *Web* tab, choose *Add a new web app → Manual configuration*
   (not the "Flask" option) and the same Python version.
5. On the web app page, set:
   * **Source code** and **Working directory**: `/home/<username>/Curso2026-2027-ODKG/HandsOn/Group02/app`
   * **Virtualenv**: `/home/<username>/.virtualenvs/explorer`
   * **Static files**: URL `/static/` → directory `/home/<username>/Curso2026-2027-ODKG/HandsOn/Group02/app/static`
6. **WSGI file.** Click the *WSGI configuration file* link and replace everything in it with the
   following. To make a secret key, run `python3 -c "import secrets; print(secrets.token_hex(32))"`
   in the console.
   ```python
   import os
   import sys

   os.environ["SECRET_KEY"] = "paste-the-generated-key-here"
   path = "/home/<username>/Curso2026-2027-ODKG/HandsOn/Group02/app"
   if path not in sys.path:
       sys.path.insert(0, path)

   from wsgi import application  # noqa: E402
   ```
7. Click **Reload**, then open the site. The first request loads the graph (about 1–2 s).
   *Error log* and *Server log* links on the Web tab show any problem.

**Updating**: `cd ~/Curso2026-2027-ODKG && git pull` in a console, then click **Reload**.

**Free-tier notes**

* Outbound HTTP is limited to an allowlist. `.wikidata.org` is on it, and the seed cache covers
  every linked entity anyway. The map tiles, Leaflet and Commons images load in the visitor's browser,
  so the allowlist does not apply to them.
* Reviews and photos are stored under `app/data/`, which persists. It is git-ignored, so
  `git pull` never touches it. The free disk quota is 512 MB.
* Free web apps are switched off after three months unless you log in and press
  *Run until 3 months from today* on the Web tab.

## Licensing

The park and art data come from the City of Chicago Data Portal (Chicago Park District datasets),
used under its terms of use; the required disclaimer is in the footer. Wikidata facts are CC0.
Images are loaded from Wikimedia Commons, each linked to its file page for author and licence.
Map tiles © OpenStreetMap contributors.
