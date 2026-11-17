import re
import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Any, Optional
from config import Config

def clean_text(val: Any) -> Optional[str]:
    """Trim text and normalize null-like placeholders to None."""
    if pd.isna(val) or val is None:
        return None
    s = str(val).strip()
    if s.lower() in ("", "nan", "null", "none", "na", "n/a"):
        return None
    return s

def clean_city(city_val: Any) -> str:
    """Standardize city names and fix encoding artifacts."""
    text = clean_text(city_val)
    if not text:
        return "Unknown"
    
    # Fix common mojibake/encoding artifacts in the dataset
    fixes = {
        "bras_lia": "Brasilia",
        "brasí_lia": "Brasilia",
        "so paulo": "Sao Paulo",
        "são paulo": "Sao Paulo",
        "secunderabad": "Hyderabad",
    }
    lowered = text.lower()
    for bad, good in fixes.items():
        if bad in lowered:
            return good
    return text.title()

def parse_cuisines(cuisines_val: Any) -> List[str]:
    """
    Parse a comma-separated cuisine string into a cleaned list of individual cuisines.
    E.g., "North Indian, Chinese" -> ["North Indian", "Chinese"]
    """
    text = clean_text(cuisines_val)
    if not text:
        return ["Not Specified"]
    
    parts = [p.strip().title() for p in text.split(",") if p.strip()]
    if not parts:
        return ["Not Specified"]
    return parts

def clean_boolean(val: Any) -> int:
    """Normalize boolean flag values (Yes/No/True/False/1/0) to 1 or 0."""
    if pd.isna(val) or val is None:
        return 0
    s = str(val).strip().lower()
    if s in ("yes", "true", "1", "y"):
        return 1
    return 0

def clean_numeric(val: Any, min_val: Optional[float] = None, max_val: Optional[float] = None, default: float = 0.0) -> float:
    """Safely convert value to float within optional bounds."""
    if pd.isna(val) or val is None:
        return default
    try:
        # Strip currency symbols, commas, spaces
        cleaned = re.sub(r"[^\d.-]", "", str(val))
        if not cleaned:
            return default
        num = float(cleaned)
        if min_val is not None and num < min_val:
            return min_val
        if max_val is not None and num > max_val:
            return max_val
        return num
    except (ValueError, TypeError):
        return default

def preprocess_dataframe(df_raw: pd.DataFrame) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """
    Execute full cleaning pipeline on the raw dataset.
    Returns (cleaned_df, stats_dict).
    Does NOT modify the input dataframe.
    """
    df = df_raw.copy()
    
    # Strip any BOM or trailing whitespace from columns
    df.columns = [c.strip().lstrip("\ufeff") for c in df.columns]
    
    initial_rows = len(df)
    
    # 1. Rename to canonical column names
    col_map = {src: can for can, src in Config.COLUMN_MAPPING.items() if src in df.columns}
    df = df.rename(columns=col_map)
    
    # 2. Drop rows without restaurant name
    df["restaurant_name"] = df["restaurant_name"].apply(clean_text)
    df = df.dropna(subset=["restaurant_name"])
    
    # 3. Clean Text Fields
    for txt_col in ["city", "locality", "locality_verbose", "address", "currency"]:
        if txt_col in df.columns:
            df[txt_col] = df[txt_col].apply(clean_text).fillna("Unknown")
            
    df["city_clean"] = df["city"].apply(clean_city)
    df["locality_clean"] = df["locality"].apply(lambda x: clean_text(x) or "Unknown")
    
    # 4. Clean Cuisines
    df["cuisines_raw"] = df["cuisines"].copy()
    df["cuisines_list"] = df["cuisines"].apply(parse_cuisines)
    # Re-assemble normalized comma-separated string for display and text matching
    df["cuisines_clean"] = df["cuisines_list"].apply(lambda lst: ", ".join(lst))
    # Pipe-separated string for easy flat CSV storage and exact token splitting
    df["cuisines_pipe"] = df["cuisines_list"].apply(lambda lst: "|".join(lst))
    
    # 5. Clean Numeric Fields
    df["cost_for_two"] = df["cost_for_two"].apply(lambda x: clean_numeric(x, min_val=0.0, default=0.0))
    df["price_range"] = df["price_range"].apply(lambda x: int(clean_numeric(x, min_val=1.0, max_val=4.0, default=1.0)))
    df["aggregate_rating"] = df["aggregate_rating"].apply(lambda x: round(clean_numeric(x, min_val=0.0, max_val=5.0, default=0.0), 1))
    df["votes"] = df["votes"].apply(lambda x: int(clean_numeric(x, min_val=0.0, default=0.0)))
    
    # Rating indicator: 0.0 means unrated in this dataset
    df["is_rated"] = (df["aggregate_rating"] > 0.0).astype(int)
    
    # 6. Clean Boolean Flags
    df["has_table_booking"] = df["has_table_booking"].apply(clean_boolean)
    df["has_online_delivery"] = df["has_online_delivery"].apply(clean_boolean)
    if "is_delivering_now" in df.columns:
        df["is_delivering_now"] = df["is_delivering_now"].apply(clean_boolean)
    else:
        df["is_delivering_now"] = 0
        
    # 7. Latitude / Longitude
    df["latitude"] = pd.to_numeric(df["latitude"], errors="coerce").fillna(0.0)
    df["longitude"] = pd.to_numeric(df["longitude"], errors="coerce").fillna(0.0)
    
    # 8. De-duplication check
    # We do NOT drop multiple branches with same name, but check exact duplicate rows if any
    duplicates_removed = initial_rows - len(df)
    
    # Re-order canonical output columns
    preferred_cols = [
        "restaurant_id",
        "restaurant_name",
        "city",
        "city_clean",
        "locality",
        "locality_clean",
        "locality_verbose",
        "address",
        "cuisines_clean",
        "cuisines_pipe",
        "cost_for_two",
        "currency",
        "price_range",
        "aggregate_rating",
        "is_rated",
        "rating_text",
        "rating_color",
        "votes",
        "has_table_booking",
        "has_online_delivery",
        "is_delivering_now",
        "latitude",
        "longitude",
    ]
    available_cols = [c for c in preferred_cols if c in df.columns]
    remaining_cols = [c for c in df.columns if c not in available_cols]
    final_df = df[available_cols + remaining_cols].copy()
    
    stats = {
        "initial_rows": initial_rows,
        "final_rows": len(final_df),
        "removed_rows": duplicates_removed,
        "unique_cuisines_count": len({c for sublist in df["cuisines_list"] for c in sublist}),
        "unique_cities_count": final_df["city_clean"].nunique(),
        "unique_localities_count": final_df["locality_clean"].nunique(),
        "rated_restaurants_count": int(final_df["is_rated"].sum()),
        "unrated_restaurants_count": int((final_df["is_rated"] == 0).sum()),
    }
    
    return final_df, stats

