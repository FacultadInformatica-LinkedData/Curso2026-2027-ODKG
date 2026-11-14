// All the SPARQL queries of the application. Prefixes are added by sparql.js.
// Every owl:sameAs is filtered to Wikidata IRIs, so the results stay the same when the
// GraphDB repository has owl:sameAs reasoning enabled (local and Wikidata IRIs merged).
import { iri, literal } from './sparql.js';

// Restricts ?nb to the selected neighbourhood, or to the neighbourhoods of the selected district.
function area(filters, variable = '?nb') {
  if (filters.neighbourhood) return `VALUES ${variable} { ${iri(filters.neighbourhood)} }`;
  if (filters.district) return `${variable} hr:isPartOfDistrict ${iri(filters.district)} .`;
  return '';
}

// ---------------------------------------------------------------- lookups (filter options)

export const districts = `
SELECT ?district ?name ?wikidata WHERE {
  ?district a hr:District ; rdfs:label ?name .
  OPTIONAL { ?district owl:sameAs ?wikidata FILTER(STRSTARTS(STR(?wikidata), STR(wd:))) }
} ORDER BY ?district`;

export const neighbourhoods = `
SELECT ?nb ?name ?district ?wikidata WHERE {
  ?nb a hr:Neighbourhood ; rdfs:label ?name ; hr:isPartOfDistrict ?district .
  OPTIONAL { ?nb owl:sameAs ?wikidata FILTER(STRSTARTS(STR(?wikidata), STR(wd:))) }
} ORDER BY ?nb`;

export const categories = `
SELECT ?category ?name WHERE {
  ?category a hr:ShelterCategory ; rdfs:label ?name .
} ORDER BY ?name`;

export const species = `
SELECT ?species ?scientificName
       (GROUP_CONCAT(DISTINCT ?ca; separator=", ") AS ?catalanName)
       (GROUP_CONCAT(DISTINCT ?es; separator=", ") AS ?spanishName)
       (SAMPLE(?same) AS ?sameAs) (SAMPLE(?broad) AS ?broadMatch)
WHERE {
  ?species a hr:TreeSpecies ; hr:scientificName ?scientificName .
  OPTIONAL { ?species hr:catalanName ?ca }
  OPTIONAL { ?species hr:spanishName ?es }
  OPTIONAL { ?species owl:sameAs ?same FILTER(STRSTARTS(STR(?same), STR(wd:))) }
  OPTIONAL { ?species skos:broadMatch ?broad }
} GROUP BY ?species ?scientificName ORDER BY ?scientificName`;

// Species of the trees of the selected district or neighbourhood, the most frequent first.
export function speciesInArea(filters) {
  return `
SELECT ?species (COUNT(?tree) AS ?trees) WHERE {
  ${area(filters)}
  ?tree hr:isLocatedInNeighbourhood ?nb ; hr:hasSpecies ?species .
} GROUP BY ?species ORDER BY DESC(?trees)`;
}

// ---------------------------------------------------------------- map

export function shelters(filters) {
  return `
SELECT ?shelter ?name ?lat ?long ?category ?address ?nb ?hours ?website ?phone ?facility ?facilityName ?wikidata
WHERE {
  ?shelter a hr:ClimateShelter ; rdfs:label ?name ; geo:lat ?lat ; geo:long ?long ;
           hr:hasShelterCategory ?category ; hr:isLocatedInNeighbourhood ?nb .
  ${filters.category ? `VALUES ?category { ${iri(filters.category)} }` : ''}
  ${area(filters)}
  OPTIONAL { ?shelter hr:streetAddress ?address }
  OPTIONAL { ?shelter hr:openingHours ?hours }
  OPTIONAL { ?shelter hr:website ?website }
  OPTIONAL { ?shelter hr:telephone ?phone }
  OPTIONAL { ?shelter hr:isHostedBy ?facility .
             ?facility rdfs:label ?facilityName ; owl:sameAs ?wikidata FILTER(STRSTARTS(STR(?wikidata), STR(wd:))) }
}`;
}

export function fountains(filters) {
  return `
SELECT ?fountain ?name ?lat ?long ?address ?nb WHERE {
  ?fountain a hr:DrinkingFountain ; geo:lat ?lat ; geo:long ?long ;
            hr:isLocatedInNeighbourhood ?nb .
  ${area(filters)}
  OPTIONAL { ?fountain rdfs:label ?name }
  OPTIONAL { ?fountain hr:streetAddress ?address }
}`;
}

export const TREE_LIMIT = 8000;

// Trees are requested only for a neighbourhood, a district or a species: there are 145,034.
export function trees(filters) {
  return `
SELECT ?tree ?lat ?long ?species ?address ?planted ?nb WHERE {
  ${filters.species ? `VALUES ?species { ${iri(filters.species)} }` : ''}
  ${area(filters)}
  ?tree hr:isLocatedInNeighbourhood ?nb ; hr:hasSpecies ?species ; a hr:StreetTree ;
        geo:lat ?lat ; geo:long ?long .
  OPTIONAL { ?tree hr:streetAddress ?address }
  OPTIONAL { ?tree hr:plantingDate ?planted }
} LIMIT ${TREE_LIMIT}`;
}

// ---------------------------------------------------------------- catalogue

// One UNION branch per type of resource. Each branch starts from its most selective pattern
// (species, neighbourhood or district) so that the endpoint does not scan all the trees.
function catalogueBody(filters, { types, search, includeTrees }) {
  const text = search ? literal(search.toLowerCase()) : null;
  const searchFilter = text
    ? `OPTIONAL { ?item hr:streetAddress ?searchAddress }
    FILTER(CONTAINS(LCASE(STR(?name)), ${text}) || CONTAINS(LCASE(STR(COALESCE(?searchAddress, ""))), ${text}))`
    : '';
  const branches = [];
  if (types.includes('shelter')) {
    branches.push(`{
    ${filters.category ? `VALUES ?category { ${iri(filters.category)} }` : ''}
    ${area(filters)}
    ?item hr:isLocatedInNeighbourhood ?nb ; a hr:ClimateShelter ; rdfs:label ?name ;
          hr:hasShelterCategory ?category .
    ${searchFilter}
    BIND("1 shelter" AS ?type)
  }`);
  }
  if (types.includes('fountain')) {
    branches.push(`{
    ${area(filters)}
    ?item hr:isLocatedInNeighbourhood ?nb ; a hr:DrinkingFountain ; rdfs:label ?name .
    ${searchFilter}
    BIND("2 fountain" AS ?type)
  }`);
  }
  if (includeTrees && types.includes('tree')) {
    branches.push(`{
    ${filters.species ? `VALUES ?species { ${iri(filters.species)} }` : ''}
    ${area(filters)}
    ${filters.species ? '?item hr:hasSpecies ?species ; hr:isLocatedInNeighbourhood ?nb .'
      : '?item hr:isLocatedInNeighbourhood ?nb ; hr:hasSpecies ?species .'}
    ?item a hr:StreetTree .
    ?species hr:scientificName ?name .
    ${searchFilter}
    BIND("3 tree" AS ?type)
  }`);
  }
  return branches.join('\n  UNION\n  ');
}

// The subquery sorts and cuts the page; address and Wikidata link are added for its rows only.
export function cataloguePage(filters, options, { limit, offset }) {
  return `
SELECT ?item ?type ?name ?category ?species ?nb ?address ?wikidata WHERE {
  {
    SELECT ?item ?type ?name ?category ?species ?nb WHERE {
  ${catalogueBody(filters, options)}
    } ORDER BY ?type ?name ?item LIMIT ${limit} OFFSET ${offset}
  }
  OPTIONAL { ?item hr:streetAddress ?address }
  OPTIONAL { ?item hr:isHostedBy/owl:sameAs ?facilityItem FILTER(STRSTARTS(STR(?facilityItem), STR(wd:))) }
  OPTIONAL { ?item hr:hasSpecies/owl:sameAs ?speciesItem FILTER(STRSTARTS(STR(?speciesItem), STR(wd:))) }
  BIND(COALESCE(?facilityItem, ?speciesItem) AS ?wikidata)
} ORDER BY ?type ?name ?item`;
}

export function catalogueCount(filters, options) {
  return `
SELECT ?type (COUNT(?item) AS ?count) WHERE {
  ${catalogueBody(filters, options)}
} GROUP BY ?type`;
}

// ---------------------------------------------------------------- neighbourhoods

export function neighbourhoodCounts(nb) {
  return `
SELECT
  (COUNT(DISTINCT ?shelter) AS ?shelters)
  (COUNT(DISTINCT ?fountain) AS ?fountains)
  (COUNT(DISTINCT ?tree) AS ?trees)
WHERE {
  { ?shelter a hr:ClimateShelter ; hr:isLocatedInNeighbourhood ${iri(nb)} }
  UNION { ?fountain a hr:DrinkingFountain ; hr:isLocatedInNeighbourhood ${iri(nb)} }
  UNION { ?tree a hr:StreetTree ; hr:isLocatedInNeighbourhood ${iri(nb)} }
}`;
}

export function neighbourhoodCategories(nb) {
  return `
SELECT ?category ?name (COUNT(?shelter) AS ?shelters) WHERE {
  ?shelter a hr:ClimateShelter ; hr:isLocatedInNeighbourhood ${iri(nb)} ;
           hr:hasShelterCategory ?category .
  ?category rdfs:label ?name .
} GROUP BY ?category ?name ORDER BY DESC(?shelters) ?name`;
}

export function neighbourhoodShelters(nb) {
  return `
SELECT ?shelter ?name ?category ?address ?facilityName ?wikidata WHERE {
  ?shelter a hr:ClimateShelter ; rdfs:label ?name ; hr:isLocatedInNeighbourhood ${iri(nb)} ;
           hr:hasShelterCategory ?category .
  OPTIONAL { ?shelter hr:streetAddress ?address }
  OPTIONAL { ?shelter hr:isHostedBy ?facility .
             ?facility rdfs:label ?facilityName ; owl:sameAs ?wikidata FILTER(STRSTARTS(STR(?wikidata), STR(wd:))) }
} ORDER BY ?name`;
}

export function topSpecies(nb, limit = 6) {
  return `
SELECT ?species (COUNT(?tree) AS ?trees) WHERE {
  ?tree a hr:StreetTree ; hr:isLocatedInNeighbourhood ${iri(nb)} ; hr:hasSpecies ?species .
} GROUP BY ?species ORDER BY DESC(?trees) LIMIT ${limit}`;
}

// One count per neighbourhood and type of resource, for the comparison table.
export const countsByNeighbourhood = `
SELECT ?nb ?type (COUNT(?item) AS ?count) WHERE {
  { ?item a hr:ClimateShelter . BIND("shelters" AS ?type) }
  UNION { ?item a hr:DrinkingFountain . BIND("fountains" AS ?type) }
  UNION { ?item a hr:StreetTree . BIND("trees" AS ?type) }
  ?item hr:isLocatedInNeighbourhood ?nb .
} GROUP BY ?nb ?type`;
