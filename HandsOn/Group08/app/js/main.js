import { renderFilterBar, showFilterFields } from './filters.js';
import { endpoint, onActivity, RESOURCE, select } from './sparql.js';
import { filters, loadLookups, lookup, onFiltersChange, setFilters } from './state.js';
import { errorMessage, formatNumber, html } from './util.js';
import { initCatalogue, refreshCatalogue, showCatalogue } from './views/catalogue.js';
import { initMap, refreshMap, showMap } from './views/map.js';
import { initNeighbourhoods, refreshNeighbourhoods } from './views/neighbourhoods.js';
import { initQuestions, runAllQuestions } from './views/questions.js';

// Filters used by each view: the Neighbourhoods view depends on the place only.
const ALL_FILTERS = ['district', 'neighbourhood', 'category', 'species'];
const VIEWS = {
  map: { init: initMap, refresh: refreshMap, show: showMap, filters: ALL_FILTERS },
  catalogue: { init: initCatalogue, refresh: refreshCatalogue, show: showCatalogue, filters: ALL_FILTERS },
  neighbourhoods: { init: initNeighbourhoods, refresh: refreshNeighbourhoods, filters: ['district', 'neighbourhood'] },
  queries: { init: initQuestions, refresh: (container) => runAllQuestions(container), filters: [] },
};

const dirty = new Set(Object.keys(VIEWS));
let current = null;

// Filters are kept in the address, e.g. #/neighbourhoods?neighbourhood=el-raval, so a view can be shared.
const URL_FILTERS = {
  district: ['District/', lookup.district],
  neighbourhood: ['Neighbourhood/', lookup.neighbourhood],
  category: ['ShelterCategory/', lookup.category],
  species: ['TreeSpecies/', lookup.speciesByIri],
};

function filtersFromAddress() {
  const params = new URLSearchParams(location.hash.split('?')[1] ?? '');
  const patch = {};
  for (const [key, [path, known]] of Object.entries(URL_FILTERS)) {
    const value = params.get(key);
    if (value && known.has(RESOURCE + path + value)) patch[key] = RESOURCE + path + value;
  }
  return patch;
}

function writeAddress() {
  const params = new URLSearchParams();
  for (const [key, [path]] of Object.entries(URL_FILTERS)) {
    if (filters[key] && VIEWS[current].filters.includes(key)) params.set(key, filters[key].slice(RESOURCE.length + path.length));
  }
  const query = params.toString();
  history.replaceState(null, '', `#/${current}${query ? `?${query}` : ''}`);
}

function container(name) {
  return document.getElementById(`view-${name}`);
}

function show(name) {
  if (!VIEWS[name]) name = 'map';
  current = name;
  for (const key of Object.keys(VIEWS)) container(key).hidden = key !== name;
  document.querySelectorAll('[data-nav]').forEach((link) => {
    link.toggleAttribute('aria-current', link.dataset.nav === name);
  });
  showFilterFields(document.getElementById('filter-bar'), VIEWS[name].filters);
  VIEWS[name].show?.();
  writeAddress();
  if (dirty.has(name)) {
    dirty.delete(name);
    VIEWS[name].refresh(container(name));
  }
}

function route() {
  show(location.hash.replace(/^#\/?/, '').split('?')[0] || 'map');
}

async function start() {
  document.getElementById('endpoint').textContent = endpoint;
  const loading = document.getElementById('loading');
  let timer;
  onActivity((pending) => {
    // Shown only for queries that take more than a moment.
    clearTimeout(timer);
    if (pending > 0) timer = setTimeout(() => { loading.hidden = false; }, 250);
    else loading.hidden = true;
  });
  try {
    await loadLookups();
  } catch (error) {
    document.getElementById('banner').hidden = false;
    document.getElementById('banner').innerHTML = html`<strong>No data.</strong> ${errorMessage(error)}`;
    return;
  }
  setFilters(filtersFromAddress());
  renderFilterBar(document.getElementById('filter-bar'));
  for (const [name, view] of Object.entries(VIEWS)) view.init(container(name));
  let previous = { ...filters };
  onFiltersChange(() => {
    const changed = Object.keys(filters).filter((key) => filters[key] !== previous[key]);
    previous = { ...filters };
    writeAddress();
    // A view is refreshed only when one of its own filters changed.
    for (const [name, view] of Object.entries(VIEWS)) {
      if (view.filters.some((key) => changed.includes(key))) dirty.add(name);
    }
    if (dirty.has(current)) {
      dirty.delete(current);
      VIEWS[current].refresh(container(current));
    }
  });
  window.addEventListener('hashchange', route);
  route();
  select('SELECT (COUNT(*) AS ?triples) WHERE { ?s ?p ?o }')
    .then(([row]) => { document.getElementById('triples').textContent = `${formatNumber(Number(row.triples))} triples`; })
    .catch(() => {});
}

start();
