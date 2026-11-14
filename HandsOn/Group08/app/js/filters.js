// Filter bar shared by the Map, Catalogue and Neighbourhoods views.
import * as Q from './queries.js';
import { select } from './sparql.js';
import { filters, lookup, onFiltersChange, setFilters } from './state.js';
import { html } from './util.js';

const SPECIES_PLACEHOLDER = 'Search species by scientific or Catalan name…';

function speciesLabel(row) {
  return row.catalanName ? `${row.scientificName} — ${row.catalanName}` : row.scientificName;
}

export function renderFilterBar(container) {
  container.innerHTML = html`
    <label class="field" data-filter="district">
      <span>District</span>
      <select id="f-district"></select>
    </label>
    <label class="field" data-filter="neighbourhood">
      <span>Neighbourhood</span>
      <select id="f-neighbourhood"></select>
    </label>
    <label class="field" data-filter="category">
      <span>Shelter category</span>
      <select id="f-category">
        <option value="">All categories</option>
        ${lookup.categories.map((row) => ({ raw: html`<option value="${row.category}">${row.name}</option>` }))}
      </select>
    </label>
    <label class="field field-wide" data-filter="species">
      <span>Tree species</span>
      <input id="f-species" list="species-list" placeholder="${SPECIES_PLACEHOLDER}" autocomplete="off">
      <datalist id="species-list"></datalist>
    </label>
    <button type="button" class="button-quiet" id="f-reset">Clear filters</button>`;

  const district = container.querySelector('#f-district');
  const neighbourhood = container.querySelector('#f-neighbourhood');
  const category = container.querySelector('#f-category');
  const species = container.querySelector('#f-species');
  const datalist = container.querySelector('#species-list');
  const bySpeciesLabel = new Map(lookup.species.map((row) => [speciesLabel(row), row.species]));
  // Species suggested in the field: those of the selected district or neighbourhood, if any.
  let areaKey = null;
  let areaSpecies = null;

  function showSpecies(rows, placeholder) {
    datalist.innerHTML = rows.map((row) => html`<option value="${speciesLabel(row)}"></option>`).join('');
    species.placeholder = placeholder;
  }

  async function loadAreaSpecies() {
    const key = filters.neighbourhood || filters.district;
    if (key === areaKey) return;
    areaKey = key;
    areaSpecies = null;
    if (!key) return showSpecies(lookup.species, SPECIES_PLACEHOLDER);
    try {
      const rows = await select(Q.speciesInArea(filters));
      if (key !== areaKey) return;
      areaSpecies = rows.map((row) => lookup.speciesByIri.get(row.species)).filter(Boolean);
      const place = lookup.neighbourhood.get(key)?.name ?? lookup.district.get(key)?.name;
      showSpecies(areaSpecies, `Search the ${areaSpecies.length} species of ${place}…`);
    } catch {
      if (key === areaKey) showSpecies(lookup.species, SPECIES_PLACEHOLDER);
    }
  }

  function sync() {
    district.innerHTML = html`<option value="">All districts</option>${lookup.districts.map((row) =>
      ({ raw: html`<option value="${row.district}">${row.name}</option>` }))}`;
    const options = lookup.neighbourhoods.filter((row) => !filters.district || row.district === filters.district);
    neighbourhood.innerHTML = html`<option value="">All neighbourhoods</option>${options.map((row) =>
      ({ raw: html`<option value="${row.nb}">${row.name}</option>` }))}`;
    district.value = filters.district;
    neighbourhood.value = filters.neighbourhood;
    category.value = filters.category;
    const selected = lookup.speciesByIri.get(filters.species);
    if (selected) species.value = speciesLabel(selected);
    else if (bySpeciesLabel.has(species.value)) species.value = '';
    loadAreaSpecies();
  }

  district.addEventListener('change', () => setFilters({ district: district.value }));
  neighbourhood.addEventListener('change', () => setFilters({ neighbourhood: neighbourhood.value }));
  category.addEventListener('change', () => setFilters({ category: category.value }));
  species.addEventListener('change', () => {
    const value = species.value.trim();
    if (!value) return setFilters({ species: '' });
    const exact = bySpeciesLabel.get(value);
    if (exact) return setFilters({ species: exact });
    // Free text: take the first species whose names contain it, in the area first.
    const text = value.toLowerCase();
    const matches = (row) => speciesLabel(row).toLowerCase().includes(text)
      || (row.spanishName ?? '').toLowerCase().includes(text);
    const match = areaSpecies?.find(matches) ?? lookup.species.find(matches);
    if (match) {
      species.value = speciesLabel(match);
      setFilters({ species: match.species });
    } else {
      species.setCustomValidity('No species with this name');
      species.reportValidity();
      setTimeout(() => species.setCustomValidity(''), 1500);
    }
  });
  container.querySelector('#f-reset').addEventListener('click', () => {
    species.value = '';
    setFilters({ district: '', neighbourhood: '', category: '', species: '' });
  });

  onFiltersChange(sync);
  sync();
}

// Shows only the fields used by the current view.
export function showFilterFields(container, keys) {
  container.hidden = !keys.length;
  container.querySelectorAll('[data-filter]').forEach((field) => {
    field.hidden = !keys.includes(field.dataset.filter);
  });
  setFieldsEnabled({ category: true, species: true });
}

const OFF_HINTS = {
  category: 'Show the climate shelters to use this filter',
  species: 'Show the street trees to use this filter',
};

// Disables the filters of the resources that the current view does not show.
export function setFieldsEnabled(state) {
  for (const [key, enabled] of Object.entries(state)) {
    const field = document.querySelector(`#filter-bar [data-filter="${key}"]`);
    if (!field) continue;
    field.querySelector('select, input').disabled = !enabled;
    field.title = enabled ? '' : OFF_HINTS[key];
  }
}
