# DineMind — Intelligent Restaurant Recommendation System

[![Python Version](https://img.shields.io/badge/Python-3.12-blue.svg)](https://www.python.org/)
[![Framework](https://img.shields.io/badge/Framework-Flask_3.1-orange.svg)](https://palletsprojects.com/p/flask/)
[![Tests](https://img.shields.io/badge/Tests-24%20Passed-brightgreen.svg)]()
[![License](https://img.shields.io/badge/License-MIT-green.svg)]()

> **Cognifyz Technologies Machine Learning Internship — Task 2**  
> **Project Name:** DineMind  
> **Core Objective:** Build an end-to-end, locally runnable restaurant recommendation web application that recommends venues according to a user's stated dining preferences using content-based filtering.

---

## 1. Project Overview

DineMind is a preference-first, content-based recommendation platform designed to help users discover restaurants that match their culinary tastes, geographic location, budget constraints, and dining requirements.

Rather than relying purely on collaborative filtering (which requires extensive user histories and suffers from severe cold-start issues) or primitive restaurant-to-restaurant search, DineMind evaluates a user's active preferences against verified restaurant attributes across **9,551 global venues** from the Cognifyz restaurant dataset.

### Key Capabilities
- **Preference-Driven Engine:** Matches user-selected cuisines, city/locality, budget range, and minimum rating.
- **Two-Stage Retrieval:**
  1. *Stage A (Hard Constraints):* Prunes non-matching geographic boundaries and budget ceilings.
  2. *Stage B (Relevance Ranking):* Computes a normalized 0–100 match score across weighted preference components.
- **Explainable Recommendations:** Every returned result includes factual, verifiable explanation tags (e.g. `"Matches cuisine: Italian"`, `"Within budget: ₹800 for two"`).
- **Secondary Similarity Feature:** Content-based similarity search to find restaurants similar to any chosen venue.
- **Graceful Fallbacks & Diagnostics:** Provides actionable guidance when strict filters produce zero matches, and falls back to general top-rated listings when preferences are left blank.

---

## 2. Dataset Architecture & Verification

The project is powered by the verified dataset provided by Cognifyz Technologies (`Dataset .csv`):

| Attribute | Measured Dataset Value |
|---|---|
| **Total Records** | 9,551 restaurants |
| **Total Columns** | 21 features |
| **Distinct Cuisines** | 146 unique cuisine types (e.g. North Indian, Chinese, Italian, Continental, Mughlai, Fast Food) |
| **Geographic Coverage** | 140 unique cities across 15 countries (New Delhi: 5,473; Gurgaon: 1,118; Noida: 1,080; Faridabad: 251) |
| **Localities** | 1,208 unique neighborhoods |
| **Price Tiers** | 1 (Budget: 4,444), 2 (Moderate: 3,113), 3 (Expensive: 1,408), 4 (Luxury: 586) |
| **Rating Range** | 0.0 to 4.9 stars (7,403 rated venues; 2,148 unrated with "Not rated" status) |

### Supported vs. Unsupported Fields (Integrity Guarantee)
- **Supported:** Restaurant Name, Cuisines, City, Locality, Full Address, Cost for Two, Currency, Price Tier, Aggregate Rating, Votes, Online Delivery flag, Table Booking flag.
- **Unsupported (Omitted per guidelines):** The dataset does **not** contain explicit dietary tags (Vegetarian, Vegan, Halal, Allergen-free) or dedicated dining types (Cafe, Bar, Fine Dining). Per project integrity guidelines, DineMind disables dietary filters rather than fabricating or guessing health guarantees from cuisine names.

---

## 3. Recommendation Scoring Algorithm

### Stage A: Hard Constraints Pruning
When strict filtering is toggled:
- Candidates outside the requested city or locality are pruned.
- Venues exceeding the specified budget ceiling or price tier are excluded.
- Venues below the minimum rating threshold are pruned.

### Stage B: Weighted Content Relevance Scoring

For each surviving candidate, a normalized match score $S \in [0, 100]$ is computed:

$$S = 100 \times \frac{\sum_{i \in \text{Active}} w_i \cdot s_i}{\sum_{i \in \text{Active}} w_i}$$

#### Component Weights and Scoring Formulations:

| Criterion | Default Weight | Formulation & Metric |
|---|---|---|
| **Cuisine Similarity** | **40%** | Combined Coverage (0.75) and Jaccard Overlap (0.25) between user's desired cuisines and restaurant's offerings. |
| **Location Match** | **20%** | Exact Locality match = 1.0; Same City match = 0.6; Non-matching = 0.0. |
| **Budget Fit** | **20%** | Closeness to desired price tier (1 to 4) or proportional fit to maximum numeric cost. |
| **Rating Quality** | **15%** | Star rating normalized to [0, 1] with logarithmic vote count damping: $s_{\text{base}} = 0.85 \cdot r_{\text{norm}} + 0.15 \cdot \frac{\ln(1+\text{votes})}{\ln(1+1000)}$. |
| **Service Attributes** | **5%** | Verifies online delivery and table booking availability if requested. |

> **Active Renormalization:** If a user omits a preference (e.g. leaves budget blank), that weight is excluded from both numerator and denominator, ensuring unselected criteria never penalize a venue.

### Deterministic Tie-Breaking
Results are sorted deterministically by:
$$\text{SortKey} = (-\text{MatchScore}, -\text{AggregateRating}, -\text{Votes}, \text{RestaurantName})$$

---

## 4. Project Structure

```text
DineMind/
├── app.py                      # Flask application factory and route definitions
├── config.py                   # Centralized configuration and schema mapping
├── requirements.txt            # Pinned dependency requirements
├── README.md                   # Complete documentation
├── cogni.md                    # Project specification & guidelines
├── pytest.ini                  # Pytest configuration
├── .env.example                # Sample environment variables
├── .gitignore                  # Git exclusions
├── data/
│   ├── raw/
│   │   ├── Dataset .csv        # Untouched raw dataset from Cognifyz Drive
│   │   └── .gitkeep
│   └── processed/
│       ├── restaurants_cleaned.csv  # Preprocessed, normalized dataset
│       └── .gitkeep
├── src/
│   ├── __init__.py
│   ├── data_loader.py          # Data ingestion and schema validation
│   ├── preprocessing.py        # Cleaning, parsing, and normalization pipeline
│   ├── feature_builder.py      # MultiLabelBinarizer & item similarity
│   ├── recommender.py          # Two-stage recommendation engine
│   ├── explanations.py         # Factual justification tag generator
│   └── validators.py           # Form input validation and sanitization
├── scripts/
│   ├── download_data.py        # Automated dataset retrieval from Drive
│   ├── inspect_dataset.py      # Quick inspection tool
│   ├── preprocess_data.py      # Repeatable preprocessing pipeline runner
│   ├── evaluate_system.py      # Automated evaluation against 10 test scenarios
│   └── verify_live_app.py      # Live Flask endpoint integration verification
├── templates/
│   ├── base.html               # Base layout with navigation and footer
│   ├── index.html              # Preference input form with interactive selectors
│   ├── results.html            # Ranked recommendation cards and diagnostics
│   ├── similar.html            # Secondary item-to-item similarity page
│   └── error.html              # User-friendly error page (404, 500)
├── static/
│   ├── css/
│   │   └── style.css           # Custom styling and color palette
│   └── js/
│       └── app.js              # Cascading dropdowns and tag selector interactivity
├── tests/
│   ├── conftest.py             # Reusable pytest fixtures
│   ├── test_preprocessing.py   # Unit tests for data cleaning functions
│   ├── test_recommender.py     # Unit tests for recommendation scoring and constraints
│   └── test_routes.py          # Integration tests for Flask routes
└── reports/
    ├── data_profile.md         # Comprehensive data profiling report
    ├── recommendation_method.md# Mathematical method specification
    ├── evaluation.md           # Measured quality evaluation report
    ├── task_brief.txt          # Extracted Cognifyz task brief
    └── Machine Learning.pdf    # Downloaded internship documentation
```

---

## 5. Getting Started & Installation

### Prerequisites
- Python 3.10+ (tested on Python 3.12)
- PowerShell (Windows) or Bash (macOS/Linux)

### Windows Setup
```powershell
# 1. Clone or navigate to the project directory
cd C:\Users\nisha\OneDrive\Desktop\Resto

# 2. Create and activate a virtual environment (optional but recommended)
py -m venv .venv
.\.venv\Scripts\Activate.ps1

# 3. Install dependencies
pip install -r requirements.txt

# 4. Preprocess the raw dataset (generates data/processed/restaurants_cleaned.csv)
python scripts/preprocess_data.py

# 5. Run test suite
pytest -q

# 6. Start the web application
python app.py
```

### macOS / Linux Setup
```bash
# 1. Navigate to directory
cd Resto

# 2. Create and activate virtual environment
python3 -m venv .venv
source .venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Preprocess dataset
python scripts/preprocess_data.py

# 5. Run test suite
pytest -q

# 6. Start the web application
python app.py
```

The application will start on **`http://127.0.0.1:5000`**.

---

## 6. Verification & Test Suite

The test suite contains **24 comprehensive unit and integration tests** verifying all layers:

```powershell
pytest -v
```

### Test Coverage Highlights:
- **Preprocessing Tests (`tests/test_preprocessing.py`):**
  - Null placeholder sanitization (`clean_text`)
  - Mojibake character resolution (`clean_city`)
  - Multi-label cuisine tokenization (`parse_cuisines`)
  - Boolean flag normalization (`clean_boolean`)
  - Numeric bounding and currency stripping (`clean_numeric`)
  - Full dataframe pipeline execution and unrated detection
- **Recommender Tests (`tests/test_recommender.py`):**
  - Cuisine-only queries
  - Location-only queries with strict locality bounds
  - Strict budget ceiling enforcement
  - Minimum rating threshold filtering
  - Multi-preference combined queries
  - Empty preference fallback to general top-rated listings
  - Zero-match diagnostic error handling
  - Deterministic score monotonicity check ($S_k \ge S_{k+1}$)
  - Item-to-item similarity calculation
- **Flask Route Tests (`tests/test_routes.py`):**
  - `GET /health` JSON healthcheck
  - `GET /` preference form rendering
  - `GET /about` documentation page
  - `POST /recommend` with active criteria
  - `POST /recommend` with empty inputs
  - `POST /recommend` with strict non-existent bounds (empty state)
  - `GET /similar/<id>` for valid and invalid venue IDs
  - Global `404` and `500` error handlers

---

## 7. Quality Evaluation Summary

Offline quality evaluation was executed across 10 functional user scenarios using `scripts/evaluate_system.py`:

| Scenario ID | Test Criteria | Results Returned | Constraint Satisfaction | Score Monotonic? |
|---|---|:---:|:---:|:---:|
| **SC-01** | Cuisine-only (North Indian) | 10 | **100.0%** | Yes |
| **SC-02** | Location-only (Gurgaon) | 10 | **100.0%** | Yes |
| **SC-03** | Budget-only (Price Range $\le$ 2) | 10 | **100.0%** | Yes |
| **SC-04** | Min Rating ($\ge$ 4.0 Stars) | 10 | **100.0%** | Yes |
| **SC-05** | Combined: Italian + New Delhi + Tier 2 + Min 3.5★ | 10 | **100.0%** | Yes |
| **SC-06** | Empty Preferences (Top-Rated Fallback) | 10 | **100.0%** | Yes |
| **SC-07** | Strict Non-Existent City (Zero Match) | 0 | **100.0%** | Yes |
| **SC-08** | Online Delivery + Table Booking | 10 | **100.0%** | Yes |
| **SC-09** | Exotic Cuisine (Tibetan) | 10 | **100.0%** | Yes |
| **SC-10** | Locality + Numeric Cost (Connaught Place, $\le$ ₹1,200) | 10 | **100.0%** | Yes |

- **Overall Constraint Satisfaction Rate:** **100.00%**
- **Score Monotonicity Across Queries:** **100.00%**
- **Within-Query Duplicate Rate:** **0.00%**
- **Result Completeness:** **100.00%**

*(For the complete evaluation breakdown, see [reports/evaluation.md](reports/evaluation.md).)*

---

## 8. Sample User Journey Walkthrough

1. **User Goal:** Wants a great **North Indian** dinner in **New Delhi (Connaught Place)** with a budget of under **₹1,200 for two** and at least **4.0★ rating**.
2. **Form Input:**
   - Cuisines: `North Indian`
   - City: `New Delhi`, Locality: `Connaught Place`
   - Max Cost: `1200`
   - Min Rating: `4.0+ ★`
   - Strict Location: `Checked`
3. **Execution Output:**
   - DineMind prunes venues outside Connaught Place or above ₹1,200.
   - Computes weighted score across cuisine overlap, budget proximity, and rating quality.
   - Returns top venues (such as *Saravana Bhavan*, *Bikanervala*, *Kake Da Hotel*) with match scores > 90%.
   - Explanation tags displayed: `"Matches cuisine: North Indian"`, `"Located in requested locality: Connaught Place"`, `"Within budget: Indian Rupees(Rs.) 800 for two"`, `"Rating 4.2★ meets your ≥4.0★ threshold"`.

---

## 9. Limitations & Future Roadmap

- **Geographic Imbalance:** Over 80% of dataset records are situated in Delhi NCR. Future enhancements could integrate multi-city federated data sources.
- **Dietary Field Absence:** Because the underlying data lacks explicit vegetarian/halal flags, DineMind avoids making unsubstantiated health claims. Future work could incorporate verified menu OCR or allergen datasets.
- **Real-Time Feedback:** Incorporating implicit user feedback (e.g. click-through and session analytics) could allow Bayesian dynamic weight tuning.

---

## 10. Project Information

- **Organization:** Cognifyz Technologies
- **Internship Program:** Machine Learning Internship
- **Task:** Task 2 — Restaurant Recommendation System
- **Implementation:** Autonomous End-to-End Build by Antigravity Agent

