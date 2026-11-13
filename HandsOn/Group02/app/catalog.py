"""In-memory catalogue of parks, facilities and artworks.

Built once at start-up from the SPARQL queries in queries.py, so the
recommendation and routing code (which compares every candidate with every
other) works on plain Python objects instead of querying per comparison.
"""
from __future__ import annotations

import re
from collections import defaultdict
from dataclasses import dataclass, field
from statistics import mean

from kg import RESOURCE_BASE, KnowledgeGraph
import queries as Q


def pretty_name(raw: str) -> str:
    """'HAMILTON (ALEXANDER)' -> 'Hamilton (Alexander)'; mixed-case text is kept."""
    if raw != raw.upper():
        return raw
    text = raw.title()
    # .title() capitalises after apostrophes: "O'Hallaren" is right, "Mary'S" is not.
    return re.sub(r"'S\b", "'s", text)


def local_path(uri: str) -> str | None:
    """Path of a resource page in this app, or None for external URIs."""
    if uri and uri.startswith(RESOURCE_BASE):
        return "/resource/" + uri[len(RESOURCE_BASE):]
    return None


@dataclass
class Place:
    uri: str
    kind: str  # "facility" | "artwork"
    raw_name: str
    lat: float
    lon: float
    park_uri: str
    facility_type: str | None = None
    official_name: str | None = None
    artists: list[tuple[str, str]] = field(default_factory=list)  # (uri, name)

    @property
    def name(self) -> str:
        return pretty_name(self.raw_name)

    @property
    def url(self) -> str:
        return local_path(self.uri) or self.uri


@dataclass
class Park:
    uri: str
    raw_name: str
    number: int | None
    wikidata: str | None
    facilities: list[Place] = field(default_factory=list)
    artworks: list[Place] = field(default_factory=list)

    @property
    def name(self) -> str:
        return pretty_name(self.raw_name)

    @property
    def slug(self) -> str:
        return self.uri.rsplit("/", 1)[-1]

    @property
    def url(self) -> str:
        return local_path(self.uri) or self.uri

    @property
    def places(self) -> list[Place]:
        return self.facilities + self.artworks

    @property
    def center(self) -> tuple[float, float] | None:
        pts = self.places
        if not pts:
            return None
        return mean(p.lat for p in pts), mean(p.lon for p in pts)


@dataclass
class FacilityGroup:
    """All facilities with the same name in the same park (e.g. 4 tennis courts)."""

    park: Park
    raw_name: str
    facilities: list[Place]

    @property
    def representative(self) -> Place:
        return self.facilities[0]

    @property
    def uris(self) -> list[str]:
        return [f.uri for f in self.facilities]


class Catalog:
    def __init__(self, parks: dict[str, Park], facilities: dict[str, Place], artworks: dict[str, Place]):
        self.parks = parks
        self.facilities = facilities
        self.artworks = artworks
        self.parks_sorted = sorted(parks.values(), key=lambda p: p.name.lower())
        groups: dict[tuple[str, str], list[Place]] = defaultdict(list)
        for facility in facilities.values():
            groups[(facility.park_uri, facility.raw_name)].append(facility)
        self.facility_groups = [
            FacilityGroup(parks[park_uri], name, sorted(items, key=lambda f: f.uri))
            for (park_uri, name), items in groups.items()
        ]

    @classmethod
    def load(cls, kg: KnowledgeGraph) -> "Catalog":
        parks: dict[str, Park] = {}
        for row in kg.select(Q.ALL_PARKS):
            park = parks.get(row["park"])
            if park is None:
                number = row["number"]
                parks[row["park"]] = Park(row["park"], row["name"], int(number) if number is not None else None, row["wikidata"])
            elif row["wikidata"] and not park.wikidata:
                park.wikidata = row["wikidata"]

        facilities: dict[str, Place] = {}
        for row in kg.select(Q.ALL_FACILITIES):
            place = Place(row["facility"], "facility", row["name"], row["lat"], row["lon"], row["park"], facility_type=row["type"])
            facilities[place.uri] = place

        artworks: dict[str, Place] = {}
        for row in kg.select(Q.ALL_ARTWORKS):
            place = Place(row["artwork"], "artwork", row["name"], row["lat"], row["lon"], row["park"], official_name=row["official"])
            artworks[place.uri] = place
        for row in kg.select(Q.ARTWORK_CREATORS):
            artwork = artworks.get(row["artwork"])
            if artwork and (row["artist"], row["artistName"]) not in artwork.artists:
                artwork.artists.append((row["artist"], row["artistName"]))

        for place in list(facilities.values()) + list(artworks.values()):
            park = parks.get(place.park_uri)
            if park is None:
                continue
            (park.facilities if place.kind == "facility" else park.artworks).append(place)
        return cls(parks, facilities, artworks)

    def place(self, uri: str) -> Place | None:
        return self.facilities.get(uri) or self.artworks.get(uri)

    def park_of(self, place: Place) -> Park:
        return self.parks[place.park_uri]

    def park_by_slug(self, slug: str) -> Park | None:
        return self.parks.get(RESOURCE_BASE + "ChicagoPark/" + slug)

    def find_park(self, text: str) -> Park | None:
        """Match what the user typed: exact (pretty or raw) name, then a unique substring."""
        needle = " ".join(text.split()).lower()
        if not needle:
            return None
        for park in self.parks_sorted:
            if needle in (park.name.lower(), park.raw_name.lower(), park.slug.lower()):
                return park
        hits = [p for p in self.parks_sorted if needle in p.name.lower()]
        return hits[0] if len(hits) == 1 else None

    def places_in_bbox(self, south: float, west: float, north: float, east: float, kinds: set[str], limit: int) -> list[Place]:
        pools = []
        if "artwork" in kinds:
            pools.append(self.artworks.values())
        if "facility" in kinds:
            pools.append(self.facilities.values())
        found: list[Place] = []
        for pool in pools:
            for place in pool:
                if south <= place.lat <= north and west <= place.lon <= east:
                    found.append(place)
                    if len(found) >= limit:
                        return found
        return found
