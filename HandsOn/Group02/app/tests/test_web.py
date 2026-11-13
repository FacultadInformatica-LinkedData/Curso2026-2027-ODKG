ARTWORK = "/resource/Artwork/Indian_Boundary_River_Suite"


def test_home(client):
    page = client.get("/")
    assert page.status_code == 200
    assert b"Generate Explorer Itinerary" in page.data
    assert b"one\xe2\x80\x99s own risk" in page.data  # mandatory disclaimer


def test_explore_demo(client):
    page = client.get("/explore?park=Lincoln+(Abraham)&budget=90&interests=Sculpture&interests=Walking")
    assert page.status_code == 200
    assert b"stop-number" in page.data


def test_explore_from_coordinates(client):
    page = client.get("/explore?lat=41.92&lon=-87.64&budget=60&interests=Family")
    assert page.status_code == 200 and b"Your start point" in page.data


def test_explore_validation(client):
    assert client.get("/explore?park=Lincoln+(Abraham)&budget=999&interests=Walking").status_code == 400
    assert client.get("/explore?park=Lincoln+(Abraham)&budget=90").status_code == 400
    assert client.get("/explore?park=Lincoln+(Abraham)&budget=90&interests=Hacking").status_code == 400
    madrid = client.get("/explore?lat=40.4168&lon=-3.7038&budget=90&interests=Walking")
    assert madrid.status_code == 400 and b"outside Chicago" in madrid.data


def test_resource_pages(client):
    for path in [
        "/resource/ChicagoPark/Lincoln_Abraham",
        "/resource/Facility/Hamilton_Alexander_Cultural_Center",
        ARTWORK,
        "/resource/Artist/Henry_Moore",
        "/resource/Owner/Chicago_Park_District",
        "/parks", "/parks?q=lincoln", "/map", "/about",
    ]:
        assert client.get(path).status_code == 200, path


def test_unknown_resources_404(client):
    assert client.get("/resource/Artwork/Does_Not_Exist").status_code == 404
    assert client.get("/resource/Nope/Lincoln_Abraham").status_code == 404
    assert client.get("/resource/Artwork/bad..slug").status_code == 404


def test_turtle_export(client):
    res = client.get(ARTWORK + "?format=ttl")
    assert res.status_code == 200
    assert res.mimetype == "text/turtle"
    assert b"pe:artworkName" in res.data
    assert b"artwork:Indian_Boundary_River_Suite" in res.data and b"schema:geo" in res.data


def test_api_places(client):
    res = client.get("/api/places?bbox=41.90,-87.66,41.95,-87.62&kinds=artwork")
    assert res.status_code == 200
    places = res.get_json()["places"]
    assert places and all(p["kind"] == "artwork" for p in places)
    assert client.get("/api/places?bbox=oops").status_code == 400


def test_no_reviews(client):
    """Reviews were removed: no form on the page, no review routes."""
    page = client.get(ARTWORK)
    assert page.status_code == 200
    assert b"<form" not in page.data and b"review" not in page.data.lower()
    for url in ("/reviews.nt", "/reviews.ttl", "/uploads/x.png"):
        assert client.get(url).status_code == 404
    assert client.post(ARTWORK + "/reviews", data={"rating": "5"}).status_code in (404, 405)
