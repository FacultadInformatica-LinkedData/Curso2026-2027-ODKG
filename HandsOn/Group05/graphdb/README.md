# Hands-on 6: Publishing the Valencia air quality knowledge graph (Group 05)

This folder documents how our linked data were published with **GraphDB** and queried with SPARQL,
following the procedure of the course slides (ODKG 12, *Publishing*), and how the ontology can be
published with **Ontoology** (optional part).

| File | Content |
|---|---|
| `queries-graphdb.sparql` | 10 SPARQL queries (G1-G10) that answer the competency questions of `requirements/applicationRequirements.html` |
| `expected-results/G1.csv` ... `G10.csv` | Results of the queries on the published data, to compare with the output of GraphDB |
| `repository-config.ttl` | Optional: configuration of the repository (same values as the GraphDB defaults) |
| `screenshots/` | Screenshots of the repository and of the queries executed in GraphDB |

## What is published

All files are imported into the **default graph** of the repository `valencia-airquality`.

| File | Content | Triples |
|---|---|---|
| `rdf/rvvcca-datos-horarios-valencia-2016-2021-curt-cas-with-links.ttl` | Knowledge graph with the links of hands-on 5 | 275,653 |
| `ontology/airquality.ttl` | Ontology (version 1.1, with labels, comments and metadata) | 56 |
| `rdf/void.ttl` | Dataset metadata (VoID/DCAT): general, structural, access and linkset metadata | 96 |

The data are the observations of 1-15 January 2020: 45,923 observations, 10 stations, 22 observable
properties and the city. 29 `owl:sameAs` links: the city and 18 magnitudes to Wikidata, and the 10
stations to their page in the GVA air quality network. The data conform to the SHACL shapes of
`shacl/shapes.ttl` (see `shacl/report.ttl`).

## 1. Linked data publishing with GraphDB

1. Download and install **GraphDB Desktop** (free) for your operating system:
   https://www.ontotext.com/products/graphdb/download/ (installation guide:
   https://graphdb.ontotext.com/documentation/11.5/graphdb-desktop-installation.html).
2. Launch the application. The server publishes the Workbench at http://localhost:7200/.
3. Create the repository: *Import* tab > *Create new repository* > *GraphDB Repository*.
   Repository ID: `valencia-airquality`. Leave the other parameters unchanged and click *Create*.
   The defaults are the ones we need: ruleset *RDFS-Plus (Optimized)* and *Disable owl:sameAs*
   checked (with sameAs reasoning GraphDB would copy every statement to the Wikidata and GVA IRIs
   and the queries would return duplicated rows).
4. Select the repository `valencia-airquality` in the selector at the top right.
5. Import the data: *Import* tab, then for each of the three files above:
   - *Get RDF data from a URL* and paste its raw GitHub URL, e.g.
     `https://raw.githubusercontent.com/a-sheg/Curso2026-2027-ODKG/HO6/HandsOn/Group05/rdf/rvvcca-datos-horarios-valencia-2016-2021-curt-cas-with-links.ttl`
     (replace `HO6` with the branch where the files are), or
   - *Upload RDF files* and select the file from the local copy of the repository.
   In the *Import settings* dialog choose *Target graphs: The default graph* and click *Import*.
6. Check that the data have been published: *SPARQL* tab, run

   ```sparql
   SELECT (COUNT(*) AS ?triples) WHERE { ?s ?p ?o }
   ```

   The explicit triples are 275,805 (275,653 + 56 + 96); GraphDB also shows the inferred ones.
   *Explore > Class hierarchy* shows the four classes of the ontology.
7. Execute the queries: paste each query of `queries-graphdb.sparql` in the *SPARQL* tab, run it,
   compare the result with `expected-results/` and save a screenshot in `screenshots/` (e.g. `G2.png`).
8. Optional: register the prefixes in *Setup > Namespaces* so that results are shown with prefixes
   (`aq:`, `obs:`, `station:`, `prop:`, `city:`, `wd:`; see the head of the RDF file).

## 2. Queries

| Query | Question (applicationRequirements.html) | Expected result |
|---|---|---|
| G1 | Instances of each class of the ontology | 45,923 observations, 22 properties, 10 stations, 1 city |
| G2 | CQ1: average NO2 per station in January 2020 | Valencia Centro 29.2 µg/m3 is the highest |
| G3 | CQ2: station with the highest PM10 level | Avda. Francia, 83 µg/m3 on 2020-01-01 00:00 |
| G4 | CQ3: daily evolution of O3 | 15 days |
| G5 | CQ4: days above the WHO 2021 guidelines (24-hour mean) per station and pollutant | 14 rows; Valencia Centro exceeded the NO2 guideline on 10 of 15 days |
| G6 | CQ5: correlation between wind speed and NO2 | Negative at 7 of 8 stations (r ≈ -0.35 to -0.45 once the square root is applied) |
| G7 | Stations, their city and their external link | 10 stations |
| G8 | Pollutants identified through their Wikidata entity | 18 magnitudes |
| G9 | Federated query to Wikidata (chemical formula and Spanish name) through the owl:sameAs links | Needs Internet access from GraphDB |
| G10 | Dataset metadata (VoID) and check that the declared statistics match the loaded data | 45,923 declared = 45,923 loaded |

The queries were tested with a SPARQL 1.1 engine on the same three files loaded in one default graph.

## 3. Dataset metadata

Following the publishing guidelines (describe the dataset with machine-readable metadata),
`rdf/void.ttl` describes the knowledge graph with VoID and DCAT:

- General metadata: title, description, creator, publisher, source dataset, dates, license (CC BY 4.0),
  subject, temporal coverage and keywords.
- Structural metadata: vocabularies used, URI space, example resources, number of triples, entities,
  classes, properties, distinct subjects/objects, and class and property partitions.
- Access metadata: data dump (raw file on GitHub) and SPARQL endpoint
  (`http://localhost:7200/repositories/valencia-airquality`, local GraphDB installation).
- Linksets: `owl:sameAs` links to Wikidata (19) and to the GVA station pages (10).

## 4. Ontology publishing with Ontoology (optional)

[Ontoology](https://ontoology.linkeddata.es/) (tutorial: https://ontoology.linkeddata.es/tutorial)
generates the documentation (Widoco), diagrams (AR2DTool) and evaluation (OOPS!) of an ontology
stored in GitHub, and opens a pull request with them.

1. `ontology/airquality.ttl` was updated to version 1.1. Labels, comments and metadata were added
   (title, description, creator, publisher, dates, license, version IRI, preferred prefix and
   namespace), because Widoco builds the documentation from them. Classes, properties, domains and
   ranges are unchanged, so the data and the mappings remain valid.
2. Ontoology needs admin rights on the GitHub repository, so the owner of the group repository
   (`a-sheg/Curso2026-2027-ODKG`) must do these steps:
   - Sign in at https://ontoology.linkeddata.es/ with GitHub and add the repository.
   - Select `HandsOn/Group05/ontology/airquality.ttl` as the ontology to be processed.
   - Push any change to the ontology (or press *Generate* in Ontoology). Ontoology opens a pull
     request with an `OnToology/` folder that contains the HTML documentation, the diagrams and
     the OOPS! evaluation.
   - Merge the pull request. If GitHub Pages is enabled, Ontoology also publishes the documentation.
3. The namespace `https://w3id.org/valencia-airquality/` is not registered in w3id.org yet. To
   make the ontology URI dereferenceable, a `.htaccess` redirect to the published documentation
   has to be added to https://github.com/perma-id/w3id.org.
