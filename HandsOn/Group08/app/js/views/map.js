// Map view (FR1, FR2, FR3, FR5): shelters, fountains and trees as switchable layers.
/* global L */
import * as Q from '../queries.js';
import { resetLog, queryPanel } from '../querylog.js';
import { select, shorten } from '../sparql.js';
import { setFieldsEnabled } from '../filters.js';
import { filters, lookup, placeName } from '../state.js';
import { errorMessage, formatDate, formatNumber, html, raw } from '../util.js';
import { entity, thumbnail, wikidataUrl } from '../wikidata.js';

const BARCELONA = [[41.32, 2.07], [41.47, 2.23]];
const LAYERS = [
  { key: 'shelters', label: 'Climate shelters', radius: 7 },
  { key: 'fountains', label: 'Drinking fountains', radius: 4 },
  { key: 'trees', label: 'Street trees', radius: 3 },
];

let map;
let renderer;
const groups = {};
const visible = { shelters: true, fountains: true, trees: true };
let status;
let areaCard;
let request = 0;

function renderAreaCard() {
  const place = lookup.neighbourhood.get(filters.neighbourhood);
  const district = lookup.district.get(place?.district ?? filters.district);
  areaCard.hidden = !district;
  if (!district) return;
  areaCard.innerHTML = place
    ? html`<p class="eyebrow">${district.name}</p><h3>${place.name}</h3>
           <a href="#/neighbourhoods">Neighbourhood summary →</a>`
    : html`<p class="eyebrow">District</p><h3>${district.name}</h3>
           <p class="muted">${lookup.neighbourhoods.filter((nb) => nb.district === district.district).length} neighbourhoods</p>`;
}

function cssVar(name) {
  return getComputedStyle(document.documentElement).getPropertyValue(name).trim();
}

function wikidataLink(value, text = 'Wikidata') {
  const url = wikidataUrl(value);
  return url ? html`<a href="${url}" target="_blank" rel="noopener">${text} ${value.split('/').pop()}</a>` : '';
}

function shelterPopup(row) {
  const category = lookup.category.get(row.category)?.name ?? shorten(row.category);
  return html`
    <div class="popup">
      ${row.wikidata ? raw('<div class="popup-wikidata" data-wikidata></div>') : ''}
      <p class="popup-kind">Climate shelter · ${category}</p>
      <h3>${row.name}</h3>
      <dl>
        ${row.address ? raw(html`<dt>Address</dt><dd>${row.address}</dd>`) : ''}
        <dt>Neighbourhood</dt><dd>${placeName(row.nb)}</dd>
        ${row.hours ? raw(html`<dt>Opening hours</dt><dd>${row.hours}</dd>`) : ''}
        ${row.phone ? raw(html`<dt>Telephone</dt><dd>${row.phone}</dd>`) : ''}
        ${row.website ? raw(html`<dt>Website</dt><dd><a href="${row.website}" target="_blank" rel="noopener">${row.website}</a></dd>`) : ''}
        ${row.wikidata ? raw(html`<dt>Hosted by</dt><dd>${row.facilityName} · ${raw(wikidataLink(row.wikidata))}</dd>`) : ''}
      </dl>
    </div>`;
}

function fountainPopup(row) {
  return html`
    <div class="popup">
      <p class="popup-kind">Drinking fountain</p>
      <h3>${row.name || shorten(row.fountain)}</h3>
      <dl>
        ${row.address ? raw(html`<dt>Address</dt><dd>${row.address}</dd>`) : ''}
        <dt>Neighbourhood</dt><dd>${placeName(row.nb)}</dd>
      </dl>
    </div>`;
}

function treePopup(row) {
  const species = lookup.speciesByIri.get(row.species) ?? {};
  const link = species.sameAs
    ? wikidataLink(species.sameAs)
    : species.broadMatch ? `${wikidataLink(species.broadMatch)} (broader taxon)` : '';
  return html`
    <div class="popup">
      ${link ? raw('<div class="popup-wikidata" data-wikidata></div>') : ''}
      <p class="popup-kind">Street tree</p>
      <h3><i>${species.scientificName ?? shorten(row.species)}</i></h3>
      <dl>
        ${species.catalanName ? raw(html`<dt>Common name</dt><dd>${species.catalanName}</dd>`) : ''}
        ${row.address ? raw(html`<dt>Address</dt><dd>${row.address}</dd>`) : ''}
        <dt>Neighbourhood</dt><dd>${placeName(row.nb)}</dd>
        ${row.planted ? raw(html`<dt>Planted</dt><dd>${formatDate(row.planted)}</dd>`) : ''}
        ${link ? raw(html`<dt>Species</dt><dd>${raw(link)}</dd>`) : ''}
      </dl>
    </div>`;
}

// Fills the Wikidata box of a pop-up (image and description) when it opens.
async function enrichPopup(event, wikidataIri) {
  const box = event.popup.getElement()?.querySelector('[data-wikidata]');
  if (!box || box.dataset.done) return;
  box.dataset.done = '1';
  box.innerHTML = '<p class="popup-loading">Loading from Wikidata…</p>';
  const data = await entity(wikidataIri);
  const image = thumbnail(data.image, 320);
  box.innerHTML = data.label || image
    ? html`${image ? raw(html`<img src="${image}" alt="${data.label}">`) : ''}
           ${data.description ? raw(html`<p>${data.description} <span class="muted">(Wikidata)</span></p>`) : ''}`
    : '';
  box.querySelector('img')?.addEventListener('load', () => event.popup.update());
  event.popup.update();
}

// Smaller markers when the whole city is visible, so that fountains do not cover the map.
function radiusFor(key) {
  const zoom = map.getZoom();
  const scale = zoom <= 12 ? 0.55 : zoom === 13 ? 0.75 : zoom === 14 ? 0.9 : 1;
  const base = LAYERS.find((layer) => layer.key === key).radius;
  return key === 'shelters' ? base * Math.max(scale, 0.75) : base * scale;
}

function resizeMarkers() {
  for (const key of Object.keys(groups)) {
    const radius = radiusFor(key);
    groups[key].eachLayer((marker) => marker.setRadius(radius));
  }
}

function addMarkers(key, rows, popup, latlng, wikidata) {
  const color = cssVar(`--layer-${key}`);
  const surface = cssVar('--surface-1');
  const radius = radiusFor(key);
  const group = groups[key];
  group.clearLayers();
  for (const row of rows) {
    const marker = L.circleMarker(latlng(row), {
      renderer, radius, color: surface, weight: key === 'shelters' ? 2 : 1, fillColor: color, fillOpacity: 0.95,
    });
    marker.bindPopup(() => popup(row), { maxWidth: 320 });
    const link = wikidata(row);
    if (link) marker.on('popupopen', (event) => enrichPopup(event, link));
    group.addLayer(marker);
  }
}

// One row per shelter, even when it is hosted by more than one facility.
function uniqueBy(rows, key) {
  const seen = new Map();
  for (const row of rows) if (!seen.has(row[key])) seen.set(row[key], row);
  return [...seen.values()];
}

function treesWanted() {
  return Boolean(filters.neighbourhood || filters.district || filters.species);
}

export function initMap(container) {
  container.innerHTML = html`
    <aside class="map-panel">
      <h2>Layers</h2>
      <ul class="layers">
        ${LAYERS.map((layer) => raw(html`
          <li><label>
            <input type="checkbox" data-layer="${layer.key}" checked>
            <span class="swatch swatch-${layer.key}"></span>${layer.label}
            <span class="layer-count" data-count="${layer.key}"></span>
          </label></li>`))}
      </ul>
      <p class="map-status" role="status"></p>
      <div class="area-card" data-area hidden></div>
      <p class="hint">Street trees are shown for the selected district, neighbourhood or species (145,034 in the city).
        The shelter category filter applies to the shelters, the species filter to the trees.</p>
      <div data-queries></div>
    </aside>
    <div class="map-canvas" id="map-canvas"></div>`;
  queryPanel(container.querySelector('[data-queries]'), 'map');
  status = container.querySelector('.map-status');
  areaCard = container.querySelector('[data-area]');
  map = L.map(container.querySelector('#map-canvas'), { preferCanvas: true }).fitBounds(BARCELONA);
  renderer = L.canvas({ padding: 0.5 });
  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 19,
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
  }).addTo(map);
  // Trees are drawn first so that fountains and shelters stay on top.
  for (const key of ['trees', 'fountains', 'shelters']) groups[key] = L.layerGroup().addTo(map);
  map.on('zoomend', resizeMarkers);
  container.querySelectorAll('[data-layer]').forEach((input) => {
    input.addEventListener('change', () => {
      visible[input.dataset.layer] = input.checked;
      setFieldsEnabled({ category: visible.shelters, species: visible.trees });
      refreshMap();
    });
  });
}

export function showMap() {
  map?.invalidateSize();
  setFieldsEnabled({ category: visible.shelters, species: visible.trees });
}

export async function refreshMap() {
  const id = ++request;
  const counts = document.querySelectorAll('[data-count]');
  renderAreaCard();
  status.textContent = 'Querying the knowledge graph…';
  resetLog('map');
  try {
    const [shelters, fountains, trees] = await Promise.all([
      visible.shelters ? select(Q.shelters(filters), { log: { view: 'map', title: 'Climate shelters' } }) : [],
      visible.fountains ? select(Q.fountains(filters), { log: { view: 'map', title: 'Drinking fountains' } }) : [],
      visible.trees && treesWanted() ? select(Q.trees(filters), { log: { view: 'map', title: 'Street trees' } }) : [],
    ]);
    if (id !== request) return; // a newer request is on its way
    const shelterRows = uniqueBy(shelters, 'shelter');
    // The canvas draws in insertion order: trees first, shelters last (on top).
    addMarkers('trees', trees, treePopup, (r) => [+r.lat, +r.long], (r) => {
      const species = lookup.speciesByIri.get(r.species);
      return species?.sameAs || species?.broadMatch;
    });
    addMarkers('fountains', fountains, fountainPopup, (r) => [+r.lat, +r.long], () => null);
    addMarkers('shelters', shelterRows, shelterPopup, (r) => [+r.lat, +r.long], (r) => r.wikidata);
    const shown = { shelters: shelterRows.length, fountains: fountains.length, trees: trees.length };
    counts.forEach((cell) => {
      const key = cell.dataset.count;
      cell.textContent = !visible[key] ? '' : key === 'trees' && !treesWanted() ? '–' : formatNumber(shown[key]);
    });
    status.textContent = trees.length === Q.TREE_LIMIT
      ? `Showing the first ${formatNumber(Q.TREE_LIMIT)} trees: choose a neighbourhood or a species to see them all.`
      : '';
    const points = [...shelterRows, ...fountains, ...trees].map((r) => [+r.lat, +r.long]);
    if (points.length && (filters.district || filters.neighbourhood || filters.species || filters.category)) {
      map.fitBounds(points, { padding: [24, 24], maxZoom: 16 });
    } else if (!points.length || !Object.values(filters).some(Boolean)) {
      map.fitBounds(BARCELONA);
    }
  } catch (error) {
    if (id === request) status.textContent = errorMessage(error);
  }
}
