/* Page behaviour: search form (FR-01), saved routes (FR-04), small helpers. */
(function () {
  "use strict";

  const STORAGE_KEY = "pe-saved-routes";
  const CHICAGO_BBOX = { south: 41.6, west: -87.95, north: 42.1, east: -87.5 };

  function loadRoutes() {
    try {
      return JSON.parse(localStorage.getItem(STORAGE_KEY)) || [];
    } catch (e) {
      return [];
    }
  }

  function saveRoutes(routes) {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(routes.slice(0, 20)));
  }

  /* --- search form: park name, map click or geolocation ------------------ */
  function setupSearch() {
    const form = document.getElementById("search-form");
    if (!form) return;
    const park = document.getElementById("park");
    const lat = document.getElementById("lat");
    const lon = document.getElementById("lon");
    const info = document.getElementById("start-point");
    const infoText = document.getElementById("start-point-text");
    const budget = document.getElementById("budget");
    const budgetOut = document.getElementById("budget-out");
    const mapEl = document.getElementById("pick-map");
    let pin = null;

    budget.addEventListener("input", () => { budgetOut.textContent = budget.value; });

    function inChicago(la, lo) {
      return la >= CHICAGO_BBOX.south && la <= CHICAGO_BBOX.north && lo >= CHICAGO_BBOX.west && lo <= CHICAGO_BBOX.east;
    }

    function setPoint(la, lo, label) {
      lat.value = la.toFixed(6);
      lon.value = lo.toFixed(6);
      park.value = "";
      infoText.textContent = label + " (" + la.toFixed(4) + ", " + lo.toFixed(4) + ")";
      info.hidden = false;
      const map = mapEl && mapEl._leafletMap;
      if (map) {
        if (pin) pin.setLatLng([la, lo]);
        else pin = L.marker([la, lo]).addTo(map);
        map.setView([la, lo], Math.max(map.getZoom(), 14));
      }
    }

    function clearPoint() {
      lat.value = "";
      lon.value = "";
      info.hidden = true;
      if (pin) { pin.remove(); pin = null; }
    }

    park.addEventListener("input", () => { if (park.value) clearPoint(); });
    document.getElementById("clear-start").addEventListener("click", clearPoint);

    if (mapEl && mapEl._leafletMap) {
      mapEl._leafletMap.on("click", (e) => {
        if (inChicago(e.latlng.lat, e.latlng.lng)) setPoint(e.latlng.lat, e.latlng.lng, "the point you picked");
        else alert("Please pick a point inside Chicago.");
      });
    }

    document.getElementById("locate").addEventListener("click", () => {
      if (!navigator.geolocation) {
        alert("Your browser cannot share its location. Pick a park or click the map instead.");
        return;
      }
      navigator.geolocation.getCurrentPosition(
        (pos) => {
          const la = pos.coords.latitude, lo = pos.coords.longitude;
          if (inChicago(la, lo)) setPoint(la, lo, "your location");
          else alert("You seem to be outside Chicago. Pick a park or click the map instead.");
        },
        () => alert("Could not get your location. Pick a park or click the map instead."),
        { enableHighAccuracy: true, timeout: 10000 }
      );
    });

    if (lat.value && lon.value) setPoint(parseFloat(lat.value), parseFloat(lon.value), "the point you picked");
  }

  /* --- saved routes (localStorage) --------------------------------------- */
  function setupSaved() {
    const save = document.getElementById("save-route");
    if (save) {
      const already = () => loadRoutes().some((r) => r.url === save.dataset.url);
      if (already()) save.textContent = "★ Saved";
      save.addEventListener("click", () => {
        const routes = loadRoutes().filter((r) => r.url !== save.dataset.url);
        routes.unshift({ title: save.dataset.title, url: save.dataset.url, saved: new Date().toISOString().slice(0, 10) });
        saveRoutes(routes);
        save.textContent = "★ Saved";
      });
    }

    const copy = document.getElementById("copy-link");
    if (copy) {
      copy.addEventListener("click", async () => {
        const url = new URL(copy.dataset.url, window.location.origin).href;
        try {
          await navigator.clipboard.writeText(url);
          copy.textContent = "Link copied";
        } catch (e) {
          window.prompt("Copy this link:", url);
        }
      });
    }

    const section = document.getElementById("saved-routes");
    if (!section) return;
    const list = section.querySelector(".saved-list");
    function draw() {
      const routes = loadRoutes();
      section.hidden = routes.length === 0;
      list.replaceChildren();
      routes.forEach((r, i) => {
        const li = document.createElement("li");
        const a = document.createElement("a");
        a.href = r.url.startsWith("/") ? r.url : "#";
        a.textContent = r.title;
        const meta = document.createElement("span");
        meta.className = "muted";
        meta.textContent = " saved " + r.saved + " ";
        const del = document.createElement("button");
        del.type = "button";
        del.className = "link-button";
        del.textContent = "remove";
        del.addEventListener("click", () => {
          const all = loadRoutes();
          all.splice(i, 1);
          saveRoutes(all);
          draw();
        });
        li.append(a, meta, del);
        list.appendChild(li);
      });
    }
    draw();
  }

  /* Highlight the map marker of a stop when its card is hovered. */
  function setupStops() {
    const mapEl = document.getElementById("route-map");
    if (!mapEl || !mapEl._leafletMap) return;
    const map = mapEl._leafletMap;
    const markers = {};
    map.eachLayer((layer) => {
      const el = layer.getElement && layer.getElement();
      if (layer instanceof L.Marker && el && el.classList.contains("stop-icon")) {
        markers[el.textContent.trim()] = layer;
      }
    });
    document.querySelectorAll(".stop[data-stop]").forEach((card) => {
      card.addEventListener("click", (e) => {
        if (e.target.closest("a")) return;
        const m = markers[card.dataset.stop];
        if (m) { map.setView(m.getLatLng(), Math.max(map.getZoom(), 16)); m.openPopup(); }
      });
    });
  }

  document.addEventListener("DOMContentLoaded", () => {
    // maps.js registers its DOMContentLoaded listener first, so the maps exist here.
    setupSearch();
    setupSaved();
    setupStops();
  });
})();
