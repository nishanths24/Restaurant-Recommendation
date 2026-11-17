import pandas as pd
import numpy as np
import os
import json

raw_path = "data/raw/Dataset .csv"
print(f"Loading {raw_path}...")
df = pd.read_csv(raw_path, encoding='utf-8')

print(f"Shape: {df.shape}")
print("Original Columns:")
for c in df.columns:
    print(f"  {repr(c)}")

# Check BOM or leading characters
df.columns = [c.strip().lstrip('\ufeff') for c in df.columns]

num_rows, num_cols = df.shape
duplicate_rows = df.duplicated().sum()

print(f"\nTotal rows: {num_rows}, Total columns: {num_cols}")
print(f"Exact duplicate rows: {duplicate_rows}")

profile_lines = []
profile_lines.append("# Data Profile: DineMind Restaurant Dataset\n")
profile_lines.append(f"**Source File:** `data/raw/Dataset .csv`  \n")
profile_lines.append(f"**File Size:** {os.path.getsize(raw_path):,} bytes  \n")
profile_lines.append(f"**Total Records:** {num_rows:,}  \n")
profile_lines.append(f"**Total Columns:** {num_cols}  \n")
profile_lines.append(f"**Exact Duplicate Rows:** {duplicate_rows}  \n\n")

profile_lines.append("## 1. Column Overview and Types\n")
profile_lines.append("| Column Name | Inferred Dtype | Non-Null Count | Missing Count | Missing % | Unique Count |")
profile_lines.append("|---|---|---|---|---|---|")

for col in df.columns:
    dtype = str(df[col].dtype)
    non_null = int(df[col].notnull().sum())
    missing = int(df[col].isnull().sum())
    missing_pct = (missing / num_rows) * 100
    unique = int(df[col].nunique(dropna=True))
    profile_lines.append(f"| `{col}` | `{dtype}` | {non_null:,} | {missing:,} | {missing_pct:.2f}% | {unique:,} |")

profile_lines.append("\n## 2. Numeric Columns Summary\n")
profile_lines.append("| Column | Min | 25% | Median | 75% | Max | Mean | Std | Suspicious / Notes |")
profile_lines.append("|---|---|---|---|---|---|---|---|---|")

num_cols_list = df.select_dtypes(include=[np.number]).columns
for col in num_cols_list:
    s = df[col].dropna()
    notes = []
    if (s == 0).sum() > 0:
        notes.append(f"{(s == 0).sum()} zeros ({((s == 0).sum()/len(s))*100:.1f}%)")
    if s.min() < 0:
        notes.append("Has negative values")
    note_str = "; ".join(notes) if notes else "Normal"
    profile_lines.append(f"| `{col}` | {s.min():.2f} | {s.quantile(0.25):.2f} | {s.median():.2f} | {s.quantile(0.75):.2f} | {s.max():.2f} | {s.mean():.2f} | {s.std():.2f} | {note_str} |")

profile_lines.append("\n## 3. Categorical Fields & Top Values\n")
cat_cols_list = df.select_dtypes(exclude=[np.number]).columns
for col in cat_cols_list:
    val_counts = df[col].value_counts(dropna=False).head(5)
    sample_str = ", ".join([f"`{k}` ({v:,})" for k, v in val_counts.items()])
    profile_lines.append(f"- **`{col}`** ({df[col].nunique()} uniques): {sample_str}")

profile_lines.append("\n## 4. Key Preference Fields Availability Assessment\n")
profile_lines.append("""
| Target Preference | Dataset Source Column | Availability Status | Notes & Usability |
|---|---|---|---|
| **Restaurant Name** | `Restaurant Name` | Available | High cardinality, 100% non-null |
| **Cuisine** | `Cuisines` | Available | 9 missing values; comma-separated strings (multi-label) |
| **City** | `City` | Available | 141 unique cities across 15 countries |
| **Locality** | `Locality`, `Locality Verbose`, `Address` | Available | Excellent granularity for location matching |
| **Cost / Budget** | `Average Cost for two`, `Currency`, `Price range` | Available | Has currency differences; Price range (1 to 4) is normalized, Average Cost is in local currency |
| **Rating** | `Aggregate rating`, `Votes`, `Rating text`, `Rating color` | Available | Continuous rating (0.0 to 5.0), 2,148 unrated (0.0 rating) |
| **Online Ordering** | `Has Online delivery` | Available | Yes/No binary flag |
| **Table Booking** | `Has Table booking` | Available | Yes/No binary flag |
| **Delivering Now** | `Is delivering now` | Available | Yes/No binary flag |
| **Dietary Tags** | *None* | **Not Available** | No explicit vegan, vegetarian, halal, or allergy tags in dataset |
| **Restaurant Type** | *None* | **Not Available** | No dedicated dining type column (e.g. Cafe, Fine Dining, Bar) |
""")

report_content = "\n".join(profile_lines)
with open("reports/data_profile.md", "w", encoding="utf-8") as f:
    f.write(report_content)

print(f"\nWrote reports/data_profile.md successfully.")
