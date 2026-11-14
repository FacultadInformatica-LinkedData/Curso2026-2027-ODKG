// Catalogue view (FR6, FR4): one table for shelters, fountains and trees, with the shared
// filters, switches for the three types, a free-text search and pagination done by the SPARQL
// endpoint (LIMIT / OFFSET).
import * as Q from '../queries.js';
import { resetLog, queryPanel } from '../querylog.js';
import { select, shorten } from '../sparql.js';
import { setFieldsEnabled } from '../filters.js';
import { filters, lookup, placeName } from '../state.js';
import { debounce, errorMessage, formatNumber, html, raw } from '../util.js';
import { wikidataUrl } from '../wikidata.js';

const PAGE_SIZE = 25;
const TYPE_NAMES = { '1 shelter': 'Climate shelter', '2 fountain': 'Drinking fountain', '3 tree': 'Street tree' };
const TYPE_LAYERS = { '1 shelter': 'shelters', '2 fountain': 'fountains', '3 tree': 'trees' };
const SWITCHES = [
  { type: 'shelter', layer: 'shelters', label: 'Climate shelters' },
  { type: 'fountain', layer: 'fountains', label: 'Drinking fountains' },
  { type: 'tree', layer: 'trees', label: 'Street trees' },
];

const view = { search: '', page: 0, pages: 1 };
const shown = { shelter: true, fountain: true, tree: true };
let seen = { category: '', species: '' };
let elements;
let request = 0;

// The 145,034 street trees are listed only within a district, a neighbourhood or a species.
function includeTrees() {
  return Boolean(filters.neighbourhood || filters.district || filters.species);
}

function types() {
  return Object.keys(shown).filter((type) => shown[type]);
}

// The shelter category applies to shelters and the species to trees. When one of them changes, the
// switches show the resources it applies to; the others can be switched on again.
function followFilters() {
  if (filters.category === seen.category && filters.species === seen.species) return;
  seen = { category: filters.category, species: filters.species };
  const none = !filters.category && !filters.species;
  shown.shelter = none || Boolean(filters.category);
  shown.fountain = none;
  shown.tree = none || Boolean(filters.species);
}

function applySwitches() {
  elements.switches.forEach((input) => { input.checked = shown[input.dataset.type]; });
  setFieldsEnabled({ category: shown.shelter, species: shown.tree });
}

export function showCatalogue() {
  if (elements) applySwitches();
}

function options() {
  return { types: types(), search: view.search, includeTrees: includeTrees() };
}

function linkCell(value) {
  const url = wikidataUrl(value);
  return url ? html`<a class="wd-badge" href="${url}" target="_blank" rel="noopener">${value.split('/').pop()}</a>` : '<span class="muted">–</span>';
}

function rowHtml(row) {
  const isTree = row.type === '3 tree';
  const species = isTree ? lookup.speciesByIri.get(row.species) : null;
  const category = row.category ? lookup.category.get(row.category)?.name ?? shorten(row.category) : '';
  const resource = html`<span class="type-pill"><span class="swatch swatch-${TYPE_LAYERS[row.type]}"></span>${TYPE_NAMES[row.type]}</span>${category ? raw(html`<span class="muted type-detail">${category}</span>`) : ''}`;
  return html`
    <tr>
      <td>${isTree ? raw(html`<i>${row.name}</i>${species?.catalanName ? raw(html`<span class="muted"> · ${species.catalanName}</span>`) : ''}`) : row.name}</td>
      <td>${raw(resource)}</td>
      <td>${row.address ?? ''}</td>
      <td>${placeName(row.nb)}</td>
      <td>${raw(linkCell(row.wikidata))}</td>
    </tr>`;
}

export function initCatalogue(container) {
  container.innerHTML = html`
    <div class="toolbar">
      <fieldset class="type-switches">
        <legend>Show</legend>
        ${SWITCHES.map((item) => raw(html`
          <label class="type-switch">
            <input type="checkbox" data-type="${item.type}" checked>
            <span class="swatch swatch-${item.layer}"></span>${item.label}
          </label>`))}
      </fieldset>
      <label class="field field-wide">
        <span>Search</span>
        <input type="search" id="c-search" placeholder="Search by name, species or address…">
      </label>
    </div>
    <p class="summary" role="status"></p>
    <div class="table-wrap">
      <table class="data-table">
        <thead><tr><th>Name or species</th><th>Resource</th><th>Address</th><th>Neighbourhood</th><th>Linked entity</th></tr></thead>
        <tbody></tbody>
      </table>
    </div>
    <nav class="pager">
      <button type="button" class="button-quiet" data-page="-1">Previous</button>
      <span class="pager-text"></span>
      <button type="button" class="button-quiet" data-page="1">Next</button>
    </nav>`;
  queryPanel(container, 'catalogue');
  elements = {
    summary: container.querySelector('.summary'),
    body: container.querySelector('tbody'),
    pagerText: container.querySelector('.pager-text'),
    previous: container.querySelector('[data-page="-1"]'),
    next: container.querySelector('[data-page="1"]'),
    switches: [...container.querySelectorAll('[data-type]')],
  };
  container.querySelector('#c-search').addEventListener('input', debounce((event) => {
    view.search = event.target.value.trim();
    refreshCatalogue();
  }));
  elements.switches.forEach((input) => input.addEventListener('change', () => {
    shown[input.dataset.type] = input.checked;
    applySwitches();
    refreshCatalogue();
  }));
  container.querySelectorAll('[data-page]').forEach((button) => button.addEventListener('click', () => {
    view.page = Math.min(Math.max(view.page + Number(button.dataset.page), 0), view.pages - 1);
    loadPage();
  }));
}

export async function refreshCatalogue() {
  view.page = 0;
  followFilters();
  applySwitches();
  const id = ++request;
  if (!types().length) {
    elements.summary.textContent = 'Switch on at least one type of resource.';
    elements.body.innerHTML = '';
    view.pages = 1;
    elements.pagerText.textContent = '';
    elements.previous.disabled = true;
    elements.next.disabled = true;
    resetLog('catalogue');
    return;
  }
  elements.summary.textContent = 'Counting…';
  resetLog('catalogue');
  try {
    const counts = await select(Q.catalogueCount(filters, options()), { log: { view: 'catalogue', title: 'Number of results' } });
    if (id !== request) return;
    const byType = Object.fromEntries(counts.map((row) => [row.type, Number(row.count)]));
    const total = Object.values(byType).reduce((sum, count) => sum + count, 0);
    view.pages = Math.max(1, Math.ceil(total / PAGE_SIZE));
    const parts = Object.entries(TYPE_NAMES)
      .filter(([type]) => byType[type])
      .map(([type, name]) => `${formatNumber(byType[type])} ${name.toLowerCase()}${byType[type] === 1 ? '' : 's'}`);
    let text = total ? `${formatNumber(total)} ${total === 1 ? 'result' : 'results'}: ${parts.join(', ')}.` : 'No results.';
    if (!includeTrees() && shown.tree) {
      text += ' Choose a district, a neighbourhood or a species to list the street trees too.';
    }
    elements.summary.textContent = text;
    await loadPage(id);
  } catch (error) {
    if (id === request) elements.summary.textContent = errorMessage(error);
  }
}

async function loadPage(id = ++request) {
  elements.pagerText.textContent = `Page ${view.page + 1} of ${formatNumber(view.pages)}`;
  elements.previous.disabled = view.page === 0;
  elements.next.disabled = view.page >= view.pages - 1;
  elements.body.classList.add('loading');
  try {
    const rows = await select(Q.cataloguePage(filters, options(), { limit: PAGE_SIZE, offset: view.page * PAGE_SIZE }),
      { log: { view: 'catalogue', title: 'Rows of the current page' } });
    if (id !== request) return;
    elements.body.innerHTML = rows.map(rowHtml).join('');
  } catch (error) {
    if (id === request) elements.summary.textContent = errorMessage(error);
  } finally {
    elements.body.classList.remove('loading');
  }
}
