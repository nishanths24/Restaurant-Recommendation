import pytest
import pandas as pd
from src.preprocessing import preprocess_dataframe
from src.recommender import RestaurantRecommender

@pytest.fixture
def recommender(sample_raw_dataframe):
    df_clean, _ = preprocess_dataframe(sample_raw_dataframe)
    return RestaurantRecommender(df_clean)

def test_cuisine_only_preference(recommender):
    prefs = {"cuisines": ["Italian"]}
    res = recommender.recommend(prefs)
    assert res["status"] == "success"
    assert len(res["recommendations"]) > 0
    top = res["recommendations"][0]
    assert "Pizza Roma" in top["restaurant_name"]
    assert any("Italian" in tag for tag in top["explanations"])

def test_location_only_preference(recommender):
    prefs = {"city": "New Delhi", "locality": "Connaught Place", "strict_location": True}
    res = recommender.recommend(prefs)
    assert res["status"] == "success"
    assert len(res["recommendations"]) > 0
    top = res["recommendations"][0]
    assert top["restaurant_name"] == "Spice Villa"
    assert top["city_clean"] == "New Delhi"
    assert top["locality_clean"] == "Connaught Place"

def test_budget_only_preference(recommender):
    prefs = {"price_range": 2, "strict_budget": True}
    res = recommender.recommend(prefs)
    assert res["status"] == "success"
    # Pizza Roma is tier 3 so it must be excluded under strict budget
    names = [r["restaurant_name"] for r in res["recommendations"]]
    assert "Pizza Roma" not in names
    for r in res["recommendations"]:
        assert r["price_range"] <= 2

def test_minimum_rating_preference(recommender):
    prefs = {"min_rating": 4.2, "strict_rating": True}
    res = recommender.recommend(prefs)
    assert res["status"] == "success"
    for r in res["recommendations"]:
        assert r["aggregate_rating"] >= 4.2

def test_combined_preference(recommender):
    prefs = {
        "cuisines": ["North Indian"],
        "city": "New Delhi",
        "price_range": 2,
        "min_rating": 4.0,
        "strict_location": True,
        "strict_budget": True,
    }
    res = recommender.recommend(prefs)
    assert res["status"] == "success"
    assert len(res["recommendations"]) == 1
    top = res["recommendations"][0]
    assert top["restaurant_name"] == "Spice Villa"
    assert top["match_score"] > 85.0

def test_empty_preferences_returns_top_rated(recommender):
    prefs = {}
    res = recommender.recommend(prefs)
    assert res["status"] == "success"
    assert res["is_empty_preferences"] is True
    assert len(res["recommendations"]) > 0
    # Highest rated first
    assert res["recommendations"][0]["aggregate_rating"] >= res["recommendations"][-1]["aggregate_rating"]

def test_no_matching_restaurants_diagnostics(recommender):
    prefs = {
        "city": "NonExistentCity",
        "strict_location": True
    }
    res = recommender.recommend(prefs)
    assert res["status"] == "no_results"
    assert len(res["recommendations"]) == 0
    assert any("NonExistentCity" in c for c in res["applied_constraints"])

def test_score_ordering_sanity(recommender):
    prefs = {"cuisines": ["Italian", "North Indian"]}
    res = recommender.recommend(prefs)
    scores = [r["match_score"] for r in res["recommendations"]]
    # Non-increasing order
    for i in range(len(scores) - 1):
        assert scores[i] >= scores[i+1]

def test_item_similarity(recommender):
    # Restaurant ID 101 is Spice Villa (North Indian)
    similars = recommender.get_similar_restaurants(101, top_k=2)
    assert isinstance(similars, list)
    assert len(similars) <= 2

