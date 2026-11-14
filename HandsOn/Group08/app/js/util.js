export function escapeHtml(value) {
  return String(value ?? '').replace(/[&<>"']/g, (char) => ({
    '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;',
  })[char]);
}

// Tagged template that escapes every interpolated value unless it is wrapped with raw().
export function html(strings, ...values) {
  return strings.reduce((out, string, index) => {
    if (index === 0) return string;
    const value = values[index - 1];
    const text = Array.isArray(value)
      ? value.map((item) => (item?.raw !== undefined ? item.raw : escapeHtml(item))).join('')
      : value?.raw !== undefined ? value.raw : escapeHtml(value);
    return out + text + string;
  }, '');
}

export function raw(text) {
  return { raw: text };
}

const numberFormat = new Intl.NumberFormat('en-GB');
const decimalFormat = new Intl.NumberFormat('en-GB', { maximumFractionDigits: 1, minimumFractionDigits: 1 });

export function formatNumber(value) {
  return value === null || value === undefined || Number.isNaN(value) ? '–' : numberFormat.format(value);
}

export function formatDecimal(value) {
  return value === null || value === undefined || !Number.isFinite(value) ? '–' : decimalFormat.format(value);
}

export function formatDate(value) {
  return value ? value.slice(0, 10) : '';
}

export function debounce(fn, wait = 350) {
  let timer;
  return (...args) => {
    clearTimeout(timer);
    timer = setTimeout(() => fn(...args), wait);
  };
}

export function errorMessage(error) {
  if (error instanceof TypeError) {
    return 'The SPARQL endpoint cannot be reached. Start the application with python serve.py and check that GraphDB is running: see README.md.';
  }
  return error.message;
}

// Minimal SPARQL syntax highlighting: strings, IRIs, variables, prefixed names, keywords, comments.
const SPARQL_TOKEN = new RegExp([
  /("(?:[^"\\]|\\.)*")/.source,
  /(<[^>\s]*>)/.source,
  /(\?\w+)/.source,
  /(\b[A-Za-z][\w-]*:[\w\-./]*|\ba\b)/.source,
  /\b(SELECT|WHERE|OPTIONAL|FILTER|NOT|EXISTS|GROUP|BY|ORDER|LIMIT|OFFSET|UNION|VALUES|BIND|AS|COUNT|DISTINCT|DESC|ASC|PREFIX|SAMPLE|GROUP_CONCAT|separator|STR|LCASE|CONTAINS|STRSTARTS|COALESCE|IF|BOUND|IN|MAX|MIN|SUM|AVG|LANG|HAVING|SERVICE)\b/.source,
  /(#[^\n]*)/.source,
].join('|'), 'g');
const TOKEN_CLASSES = ['str', 'iri', 'var', 'pname', 'kw', 'comment'];

export function highlightSparql(text) {
  let out = '';
  let last = 0;
  for (const match of text.matchAll(SPARQL_TOKEN)) {
    const group = match.slice(1).findIndex((value) => value !== undefined);
    out += escapeHtml(text.slice(last, match.index));
    out += `<span class="tok-${TOKEN_CLASSES[group]}">${escapeHtml(match[0])}</span>`;
    last = match.index + match[0].length;
  }
  return out + escapeHtml(text.slice(last));
}
