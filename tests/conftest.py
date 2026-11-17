import pytest
import pandas as pd
import numpy as np
from pathlib import Path

@pytest.fixture
def sample_raw_dataframe():
    """Synthetic raw dataframe mimicking the real dataset schema for testing."""
    data = {
        "\ufeffRestaurant ID": [101, 102, 103, 104, 105],
        "Restaurant Name": ["Spice Villa", "Pizza Roma", "Curry Express", "  Taco Fiesta  ", None],
        "Country Code": [1, 1, 1, 1, 1],
        "City": ["New Delhi", "New Delhi", "Bras_lia", "Noida", "New Delhi"],
        "Address": ["Connaught Place", "Saket", "Sector 18", "Sector 62", "Unknown"],
        "Locality": ["Connaught Place", "Saket", "Sector 18", "Sector 62", "Unknown"],
        "Locality Verbose": ["Connaught Place, New Delhi", "Saket, New Delhi", "Sector 18, Noida", "Sector 62, Noida", "Unknown"],
        "Longitude": [77.21, 77.20, 0.0, 77.36, 0.0],
        "Latitude": [28.63, 28.52, 0.0, 28.60, 0.0],
        "Cuisines": ["North Indian, Mughlai", "Italian, Pizza", None, "Mexican, Fast Food", "Chinese"],
        "Average Cost for two": ["800", "1200", "300", "invalid_cost", "500"],
        "Currency": ["Indian Rupees(Rs.)", "Indian Rupees(Rs.)", "Indian Rupees(Rs.)", "Indian Rupees(Rs.)", "Indian Rupees(Rs.)"],
        "Has Table booking": ["Yes", "No", "No", "No", "No"],
        "Has Online delivery": ["Yes", "Yes", "No", "No", "No"],
        "Is delivering now": ["No", "No", "No", "No", "No"],
        "Switch to order menu": ["No", "No", "No", "No", "No"],
        "Price range": [2, 3, 1, 99, 2],
        "Aggregate rating": [4.5, 4.0, 0.0, -1.0, 3.8],
        "Rating color": ["Dark Green", "Green", "White", "White", "Yellow"],
        "Rating text": ["Excellent", "Very Good", "Not rated", "Not rated", "Good"],
        "Votes": [450, 210, 0, "bad_votes", 15],
    }
    return pd.DataFrame(data)
