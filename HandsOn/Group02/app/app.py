"""Personalized Chicago Park & Art Explorer (Group02, ODKG 2026-27).

Run locally:   python app.py            -> http://127.0.0.1:5050
PythonAnywhere: see README.md (the WSGI file calls create_app()).
"""
from __future__ import annotations

import logging
import math
import os
import re
from dataclasses import dataclass
from pathlib import Path

from flask import Blueprint, Flask, Response, abort, current_app, jsonify, render_template, request
from rdflib import Graph, Namespace, URIRef
from rdflib.namespace import OWL, RDF, RDFS, XSD

import queries as Q
from catalog import Catalog, local_path, pretty_name
from kg import PE, RESOURCE_BASE, KnowledgeGraph
from recommender import (
    DETOUR_FACTOR, DWELL_MINUTES, INTEREST_FACILITIES, INTERESTS, WALK_SPEED_KMH,
    build_itinerary, recommend_facilities, search_radius_km,
)
from wikidata import WikidataClient

APP_DIR = Path(__file__).resolve().parent
RDF_FILES = ("facilities-with-links.nt", "park-art-with-links.nt")
KINDS = ("ChicagoPark", "Facility", "Artwork", "Artist", "Owner")
SLUG = re.compile(r"^[A-Za-z0-9_]{1,200}$")
CHICAGO_BBOX = (41.60, -87.95, 42.10, -87.50)  # south, west, north, east
BUDGET_MIN, BUDGET_MAX, BUDGET_DEFAULT = 30, 180, 90
MAX_API_PLACES = 500

DISCLAIMER = (
    "This site provides applications using data that has been modified for use from its "
    "original source, www.cityofchicago.org, the official website of the City of Chicago. "
    "The City of Chicago makes no claims as to the content, accuracy, timeliness, or "
    "completeness of any of the data provided at this site. The data provided at this site "
    "is subject to change at any time. It is understood that the data provided at this site "
    "is being used at one’s own risk."
)

PREFIXES = {
    "pe": PE,
    "schema": "http://schema.org/",
    "rdf": str(RDF),
    "rdfs": str(RDFS),
    "owl": str(OWL),
    "xsd": str(XSD),
    "res": RESOURCE_BASE,
    "wd": "http://www.wikidata.org/entity/",
}

# Turtle exports: one prefix per class, because a prefixed name cannot contain "/".
TURTLE_PREFIXES = {
    "pe": PE, "schema": "http://schema.org/", "rdf": str(RDF), "rdfs": str(RDFS),
    "owl": str(OWL), "xsd": str(XSD), "wd": "http://www.wikidata.org/entity/",
    **{name.lower(): f"{RESOURCE_BASE}{name}/" for name in (
        "ChicagoPark", "Facility", "Artwork", "Artist", "Owner", "GeoCoordinates",
    )},
}
TURTLE_PREFIXES["park"] = TURTLE_PREFIXES.pop("chicagopark")
TURTLE_PREFIXES["geo"] = TURTLE_PREFIXES.pop("geocoordinates")

log = logging.getLogger("explorer")
bp = Blueprint("main", __name__)


@dataclass
class Services:
    kg: KnowledgeGraph
    catalog: Catalog
    wikidata: WikidataClient
    stats: dict


def svc() -> Services:
    return current_app.extensions["explorer"]


def create_app(overrides: dict | None = None) -> Flask:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
    app = Flask(__name__)
    app.config.from_mapping(
        RDF_DIR=os.environ.get("RDF_DIR", str(APP_DIR.parent / "rdf")),
        SPARQL_ENDPOINT=os.environ.get("SPARQL_ENDPOINT") or None,
        DATA_DIR=os.environ.get("DATA_DIR", str(APP_DIR / "data")),
        WIKIDATA_ENABLED=os.environ.get("WIKIDATA_ENABLED", "1") != "0",
    )
    if overrides:
        app.config.update(overrides)

    data_dir = Path(app.config["DATA_DIR"])
    data_dir.mkdir(parents=True, exist_ok=True)
    rdf_dir = Path(app.config["RDF_DIR"])
    kg = KnowledgeGraph([rdf_dir / name for name in RDF_FILES], endpoint=app.config["SPARQL_ENDPOINT"])
    catalog = Catalog.load(kg)
    stats = {
        "triples": len(kg),
        "classes": {
            row["class"]: (int(row["individuals"]), int(row["linkedIndividuals"]))
            for row in kg.select(Q.CLASS_COUNTS)
        },
        "source": kg.source,
    }
    log.info("Knowledge graph ready: %s triples, %s parks, %s facilities, %s artworks (%s)",
             stats["triples"], len(catalog.parks), len(catalog.facilities), len(catalog.artworks), kg.source)

    app.extensions["explorer"] = Services(
        kg=kg,
        catalog=catalog,
        wikidata=WikidataClient(
            data_dir / "wikidata_cache.json",
            seed_path=APP_DIR / "wikidata_seed.json",
            enabled=app.config["WIKIDATA_ENABLED"],
        ),
        stats=stats,
    )
    app.register_blueprint(bp)
    app.jinja_env.filters.update(curie=curie, local=lambda uri: local_path(uri) or uri, pretty=pretty_name)

    @app.context_processor
    def inject_globals():
        return {"DISCLAIMER": DISCLAIMER}

    @app.errorhandler(404)
    def not_found(_):
        return render_template("error.html", code=404, message="We could not find that page or resource."), 404

    return app


# --- helpers ---------------------------------------------------------------

def curie(uri) -> str:
    text = str(uri)
    for prefix, ns in PREFIXES.items():
        if text.startswith(ns) and len(text) > len(ns):
            return f"{prefix}:{text[len(ns):]}"
    return text


def turtle_response(triples) -> Response:
    graph = Graph(bind_namespaces="none")
    for prefix, ns in TURTLE_PREFIXES.items():
        graph.bind(prefix, Namespace(ns))
    for triple in triples:
        graph.add(triple)
    return Response(graph.serialize(format="turtle"), mimetype="text/turtle")


def resource_uri(kind: str, slug: str) -> URIRef:
    if kind not in KINDS or not SLUG.match(slug):
        abort(404)
    return URIRef(f"{RESOURCE_BASE}{kind}/{slug}")


def linked_data(uri: URIRef) -> dict:
    """Triples about the resource, for the 'Linked data' panel."""
    kg = svc().kg
    return {
        "uri": str(uri),
        "outgoing": kg.select(Q.RESOURCE_OUTGOING, s=uri),
        "incoming": kg.select(Q.RESOURCE_INCOMING, o=uri)[:60],
    }


def marker(place, **extra) -> dict:
    return {
        "lat": place.lat, "lon": place.lon, "name": place.name, "url": place.url,
        "kind": place.kind, **extra,
    }


def _parse_float(value: str | None) -> float | None:
    try:
        number = float(value)  # type: ignore[arg-type]
    except (TypeError, ValueError):
        return None
    return number if math.isfinite(number) else None


def parse_explore(args) -> tuple[dict, list[str]]:
    catalog = svc().catalog
    errors: list[str] = []
    form = {
        "park": args.get("park", "").strip()[:120],
        "lat": args.get("lat", "").strip()[:20],
        "lon": args.get("lon", "").strip()[:20],
        "budget": BUDGET_DEFAULT,
        "interests": [],
        "start": None,
        "start_label": None,
        "start_park": None,
    }
    try:
        form["budget"] = int(args.get("budget", BUDGET_DEFAULT))
        if not BUDGET_MIN <= form["budget"] <= BUDGET_MAX:
            raise ValueError
    except ValueError:
        errors.append(f"The time budget must be between {BUDGET_MIN} and {BUDGET_MAX} minutes.")
        form["budget"] = BUDGET_DEFAULT

    chosen = args.getlist("interests")
    if any(i not in INTERESTS for i in chosen):
        errors.append("Unknown interest selected.")
    form["interests"] = [i for i in INTERESTS if i in chosen]
    if not form["interests"]:
        errors.append("Pick at least one interest.")

    park_id = args.get("park_id", "").strip()
    if form["lat"] or form["lon"]:
        lat, lon = _parse_float(form["lat"]), _parse_float(form["lon"])
        south, west, north, east = CHICAGO_BBOX
        if lat is None or lon is None:
            errors.append("The location is not valid. Choose a park instead.")
        elif not (south <= lat <= north and west <= lon <= east):
            errors.append(
                f"Your location ({lat:.3f}, {lon:.3f}) is outside Chicago, so there is nothing to walk to. "
                "Choose a starting park instead."
            )
            form["lat"] = form["lon"] = ""
        else:
            form["start"], form["start_label"] = (lat, lon), "your start point"
    else:
        park = catalog.park_by_slug(park_id) if park_id and SLUG.match(park_id) else None
        if park is None and form["park"]:
            park = catalog.find_park(form["park"])
            if park is None:
                errors.append(f"No park called “{form['park']}”. Pick one from the list.")
        if park is not None:
            form["park"] = park.name
            form["start"], form["start_label"], form["start_park"] = park.center, park.name, park
        elif not form["park"]:
            errors.append("Choose a starting park, or use your location.")
    return form, errors


# --- pages -----------------------------------------------------------------

@bp.get("/")
def index():
    s = svc()
    form = {"park": request.args.get("park", "")[:120], "budget": BUDGET_DEFAULT, "interests": ["Sculpture", "Walking"], "lat": "", "lon": ""}
    return render_template("index.html", form=form, errors=[], **_search_context(s))


def _search_context(s: Services) -> dict:
    return {
        "parks": s.catalog.parks_sorted,
        "interests": INTERESTS,
        "budget_range": (BUDGET_MIN, BUDGET_MAX),
        "stats": s.stats,
        "counts": {
            "parks": len(s.catalog.parks), "facilities": len(s.catalog.facilities),
            "artworks": len(s.catalog.artworks),
            "linked_parks": sum(1 for p in s.catalog.parks.values() if p.wikidata),
        },
    }


@bp.get("/explore")
def explore():
    s = svc()
    form, errors = parse_explore(request.args)
    if errors:
        return render_template("index.html", form=form, errors=errors, **_search_context(s)), 400

    start, interests, budget = form["start"], form["interests"], form["budget"]
    itinerary = build_itinerary(s.catalog, start, interests, budget)
    recommendations = recommend_facilities(s.catalog, start, interests, budget)

    markers = [
        marker(stop.place, number=stop.order, sub=s.catalog.park_of(stop.place).name)
        for stop in itinerary.stops
    ]
    markers += [
        marker(rec.place, kind="recommendation", sub=f"{s.catalog.park_of(rec.place).name} · {rec.distance_km:.1f} km")
        for rec in recommendations
        if rec.place.uri not in {stop.place.uri for stop in itinerary.stops}
    ]
    map_data = {
        "start": {"lat": start[0], "lon": start[1], "label": form["start_label"]},
        "route": [list(start)] + [[st.place.lat, st.place.lon] for st in itinerary.stops],
        "markers": markers,
    }
    return render_template(
        "explore.html",
        form=form,
        itinerary=itinerary,
        recommendations=recommendations,
        catalog=s.catalog,
        radius_km=search_radius_km(budget),
        map_data=map_data,
        route_title=f"{form['start_label'][:1].upper()}{form['start_label'][1:]}: {' & '.join(interests)} walk",
        share_url=request.full_path.rstrip("?"),
    )


@bp.get("/parks")
def parks():
    catalog = svc().catalog
    query = request.args.get("q", "").strip()[:100]
    needle = query.lower()
    found = [p for p in catalog.parks_sorted if not needle or needle in p.name.lower()]
    return render_template("parks.html", parks=found, query=query, total=len(catalog.parks))


@bp.get("/map")
def full_map():
    return render_template("map.html")


@bp.get("/api/places")
def api_places():
    try:
        south, west, north, east = (float(x) for x in request.args.get("bbox", "").split(","))
    except ValueError:
        return jsonify(error="bbox must be south,west,north,east"), 400
    if not (-90 <= south <= north <= 90 and -180 <= west <= east <= 180):
        return jsonify(error="bbox out of range"), 400
    kinds = set(request.args.get("kinds", "artwork,facility").split(",")) & {"artwork", "facility"}
    catalog = svc().catalog
    places = catalog.places_in_bbox(south, west, north, east, kinds, MAX_API_PLACES)
    return jsonify(
        places=[marker(p, sub=catalog.park_of(p).name) for p in places],
        truncated=len(places) >= MAX_API_PLACES,
    )


@bp.get("/about")
def about():
    return render_template(
        "about.html",
        queries=Q.QUERIES,
        stats=svc().stats,
        settings={
            "walk_speed": WALK_SPEED_KMH, "detour": DETOUR_FACTOR, "dwell": DWELL_MINUTES,
            "interest_facilities": {k: sorted(v) for k, v in INTEREST_FACILITIES.items() if v},
        },
    )


# --- resource pages (one per class of the ontology) ------------------------

@bp.get("/resource/<kind>/<slug>")
def resource(kind: str, slug: str):
    uri = resource_uri(kind, slug)
    if request.args.get("format") == "ttl":
        graph = svc().kg.describe(uri)
        if len(graph) == 0:
            abort(404)
        return turtle_response(graph)
    return {
        "ChicagoPark": park_page,
        "Facility": place_page,
        "Artwork": place_page,
        "Artist": agent_page,
        "Owner": agent_page,
    }[kind](kind, uri)


def park_page(kind: str, uri: URIRef):
    s = svc()
    rows = s.kg.select(Q.PARK_DETAIL, park=uri)
    if not rows:
        abort(404)
    park = s.catalog.parks[str(uri)]
    facilities = s.kg.select(Q.PARK_FACILITIES, park=uri)
    artworks: dict[str, dict] = {}
    for row in s.kg.select(Q.PARK_ARTWORKS, park=uri):
        art = artworks.setdefault(row["artwork"], {**row, "artists": []})
        if row["artistName"] and row["artistName"] not in art["artists"]:
            art["artists"].append(row["artistName"])
    artworks = list(artworks.values())
    grouped: dict[str, list[dict]] = {}
    for f in facilities:
        grouped.setdefault(f["name"], []).append(f)
    markers = [
        {"lat": a["lat"], "lon": a["lon"], "name": a["name"], "url": local_path(a["artwork"]), "kind": "artwork", "sub": ", ".join(a["artists"])}
        for a in artworks
    ] + [
        {"lat": f["lat"], "lon": f["lon"], "name": pretty_name(f["name"]), "url": local_path(f["facility"]), "kind": "facility", "sub": f["type"].title()}
        for f in facilities
    ]
    return render_template(
        "park.html",
        park=park,
        detail=rows[0],
        facility_groups=sorted(grouped.items()),
        artworks=artworks,
        wikidata=s.wikidata.entity(rows[0]["wikidata"]),
        map_data={"markers": markers},
        linked=linked_data(uri),
    )


def place_page(kind: str, uri: URIRef):
    s = svc()
    query = Q.FACILITY_DETAIL if kind == "Facility" else Q.ARTWORK_DETAIL
    rows = s.kg.select(query, **{kind.lower(): uri})
    if not rows:
        abort(404)
    detail = rows[0]
    artists, owners = [], []
    if kind == "Artwork":
        artists = s.kg.select(Q.ARTWORK_ARTISTS, artwork=uri)
        for artist in artists:
            artist["wd"] = s.wikidata.entity(artist["wikidata"])
        owners = s.kg.select(Q.ARTWORK_OWNERS, artwork=uri)
    place = s.catalog.place(str(uri))
    siblings = []
    if kind == "Facility" and place:
        siblings = [f for f in s.catalog.park_of(place).facilities if f.raw_name == place.raw_name and f.uri != place.uri]
    name = pretty_name(detail["name"])
    return render_template(
        "place.html",
        kind=kind,
        uri=str(uri),
        name=name,
        detail=detail,
        artists=artists,
        owners=owners,
        siblings=siblings,
        park_wikidata=s.wikidata.entity(detail["parkWikidata"]),
        map_data={"markers": [{"lat": detail["lat"], "lon": detail["lon"], "name": name, "url": None, "kind": kind.lower()}]},
        linked=linked_data(uri),
    )


def agent_page(kind: str, uri: URIRef):
    s = svc()
    if kind == "Artist":
        rows = s.kg.select(Q.ARTIST_DETAIL, artist=uri)
        works = s.kg.select(Q.ARTIST_WORKS, artist=uri)
    else:
        rows = s.kg.select(Q.OWNER_DETAIL, owner=uri)
        works = s.kg.select(Q.OWNER_WORKS, owner=uri)
    if not rows:
        abort(404)
    detail = rows[0]
    markers = [
        {"lat": w["lat"], "lon": w["lon"], "name": w["name"], "url": local_path(w["artwork"]), "kind": "artwork", "sub": pretty_name(w["parkName"])}
        for w in works
    ]
    return render_template(
        "agent.html",
        kind=kind,
        detail=detail,
        works=works,
        wikidata=s.wikidata.entity(detail.get("wikidata")),
        map_data={"markers": markers},
        linked=linked_data(uri),
    )


if __name__ == "__main__":
    create_app().run(
        host=os.environ.get("HOST", "127.0.0.1"),
        port=int(os.environ.get("PORT", "5050")),
        debug=os.environ.get("FLASK_DEBUG") == "1",
    )
