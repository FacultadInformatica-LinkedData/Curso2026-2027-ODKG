import { resolveEndpoint, WIKIDATA_SPARQL } from './config.js';
import { record } from './querylog.js';

export const RESOURCE = 'https://w3id.org/barcelona-heat-relief/resource/';

export const PREFIX_MAP = {
  hr: 'https://w3id.org/barcelona-heat-relief/ontology/HeatRelief#',
  rdfs: 'http://www.w3.org/2000/01/rdf-schema#',
  owl: 'http://www.w3.org/2002/07/owl#',
  skos: 'http://www.w3.org/2004/02/skos/core#',
  geo: 'http://www.w3.org/2003/01/geo/wgs84_pos#',
  xsd: 'http://www.w3.org/2001/XMLSchema#',
  wd: 'http://www.wikidata.org/entity/',
  shelter: `${RESOURCE}ClimateShelter/`,
  fountain: `${RESOURCE}DrinkingFountain/`,
  tree: `${RESOURCE}StreetTree/`,
  species: `${RESOURCE}TreeSpecies/`,
  neighbourhood: `${RESOURCE}Neighbourhood/`,
  district: `${RESOURCE}District/`,
  shelterCat: `${RESOURCE}ShelterCategory/`,
  facility: `${RESOURCE}Facility/`,
};

export const PREFIXES = Object.entries(PREFIX_MAP)
  .map(([prefix, iri]) => `PREFIX ${prefix}: <${iri}>`)
  .join('\n');

export const endpoint = resolveEndpoint();

// Number of queries in progress, shown by the loading bar.
let pending = 0;
const activityListeners = new Set();

export function onActivity(listener) {
  activityListeners.add(listener);
}

function setPending(delta) {
  pending += delta;
  activityListeners.forEach((listener) => listener(pending));
}

// Runs a SELECT query and returns { vars, rows }, where each row maps a variable to its value.
// log: { view, title } shows the query in the SPARQL panel of that view.
export async function selectRaw(query, { url = endpoint, method = 'POST', prefixes = PREFIXES, log } = {}) {
  const text = prefixes ? `${prefixes}\n${query}` : query;
  if (log) record(log, url === WIKIDATA_SPARQL ? 'Wikidata' : 'our knowledge graph', query);
  const headers = { Accept: 'application/sparql-results+json' };
  setPending(1);
  try {
    const response = method === 'GET'
      ? await fetch(`${url}?${new URLSearchParams({ query: text, format: 'json' })}`, { headers })
      : await fetch(url, { method: 'POST', headers, body: new URLSearchParams({ query: text }) });
    if (!response.ok) {
      const detail = (await response.text()).slice(0, 400);
      throw new Error(`The SPARQL endpoint answered ${response.status}: ${detail}`);
    }
    const data = await response.json();
    const rows = data.results.bindings.map((binding) =>
      Object.fromEntries(Object.entries(binding).map(([name, term]) => [name, term.value])));
    return { vars: data.head.vars, rows };
  } finally {
    setPending(-1);
  }
}

export async function select(query, options) {
  return (await selectRaw(query, options)).rows;
}

// Only IRIs of our own resources are written into queries.
export function iri(value) {
  if (typeof value !== 'string' || !value.startsWith(RESOURCE) || /[<>"{}|^`\\\s]/.test(value)) {
    throw new Error(`Unexpected IRI: ${value}`);
  }
  return `<${value}>`;
}

// SPARQL string literal (JSON escaping is valid SPARQL escaping).
export function literal(value) {
  return JSON.stringify(String(value));
}

export function shorten(value) {
  for (const [prefix, base] of Object.entries(PREFIX_MAP)) {
    if (value.startsWith(base) && value.length > base.length) return `${prefix}:${value.slice(base.length)}`;
  }
  return value;
}
