// SPARQL endpoints the application can query.
// - proxy (default): serve.py, which serves the application and forwards every query to the
//   GraphDB repository, so the browser talks to one server only.
// - graphdb: the GraphDB repository queried directly (GraphDB must allow CORS).
// Another endpoint can be chosen with the URL parameter ?endpoint=graphdb|<full URL>.
export const ENDPOINTS = {
  proxy: `${location.origin}/sparql`,
  graphdb: 'http://localhost:7200/repositories/barcelona-heat-relief',
};

export const WIKIDATA_SPARQL = 'https://query.wikidata.org/sparql';

export function resolveEndpoint() {
  const param = new URLSearchParams(location.search).get('endpoint');
  if (param) return ENDPOINTS[param] ?? param;
  return ENDPOINTS.proxy;
}
