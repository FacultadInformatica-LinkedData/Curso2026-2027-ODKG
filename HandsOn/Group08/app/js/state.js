// Filters shared by all the views, and the lookups loaded once from the knowledge graph.
import * as Q from './queries.js';
import { select } from './sparql.js';

export const filters = { district: '', neighbourhood: '', category: '', species: '' };

const listeners = new Set();

export function onFiltersChange(listener) {
  listeners.add(listener);
}

export function setFilters(patch) {
  const next = { ...filters, ...patch };
  // A neighbourhood always belongs to the selected district.
  if (patch.neighbourhood) next.district = lookup.neighbourhood.get(patch.neighbourhood)?.district ?? next.district;
  if (patch.district !== undefined && !patch.neighbourhood && next.neighbourhood
      && lookup.neighbourhood.get(next.neighbourhood)?.district !== next.district) {
    next.neighbourhood = '';
  }
  const changed = Object.keys(next).some((key) => next[key] !== filters[key]);
  Object.assign(filters, next);
  if (changed) listeners.forEach((listener) => listener(filters));
}

export const lookup = {
  districts: [],
  neighbourhoods: [],
  categories: [],
  species: [],
  district: new Map(),
  neighbourhood: new Map(),
  category: new Map(),
  speciesByIri: new Map(),
};

export async function loadLookups() {
  const [districts, neighbourhoods, categories, species] = await Promise.all([
    select(Q.districts), select(Q.neighbourhoods), select(Q.categories), select(Q.species),
  ]);
  lookup.districts = districts;
  lookup.neighbourhoods = neighbourhoods.sort((a, b) => a.name.localeCompare(b.name, 'ca'));
  lookup.categories = categories;
  lookup.species = species;
  districts.forEach((row) => lookup.district.set(row.district, row));
  neighbourhoods.forEach((row) => lookup.neighbourhood.set(row.nb, row));
  categories.forEach((row) => lookup.category.set(row.category, row));
  species.forEach((row) => lookup.speciesByIri.set(row.species, row));
}

export function placeName(nb) {
  const row = lookup.neighbourhood.get(nb);
  if (!row) return '';
  const district = lookup.district.get(row.district);
  return district ? `${row.name} (${district.name})` : row.name;
}

export function hasFilters() {
  return Object.values(filters).some(Boolean);
}
