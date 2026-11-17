import pandas as pd
from collections import Counter

df = pd.read_csv("data/raw/Dataset .csv", encoding='utf-8')
df.columns = [c.strip().lstrip('\ufeff') for c in df.columns]

# Split cuisines
all_cuisines = []
for c in df['Cuisines'].dropna():
    tokens = [t.strip() for t in c.split(',') if t.strip()]
    all_cuisines.extend(tokens)

cuisine_counts = Counter(all_cuisines)
print(f"Total unique individual cuisines: {len(cuisine_counts)}")
print("Top 20 individual cuisines:")
for c, cnt in cuisine_counts.most_common(20):
    print(f"  {c}: {cnt}")

print("\nTop 15 cities:")
for city, cnt in df['City'].value_counts().head(15).items():
    print(f"  {city}: {cnt}")

print("\nPrice range counts:")
print(df['Price range'].value_counts().sort_index())

print("\nRating distributions (non-zero):")
rated = df[df['Aggregate rating'] > 0]
print(rated['Aggregate rating'].describe())
