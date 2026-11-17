import csv
import os

filepath = 'data/raw/Dataset .csv'

print(f"File exists: {os.path.exists(filepath)}")
print(f"File size: {os.path.getsize(filepath)} bytes")

# Read header and first few lines using csv module (doesn't require pandas yet)
with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
    reader = csv.reader(f)
    header = next(reader)
    print(f"\nTotal columns: {len(header)}")
    print("Columns:")
    for i, col in enumerate(header):
        print(f"  [{i}] {col}")
    
    sample_rows = []
    for _ in range(5):
        try:
            sample_rows.append(next(reader))
        except StopIteration:
            break

print(f"\nRead {len(sample_rows)} sample rows.")
for r_idx, row in enumerate(sample_rows):
    print(f"\n--- Sample Row {r_idx + 1} ---")
    for col, val in zip(header, row):
        print(f"  {col}: {val}")

