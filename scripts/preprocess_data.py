import sys
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from config import Config
from src.data_loader import load_raw_data, validate_raw_columns
from src.preprocessing import preprocess_dataframe

def main():
    print("=" * 60)
    print("DineMind Data Preprocessing Pipeline")
    print("=" * 60)
    
    print(f"Loading raw dataset from: {Config.RAW_DATA_PATH}")
    df_raw = load_raw_data()
    print(f"Loaded raw records: {len(df_raw):,} rows, {len(df_raw.columns)} columns")
    
    print("Validating raw columns against canonical schema...")
    val = validate_raw_columns(df_raw)
    print(f"Found {len(val['found'])} canonical columns.")
    if val['missing']:
        print(f"Note - Unmapped canonical columns: {list(val['missing'].keys())}")
        
    print("\nExecuting data cleaning and normalization...")
    df_clean, stats = preprocess_dataframe(df_raw)
    
    # Ensure processed directory exists
    Config.PROCESSED_DATA_PATH.parent.mkdir(parents=True, exist_ok=True)
    
    print(f"Saving cleaned dataset to: {Config.PROCESSED_DATA_PATH}")
    df_clean.to_csv(Config.PROCESSED_DATA_PATH, index=False, encoding="utf-8")
    
    print("\n--- Preprocessing Pipeline Summary ---")
    print(f"  Initial records:           {stats['initial_rows']:,}")
    print(f"  Processed valid records:   {stats['final_rows']:,}")
    print(f"  Excluded records:          {stats['removed_rows']:,}")
    print(f"  Unique distinct cuisines:  {stats['unique_cuisines_count']:,}")
    print(f"  Unique cities:             {stats['unique_cities_count']:,}")
    print(f"  Unique localities:         {stats['unique_localities_count']:,}")
    print(f"  Rated restaurants:         {stats['rated_restaurants_count']:,}")
    print(f"  Unrated restaurants:       {stats['unrated_restaurants_count']:,}")
    print("\nPreprocessing completed successfully.")

if __name__ == "__main__":
    main()
