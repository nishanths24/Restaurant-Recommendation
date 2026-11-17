import os
import pandas as pd
from pathlib import Path
from config import Config

def load_raw_data(filepath=None) -> pd.DataFrame:
    """
    Load raw restaurant dataset safely without altering it.
    Handles BOM and encoding issues gracefully.
    """
    path = Path(filepath) if filepath else Config.RAW_DATA_PATH
    if not path.exists():
        raise FileNotFoundError(f"Raw dataset not found at: {path}")

    # Read with utf-8 encoding and clean BOM characters
    df = pd.read_csv(path, encoding="utf-8")
    df.columns = [c.strip().lstrip("\ufeff") for c in df.columns]
    return df

def validate_raw_columns(df: pd.DataFrame) -> dict:
    """
    Check availability of canonical columns in raw dataframe.
    Returns a dict with 'found', 'missing', and 'mapping'.
    """
    found = {}
    missing = {}
    
    for canonical_name, source_name in Config.COLUMN_MAPPING.items():
        if source_name in df.columns:
            found[canonical_name] = source_name
        else:
            missing[canonical_name] = source_name
            
    return {
        "found": found,
        "missing": missing,
        "is_valid": len(missing) == 0 or ("Restaurant ID" in df.columns and "Restaurant Name" in df.columns)
    }

def load_processed_data(filepath=None) -> pd.DataFrame:
    """
    Load preprocessed restaurant dataset.
    """
    path = Path(filepath) if filepath else Config.PROCESSED_DATA_PATH
    if not path.exists():
        raise FileNotFoundError(f"Processed dataset not found at: {path}. Run scripts/preprocess_data.py first.")
    
    df = pd.read_csv(path, encoding="utf-8")
    return df

