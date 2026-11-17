from typing import Dict, Any, List, Optional
from config import Config

class PreferenceValidationError(Exception):
    """Raised when submitted user preferences fail validation."""
    pass

def sanitize_string(val: Any) -> Optional[str]:
    if val is None:
        return None
    s = str(val).strip()
    return s if s else None

def validate_and_normalize_preferences(raw_prefs: Dict[str, Any], available_cuisines: Optional[List[str]] = None, available_cities: Optional[List[str]] = None) -> Dict[str, Any]:
    """
    Validate and normalize incoming user preferences.
    Returns a cleaned preferences dictionary.
    """
    prefs = {}
    
    # 1. Cuisines
    raw_cuisines = raw_prefs.get("cuisines", [])
    if isinstance(raw_cuisines, str):
        if raw_cuisines.strip().lower() in ("any", "all", ""):
            cleaned_cuisines = []
        else:
            cleaned_cuisines = [c.strip().title() for c in raw_cuisines.split(",") if c.strip()]
    elif isinstance(raw_cuisines, (list, tuple)):
        cleaned_cuisines = [str(c).strip().title() for c in raw_cuisines if str(c).strip() and str(c).strip().lower() not in ("any", "all")]
    else:
        cleaned_cuisines = []
        
    prefs["cuisines"] = cleaned_cuisines
    
    # 2. Location (City and Locality)
    city = sanitize_string(raw_prefs.get("city"))
    if city and city.lower() in ("any", "all", "all cities"):
        city = None
    prefs["city"] = city
    
    locality = sanitize_string(raw_prefs.get("locality"))
    if locality and locality.lower() in ("any", "all", "all localities"):
        locality = None
    prefs["locality"] = locality
    
    # 3. Budget / Price Range
    raw_price_range = raw_prefs.get("price_range")
    if raw_price_range in (None, "", "any", "Any"):
        prefs["price_range"] = None
    else:
        try:
            val = int(raw_price_range)
            if 1 <= val <= 4:
                prefs["price_range"] = val
            else:
                prefs["price_range"] = None
        except (ValueError, TypeError):
            prefs["price_range"] = None
            
    raw_max_cost = raw_prefs.get("max_cost")
    if raw_max_cost in (None, "", "any", "Any"):
        prefs["max_cost"] = None
    else:
        try:
            cost_val = float(str(raw_max_cost).replace(",", "").strip())
            prefs["max_cost"] = max(0.0, cost_val) if cost_val > 0 else None
        except (ValueError, TypeError):
            prefs["max_cost"] = None
            
    # 4. Minimum Rating
    raw_min_rating = raw_prefs.get("min_rating")
    if raw_min_rating in (None, "", "any", "Any"):
        prefs["min_rating"] = 0.0
    else:
        try:
            r_val = float(raw_min_rating)
            prefs["min_rating"] = max(0.0, min(5.0, round(r_val, 1)))
        except (ValueError, TypeError):
            prefs["min_rating"] = 0.0
            
    # 5. Flags (Online Delivery / Table Booking)
    raw_delivery = sanitize_string(raw_prefs.get("online_delivery"))
    if raw_delivery and raw_delivery.lower() in ("yes", "1", "true"):
        prefs["online_delivery"] = 1
    elif raw_delivery and raw_delivery.lower() in ("no", "0", "false"):
        prefs["online_delivery"] = 0
    else:
        prefs["online_delivery"] = None
        
    raw_table = sanitize_string(raw_prefs.get("table_booking"))
    if raw_table and raw_table.lower() in ("yes", "1", "true"):
        prefs["table_booking"] = 1
    elif raw_table and raw_table.lower() in ("no", "0", "false"):
        prefs["table_booking"] = 0
    else:
        prefs["table_booking"] = None
        
    # 6. Strict filtering options
    def parse_bool(val: Any) -> bool:
        if isinstance(val, bool):
            return val
        if not val:
            return False
        return str(val).lower() in ("1", "true", "yes", "on")

    prefs["strict_location"] = parse_bool(raw_prefs.get("strict_location", True))
    prefs["strict_budget"] = parse_bool(raw_prefs.get("strict_budget", False))
    prefs["strict_rating"] = parse_bool(raw_prefs.get("strict_rating", False))
    
    # 7. Top K Results
    raw_top_k = raw_prefs.get("top_k", Config.TOP_K_DEFAULT)
    try:
        top_k = int(raw_top_k)
        prefs["top_k"] = max(1, min(Config.TOP_K_MAX, top_k))
    except (ValueError, TypeError):
        prefs["top_k"] = Config.TOP_K_DEFAULT
        
    # Check if preferences are completely empty
    has_any_pref = bool(
        prefs["cuisines"]
        or prefs["city"]
        or prefs["locality"]
        or prefs["price_range"]
        or prefs["max_cost"]
        or prefs["min_rating"] > 0.0
        or prefs["online_delivery"] is not None
        or prefs["table_booking"] is not None
    )
    prefs["is_empty"] = not has_any_pref
    
    return prefs
