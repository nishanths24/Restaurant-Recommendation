from typing import Dict, List, Any

def generate_explanation_tags(row: Dict[str, Any], user_prefs: Dict[str, Any], score_details: Dict[str, float]) -> List[str]:
    """
    Generate factual, verifiable explanation tags for why a restaurant was recommended.
    Explanations are strictly grounded in the restaurant's actual attributes.
    """
    tags = []
    
    # Empty preferences scenario
    if user_prefs.get("is_empty", False):
        if row.get("aggregate_rating", 0.0) >= 4.0:
            tags.append(f"Top-rated overall ({row.get('aggregate_rating', 0.0)}★ with {row.get('votes', 0):,} votes)")
        else:
            tags.append("Popular listing from dataset")
        return tags
        
    # 1. Cuisine Match
    user_cuisines = user_prefs.get("cuisines", [])
    if user_cuisines:
        rest_cuisines_raw = str(row.get("cuisines_clean", ""))
        rest_cuisines = [c.strip().title() for c in rest_cuisines_raw.split(",") if c.strip()]
        matched = [c for c in user_cuisines if any(c.lower() in rc.lower() or rc.lower() in c.lower() for rc in rest_cuisines)]
        if matched:
            tags.append(f"Matches cuisine: {', '.join(matched)}")
            
    # 2. Location Match
    pref_locality = user_prefs.get("locality")
    pref_city = user_prefs.get("city")
    rest_locality = str(row.get("locality_clean", ""))
    rest_city = str(row.get("city_clean", ""))
    
    if pref_locality and pref_locality.lower() in rest_locality.lower():
        tags.append(f"Located in requested locality: {rest_locality}")
    elif pref_city and pref_city.lower() in rest_city.lower():
        tags.append(f"Located in {rest_city} ({rest_locality})")
        
    # 3. Budget Fit
    pref_price_range = user_prefs.get("price_range")
    pref_max_cost = user_prefs.get("max_cost")
    rest_price_range = row.get("price_range", 1)
    rest_cost = row.get("cost_for_two", 0)
    currency = row.get("currency", "")
    
    if pref_max_cost and rest_cost > 0:
        if rest_cost <= pref_max_cost:
            tags.append(f"Within budget: {currency} {int(rest_cost):,} for two (under {currency} {int(pref_max_cost):,})")
    elif pref_price_range:
        tier_names = {1: "Budget ($)", 2: "Moderate ($$)", 3: "Expensive ($$$)", 4: "Luxury ($$$$)"}
        if rest_price_range <= pref_price_range:
            tags.append(f"Fits budget tier: {tier_names.get(rest_price_range, f'Tier {rest_price_range}')}")
            
    # 4. Rating Quality
    pref_min_rating = user_prefs.get("min_rating", 0.0)
    rest_rating = row.get("aggregate_rating", 0.0)
    rating_text = row.get("rating_text", "")
    votes = row.get("votes", 0)
    
    if pref_min_rating > 0.0 and rest_rating >= pref_min_rating:
        tags.append(f"Rating {rest_rating}★ ({rating_text}) meets your ≥{pref_min_rating}★ threshold")
    elif rest_rating >= 4.0:
        tags.append(f"Highly rated: {rest_rating}★ ({rating_text}) with {votes:,} votes")
        
    # 5. Service Features
    if user_prefs.get("online_delivery") == 1 and row.get("has_online_delivery") == 1:
        tags.append("Offers online delivery")
    if user_prefs.get("table_booking") == 1 and row.get("has_table_booking") == 1:
        tags.append("Offers table booking")
        
    # Fallback if no specific condition triggered but it scored well
    if not tags:
        tags.append(f"Good overall match ({row.get('aggregate_rating', 0.0)}★ in {rest_city})")
        
    return tags
