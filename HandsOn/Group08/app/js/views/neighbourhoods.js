// Neighbourhoods view (FR7, FR8, FR9): summary of the selected neighbourhood with species
// cards enriched with Wikidata, and a comparison of all neighbourhoods per inhabitant.
import * as Q from '../queries.js';
import { resetLog, queryPanel } from '../querylog.js';
import { select } from '../sparql.js';
import { filters, lookup, setFilters } from '../state.js';
import { errorMessage, formatDecimal, formatNumber, html, raw } from '../util.js';
import { entities, qid, thumbnail, wikidataUrl } from '../wikidata.js';

let elements;
let request = 0;
let comparison = null; // rows of the comparison table, loaded once
const sort = { key: 'sheltersPer10k', descending: true };

// layer: colour of the bar drawn in the cells when the table is sorted by that column.
const COLUMNS = [
  { key: 'name', label: 'Neighbourhood', text: true },
  { key: 'district', label: 'District', text: true },
  { key: 'population', label: 'Population', layer: 'neutral' },
  { key: 'shelters', label: 'Shelters', layer: 'shelters' },
  { key: 'fountains', label: 'Fountains', layer: 'fountains' },
  { key: 'trees', label: 'Trees', layer: 'trees' },
  { key: 'sheltersPer10k', label: 'Shelters per 10,000 inh.', decimal: true, layer: 'shelters' },
  { key: 'fountainsPer10k', label: 'Fountains per 10,000 inh.', decimal: true, layer: 'fountains' },
  { key: 'treesPer1k', label: 'Trees per 1,000 inh.', decimal: true, layer: 'trees' },
];

function wikidataLink(value, text) {
  const url = wikidataUrl(value);
  return url ? html`<a href="${url}" target="_blank" rel="noopener">${text ?? `Wikidata ${qid(value)}`}</a>` : '';
}

export function initNeighbourhoods(container) {
  container.innerHTML = html`
    <section class="nb-summary" aria-live="polite"></section>
    <div data-queries-nb></div>
    <section class="nb-compare">
      <div class="section-head">
        <h2>Compare neighbourhoods</h2>
        <p class="muted">Counts from our knowledge graph; population from Wikidata (P1082) through the
          <code>owl:sameAs</code> link of each neighbourhood. Click a column to sort, a name to open it.</p>
      </div>
      <p class="compare-status" role="status"></p>
      <div class="table-wrap"><table class="data-table compare-table"><thead></thead><tbody></tbody></table></div>
      <div data-queries-compare></div>
    </section>`;
  queryPanel(container.querySelector('[data-queries-nb]'), 'neighbourhoods', 'SPARQL used for this neighbourhood');
  queryPanel(container.querySelector('[data-queries-compare]'), 'comparison', 'SPARQL used for the comparison');
  elements = {
    summary: container.querySelector('.nb-summary'),
    status: container.querySelector('.compare-status'),
    head: container.querySelector('.compare-table thead'),
    body: container.querySelector('.compare-table tbody'),
  };
  elements.head.addEventListener('click', (event) => {
    const key = event.target.closest('th')?.dataset.key;
    if (!key) return;
    sort.descending = sort.key === key ? !sort.descending : !COLUMNS.find((c) => c.key === key).text;
    sort.key = key;
    renderComparison();
  });
  elements.body.addEventListener('click', (event) => {
    const nb = event.target.closest('[data-nb]')?.dataset.nb;
    if (!nb) return;
    setFilters({ neighbourhood: nb });
    window.scrollTo({ top: 0, behavior: 'smooth' });
  });
}

export async function refreshNeighbourhoods() {
  renderComparison();
  if (!comparison) loadComparison();
  const nb = filters.neighbourhood;
  if (!nb) {
    elements.summary.innerHTML = html`
      <div class="empty-state">
        <h2>Choose a neighbourhood</h2>
        <p>Select one in the filter bar, or click a name in the table below, to see its shelters,
           fountains, trees and most frequent species.</p>
      </div>`;
    return;
  }
  const id = ++request;
  const place = lookup.neighbourhood.get(nb);
  const district = lookup.district.get(place.district);
  elements.summary.innerHTML = html`<p class="muted">Loading ${place.name}…</p>`;
  resetLog('neighbourhoods');
  const log = (title) => ({ log: { view: 'neighbourhoods', title } });
  try {
    const [[counts], categories, top, shelters] = await Promise.all([
      select(Q.neighbourhoodCounts(nb), log('Shelters, fountains and trees of the neighbourhood')),
      select(Q.neighbourhoodCategories(nb), log('Shelters per category')),
      select(Q.topSpecies(nb), log('Most frequent tree species')),
      select(Q.neighbourhoodShelters(nb), log('List of climate shelters')),
    ]);
    if (id !== request) return;
    renderSummary({ place, district, counts, categories, top, shelters, wikidata: new Map() });
    // Second step: Wikidata data of the neighbourhood and of its species.
    const speciesRows = top.map((row) => lookup.speciesByIri.get(row.species) ?? {});
    const wikidata = await entities([place.wikidata, ...speciesRows.flatMap((s) => [s.sameAs, s.broadMatch])].filter(Boolean),
      { view: 'neighbourhoods', title: 'Population, images and common names of the linked items' });
    if (id !== request) return;
    renderSummary({ place, district, counts, categories, top, shelters, wikidata });
  } catch (error) {
    if (id === request) elements.summary.innerHTML = html`<p class="error">${errorMessage(error)}</p>`;
  }
}

function renderSummary({ place, district, counts, categories, top, shelters, wikidata }) {
  const info = wikidata.get(qid(place.wikidata)) ?? {};
  const image = thumbnail(info.image, 480);
  const maxCategory = Math.max(1, ...categories.map((row) => Number(row.shelters)));
  const uniqueShelters = [...new Map(shelters.map((row) => [row.shelter, row])).values()];
  elements.summary.innerHTML = html`
    <header class="nb-header">
      <div>
        <p class="eyebrow">${district?.name ?? ''} district · ${raw(wikidataLink(district?.wikidata, 'district on Wikidata'))}</p>
        <h2>${place.name}</h2>
        <p class="muted">${info.description ?? ''}
          ${info.population ? raw(html`· population <strong>${formatNumber(info.population)}</strong> (Wikidata)`) : ''}
          · ${raw(wikidataLink(place.wikidata))}</p>
      </div>
      ${image ? raw(html`<img class="nb-image" src="${image}" alt="${place.name}" loading="lazy">`) : ''}
    </header>
    <div class="tiles">
      <div class="tile"><span class="tile-value">${formatNumber(Number(counts.shelters))}</span><span class="tile-label"><span class="swatch swatch-shelters"></span>Climate shelters</span></div>
      <div class="tile"><span class="tile-value">${formatNumber(Number(counts.fountains))}</span><span class="tile-label"><span class="swatch swatch-fountains"></span>Drinking fountains</span></div>
      <div class="tile"><span class="tile-value">${formatNumber(Number(counts.trees))}</span><span class="tile-label"><span class="swatch swatch-trees"></span>Street trees</span></div>
    </div>
    <div class="nb-grid">
      <section class="card">
        <h3>Shelters by category</h3>
        ${categories.length ? raw(html`
          <ul class="bars">
            ${categories.map((row) => raw(html`
              <li title="${row.name}: ${row.shelters} shelters">
                <span class="bar-label">${row.name}</span>
                <span class="bar-track"><span class="bar" style="width:${(100 * Number(row.shelters)) / maxCategory}%"></span></span>
                <span class="bar-value">${row.shelters}</span>
              </li>`))}
          </ul>`) : raw('<p class="muted">No climate shelters in this neighbourhood.</p>')}
      </section>
      <section class="card">
        <h3>Climate shelters</h3>
        <ul class="shelter-list">
          ${uniqueShelters.map((row) => raw(html`
            <li><strong>${row.name}</strong>
              <span class="muted">${lookup.category.get(row.category)?.name ?? ''}${row.address ? ` · ${row.address}` : ''}</span>
              ${row.wikidata ? raw(html`<span class="muted"> · hosted by ${row.facilityName}</span> <a class="wd-badge" href="${wikidataUrl(row.wikidata)}" target="_blank" rel="noopener">${qid(row.wikidata)}</a>`) : ''}
            </li>`))}
        </ul>
      </section>
    </div>
    <section>
      <h3>Most frequent species</h3>
      <div class="species-grid">
        ${top.map((row) => raw(speciesCard(row, wikidata)))}
      </div>
    </section>`;
}

function speciesCard(row, wikidata) {
  const species = lookup.speciesByIri.get(row.species) ?? {};
  const link = species.sameAs || species.broadMatch;
  const info = wikidata.get(qid(link)) ?? {};
  const image = thumbnail(info.image, 360);
  const commonEn = info.commonNames?.slice(0, 2).join(', ');
  return html`
    <article class="species-card">
      ${image ? raw(html`<img src="${image}" alt="${species.scientificName}" loading="lazy">`) : raw('<div class="species-placeholder" aria-hidden="true"></div>')}
      <div class="species-body">
        <h4><i>${species.scientificName}</i></h4>
        <p>${species.catalanName || species.spanishName}${commonEn ? ` · ${commonEn}` : ''}</p>
        <p class="muted">${formatNumber(Number(row.trees))} trees ·
          ${link ? raw(wikidataLink(link, species.sameAs ? `Wikidata ${qid(link)}` : `broader taxon ${qid(link)}`)) : 'no Wikidata link'}</p>
      </div>
    </article>`;
}

async function loadComparison() {
  comparison = [];
  elements.status.textContent = 'Counting the resources of every neighbourhood…';
  try {
    const counts = await select(Q.countsByNeighbourhood, { log: { view: 'comparison', title: 'Counts per neighbourhood' } });
    const rows = new Map(lookup.neighbourhoods.map((nb) => [nb.nb, {
      nb: nb.nb,
      name: nb.name,
      district: lookup.district.get(nb.district)?.name ?? '',
      wikidata: nb.wikidata,
      population: null,
      shelters: 0,
      fountains: 0,
      trees: 0,
    }]));
    for (const row of counts) if (rows.has(row.nb)) rows.get(row.nb)[row.type] = Number(row.count);
    comparison = [...rows.values()];
    computeRatios();
    elements.status.textContent = 'Loading the population from Wikidata…';
    renderComparison();
    try {
      const wikidata = await entities(comparison.map((row) => row.wikidata).filter(Boolean),
        { view: 'comparison', title: 'Population of the neighbourhoods' });
      for (const row of comparison) row.population = wikidata.get(qid(row.wikidata))?.population ?? null;
      computeRatios();
      elements.status.textContent = '';
    } catch {
      elements.status.textContent = 'Wikidata could not be reached: the population and the ratios are not available.';
    }
    renderComparison();
  } catch (error) {
    comparison = null;
    elements.status.textContent = errorMessage(error);
  }
}

function computeRatios() {
  for (const row of comparison) {
    const per = (count, base) => (row.population ? (count * base) / row.population : null);
    row.sheltersPer10k = per(row.shelters, 10000);
    row.fountainsPer10k = per(row.fountains, 10000);
    row.treesPer1k = per(row.trees, 1000);
  }
}

function renderComparison() {
  elements.head.innerHTML = html`<tr>${COLUMNS.map((column) => raw(html`
    <th data-key="${column.key}" class="${column.text ? '' : 'num'} ${sort.key === column.key ? 'sorted' : ''}"
        aria-sort="${sort.key === column.key ? (sort.descending ? 'descending' : 'ascending') : 'none'}">
      <button type="button">${column.label}${sort.key === column.key ? (sort.descending ? ' ↓' : ' ↑') : ''}</button>
    </th>`))}</tr>`;
  if (!comparison?.length) {
    elements.body.innerHTML = '';
    return;
  }
  const column = COLUMNS.find((c) => c.key === sort.key);
  const rows = [...comparison].sort((a, b) => {
    const x = a[sort.key];
    const y = b[sort.key];
    if (x === null || x === undefined) return 1;
    if (y === null || y === undefined) return -1;
    const order = column.text ? String(x).localeCompare(String(y), 'ca') : x - y;
    return sort.descending ? -order : order;
  });
  const max = column.text ? 0 : Math.max(0, ...comparison.map((row) => row[sort.key] ?? 0));
  const value = (row, c) => (c.decimal ? formatDecimal(row[c.key]) : formatNumber(row[c.key]));
  elements.body.innerHTML = rows.map((row) => html`
    <tr class="${row.nb === filters.neighbourhood ? 'selected' : ''}">
      ${COLUMNS.map((c) => {
        if (c.key === 'name') return raw(html`<td><button type="button" class="link-button" data-nb="${row.nb}">${row.name}</button></td>`);
        if (c.text) return raw(html`<td>${row[c.key]}</td>`);
        if (c.key === sort.key && max > 0 && row[c.key] !== null) {
          return raw(html`<td class="num sorted-cell"><span class="cell-bar cell-bar-${c.layer}" style="width:${(100 * row[c.key]) / max}%"></span><span class="cell-value">${value(row, c)}</span></td>`);
        }
        return raw(html`<td class="num">${value(row, c)}</td>`);
      })}
    </tr>`).join('');
}
