# Barcelona Heat Relief: application

Web application that exploits the knowledge graph of Group 08. Every figure, list and filter comes
from a SPARQL query to the knowledge graph published in GraphDB. Images, descriptions, common names
and population come from Wikidata, reached through the `owl:sameAs` and `skos:broadMatch` links of
the graph.

## How to run it

Requirements: GraphDB Desktop, Python 3 and Internet access (map tiles, Leaflet and Wikidata).

1. Once: in GraphDB create the repository `barcelona-heat-relief` (ruleset without inference,
   "Disable owl:sameAs" checked) and import these files of `HandsOn/Group08` into the default graph:
   - `ontology/HeatRelief.ttl`
   - `rdf/areas-with-links.ttl`
   - `rdf/xarxa-refugis-climatics-with-links.ttl`
   - `rdf/fonts-beure-2026-with-links.ttl`
   - `rdf/arbrat-viari-with-links.ttl`

   The repository then holds 1,567,801 statements (`SELECT (COUNT(*) AS ?n) WHERE { ?s ?p ?o }`).
2. Start GraphDB Desktop.
3. From this folder run `python serve.py`: it opens http://localhost:8080/ in the browser.
   Stop it with Ctrl+C.

`serve.py` (Python standard library only) serves the files of this folder and forwards every
request to `/sparql` to the GraphDB repository, so the browser talks to one server only and GraphDB
needs no CORS setting. Options: `--port`, `--graphdb <SPARQL endpoint of the repository>`,
`--no-browser`.

## Views

| View | Content | Requirements |
|---|---|---|
| Filter bar | District, neighbourhood, shelter category and tree species (scientific or Catalan name; with a district or neighbourhood, only its species are suggested, the most frequent first). Map and Catalogue use all four, Neighbourhoods only district and neighbourhood. The category is disabled when the shelters are hidden, the species when the trees are hidden | FR2, FR3, FR4 |
| Map | Shelters, fountains and trees as layers that can be switched on and off; pop-up with the details of each resource | FR1, FR5 |
| Catalogue | Table of the resources with the same filters, a switch for each type, free-text search and pages. Choosing a shelter category shows the shelters only and choosing a species the trees only; the other types can be switched on again | FR6 |
| Neighbourhoods | Summary of the selected neighbourhood, cards of its most frequent species with Wikidata data, comparison of all neighbourhoods per inhabitant | FR7, FR8, FR9 |
| Queries | The eight questions of `requirements/applicationRequirements.html` (section 5), each with its SPARQL query and its result, and a free SPARQL editor | |

Map, Catalogue and Neighbourhoods end with a "SPARQL used" panel that shows the queries sent for the
current selection. Street trees (145,034) are requested only for a selected district, neighbourhood
or species, and the map shows at most 8,000 at a time. The filters are kept in the address, for
example `#/map?district=ciutat-vella&neighbourhood=el-raval`.

## Files

| File | Content |
|---|---|
| `index.html`, `css/style.css` | Page and styles |
| `js/main.js` | Views and address of the page |
| `js/state.js`, `js/filters.js` | Shared filters and their options (read from the graph) |
| `js/config.js` | SPARQL endpoints (default: `/sparql` of `serve.py`) |
| `js/sparql.js` | Sends the queries and adds the PREFIX declarations |
| `js/queries.js` | SPARQL queries of the Map, Catalogue and Neighbourhoods views |
| `js/querylog.js` | "SPARQL used" panels |
| `js/wikidata.js` | Queries to the Wikidata SPARQL endpoint |
| `js/views/` | One file per view |
| `serve.py` | Local server and forwarding of the queries to GraphDB |

Data: Ajuntament de Barcelona, Open Data BCN (CC BY 4.0); Wikidata (CC0); map tiles by
OpenStreetMap contributors.
