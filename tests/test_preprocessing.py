import pytest
import pandas as pd
from src.preprocessing import (
    clean_text,
    clean_city,
    parse_cuisines,
    clean_boolean,
    clean_numeric,
    preprocess_dataframe,
)

def test_clean_text():
    assert clean_text("  Hello World  ") == "Hello World"
    assert clean_text("") is None
    assert clean_text("null") is None
    assert clean_text("N/A") is None
    assert clean_text("NAN") is None
    assert clean_text(None) is None

def test_clean_city():
    assert clean_city("new delhi") == "New Delhi"
    assert clean_city("Bras_lia") == "Brasilia"
    assert clean_city("so paulo") == "Sao Paulo"
    assert clean_city("") == "Unknown"

def test_parse_cuisines():
    assert parse_cuisines("North Indian, Chinese, Italian") == ["North Indian", "Chinese", "Italian"]
    assert parse_cuisines(None) == ["Not Specified"]
    assert parse_cuisines("   ") == ["Not Specified"]
    assert parse_cuisines("japanese") == ["Japanese"]

def test_clean_boolean():
    assert clean_boolean("Yes") == 1
    assert clean_boolean("yes") == 1
    assert clean_boolean(True) == 1
    assert clean_boolean("No") == 0
    assert clean_boolean(None) == 0
    assert clean_boolean("other") == 0

def test_clean_numeric():
    assert clean_numeric("1,200") == 1200.0
    assert clean_numeric("$45.50") == 45.50
    assert clean_numeric("invalid", default=0.0) == 0.0
    assert clean_numeric(-10, min_val=0.0) == 0.0
    assert clean_numeric(99, max_val=4.0) == 4.0

def test_preprocess_dataframe(sample_raw_dataframe):
    df_clean, stats = preprocess_dataframe(sample_raw_dataframe)
    
    # 5th row had None for restaurant name and should be dropped
    assert len(df_clean) == 4
    assert stats["removed_rows"] == 1
    
    # Check canonical column presence
    assert "restaurant_name" in df_clean.columns
    assert "cuisines_clean" in df_clean.columns
    assert "cuisines_pipe" in df_clean.columns
    assert "price_range" in df_clean.columns
    assert "aggregate_rating" in df_clean.columns
    assert "is_rated" in df_clean.columns
    
    # Check invalid numeric handling in 4th row (Taco Fiesta)
    taco_row = df_clean[df_clean["restaurant_name"] == "Taco Fiesta"].iloc[0]
    assert taco_row["cost_for_two"] == 0.0
    assert taco_row["price_range"] == 4  # Clamped to max_val 4
    assert taco_row["aggregate_rating"] == 0.0  # Clamped to min_val 0
    assert taco_row["votes"] == 0
    
    # Check city cleaning
    curry_row = df_clean[df_clean["restaurant_name"] == "Curry Express"].iloc[0]
    assert curry_row["city_clean"] == "Brasilia"
    assert curry_row["cuisines_clean"] == "Not Specified"

