import os
from pathlib import Path
from dotenv import load_dotenv

# Base directory
BASE_DIR = Path(__file__).resolve().parent

# Load .env if present
load_dotenv(BASE_DIR / ".env")

class Config:
    BASE_DIR = BASE_DIR
    RAW_DATA_PATH = Path(os.getenv("RAW_DATA_PATH", BASE_DIR / "data" / "raw" / "Dataset .csv"))
    PROCESSED_DATA_PATH = Path(os.getenv("PROCESSED_DATA_PATH", BASE_DIR / "data" / "processed" / "restaurants_cleaned.csv"))
    FEATURES_PATH = Path(os.getenv("FEATURES_PATH", BASE_DIR / "data" / "processed" / "feature_matrix.joblib"))
    
    # Recommendation defaults
    TOP_K_DEFAULT = int(os.getenv("TOP_K_DEFAULT", 10))
    TOP_K_MAX = int(os.getenv("TOP_K_MAX", 50))
    
    # Flask settings
    FLASK_HOST = os.getenv("FLASK_HOST", "127.0.0.1")
    FLASK_PORT = int(os.getenv("FLASK_PORT", 5000))
    FLASK_DEBUG = os.getenv("FLASK_DEBUG", "False").lower() in ("true", "1", "t")
    SECRET_KEY = os.getenv("SECRET_KEY", "dinemind-recommendation-secret-key-2026")
    
    # Default recommendation weights (normalized to 1.0)
    DEFAULT_WEIGHTS = {
        "cuisine": 0.40,
        "location": 0.20,
        "budget": 0.20,
        "rating": 0.15,
        "features": 0.05,  # delivery / table booking
    }

    # Canonical Column Mapping
    COLUMN_MAPPING = {
        "restaurant_id": "Restaurant ID",
        "restaurant_name": "Restaurant Name",
        "country_code": "Country Code",
        "city": "City",
        "locality": "Locality",
        "locality_verbose": "Locality Verbose",
        "address": "Address",
        "longitude": "Longitude",
        "latitude": "Latitude",
        "cuisines": "Cuisines",
        "cost_for_two": "Average Cost for two",
        "currency": "Currency",
        "has_table_booking": "Has Table booking",
        "has_online_delivery": "Has Online delivery",
        "is_delivering_now": "Is delivering now",
        "switch_to_order_menu": "Switch to order menu",
        "price_range": "Price range",
        "aggregate_rating": "Aggregate rating",
        "rating_color": "Rating color",
        "rating_text": "Rating text",
        "votes": "Votes",
    }

