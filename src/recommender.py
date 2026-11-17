import numpy as np
import pandas as pd
from typing import Dict, List, Any, Optional, Tuple
from config import Config
from src.validators import validate_and_normalize_preferences
from src.explanations import generate_explanation_tags
from src.feature_builder import FeatureBuilder

class RestaurantRecommender:
    """
    Transparent, preference-based content recommendation engine for DineMind.
    Implements two-stage filtering:
      Stage A: Strict constraints filtering
      Stage B: Multi-criteria weighted relevance scoring
    """
    def __init__(self, df: pd.DataFrame, feature_builder: Optional[FeatureBuilder] = None):
        self.df = df.copy()
        self.weights = Config.DEFAULT_WEIGHTS.copy()
        
        # Precompute individual cuisines list for faster matching
        self.df["_cuisines_set"] = self.df["cuisines_clean"].apply(
            lambda x: {c.strip().title() for c in str(x).split(",") if c.strip()}
        )
        
        # Unique values for dropdown menus
        self.available_cuisines = sorted(list({c for s in self.df["_cuisines_set"] for c in s if c != "Not Specified"}))
        self.available_cities = sorted(list(self.df["city_clean"].dropna().unique()))
        
        # Locality map per city for responsive dropdowns
        self.city_localities = {}
        for city, group in self.df.groupby("city_clean"):
            self.city_localities[city] = sorted(list(group["locality_clean"].dropna().unique()))
            
        # Optional feature builder for item-to-item similarity
        if feature_builder is None:
            self.feature_builder = FeatureBuilder().fit(self.df)
        else:
            self.feature_builder = feature_builder

    def get_filter_options(self) -> Dict[str, Any]:
        """Return dataset-driven options for the frontend preference form."""
        return {
            "cuisines": self.available_cuisines,
            "cities": self.available_cities,
            "city_localities": self.city_localities,
            "price_tiers": [
                {"value": 1, "label": "Budget ($) - Everyday affordable dining"},
                {"value": 2, "label": "Moderate ($$) - Mid-range casual dining"},
                {"value": 3, "label": "Expensive ($$$) - Upscale dining"},
                {"value": 4, "label": "Luxury ($$$$) - Fine dining & premium"},
            ],
            "rating_thresholds": [
                {"value": 4.5, "label": "4.5+ ★ (Excellent)"},
                {"value": 4.0, "label": "4.0+ ★ (Very Good)"},
                {"value": 3.5, "label": "3.5+ ★ (Good)"},
                {"value": 3.0, "label": "3.0+ ★ (Average+)"},
                {"value": 0.0, "label": "Any Rating (Include unrated)"},
            ],
            "total_restaurants": len(self.df),
            "total_cuisines": len(self.available_cuisines),
            "total_cities": len(self.available_cities),
        }

    def _apply_hard_constraints(self, df_candidates: pd.DataFrame, prefs: Dict[str, Any]) -> Tuple[pd.DataFrame, List[str]]:
        """
        Stage A: Exclude rows that violate strict user constraints.
        Returns (filtered_candidates, list_of_applied_constraints).
        """
        applied_constraints = []
        df_sub = df_candidates
        
        # 1. Location constraint
        if prefs.get("strict_location") and prefs.get("city"):
            pref_city = prefs["city"].lower()
            df_sub = df_sub[df_sub["city_clean"].str.lower() == pref_city]
            applied_constraints.append(f"City must be '{prefs['city']}'")
            
            if prefs.get("locality"):
                pref_loc = prefs["locality"].lower()
                df_sub = df_sub[df_sub["locality_clean"].str.lower() == pref_loc]
                applied_constraints.append(f"Locality must be '{prefs['locality']}'")

        # 2. Strict Budget constraint
        if prefs.get("strict_budget"):
            if prefs.get("max_cost"):
                df_sub = df_sub[df_sub["cost_for_two"] <= prefs["max_cost"]]
                applied_constraints.append(f"Cost for two must be ≤ {prefs['max_cost']}")
            elif prefs.get("price_range"):
                df_sub = df_sub[df_sub["price_range"] <= prefs["price_range"]]
                applied_constraints.append(f"Price tier must be ≤ {prefs['price_range']}")

        # 3. Strict Rating constraint
        if prefs.get("strict_rating") and prefs.get("min_rating", 0.0) > 0.0:
            df_sub = df_sub[df_sub["aggregate_rating"] >= prefs["min_rating"]]
            applied_constraints.append(f"Rating must be ≥ {prefs['min_rating']}★")
            
        # 4. Strict Delivery constraint
        if prefs.get("online_delivery") == 1:
            # If user explicitly requested delivery, we can filter or weight
            # We keep it as soft or strict based on strict flag
            pass

        return df_sub, applied_constraints

    def _calculate_relevance_scores(self, df_candidates: pd.DataFrame, prefs: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Stage B: Calculate normalized 0-100 score for each candidate restaurant.
        """
        user_cuisines = set(prefs.get("cuisines", []))
        pref_city = prefs.get("city")
        pref_locality = prefs.get("locality")
        pref_price_range = prefs.get("price_range")
        pref_max_cost = prefs.get("max_cost")
        pref_min_rating = prefs.get("min_rating", 0.0)
        pref_delivery = prefs.get("online_delivery")
        pref_table = prefs.get("table_booking")
        
        # Determine active components and weights
        active_weights = {}
        if user_cuisines:
            active_weights["cuisine"] = self.weights["cuisine"]
        if pref_city or pref_locality:
            active_weights["location"] = self.weights["location"]
        if pref_price_range is not None or pref_max_cost is not None:
            active_weights["budget"] = self.weights["budget"]
        if pref_min_rating > 0.0:
            active_weights["rating"] = self.weights["rating"]
        else:
            # Even if no min rating is requested, rating quality provides general quality signal
            active_weights["rating"] = self.weights["rating"] * 0.5
        if pref_delivery is not None or pref_table is not None:
            active_weights["features"] = self.weights["features"]
            
        sum_weights = sum(active_weights.values())
        if sum_weights <= 0:
            # Empty preference fallback: purely rating quality driven
            sum_weights = 1.0
            active_weights = {"rating": 1.0}

        results = []
        
        for idx, row in df_candidates.iterrows():
            component_scores = {}
            
            # --- 1. Cuisine Score ---
            if "cuisine" in active_weights:
                rest_cuisines = row["_cuisines_set"]
                # Case-insensitive overlap
                matched = {u for u in user_cuisines if any(u.lower() == r.lower() or u.lower() in r.lower() for r in rest_cuisines)}
                if not matched:
                    component_scores["cuisine"] = 0.0
                else:
                    coverage = len(matched) / len(user_cuisines)
                    jaccard = len(matched) / max(1, len(user_cuisines | rest_cuisines))
                    component_scores["cuisine"] = 0.75 * coverage + 0.25 * jaccard
            else:
                component_scores["cuisine"] = 0.0
                
            # --- 2. Location Score ---
            if "location" in active_weights:
                rest_city = str(row["city_clean"]).lower()
                rest_loc = str(row["locality_clean"]).lower()
                score_loc = 0.0
                if pref_city:
                    if pref_city.lower() == rest_city:
                        score_loc = 0.6
                        if pref_locality and pref_locality.lower() == rest_loc:
                            score_loc = 1.0
                        elif not pref_locality:
                            score_loc = 1.0
                    else:
                        score_loc = 0.0
                elif pref_locality:
                    score_loc = 1.0 if pref_locality.lower() in rest_loc else 0.0
                component_scores["location"] = score_loc
            else:
                component_scores["location"] = 0.0
                
            # --- 3. Budget Score ---
            if "budget" in active_weights:
                rest_price = row["price_range"]
                rest_cost = row["cost_for_two"]
                score_budget = 0.5
                if pref_max_cost is not None and pref_max_cost > 0:
                    if rest_cost <= pref_max_cost:
                        # Closer to budget from below gets high score
                        ratio = rest_cost / pref_max_cost if pref_max_cost > 0 else 1.0
                        score_budget = 0.8 + 0.2 * ratio
                    else:
                        over = rest_cost - pref_max_cost
                        score_budget = max(0.0, 1.0 - (over / pref_max_cost))
                elif pref_price_range is not None:
                    if rest_price <= pref_price_range:
                        # Exactly in preferred tier or lower
                        diff = pref_price_range - rest_price
                        score_budget = 1.0 - (diff * 0.1)
                    else:
                        diff = rest_price - pref_price_range
                        score_budget = max(0.0, 1.0 - (diff * 0.4))
                component_scores["budget"] = score_budget
            else:
                component_scores["budget"] = 0.0
                
            # --- 4. Rating Score ---
            rest_rating = row["aggregate_rating"]
            rest_votes = row["votes"]
            is_rated = row["is_rated"]
            if is_rated:
                norm_rating = max(0.0, min(1.0, (rest_rating - 1.0) / 4.0))
                popularity = min(1.0, np.log1p(rest_votes) / np.log1p(1000.0))
                base_rating_score = 0.85 * norm_rating + 0.15 * popularity
                if pref_min_rating > 0.0:
                    if rest_rating >= pref_min_rating:
                        base_rating_score = min(1.0, base_rating_score * 1.1)
                    else:
                        deficit = pref_min_rating - rest_rating
                        base_rating_score = max(0.0, base_rating_score - deficit * 0.3)
                component_scores["rating"] = base_rating_score
            else:
                # Unrated handling
                component_scores["rating"] = 0.2 if pref_min_rating > 0.0 else 0.4
                
            # --- 5. Features Score (Online Delivery / Table Booking) ---
            if "features" in active_weights:
                f_scores = []
                if pref_delivery is not None:
                    f_scores.append(1.0 if row["has_online_delivery"] == pref_delivery else 0.0)
                if pref_table is not None:
                    f_scores.append(1.0 if row["has_table_booking"] == pref_table else 0.0)
                component_scores["features"] = np.mean(f_scores) if f_scores else 0.0
            else:
                component_scores["features"] = 0.0
                
            # --- Weighted Final Score ---
            weighted_sum = sum(active_weights[comp] * component_scores[comp] for comp in active_weights)
            final_score = round((weighted_sum / sum_weights) * 100.0, 1)
            
            # Format row data for display and explanations
            row_dict = {
                "restaurant_id": int(row["restaurant_id"]),
                "restaurant_name": row["restaurant_name"],
                "cuisines_clean": row["cuisines_clean"],
                "city_clean": row["city_clean"],
                "locality_clean": row["locality_clean"],
                "locality_verbose": row["locality_verbose"],
                "address": row["address"],
                "price_range": int(row["price_range"]),
                "cost_for_two": float(row["cost_for_two"]),
                "currency": row["currency"],
                "aggregate_rating": float(row["aggregate_rating"]),
                "is_rated": int(row["is_rated"]),
                "rating_text": row["rating_text"],
                "rating_color": row["rating_color"],
                "votes": int(row["votes"]),
                "has_online_delivery": int(row["has_online_delivery"]),
                "has_table_booking": int(row["has_table_booking"]),
                "latitude": float(row["latitude"]),
                "longitude": float(row["longitude"]),
                "match_score": final_score,
                "score_details": component_scores,
            }
            row_dict["explanations"] = generate_explanation_tags(row_dict, prefs, component_scores)
            results.append(row_dict)
            
        # Deterministic sorting: match_score DESC, rating DESC, votes DESC, restaurant_name ASC
        results.sort(
            key=lambda x: (
                -x["match_score"],
                -x["aggregate_rating"],
                -x["votes"],
                x["restaurant_name"]
            )
        )
        return results

    def recommend(self, user_preferences: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute full recommendation pipeline for given user preferences.
        Returns structured dictionary with metadata, results, and constraint diagnostics.
        """
        # 1. Normalize preferences
        prefs = validate_and_normalize_preferences(
            user_preferences,
            available_cuisines=self.available_cuisines,
            available_cities=self.available_cities
        )
        
        # 2. Stage A: Apply Hard Constraints
        df_candidates, applied_constraints = self._apply_hard_constraints(self.df, prefs)
        
        total_matched_candidates = len(df_candidates)
        
        if total_matched_candidates == 0:
            return {
                "status": "no_results",
                "message": "No restaurants matched all your strict criteria. Try relaxing budget or location filters.",
                "applied_constraints": applied_constraints,
                "preferences": prefs,
                "recommendations": [],
                "total_candidates": 0,
            }
            
        # 3. Stage B: Score and Rank
        ranked = self._calculate_relevance_scores(df_candidates, prefs)
        
        top_k = prefs["top_k"]
        top_results = ranked[:top_k]
        
        return {
            "status": "success",
            "message": "Top recommendations generated successfully.",
            "applied_constraints": applied_constraints,
            "preferences": prefs,
            "recommendations": top_results,
            "total_candidates": total_matched_candidates,
            "returned_count": len(top_results),
            "is_empty_preferences": prefs.get("is_empty", False),
        }

    def get_similar_restaurants(self, restaurant_id: int, top_k: int = 5) -> List[Dict[str, Any]]:
        """Secondary feature: content-based restaurant-to-restaurant similarity."""
        return self.feature_builder.compute_restaurant_similarity(self.df, restaurant_id, top_k=top_k)
