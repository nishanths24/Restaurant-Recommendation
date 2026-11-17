# Data Profile: DineMind Restaurant Dataset

**Source File:** `data/raw/Dataset .csv`  

**File Size:** 2,249,716 bytes  

**Total Records:** 9,551  

**Total Columns:** 21  

**Exact Duplicate Rows:** 0  


## 1. Column Overview and Types

| Column Name | Inferred Dtype | Non-Null Count | Missing Count | Missing % | Unique Count |
|---|---|---|---|---|---|
| `Restaurant ID` | `int64` | 9,551 | 0 | 0.00% | 9,551 |
| `Restaurant Name` | `str` | 9,551 | 0 | 0.00% | 7,446 |
| `Country Code` | `int64` | 9,551 | 0 | 0.00% | 15 |
| `City` | `str` | 9,551 | 0 | 0.00% | 141 |
| `Address` | `str` | 9,551 | 0 | 0.00% | 8,918 |
| `Locality` | `str` | 9,551 | 0 | 0.00% | 1,208 |
| `Locality Verbose` | `str` | 9,551 | 0 | 0.00% | 1,265 |
| `Longitude` | `float64` | 9,551 | 0 | 0.00% | 8,120 |
| `Latitude` | `float64` | 9,551 | 0 | 0.00% | 8,677 |
| `Cuisines` | `str` | 9,542 | 9 | 0.09% | 1,825 |
| `Average Cost for two` | `int64` | 9,551 | 0 | 0.00% | 140 |
| `Currency` | `str` | 9,551 | 0 | 0.00% | 12 |
| `Has Table booking` | `str` | 9,551 | 0 | 0.00% | 2 |
| `Has Online delivery` | `str` | 9,551 | 0 | 0.00% | 2 |
| `Is delivering now` | `str` | 9,551 | 0 | 0.00% | 2 |
| `Switch to order menu` | `str` | 9,551 | 0 | 0.00% | 1 |
| `Price range` | `int64` | 9,551 | 0 | 0.00% | 4 |
| `Aggregate rating` | `float64` | 9,551 | 0 | 0.00% | 33 |
| `Rating color` | `str` | 9,551 | 0 | 0.00% | 6 |
| `Rating text` | `str` | 9,551 | 0 | 0.00% | 6 |
| `Votes` | `int64` | 9,551 | 0 | 0.00% | 1,012 |

## 2. Numeric Columns Summary

| Column | Min | 25% | Median | 75% | Max | Mean | Std | Suspicious / Notes |
|---|---|---|---|---|---|---|---|---|
| `Restaurant ID` | 53.00 | 301962.50 | 6004089.00 | 18352291.50 | 18500652.00 | 9051128.35 | 8791521.28 | Normal |
| `Country Code` | 1.00 | 1.00 | 1.00 | 1.00 | 216.00 | 18.37 | 56.75 | Normal |
| `Longitude` | -157.95 | 77.08 | 77.19 | 77.28 | 174.83 | 64.13 | 41.47 | 498 zeros (5.2%); Has negative values |
| `Latitude` | -41.33 | 28.48 | 28.57 | 28.64 | 55.98 | 25.85 | 11.01 | 498 zeros (5.2%); Has negative values |
| `Average Cost for two` | 0.00 | 250.00 | 400.00 | 700.00 | 800000.00 | 1199.21 | 16121.18 | 18 zeros (0.2%) |
| `Price range` | 1.00 | 1.00 | 2.00 | 2.00 | 4.00 | 1.80 | 0.91 | Normal |
| `Aggregate rating` | 0.00 | 2.50 | 3.20 | 3.70 | 4.90 | 2.67 | 1.52 | 2148 zeros (22.5%) |
| `Votes` | 0.00 | 5.00 | 31.00 | 131.00 | 10934.00 | 156.91 | 430.17 | 1094 zeros (11.5%) |

## 3. Categorical Fields & Top Values

- **`Restaurant Name`** (7446 uniques): `Cafe Coffee Day` (83), `Domino's Pizza` (79), `Subway` (63), `Green Chick Chop` (51), `McDonald's` (48)
- **`City`** (141 uniques): `New Delhi` (5,473), `Gurgaon` (1,118), `Noida` (1,080), `Faridabad` (251), `Ghaziabad` (25)
- **`Address`** (8918 uniques): `Dilli Haat, INA, New Delhi` (11), `Sector 41, Noida` (11), `Greater Kailash (GK) 1, New Delhi` (10), `The Imperial, Janpath, New Delhi` (9), `Cyber Hub, DLF Cyber City, Gurgaon` (8)
- **`Locality`** (1208 uniques): `Connaught Place` (122), `Rajouri Garden` (99), `Shahdara` (87), `Defence Colony` (86), `Malviya Nagar` (85)
- **`Locality Verbose`** (1265 uniques): `Connaught Place, New Delhi` (122), `Rajouri Garden, New Delhi` (99), `Shahdara, New Delhi` (87), `Defence Colony, New Delhi` (86), `Pitampura, New Delhi` (85)
- **`Cuisines`** (1825 uniques): `North Indian` (936), `North Indian, Chinese` (511), `Chinese` (354), `Fast Food` (354), `North Indian, Mughlai` (334)
- **`Currency`** (12 uniques): `Indian Rupees(Rs.)` (8,652), `Dollar($)` (482), `Pounds(��)` (80), `Brazilian Real(R$)` (60), `Emirati Diram(AED)` (60)
- **`Has Table booking`** (2 uniques): `No` (8,393), `Yes` (1,158)
- **`Has Online delivery`** (2 uniques): `No` (7,100), `Yes` (2,451)
- **`Is delivering now`** (2 uniques): `No` (9,517), `Yes` (34)
- **`Switch to order menu`** (1 uniques): `No` (9,551)
- **`Rating color`** (6 uniques): `Orange` (3,737), `White` (2,148), `Yellow` (2,100), `Green` (1,079), `Dark Green` (301)
- **`Rating text`** (6 uniques): `Average` (3,737), `Not rated` (2,148), `Good` (2,100), `Very Good` (1,079), `Excellent` (301)

## 4. Key Preference Fields Availability Assessment


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
