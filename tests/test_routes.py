import pytest
from app import create_app
from config import Config

@pytest.fixture
def client():
    app = create_app()
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client

def test_health_endpoint(client):
    res = client.get("/health")
    assert res.status_code == 200
    data = res.get_json()
    assert data["status"] == "healthy"
    assert data["total_restaurants"] > 0

def test_index_page(client):
    res = client.get("/")
    assert res.status_code == 200
    assert b"DineMind" in res.data
    assert b"Preferred Cuisines" in res.data
    assert b"Destination & Locality" in res.data

def test_about_page(client):
    res = client.get("/about")
    assert res.status_code == 200
    assert b"Recommendation Methodology" in res.data
    assert b"Cognifyz Technologies" in res.data

def test_recommend_endpoint_valid_cuisine(client):
    form_data = {
        "cuisines": "North Indian",
        "city": "New Delhi",
        "price_range": "2",
        "min_rating": "3.5",
        "top_k": "5",
        "strict_location": "true",
    }
    res = client.post("/recommend", data=form_data)
    assert res.status_code == 200
    assert b"Recommended Dining Options" in res.data
    assert b"North Indian" in res.data
    assert b"WHY RECOMMENDED" in res.data

def test_recommend_endpoint_empty_preferences(client):
    res = client.post("/recommend", data={})
    assert res.status_code == 200
    assert b"Recommended Dining Options" in res.data
    assert b"General Top Rated" in res.data

def test_recommend_endpoint_no_matches(client):
    form_data = {
        "city": "NonExistentCity12345",
        "strict_location": "true",
    }
    res = client.post("/recommend", data=form_data)
    assert res.status_code == 200
    assert b"No Matching Restaurants Found" in res.data

def test_similar_restaurant_endpoint(client):
    # Fetch first valid restaurant id from health or known dataset
    res = client.get("/similar/6317637")  # Le Petit Souffle
    assert res.status_code in (200, 404)
    if res.status_code == 200:
        assert b"Similar" in res.data

def test_similar_restaurant_not_found(client):
    res = client.get("/similar/999999999")
    assert res.status_code == 404
    assert b"Restaurant Not Found" in res.data

def test_404_error_handler(client):
    res = client.get("/non-existent-route-xyz")
    assert res.status_code == 404
    assert b"Page Not Found" in res.data
