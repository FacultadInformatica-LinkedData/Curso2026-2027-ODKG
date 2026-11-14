// Queries view: the eight questions that the knowledge graph must answer
// (applicationRequirements.html, section 5), each with its SPARQL query and its results,
// plus a free SPARQL editor.
import { iri, PREFIXES, selectRaw, shorten } from '../sparql.js';
import { lookup } from '../state.js';
import { errorMessage, formatNumber, highlightSparql, html, raw } from '../util.js';
import { entities, entityQuery, qid, wikidataUrl } from '../wikidata.js';

const DEFAULT_NB = 'https://w3id.org/barcelona-heat-relief/resource/Neighbourhood/la-dreta-de-l-eixample';
const DEFAULT_CATEGORY = 'https://w3id.org/barcelona-heat-relief/resource/ShelterCategory/Library';

export const QUESTIONS = [
  {
    title: 'Which climate shelters are in a given neighbourhood and of what category are they?',
    params: ['neighbourhood'],
    query: ({ neighbourhood }) => `
SELECT ?shelter ?name ?category ?address WHERE {
  ?shelter a hr:ClimateShelter ;
           rdfs:label ?name ;
           hr:isLocatedInNeighbourhood ${iri(neighbourhood)} ;
           hr:hasShelterCategory/rdfs:label ?category .
  OPTIONAL { ?shelter hr:streetAddress ?address }
}
ORDER BY ?category ?name`,
  },
  {
    title: 'How many drinking fountains does each district have?',
    params: [],
    query: () => `
SELECT ?district ?name ?wikidata (COUNT(?fountain) AS ?fountains) WHERE {
  ?fountain a hr:DrinkingFountain ;
            hr:isLocatedInNeighbourhood/hr:isPartOfDistrict ?district .
  ?district rdfs:label ?name ;
            owl:sameAs ?wikidata .
  FILTER(STRSTARTS(STR(?wikidata), STR(wd:)))
}
GROUP BY ?district ?name ?wikidata
ORDER BY DESC(?fountains)`,
  },
  {
    title: 'Which are the most frequent tree species in a given neighbourhood?',
    params: ['neighbourhood'],
    query: ({ neighbourhood }) => `
SELECT ?species ?scientificName (COUNT(?tree) AS ?trees) WHERE {
  ?tree a hr:StreetTree ;
        hr:isLocatedInNeighbourhood ${iri(neighbourhood)} ;
        hr:hasSpecies ?species .
  ?species hr:scientificName ?scientificName .
}
GROUP BY ?species ?scientificName
ORDER BY DESC(?trees)
LIMIT 10`,
  },
  {
    title: 'Which neighbourhoods have no shelter of a given category?',
    params: ['category'],
    query: ({ category }) => `
SELECT ?neighbourhood ?name ?district WHERE {
  ?neighbourhood a hr:Neighbourhood ;
                 rdfs:label ?name ;
                 hr:isPartOfDistrict/rdfs:label ?district .
  FILTER NOT EXISTS {
    ?shelter hr:isLocatedInNeighbourhood ?neighbourhood ;
             hr:hasShelterCategory ${iri(category)} .
  }
}
ORDER BY ?district ?name`,
  },
  {
    title: 'How many trees were planted since a given year in each district?',
    params: ['year'],
    query: ({ year }) => `
SELECT ?district ?name (COUNT(?tree) AS ?trees) WHERE {
  ?tree a hr:StreetTree ;
        hr:plantingDate ?date ;
        hr:isLocatedInNeighbourhood/hr:isPartOfDistrict ?district .
  ?district rdfs:label ?name .
  FILTER(?date >= "${Number(year)}-01-01T00:00:00"^^xsd:dateTime)
}
GROUP BY ?district ?name
ORDER BY DESC(?trees)`,
  },
  {
    title: 'Which resources (shelters, fountains) and how many trees are in a given neighbourhood?',
    params: ['neighbourhood'],
    query: ({ neighbourhood }) => `
SELECT ?type ?resource ?name ?address WHERE {
  {
    ?resource a hr:ClimateShelter ; rdfs:label ?name ;
              hr:isLocatedInNeighbourhood ${iri(neighbourhood)} .
    OPTIONAL { ?resource hr:streetAddress ?address }
    BIND("Climate shelter" AS ?type)
  } UNION {
    ?resource a hr:DrinkingFountain ; rdfs:label ?name ;
              hr:isLocatedInNeighbourhood ${iri(neighbourhood)} .
    OPTIONAL { ?resource hr:streetAddress ?address }
    BIND("Drinking fountain" AS ?type)
  } UNION {
    SELECT ("Street trees" AS ?type) (STR(COUNT(?tree)) AS ?name) WHERE {
      ?tree a hr:StreetTree ; hr:isLocatedInNeighbourhood ${iri(neighbourhood)} .
    }
  }
}
ORDER BY ?type ?name`,
  },
  {
    title: 'Which shelters correspond to a facility that has a Wikidata item?',
    params: [],
    query: () => `
SELECT ?shelter ?name ?facility ?facilityName ?wikidata WHERE {
  ?shelter a hr:ClimateShelter ;
           rdfs:label ?name ;
           hr:isHostedBy ?facility .
  ?facility rdfs:label ?facilityName ;
            owl:sameAs ?wikidata .
  FILTER(STRSTARTS(STR(?wikidata), STR(wd:)))
}
ORDER BY ?name`,
  },
  {
    title: 'Which species of a neighbourhood are linked to Wikidata and what are their common names?',
    params: ['neighbourhood'],
    wikidataNames: true,
    query: ({ neighbourhood }) => `
SELECT ?species ?scientificName ?catalanName ?link ?wikidata (COUNT(?tree) AS ?trees) WHERE {
  ?tree a hr:StreetTree ;
        hr:isLocatedInNeighbourhood ${iri(neighbourhood)} ;
        hr:hasSpecies ?species .
  ?species hr:scientificName ?scientificName .
  OPTIONAL { ?species hr:catalanName ?catalanName }
  { ?species owl:sameAs ?wikidata . BIND("owl:sameAs" AS ?link) }
  UNION
  { ?species skos:broadMatch ?wikidata . BIND("skos:broadMatch" AS ?link) }
  FILTER(STRSTARTS(STR(?wikidata), STR(wd:)))
}
GROUP BY ?species ?scientificName ?catalanName ?link ?wikidata
ORDER BY DESC(?trees)`,
  },
];

function paramField(name, index) {
  if (name === 'neighbourhood') {
    return html`<label class="field"><span>Neighbourhood</span><select data-param="neighbourhood">
      ${lookup.neighbourhoods.map((row) => raw(html`<option value="${row.nb}" ${row.nb === DEFAULT_NB ? 'selected' : ''}>${row.name}</option>`))}
    </select></label>`;
  }
  if (name === 'category') {
    return html`<label class="field"><span>Shelter category</span><select data-param="category">
      ${lookup.categories.map((row) => raw(html`<option value="${row.category}" ${row.category === DEFAULT_CATEGORY ? 'selected' : ''}>${row.name}</option>`))}
    </select></label>`;
  }
  return html`<label class="field"><span>Year</span>
    <input type="number" data-param="year" value="2020" min="2001" max="2026" id="q${index}-year"></label>`;
}

function cell(value, name) {
  if (value === undefined) return '';
  if (wikidataUrl(value)) return html`<a href="${wikidataUrl(value)}" target="_blank" rel="noopener">wd:${qid(value)}</a>`;
  if (/^https?:\/\//.test(value)) return html`<span class="iri">${shorten(value)}</span>`;
  if (name === 'scientificName') return html`<i>${value}</i>`;
  return html`${value}`;
}

function resultTable({ vars, rows }, limit = 200) {
  if (!rows.length) return '<p class="muted">No results.</p>';
  return html`
    <p class="muted">${formatNumber(rows.length)} rows${rows.length > limit ? `, first ${limit} shown` : ''}.</p>
    <div class="table-wrap"><table class="data-table compact">
      <thead><tr>${vars.map((v) => raw(html`<th>${v}</th>`))}</tr></thead>
      <tbody>${rows.slice(0, limit).map((row) => raw(html`<tr>${vars.map((v) => raw(html`<td>${raw(cell(row[v], v))}</td>`))}</tr>`))}</tbody>
    </table></div>`;
}

async function run(question, card) {
  const params = Object.fromEntries([...card.querySelectorAll('[data-param]')].map((input) => [input.dataset.param, input.value]));
  const query = question.query(params).trim();
  const output = card.querySelector('.q-output');
  card.querySelector('.q-sparql').innerHTML = highlightSparql(query);
  output.innerHTML = '<p class="muted">Running…</p>';
  const start = performance.now();
  try {
    const result = await selectRaw(query);
    const ms = Math.round(performance.now() - start);
    output.innerHTML = html`<p class="muted">Answered in ${formatNumber(ms)} ms by the knowledge graph.</p>${raw(resultTable(result))}`;
    if (question.wikidataNames && result.rows.length) {
      // Second step: common names of the linked items, asked to Wikidata.
      const links = result.rows.map((row) => row.wikidata);
      const ids = [...new Set(links.map(qid).filter(Boolean))];
      const data = await entities(links);
      result.vars.push('wikidataLabel', 'wikidataCommonNames');
      for (const row of result.rows) {
        const info = data.get(qid(row.wikidata)) ?? {};
        row.wikidataLabel = info.label ?? '';
        row.wikidataCommonNames = (info.commonNames ?? []).slice(0, 4).join(', ');
      }
      output.innerHTML = html`<p class="muted">Answered in ${formatNumber(ms)} ms by the knowledge graph,
        then enriched with the English labels and taxon common names (P1843) of the ${ids.length} linked Wikidata items.</p>
        ${raw(resultTable(result))}
        <details><summary>Query sent to Wikidata</summary><pre>${raw(highlightSparql(entityQuery(ids)))}</pre></details>`;
    }
  } catch (error) {
    output.innerHTML = html`<p class="error">${errorMessage(error)}</p>`;
  }
}

export function initQuestions(container) {
  container.innerHTML = html`
    <div class="section-head">
      <h2>Questions answered by the knowledge graph</h2>
      <p class="muted">The eight questions of the application requirements, each answered by a SPARQL query on the
        published knowledge graph. The prefixes used by every query are listed at the end of the page.</p>
    </div>
    <ol class="questions">
      ${QUESTIONS.map((question, index) => raw(html`
        <li class="card question" data-index="${index}">
          <h3><span class="q-number">Q${index + 1}</span> ${question.title}</h3>
          <div class="q-controls">
            ${question.params.map((name) => raw(paramField(name, index)))}
            <button type="button" class="button" data-run>Run query</button>
          </div>
          <details><summary>SPARQL query</summary><pre class="q-sparql"></pre></details>
          <div class="q-output"></div>
        </li>`))}
    </ol>
    <section class="card">
      <h3>Write your own query</h3>
      <textarea id="free-query" rows="8" spellcheck="false">SELECT ?class (COUNT(?resource) AS ?resources) WHERE {
  ?resource a ?class .
  FILTER(STRSTARTS(STR(?class), STR(hr:)))
}
GROUP BY ?class
ORDER BY DESC(?resources)</textarea>
      <div class="q-controls"><button type="button" class="button" id="free-run">Run query</button></div>
      <div class="q-output" id="free-output"></div>
    </section>
    <details class="card"><summary>Prefixes</summary><pre>${raw(highlightSparql(PREFIXES))}</pre></details>`;

  container.querySelectorAll('.question').forEach((card) => {
    const question = QUESTIONS[Number(card.dataset.index)];
    card.querySelector('.q-sparql').innerHTML = highlightSparql(question.query(
      Object.fromEntries([...card.querySelectorAll('[data-param]')].map((input) => [input.dataset.param, input.value])),
    ).trim());
    card.querySelector('[data-run]').addEventListener('click', () => run(question, card));
    card.querySelectorAll('[data-param]').forEach((input) => input.addEventListener('change', () => run(question, card)));
  });
  container.querySelector('#free-run').addEventListener('click', async () => {
    const output = container.querySelector('#free-output');
    output.innerHTML = '<p class="muted">Running…</p>';
    try {
      output.innerHTML = resultTable(await selectRaw(container.querySelector('#free-query').value));
    } catch (error) {
      output.innerHTML = html`<p class="error">${errorMessage(error)}</p>`;
    }
  });
}

export function runAllQuestions(container) {
  container.querySelectorAll('.question').forEach((card) => {
    if (!card.querySelector('.q-output').innerHTML) run(QUESTIONS[Number(card.dataset.index)], card);
  });
}
