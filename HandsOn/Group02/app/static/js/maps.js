/* Leaflet helpers shared by every page with a map.
 * A map is declared in HTML as <div data-map="ID-data"> plus a
 * <script type="application/json" id="ID-data"> holding:
 *   { center?, zoom?, picker?, start?: {lat, lon, label},
 *     route?: [[lat, lon], ...], markers: [{lat, lon, name, url, kind, number?, sub?}] }
 */
(function () {
  "use strict";

  const COLORS = {
    artwork: "#e76f51",
    facility: "#2d6a4f",
    recommendation: "#3a6ea5",
    start: "#1b4332",
  };
  const CHICAGO = [41.88, -87.66];

  function baseMap(el, center, zoom) {
    const map = L.map(el, { scrollWheelZoom: false }).setView(center || CHICAGO, zoom || 11);
    L.tileLayer("https://tile.openstreetmap.org/{z}/{x}/{y}.png", {
      maxZoom: 19,
      attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
    }).addTo(map);
    map.on("focus", () => map.scrollWheelZoom.enable());
    map.on("blur", () => map.scrollWheelZoom.disable());
    return map;
  }

  /* Leaflet measures its container once; re-measure when the layout changes
   * (hidden tabs, late CSS, window resizes) and re-fit until the user moves the map. */
  function keepSized(el, map, fit) {
    if (!window.ResizeObserver) return;
    let touched = false;
    ["mousedown", "wheel", "touchstart", "keydown"].forEach((ev) =>
      el.addEventListener(ev, () => { touched = true; }, { passive: true }));
    new ResizeObserver(() => {
      map.invalidateSize();
      if (!touched && fit) fit();
    }).observe(el);
  }

  function popup(m) {
    const box = document.createElement("div");
    const title = document.createElement(m.url ? "a" : "strong");
    title.textContent = (m.number ? m.number + ". " : "") + m.name;
    if (m.url) title.href = m.url;
    box.appendChild(title);
    if (m.sub) {
      const sub = document.createElement("div");
      sub.className = "popup-sub";
      sub.textContent = m.sub;
      box.appendChild(sub);
    }
    return box;
  }

  function markerFor(m) {
    if (m.number) {
      const icon = L.divIcon({
        className: "stop-icon",
        html: "<span>" + Number(m.number) + "</span>",
        iconSize: [28, 28],
        iconAnchor: [14, 14],
      });
      return L.marker([m.lat, m.lon], { icon: icon, zIndexOffset: 1000 });
    }
    return L.circleMarker([m.lat, m.lon], {
      radius: m.kind === "recommendation" ? 8 : 6,
      color: "#fff",
      weight: 1.5,
      fillColor: COLORS[m.kind] || COLORS.facility,
      fillOpacity: 0.9,
    });
  }

  function addMarkers(layer, markers) {
    markers.forEach((m) => markerFor(m).bindPopup(popup(m)).addTo(layer));
  }

  function render(el, data) {
    const map = baseMap(el, data.center, data.zoom);
    const bounds = [];
    if (data.route && data.route.length > 1) {
      L.polyline(data.route, { color: COLORS.start, weight: 4, opacity: 0.75, dashArray: "8 6" }).addTo(map);
      data.route.forEach((p) => bounds.push(p));
    }
    if (data.start) {
      L.circleMarker([data.start.lat, data.start.lon], {
        radius: 10, color: "#fff", weight: 3, fillColor: COLORS.start, fillOpacity: 1,
      }).bindPopup(popup({ name: "Start: " + data.start.label })).addTo(map);
      bounds.push([data.start.lat, data.start.lon]);
    }
    addMarkers(map, data.markers || []);
    (data.markers || []).forEach((m) => bounds.push([m.lat, m.lon]));
    function fit() {
      if (bounds.length === 1) map.setView(bounds[0], 16);
      else if (bounds.length > 1) map.fitBounds(bounds, { padding: [30, 30], maxZoom: 17 });
    }
    fit();
    keepSized(el, map, fit);
    el._leafletMap = map;
    el.dispatchEvent(new CustomEvent("map-ready", { detail: map }));
    return map;
  }

  /* /map page: load markers for the visible area only. */
  function liveMap(el) {
    const map = baseMap(el, CHICAGO, 12);
    keepSized(el, map, null);
    const layer = L.layerGroup().addTo(map);
    const status = document.getElementById("map-status");
    const showArt = document.getElementById("show-artworks");
    const showFac = document.getElementById("show-facilities");
    let pending = null;

    async function refresh() {
      const kinds = [];
      if (showArt.checked) kinds.push("artwork");
      if (showFac.checked && map.getZoom() >= 14) kinds.push("facility");
      layer.clearLayers();
      if (!kinds.length) {
        status.textContent = showFac.checked ? "Zoom in to see facilities." : "Nothing selected.";
        return;
      }
      const b = map.getBounds();
      const bbox = [b.getSouth(), b.getWest(), b.getNorth(), b.getEast()].map((x) => x.toFixed(5)).join(",");
      if (pending) pending.abort();
      pending = new AbortController();
      try {
        const res = await fetch(el.dataset.api + "?bbox=" + bbox + "&kinds=" + kinds.join(","), { signal: pending.signal });
        const data = await res.json();
        addMarkers(layer, data.places);
        let text = data.places.length + " places in view";
        if (data.truncated) text += " (first " + data.places.length + " only, zoom in for more)";
        if (showFac.checked && map.getZoom() < 14) text += ". Zoom in to see facilities.";
        status.textContent = text;
      } catch (err) {
        if (err.name !== "AbortError") status.textContent = "Could not load places.";
      }
    }
    map.on("moveend", refresh);
    showArt.addEventListener("change", refresh);
    showFac.addEventListener("change", refresh);
    refresh();
  }

  document.addEventListener("DOMContentLoaded", () => {
    document.querySelectorAll("[data-map]").forEach((el) => {
      const json = document.getElementById(el.dataset.map);
      if (json) render(el, JSON.parse(json.textContent));
    });
    const live = document.getElementById("explore-map");
    if (live) liveMap(live);
  });

  window.ExplorerMaps = { render: render, colors: COLORS };
})();
