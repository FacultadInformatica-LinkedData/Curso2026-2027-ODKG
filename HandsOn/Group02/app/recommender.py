"""Recommendation (FR-02, FR-06) and itinerary building (FR-03).

Every tunable number is a constant at the top of this file and is documented
in README.md.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field

from catalog import Catalog, FacilityGroup, Place
from reviews import Aggregate, TAGS

INTERESTS = ("Sculpture", "Sports", "Family", "Walking", "Culture")

# FR-02: which facility names (pe:facilityName) serve each interest.
INTEREST_FACILITIES: dict[str, set[str]] = {
    "Sports": {
        "BASKETBALL COURT", "BASEBALL", "TENNIS COURT", "FOOTBALL/SOCCER COMBO FIELD",
        "GYMNASIUM", "FITNESS CENTER", "POOL", "VOLLEYBALL", "VOLLEYBALL (SAND)",
        "PICKLEBALL COURT", "TRACK", "MINI-PITCH", "ARTIFICIAL TURF", "GOLF", "SKATE PARK",
        "HANDBALL/RACQUET", "BOXING CENTER", "SPORT ROLLER COURT", "ICE SKATING",
        "CLIMBING WALL", "CRICKET FIELD", "ARCHERY RANGE", "BOCCE COURT", "HORSESHOE COURT",
        "ROWING CLUB", "BOWLING GREEN", "CROQUET", "SHUFFLEBOARD", "WHEELCHAIR ACCESSIBLE BALLFIELD",
    },
    "Family": {
        "PLAYGROUND", "SPRAY FEATURE", "WATER PLAYGROUND", "NATURAL PLAY AREA", "CAROUSEL",
        "BEACH", "DOG FRIENDLY AREA", "SLED HILL", "MODEL TRAIN DISPLAY", "GAME TABLES", "TEEN CENTER",
    },
    "Walking": {
        "GARDEN", "COMMUNITY GARDEN", "NATURE/BIRD SANCTUARY", "LAGOON", "WETLAND AREA", "BEACH",
        "PLAZA", "MOUNTAIN BIKE TRAIL", "HARBOR", "CASTING PIER", "ALFRED CALDWELL LILY POND",
        "MODEL YACHT BASIN",
    },
    "Culture": {
        "CULTURAL CENTER", "GALLERY", "CONSERVATORY", "NATURE CENTER", "BAND SHELL",
        "MODEL TRAIN DISPLAY", "SENIOR CENTER",
    },
    "Sculpture": set(),
}

# Artworks are not typed in the source data, so they match these interests.
ARTWORK_INTEREST_WEIGHT = {"Sculpture": 1.0, "Culture": 0.8, "Walking": 0.4}

# FR-06: what a tag says about an interest (+) and tags that count against a place (-).
TAG_INTERESTS: dict[str, set[str]] = {
    "family-friendly": {"Family"},
    "quiet": {"Walking", "Sculpture", "Culture"},
    "historic": {"Sculpture", "Culture"},
    "well-maintained": set(INTERESTS),
    "accessible": set(INTERESTS),
}
NEGATIVE_TAGS = {"crowded": 0.3}
RATING_WEIGHT = 0.6      # per star above / below 3
TAG_WEIGHT = 0.3         # if every review carries the tag
CONFIDENCE_PRIOR = 2     # n / (n + prior): 1 review counts 1/3, 4 reviews 2/3

# Routing
WALK_SPEED_KMH = 5.0
DETOUR_FACTOR = 1.25     # streets are longer than straight lines
DWELL_MINUTES = {"artwork": 10, "facility": 15}
DISTANCE_PENALTY = 0.5   # recommendation score lost per km
MIN_RADIUS_KM, MAX_RADIUS_KM = 1.0, 5.0

assert set(TAG_INTERESTS) | set(NEGATIVE_TAGS) == set(TAGS)


def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    r = 6371.0088
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp, dl = p2 - p1, math.radians(lon2 - lon1)
    a = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * r * math.asin(math.sqrt(a))


def walk_minutes(km: float) -> float:
    return km * DETOUR_FACTOR / WALK_SPEED_KMH * 60


def search_radius_km(budget_min: int) -> float:
    """How far it makes sense to look: half the budget spent walking out."""
    reach = (budget_min / 2) / 60 * WALK_SPEED_KMH / DETOUR_FACTOR
    return max(MIN_RADIUS_KM, min(MAX_RADIUS_KM, reach))


def interest_match(place: Place, interests: list[str]) -> tuple[float, list[str]]:
    if place.kind == "artwork":
        matched = [i for i in interests if i in ARTWORK_INTEREST_WEIGHT]
        return sum(ARTWORK_INTEREST_WEIGHT[i] for i in matched), matched
    matched = [i for i in interests if place.raw_name in INTEREST_FACILITIES[i]]
    return float(len(matched)), matched


def review_boost(agg: Aggregate | None, interests: list[str]) -> tuple[float, list[str]]:
    """FR-06: aggregated ratings and tags as a secondary ranking signal."""
    if agg is None or agg.count == 0:
        return 0.0, []
    confidence = agg.count / (agg.count + CONFIDENCE_PRIOR)
    boost = RATING_WEIGHT * (agg.average - 3) * confidence
    reasons = [f"★ {agg.average:.1f} ({agg.count} review{'s' if agg.count != 1 else ''})"]
    for tag, n in agg.tags.items():
        share = n / agg.count
        if tag in NEGATIVE_TAGS:
            boost -= NEGATIVE_TAGS[tag] * share
            reasons.append(f"tagged {tag}")
        elif TAG_INTERESTS.get(tag, set()) & set(interests):
            boost += TAG_WEIGHT * share
            reasons.append(f"tagged {tag}")
    return boost, reasons


@dataclass
class Recommendation:
    group: FacilityGroup
    distance_km: float
    score: float
    matched: list[str]
    reasons: list[str]
    aggregate: Aggregate

    @property
    def place(self) -> Place:
        return self.group.representative

    @property
    def walk_min(self) -> float:
        return walk_minutes(self.distance_km)


def _group_aggregate(group_uris: list[str], aggregates: dict[str, Aggregate]) -> Aggregate:
    return Aggregate.merge(aggregates[u] for u in group_uris if u in aggregates)


def recommend_facilities(
    catalog: Catalog,
    start: tuple[float, float],
    interests: list[str],
    budget_min: int,
    aggregates: dict[str, Aggregate],
    limit: int = 10,
) -> list[Recommendation]:
    """FR-02: facilities near the start that match the interests, best first."""
    radius = search_radius_km(budget_min)
    results = []
    for group in catalog.facility_groups:
        rep = group.representative
        match, matched = interest_match(rep, interests)
        if match <= 0:
            continue
        dist = haversine_km(start[0], start[1], rep.lat, rep.lon)
        if dist > radius:
            continue
        agg = _group_aggregate(group.uris, aggregates)
        boost, review_reasons = review_boost(agg, interests)
        score = match - DISTANCE_PENALTY * dist + boost
        reasons = [f"matches {', '.join(matched)}", f"{dist:.1f} km away (~{walk_minutes(dist):.0f} min walk)"]
        if len(group.facilities) > 1:
            reasons.append(f"{len(group.facilities)} in this park")
        results.append(Recommendation(group, dist, score, matched, reasons + review_reasons, agg))
    results.sort(key=lambda r: (-r.score, r.distance_km))
    return results[:limit]


@dataclass
class Candidate:
    place: Place
    value: float
    matched: list[str]
    reasons: list[str]
    aggregate: Aggregate
    uris: list[str]  # reviews of every facility of a group count

    @property
    def dwell(self) -> int:
        return DWELL_MINUTES[self.place.kind]


@dataclass
class Stop:
    order: int
    candidate: Candidate
    leg_km: float
    leg_min: float
    arrive_min: float
    depart_min: float

    @property
    def place(self) -> Place:
        return self.candidate.place


@dataclass
class Itinerary:
    start: tuple[float, float]
    budget_min: int
    stops: list[Stop] = field(default_factory=list)

    @property
    def total_min(self) -> float:
        return self.stops[-1].depart_min if self.stops else 0.0

    @property
    def total_km(self) -> float:
        return sum(s.leg_km for s in self.stops)


def _candidates(catalog, start, interests, budget_min, aggregates) -> list[Candidate]:
    radius = search_radius_km(budget_min)
    found = []
    sources: list[tuple[Place, list[str]]] = [(a, [a.uri]) for a in catalog.artworks.values()]
    sources += [(g.representative, g.uris) for g in catalog.facility_groups]
    for place, uris in sources:
        match, matched = interest_match(place, interests)
        if match <= 0:
            continue
        if haversine_km(start[0], start[1], place.lat, place.lon) > radius:
            continue
        agg = Aggregate.merge(aggregates[u] for u in uris if u in aggregates)
        boost, review_reasons = review_boost(agg, interests)
        value = max(0.1, match + boost)
        found.append(Candidate(place, value, matched, [f"matches {', '.join(matched)}"] + review_reasons, agg, uris))
    return found


def _leg(a: tuple[float, float], b: Place) -> float:
    return haversine_km(a[0], a[1], b.lat, b.lon)


def _path_minutes(start, route: list[Candidate]) -> float:
    total, pos = 0.0, start
    for c in route:
        total += walk_minutes(_leg(pos, c.place)) + c.dwell
        pos = (c.place.lat, c.place.lon)
    return total


def _extend(start, route: list[Candidate], pool: list[Candidate], budget: float) -> bool:
    """Greedy: keep adding the stop with the most value per minute that still fits."""
    used = {id(c) for c in route}
    used_facility_names = {c.place.raw_name for c in route if c.place.kind == "facility"}
    elapsed = _path_minutes(start, route)
    added = False
    while True:
        pos = (route[-1].place.lat, route[-1].place.lon) if route else start
        best, best_utility, best_cost = None, -1.0, 0.0
        for c in pool:
            if id(c) in used:
                continue
            if c.place.kind == "facility" and c.place.raw_name in used_facility_names:
                continue  # one basketball court per walk is enough
            cost = walk_minutes(_leg(pos, c.place)) + c.dwell
            if elapsed + cost > budget:
                continue
            utility = c.value / cost
            if utility > best_utility:
                best, best_utility, best_cost = c, utility, cost
        if best is None:
            return added
        route.append(best)
        used.add(id(best))
        if best.place.kind == "facility":
            used_facility_names.add(best.place.raw_name)
        elapsed += best_cost
        added = True


def _two_opt(start, route: list[Candidate]) -> list[Candidate]:
    """Shorten the open path (the start is fixed) by reversing segments."""
    best = route[:]
    best_len = _path_minutes(start, best)
    improved = True
    while improved:
        improved = False
        for i in range(len(best) - 1):
            for k in range(i + 1, len(best)):
                trial = best[:i] + best[i:k + 1][::-1] + best[k + 1:]
                trial_len = _path_minutes(start, trial)
                if trial_len < best_len - 1e-9:
                    best, best_len, improved = trial, trial_len, True
    return best


def build_itinerary(
    catalog: Catalog,
    start: tuple[float, float],
    interests: list[str],
    budget_min: int,
    aggregates: dict[str, Aggregate],
) -> Itinerary:
    """FR-03: a walk from the start through the best stops that fits the time budget."""
    pool = _candidates(catalog, start, interests, budget_min, aggregates)
    route: list[Candidate] = []
    for _ in range(4):  # greedy fill, shorten, refill the time 2-opt saved
        grew = _extend(start, route, pool, budget_min)
        if len(route) > 2:
            route = _two_opt(start, route)
        if not grew:
            break

    itinerary = Itinerary(start, budget_min)
    pos, clock = start, 0.0
    for order, c in enumerate(route, start=1):
        km = _leg(pos, c.place)
        leg = walk_minutes(km)
        arrive = clock + leg
        clock = arrive + c.dwell
        itinerary.stops.append(Stop(order, c, km, leg, arrive, clock))
        pos = (c.place.lat, c.place.lon)
    return itinerary
