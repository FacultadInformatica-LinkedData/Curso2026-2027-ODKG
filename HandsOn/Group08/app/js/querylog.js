// SPARQL queries sent by each view, shown in the "SPARQL used in this view" panel at its bottom.
// A query replaces the previous one with the same title, e.g. the page of the catalogue.
import { html } from './util.js';

const logs = new Map();
const panels = new Map();

function render(view) {
  const list = panels.get(view);
  if (!list) return;
  const entries = logs.get(view) ?? [];
  list.innerHTML = entries.length
    ? entries.map((entry) => html`
        <p class="query-title">${entry.title} <span class="muted">(${entry.target})</span></p>
        <pre class="query-text">${entry.text}</pre>`).join('')
    : '<p class="muted">No query sent yet.</p>';
}

export function resetLog(view) {
  logs.set(view, []);
  render(view);
}

export function record({ view, title }, target, text) {
  const entries = (logs.get(view) ?? []).filter((entry) => entry.title !== title);
  entries.push({ title, target, text: text.trim() });
  logs.set(view, entries);
  render(view);
}

export function queryPanel(container, view, label = 'SPARQL used in this view') {
  const panel = document.createElement('details');
  panel.className = 'query-panel';
  panel.innerHTML = html`
    <summary>${label}</summary>
    <p class="muted">Queries sent for the current selection. The queries to our knowledge graph are
      sent with the PREFIX declarations of <code>js/sparql.js</code> (hr:, rdfs:, owl:, skos:, geo:, wd:).</p>
    <div class="query-list"></div>`;
  container.append(panel);
  panels.set(view, panel.querySelector('.query-list'));
  render(view);
}
