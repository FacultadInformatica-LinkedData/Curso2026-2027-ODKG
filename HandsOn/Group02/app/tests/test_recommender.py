import pytest

from recommender import (
    build_itinerary, haversine_km, recommend_facilities, review_boost, walk_minutes,
)
from reviews import Aggregate


def test_haversine_known_distance():
    # Chicago Cultural Center to Lincoln Park Zoo is about 4.4 km
    assert haversine_km(41.8837, -87.6249, 41.9211, -87.6340) == pytest.approx(4.22, abs=0.15)
    assert haversine_km(41.9, -87.6, 41.9, -87.6) == 0


def test_walk_minutes():
    assert walk_minutes(5 / 1.25) == pytest.approx(60)


@pytest.mark.parametrize("budget", [30, 60, 90, 180])
@pytest.mark.parametrize("interests", [["Sculpture", "Walking"], ["Sports", "Family"], ["Culture"]])
def test_itinerary_fits_budget(services, budget, interests):
    lincoln = services.catalog.find_park("Lincoln (Abraham)")
    itinerary = build_itinerary(services.catalog, lincoln.center, interests, budget, {})
    assert itinerary.stops, "expected at least one stop near Lincoln Park"
    assert itinerary.total_min <= budget
    times = [s.arrive_min for s in itinerary.stops]
    assert times == sorted(times)
    uris = [s.place.uri for s in itinerary.stops]
    assert len(uris) == len(set(uris))


def test_demo_scenario(services):
    """90 minutes, Sculpture + Walking, starting at Lincoln Park: an art walk."""
    lincoln = services.catalog.find_park("Lincoln (Abraham)")
    itinerary = build_itinerary(services.catalog, lincoln.center, ["Sculpture", "Walking"], 90, {})
    assert len(itinerary.stops) >= 4
    assert any(s.place.kind == "artwork" for s in itinerary.stops)


def test_recommendations_match_interests(services):
    lincoln = services.catalog.find_park("Lincoln (Abraham)")
    recs = recommend_facilities(services.catalog, lincoln.center, ["Family"], 90, {})
    assert recs
    assert all("Family" in r.matched for r in recs)
    assert [r.score for r in recs] == sorted((r.score for r in recs), reverse=True)


def test_review_boost():
    good = Aggregate(count=4, rating_sum=20)
    good.tags.update({"family-friendly": 4})
    bad = Aggregate(count=4, rating_sum=4)
    bad.tags.update({"crowded": 4})
    assert review_boost(good, ["Family"])[0] > 0
    assert review_boost(bad, ["Family"])[0] < 0
    assert review_boost(None, ["Family"])[0] == 0


def test_reviews_change_ranking(services):
    """FR-06: a well-reviewed facility moves up the recommendations."""
    lincoln = services.catalog.find_park("Lincoln (Abraham)")
    before = recommend_facilities(services.catalog, lincoln.center, ["Family"], 90, {})
    last = before[-1]
    praise = Aggregate(count=10, rating_sum=50)
    praise.tags.update({"family-friendly": 10})
    after = recommend_facilities(services.catalog, lincoln.center, ["Family"], 90, {last.place.uri: praise})
    rank_before = [r.place.uri for r in before].index(last.place.uri)
    rank_after = [r.place.uri for r in after].index(last.place.uri)
    assert rank_after < rank_before
