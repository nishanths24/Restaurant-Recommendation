# DineMind Recommendation Method Specification

## 1. Overview and Core Philosophy

DineMind is an end-to-end, content-based recommendation engine for restaurant selection. Unlike simple search engines or collaborative filtering models (which suffer from severe user cold-start and require private user interaction histories), DineMind uses a **preference-driven content scoring model**.

The recommendation pipeline evaluates a user's stated dining preferences (Cuisine, City/Locality, Budget/Price Tier, Minimum Rating, and Service Features like Delivery and Table Booking) directly against restaurant attributes extracted from the Cognifyz restaurant dataset.

---

## 2. Two-Stage Filtering and Ranking Architecture

### Stage A: Hard Constraint Filtering (Constraint Satisfaction)
When a user sets strict criteria (e.g., must be in a specific city, within a strict budget ceiling, or meet a minimum rating threshold), candidate restaurants violating these boundaries are pruned first.

1. **Location Constraint:**
   - City check: $\text{City}_{\text{rest}} == \text{City}_{\text{user}}$
   - Locality check: $\text{Locality}_{\text{rest}} == \text{Locality}_{\text{user}}$ (if selected)
2. **Strict Budget Ceiling:**
   - Either $\text{Cost}_{\text{two}} \le \text{MaxBudget}_{\text{user}}$ or $\text{PriceRange}_{\text{rest}} \le \text{PriceRange}_{\text{user}}$.
3. **Strict Minimum Rating:**
   - $\text{Rating}_{\text{rest}} \ge \text{RatingThreshold}_{\text{user}}$. Unrated restaurants (0.0 rating) are excluded when a strict minimum rating > 0 is enforced.

If Stage A results in zero candidates, the system returns diagnostic information highlighting which constraints were too restrictive, allowing the user to relax them.

---

### Stage B: Multi-Criteria Content Relevance Scoring

Each candidate restaurant is assigned a normalized match score $S \in [0, 100]$:

$$S = 100 \times \frac{\sum_{i \in \text{Active}} w_i \cdot s_i}{\sum_{i \in \text{Active}} w_i}$$

Where:
- $s_i \in [0, 1]$ is the normalized component score for criterion $i$.
- $w_i > 0$ is the configurable importance weight for criterion $i$.
- $\text{Active}$ is the subset of criteria explicitly provided by the user.

> **Key Invariance Property:** If a user does not specify a preference for criterion $i$, that criterion is excluded from both the numerator and the denominator. A restaurant is **never penalized** for preferences the user did not specify.

---

## 3. Mathematical Definitions of Component Scores

### 3.1 Cuisine Similarity Score ($s_{\text{cuisine}}$)
- **Weight:** $w_{\text{cuisine}} = 0.40$
- Let $U$ be the set of cuisines requested by the user, and $R$ be the set of cuisines served by the restaurant.
- **Coverage:** How thoroughly does the restaurant fulfill user desires?
  $$\text{Coverage}(U, R) = \frac{|U \cap R|}{|U|}$$
- **Jaccard Specialization:** How focused is the restaurant on these cuisines?
  $$\text{Jaccard}(U, R) = \frac{|U \cap R|}{|U \cup R|}$$
- **Combined Score:**
  $$s_{\text{cuisine}} = 0.75 \cdot \text{Coverage}(U, R) + 0.25 \cdot \text{Jaccard}(U, R)$$
- If $|U \cap R| = 0$, then $s_{\text{cuisine}} = 0.0$.

### 3.2 Location Fit Score ($s_{\text{location}}$)
- **Weight:** $w_{\text{location}} = 0.20$
- If both City and Locality are requested:
  $$s_{\text{location}} = \begin{cases} 1.0 & \text{if Locality matches} \\ 0.6 & \text{if City matches but Locality differs} \\ 0.0 & \text{otherwise} \end{cases}$$
- If only City is requested:
  $$s_{\text{location}} = \begin{cases} 1.0 & \text{if City matches} \\ 0.0 & \text{otherwise} \end{cases}$$

### 3.3 Budget Fit Score ($s_{\text{budget}}$)
- **Weight:** $w_{\text{budget}} = 0.20$
- **Numeric Cost ($C$) vs User Max ($B$):**
  $$s_{\text{budget}} = \begin{cases} 0.8 + 0.2 \cdot \frac{C}{B} & \text{if } C \le B \\ \max\left(0.0, 1.0 - \frac{C - B}{B}\right) & \text{if } C > B \end{cases}$$
- **Price Range Tier ($P_{\text{rest}} \in [1, 4]$) vs Preferred Tier ($P_{\text{user}}$):**
  $$s_{\text{budget}} = \begin{cases} 1.0 - 0.1 \cdot (P_{\text{user}} - P_{\text{rest}}) & \text{if } P_{\text{rest}} \le P_{\text{user}} \\ \max\left(0.0, 1.0 - 0.4 \cdot (P_{\text{rest}} - P_{\text{user}})\right) & \text{if } P_{\text{rest}} > P_{\text{user}} \end{cases}$$

### 3.4 Rating Quality Score ($s_{\text{rating}}$)
- **Weight:** $w_{\text{rating}} = 0.15$
- Normalized star rating (1.0 to 5.0 scale):
  $$r_{\text{norm}} = \frac{\text{Rating} - 1.0}{4.0}$$
- Confidence/Votes damping:
  $$v_{\text{factor}} = \min\left(1.0, \frac{\ln(1 + \text{Votes})}{\ln(1 + 1000)}\right)$$
- Base rating quality:
  $$s_{\text{base}} = 0.85 \cdot r_{\text{norm}} + 0.15 \cdot v_{\text{factor}}$$
- If user set a minimum rating threshold $R_{\text{min}}$:
  $$s_{\text{rating}} = \begin{cases} \min(1.0, 1.1 \cdot s_{\text{base}}) & \text{if } \text{Rating} \ge R_{\text{min}} \\ \max(0.0, s_{\text{base}} - 0.3 \cdot (R_{\text{min}} - \text{Rating})) & \text{if } \text{Rating} < R_{\text{min}} \end{cases}$$
- **Unrated Restaurants ($\text{Rating} = 0.0$):**
  Assigned a transparent neutral baseline score ($s_{\text{rating}} = 0.2$ if user requested $\ge$ rating; $0.4$ otherwise), preventing unrated listings from polluting strict searches while still allowing them to be discovered in general exploration.

### 3.5 Service Features Score ($s_{\text{features}}$)
- **Weight:** $w_{\text{features}} = 0.05$
- Evaluates online delivery and table booking availability when explicitly requested by user.

---

## 4. Deterministic Tie-Breaking Order

Recommendations are ranked according to a 4-tuple comparison key:
$$\text{SortKey} = (-\text{MatchScore}, -\text{AggregateRating}, -\text{Votes}, \text{RestaurantName})$$
This guarantees reproducible, consistent ranking without nondeterministic jitter.

---

## 5. Transparent Explanation Tags

Every recommendation produces factual, auditable justification tags derived strictly from verified record attributes:
1. Cuisine match confirmation (e.g. `"Matches cuisine: Italian, Pizza"`).
2. Location confirmation (e.g. `"Located in requested locality: Connaught Place"`).
3. Budget confirmation (e.g. `"Within budget: Indian Rupees(Rs.) 800 for two"`).
4. Rating threshold confirmation (e.g. `"Rating 4.5★ (Excellent) meets your ≥4.0★ threshold"`).
5. Delivery and booking confirmations.

No vague or fabricated claims (e.g., "Trending near you" or "Allergy safe") are ever generated.

