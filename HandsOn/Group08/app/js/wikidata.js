// Enrichment from Wikidata. The application first queries our knowledge graph, takes the
// Wikidata IRIs reached through owl:sameAs / skos:broadMatch, and then asks Wikidata for
// labels, descriptions, images, population and taxon common names of those items.
import { WIKIDATA_SPARQL } from './config.js';
import { selectRaw } from './sparql.js';

const cache = new Map();

export function qid(value) {
  const match = /^https?:\/\/www\.wikidata\.org\/entity\/(Q\d+)$/.exec(value ?? '');
  return match ? match[1] : null;
}

export function wikidataUrl(value) {
  const id = qid(value);
  return id ? `https://www.wikidata.org/wiki/${id}` : null;
}

export function thumbnail(image, width = 320) {
  return image ? `${image.replace(/^http:/, 'https:')}?width=${width}` : null;
}

export function entityQuery(ids) {
  return `PREFIX wd: <http://www.wikidata.org/entity/>
PREFIX wdt: <http://www.wikidata.org/prop/direct/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX schema: <http://schema.org/>
SELECT ?item (SAMPLE(?en) AS ?labelEn) (SAMPLE(?ca) AS ?labelCa) (SAMPLE(?es) AS ?labelEs)
       (SAMPLE(?desc) AS ?description) (SAMPLE(?img) AS ?image) (MAX(?pop) AS ?population)
       (GROUP_CONCAT(DISTINCT ?common; separator="|") AS ?commonNames)
WHERE {
  VALUES ?item { ${ids.map((id) => `wd:${id}`).join(' ')} }
  OPTIONAL { ?item rdfs:label ?en FILTER(LANG(?en) = "en") }
  OPTIONAL { ?item rdfs:label ?ca FILTER(LANG(?ca) = "ca") }
  OPTIONAL { ?item rdfs:label ?es FILTER(LANG(?es) = "es") }
  OPTIONAL { ?item schema:description ?desc FILTER(LANG(?desc) = "en") }
  OPTIONAL { ?item wdt:P18 ?img }
  OPTIONAL { ?item wdt:P1082 ?pop }
  OPTIONAL { ?item wdt:P1843 ?common FILTER(LANG(?common) = "en") }
} GROUP BY ?item`;
}

async function fetchChunk(ids, log) {
  const { rows } = await selectRaw(entityQuery(ids), { url: WIKIDATA_SPARQL, method: 'GET', prefixes: '', log });
  const found = new Map();
  for (const row of rows) {
    found.set(qid(row.item), {
      label: row.labelEn || row.labelCa || row.labelEs || '',
      description: row.description || '',
      image: row.image || null,
      population: row.population ? Number(row.population) : null,
      commonNames: row.commonNames ? row.commonNames.split('|') : [],
    });
  }
  return found;
}

// Returns a Map QID -> entity data. Items that Wikidata cannot provide map to {}.
export async function entities(values, log) {
  const ids = [...new Set(values.map(qid).filter(Boolean))];
  const missing = ids.filter((id) => !cache.has(id));
  for (let start = 0; start < missing.length; start += 100) {
    const chunk = missing.slice(start, start + 100);
    const request = fetchChunk(chunk, log);
    for (const id of chunk) {
      cache.set(id, request.then((found) => found.get(id) ?? {}, () => {
        cache.delete(id); // do not keep failures: retry next time
        return {};
      }));
    }
  }
  const result = new Map();
  for (const id of ids) result.set(id, await cache.get(id));
  return result;
}

export async function entity(value) {
  const id = qid(value);
  return id ? (await entities([value])).get(id) : {};
}
