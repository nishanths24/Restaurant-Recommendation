import numpy as np
import pandas as pd
from typing import List, Dict, Any, Tuple
from sklearn.preprocessing import MultiLabelBinarizer
from sklearn.metrics.pairwise import cosine_similarity
import joblib
from pathlib import Path
from config import Config

class FeatureBuilder:
    """
    Constructs multi-hot and numeric feature representations for content-based
    recommendation and item-to-item similarity matching.
    """
    def __init__(self):
        self.mlb = MultiLabelBinarizer()
        self.cuisine_classes = []
        self.cuisine_matrix = None
        self.fitted = False

    def fit(self, df: pd.DataFrame) -> "FeatureBuilder":
        """
        Fit MultiLabelBinarizer on restaurant cuisine lists.
        """
        cuisines_series = df["cuisines_clean"].apply(
            lambda x: [c.strip() for c in str(x).split(",") if c.strip() and c.strip() != "Not Specified"]
        )
        self.cuisine_matrix = self.mlb.fit_transform(cuisines_series)
        self.cuisine_classes = list(self.mlb.classes_)
        self.fitted = True
        return self

    def save(self, filepath=None):
        """Save fitted feature builder to disk."""
        path = Path(filepath) if filepath else Config.FEATURES_PATH
        path.parent.mkdir(parents=True, exist_ok=True)
        joblib.dump({"mlb": self.mlb, "classes": self.cuisine_classes}, path)

    def load(self, filepath=None) -> "FeatureBuilder":
        """Load fitted feature builder from disk."""
        path = Path(filepath) if filepath else Config.FEATURES_PATH
        if not path.exists():
            raise FileNotFoundError(f"Feature artifact not found at {path}")
        data = joblib.load(path)
        self.mlb = data["mlb"]
        self.cuisine_classes = data["classes"]
        self.fitted = True
        return self

    def transform_cuisines(self, cuisines_list: List[str]) -> np.ndarray:
        """
        Transform a list of cuisines (or list of lists) into multi-hot vector.
        """
        if not self.fitted:
            raise ValueError("FeatureBuilder has not been fitted.")
        cleaned = [[c.strip() for c in cuisines_list if c.strip() in self.mlb.classes_]]
        return self.mlb.transform(cleaned)[0]

    def compute_restaurant_similarity(self, df: pd.DataFrame, target_id: int, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Compute item-to-item similarity between a chosen restaurant and all others.
        Used for secondary 'Similar Restaurants' feature.
        """
        if not self.fitted or self.cuisine_matrix is None:
            self.fit(df)
            
        target_idx_matches = df.index[df["restaurant_id"] == target_id].tolist()
        if not target_idx_matches:
            return []
        target_idx = target_idx_matches[0]
        
        target_vec = self.cuisine_matrix[target_idx].reshape(1, -1)
        sim_scores = cosine_similarity(target_vec, self.cuisine_matrix)[0]
        
        # Combine with price and rating proximity
        target_price = df.iloc[target_idx]["price_range"]
        target_rating = df.iloc[target_idx]["aggregate_rating"]
        
        results = []
        for idx, sim in enumerate(sim_scores):
            if idx == target_idx:
                continue
            row = df.iloc[idx]
            # Price distance penalty
            price_sim = 1.0 - (abs(row["price_range"] - target_price) / 3.0)
            # Rating distance
            rating_sim = 1.0 - (abs(row["aggregate_rating"] - target_rating) / 5.0)
            
            combined_sim = (0.60 * sim) + (0.25 * price_sim) + (0.15 * rating_sim)
            results.append({
                "restaurant_id": int(row["restaurant_id"]),
                "restaurant_name": row["restaurant_name"],
                "cuisines": row["cuisines_clean"],
                "city": row["city_clean"],
                "locality": row["locality_clean"],
                "price_range": int(row["price_range"]),
                "cost_for_two": float(row["cost_for_two"]),
                "currency": row["currency"],
                "rating": float(row["aggregate_rating"]),
                "rating_text": row["rating_text"],
                "votes": int(row["votes"]),
                "similarity_score": round(float(combined_sim * 100), 1),
            })
            
        results.sort(key=lambda x: (-x["similarity_score"], -x["rating"], x["restaurant_name"]))
        return results[:top_k]

