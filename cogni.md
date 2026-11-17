# DineMind --- End-to-End Project Build Specification

> **Project:** DineMind --- Restaurant Recommendation System\
> **Assignment:** Cognifyz Technologies --- Machine Learning Task 2\
> **Primary objective:** Build a working restaurant recommendation web
> application that recommends restaurants according to a user's stated
> preferences.\
> **Intended executor:** Antigravity coding agent\
> **Implementation mode:** Build, run, test, document, and verify the
> complete project---not merely generate sample code.

------------------------------------------------------------------------

## 1. Mission and expected outcome

Build **DineMind**, an end-to-end, locally runnable restaurant
recommendation system. A user should be able to enter preferences such
as cuisine, location, budget, minimum rating, dining type, and dietary
requirements, then receive a ranked list of restaurants that best match
those preferences.

The system must use the dataset supplied in the Google Drive folder:

https://drive.google.com/drive/folders/1fNkM8LQpjFFviVrcqu5VNPbKnHXlM32M

The first engineering task is to inspect the folder and identify the
actual dataset file(s), format, columns, geographic coverage, row count,
and data quality. Do not assume a particular schema, dataset source, or
column naming convention. Do not fabricate restaurant records or claim
that unavailable fields exist.

The finished result must include: - A reproducible data inspection and
preprocessing pipeline. - A content-based recommendation engine. - A
usable web interface for collecting preferences and displaying
results. - Meaningful ranking explanations and sensible handling of
filters. - Tests and a small evaluation report. - Clear setup
instructions and project documentation.

**Important distinction:** This is a *user-preference-based*
recommendation system. Do not implement only "enter a restaurant name
and find similar restaurants." Restaurant-to-restaurant similarity may
be an optional secondary feature, but the main flow must start with user
preferences.

## 2. Assignment requirements mapped to implementation

The assignment brief specifies the following:

1.  Preprocess the dataset by handling missing values and encoding
    categorical variables.
2.  Determine recommendation criteria, for example cuisine preference
    and price range.
3.  Implement content-based filtering so users receive restaurants
    similar to their preferred criteria.
4.  Test the system with sample user preferences and evaluate
    recommendation quality.

Implement each requirement explicitly and make it demonstrable in the
application and README.

## 3. Work rules for the coding agent

Follow these rules throughout development:

1.  **Inspect before coding.** Explore the repository and the supplied
    Drive dataset before selecting columns or writing preprocessing
    logic.
2.  **Preserve the raw data.** Never overwrite the original dataset.
    Store processed outputs separately.
3.  **Be schema-aware.** Build a column-mapping/configuration layer
    instead of scattering hard-coded column names across the codebase.
4.  **Do not invent data.** No fabricated restaurant names, ratings,
    prices, coordinates, reviews, or evaluation results.
5.  **Make assumptions visible.** Record any inferred column mapping,
    missing field, unsupported feature, or fallback behavior in
    documentation.
6.  **Make the project runnable.** Install dependencies, execute
    preprocessing, start the app, and run tests. Do not stop after
    writing files.
7.  **Avoid unnecessary complexity.** A transparent, well-tested
    content-based model is preferred over an unnecessarily complex
    deep-learning model.
8.  **Keep secrets out of source control.** Use environment variables
    for optional credentials. The core application must not require a
    paid API.
9.  **Handle failure gracefully.** Missing dataset, malformed CSV, empty
    filters, and unknown preference values must produce helpful messages
    rather than stack traces in the browser.
10. **Do not claim external integrations that are not implemented.**
    Maps, live availability, delivery links, and live restaurant data
    are out of scope unless genuinely available and configured.

## 4. Phase 0 --- Repository and dataset discovery

### 4.1 Inspect the workspace

Before modifying anything: - List all files and directories in the
project workspace. - Identify existing code, virtual environments,
notebooks, datasets, and Git status. - Do not delete useful existing
work without a clear reason. - If this is a new workspace, create the
project structure in Section 12.

### 4.2 Retrieve and inspect the supplied dataset

Open the Google Drive folder above. Determine whether it contains: -
CSV, Excel, JSON, ZIP, or other data files. - More than one dataset or
supporting document. - A task brief, data dictionary, or column
description.

If access is denied or the files cannot be downloaded: - Do not silently
substitute an unrelated public dataset. - Report the access issue to the
user and request the dataset file or permission. - You may continue
building schema-independent scaffolding, but do not claim the real
dataset pipeline is complete.

For every candidate dataset, record: - File name and format. - Number of
rows and columns. - Column names and inferred data types. - Duplicate
row count. - Missing-value count and percentage per column. -
Unique-value counts for categorical fields. - Numeric ranges and
suspicious values. - Example values, excluding any sensitive
information. - Whether the data contains restaurant name, cuisine,
locality/city, rating, votes/reviews, cost/price, address,
online-order/table-booking flags, or dietary information.

Create `reports/data_profile.md` with these findings. Do not paste the
entire dataset into the report.

### 4.3 Dataset selection

Choose the most relevant restaurant dataset in the supplied folder. If
several files exist, explain the selection. Prefer the file with the
most usable restaurant attributes for preference matching.

Create a configurable dataset path, for example: -
`data/raw/restaurants.csv` for the source copy. -
`data/processed/restaurants_cleaned.csv` for cleaned data.

The actual filename may differ. Update configuration and documentation
accordingly.

## 5. Product behavior and user journey

### Main user journey

1.  User opens the DineMind home page.
2.  User chooses one or more cuisines, or selects "Any cuisine."
3.  User chooses a location/locality, or selects "Any location" if
    supported by the data.
4.  User sets a maximum budget (or budget band) using the dataset's
    actual price field.
5.  User optionally sets a minimum rating.
6.  User can select supported dietary preferences and restaurant
    attributes, such as vegetarian-friendly, online ordering, or table
    booking, only if reliable dataset fields exist.
7.  User submits the form.
8.  The backend validates the preferences, applies hard constraints,
    calculates a relevance score, and returns the top matching
    restaurants.
9.  The results page displays restaurant details, match score, and a
    short explanation of why each result was recommended.
10. User can adjust preferences and submit again.

### Required preference inputs

Implement only fields supported by the inspected dataset. The following
are the desired fields, in priority order:

  -----------------------------------------------------------------------
  Preference              Input type              Behavior
  ----------------------- ----------------------- -----------------------
  Cuisine                 Multi-select            Match one or more
                                                  preferred cuisines

  Location/locality       Select or text/select   Prefer restaurants in
                          control                 chosen area

  Maximum budget          Numeric input or budget Exclude or penalize
                          bands                   restaurants above
                                                  budget

  Minimum rating          Numeric/select          Exclude or penalize
                                                  restaurants below
                                                  threshold

  Dietary preference      Multi-select            Use only if dataset
                                                  supports it

  Restaurant type         Select/multi-select     Use only if dataset
                                                  supports it

  Online ordering         Yes / No / Any          Use only if field
                                                  exists

  Table booking           Yes / No / Any          Use only if field
                                                  exists

  Number of               Select                  Default 10; enforce a
  recommendations                                 safe maximum
  -----------------------------------------------------------------------

If a field is absent, hide or disable that control and document that the
dataset does not support it. Never infer a restaurant is vegetarian,
vegan, halal, or allergy-safe from its name or cuisine label.

### Empty and partial preferences

-   Allow users to leave optional preferences blank.
-   If no preference is selected, show a clear validation prompt or a
    clearly labeled general top-rated list---not a misleading
    "personalized" result.
-   Do not let an empty preference vector silently return arbitrary
    results.
-   If filters produce no matches, explain which constraints may be too
    strict and offer a reset/relax-filters action.

## 6. Data preprocessing requirements

Implement preprocessing in a separate module/script. It must be
repeatable and must not modify raw source files.

### 6.1 Column mapping

Create a central mapping/configuration file that maps canonical
application fields to actual dataset columns. Suggested canonical
fields:

-   `restaurant_name`
-   `cuisines`
-   `location`
-   `address`
-   `rating`
-   `rating_count` or `votes`
-   `cost_for_two` or `average_cost`
-   `restaurant_type`
-   `online_order`
-   `table_booking`
-   `dietary_tags`

Only map a canonical field when a suitable source column exists. Record
unmapped fields. If multiple columns could represent the same field,
inspect sample values and select the correct one deliberately.

### 6.2 Cleaning steps

At minimum: - Normalize column names for internal processing while
preserving original names in the data profile. - Trim whitespace and
normalize empty strings, `"null"`, `"NA"`, `"N/A"`, and similar
placeholders to missing values. - Remove exact duplicate rows. - Handle
duplicate restaurant listings carefully: do not merge different branches
merely because the restaurant name is the same. Use location/address
where available. - Standardize categorical values (case, whitespace,
separators, common spelling variants) without changing their meaning. -
Parse numeric fields robustly. Handle currency symbols, commas, text
suffixes, and malformed values. - Convert rating and cost fields to
numeric values where possible. - Validate plausible ranges based on the
actual dataset. Treat outliers conservatively; do not invent replacement
values. - Normalize cuisine strings into a consistent list
representation. Handle delimiters such as commas, slashes, and
ampersands based on observed data. - Preserve unknown or missing values
as unknown rather than turning them into a false category.

### 6.3 Missing-value strategy

Use field-specific strategies and document them: - Restaurant name: rows
without a usable name should normally be excluded from
recommendations. - Cuisine/location/type: preserve as unknown or "Not
specified"; do not fabricate a value. - Rating: do not automatically
assign a high rating. Either leave missing and apply a documented
neutral treatment, or exclude from rating-based ranking when the user
sets a minimum rating. - Cost: leave missing if it cannot be parsed.
When the user sets a strict maximum budget, decide explicitly whether
unknown-cost restaurants should be excluded; explain this behavior in
the UI. - Boolean fields: normalize only recognized values (e.g. yes/no,
true/false, 1/0). Unknown values remain unknown.

Avoid indiscriminate mean/mode imputation for recommendation attributes.
Imputation can make a restaurant appear to satisfy a preference it does
not actually satisfy.

### 6.4 Encoding and feature preparation

Use suitable representations: - Multi-label cuisine:
`MultiLabelBinarizer` or a controlled multi-hot representation. -
Categorical location/type: one-hot encoding or a controlled token
representation. - Text fields: TF-IDF for meaningful descriptive text if
available. - Numeric rating/cost: scale numeric features for similarity
calculations, but keep raw values for display and rule-based filters. -
Boolean features: map known values to numeric/binary representations,
retaining unknown status.

Use a `ColumnTransformer` or a clearly separated feature-building
pipeline where appropriate. Avoid encoding restaurant IDs, names,
addresses, or other high-cardinality identifiers as if they were
preference signals.

Save the cleaned data and, if useful, the fitted feature artifacts in
`data/processed/` or a clearly documented model-artifact directory.

## 7. Recommendation engine --- content-based filtering

### 7.1 Recommended approach

Implement a transparent **content-based preference scoring model**. The
user preference profile is compared against each restaurant's available
attributes. A practical first version can combine: - Multi-hot cuisine
similarity. - Location match. - Price/budget fit. - Rating quality. -
Restaurant type or dietary match where supported. - Optional text
similarity using TF-IDF if the dataset has meaningful descriptive text.

Use cosine similarity for encoded feature vectors where appropriate. For
numeric preferences such as maximum budget, use a budget-fit score
rather than blindly treating raw cost as a similarity feature.

### 7.2 Candidate filtering and ranking

Use two stages:

**Stage A --- Hard constraints** - Exclude rows that violate explicitly
strict filters, such as a selected locality or a maximum budget, if the
UI communicates them as strict. - Apply a minimum rating as a hard
filter only when the user chooses that behavior. - Do not treat missing
values as a successful match for a strict requirement. - Keep "Any"
preferences out of filtering.

**Stage B --- Relevance ranking** Calculate a normalized score from 0 to
100. Suggested starting weights (make configurable and explain them):

  Component                      Initial weight
  ---------------------------- ----------------
  Cuisine match                            0.40
  Location match                           0.20
  Budget fit                               0.20
  Rating quality                           0.15
  Other supported attributes               0.05

These are initial engineering defaults, not measured truths. Adjust only
after testing. If a component is unsupported or the user did not provide
that preference, redistribute or renormalize the active weights so the
final score remains meaningful. Do not penalize a restaurant for a
preference the user did not specify.

Possible scoring definitions: - **Cuisine:** Jaccard overlap or cosine
similarity between preferred and restaurant cuisine multi-hot vectors. -
**Location:** exact locality match = 1; related/nearby match only if the
data actually provides a defensible relationship; otherwise 0. Avoid
pretending different localities are geographically close. - **Budget:**
1 when comfortably within budget, declining as cost approaches/exceeds
the maximum; if maximum budget is a hard constraint, restaurants above
it should already have been filtered out. - **Rating:** normalize valid
ratings to the known rating scale. Consider rating count only if it
exists; do not compare ratings on different scales without
normalization. - **Other attributes:** exact match or multi-label
overlap for supported fields.

Document the exact formula used in `reports/recommendation_method.md`.

### 7.3 Example scoring structure

Use a configurable weighted score such as:

`score = 100 * sum(active_weight_i * component_score_i) / sum(active_weight_i)`

Where each `component_score_i` is between 0 and 1 and only active user
preferences contribute. Ensure all edge cases are handled: - No active
preference components. - Missing restaurant attributes. - Zero or
invalid numeric values. - Empty cuisine lists. - All candidates filtered
out. - Equal scores.

Tie-breakers should be deterministic, for example by valid rating and
then restaurant name. Do not imply that the score is a probability or a
guarantee of user satisfaction. Label it "Match score" or "Preference
match," not "accuracy."

### 7.4 Recommendation explanations

For each result, generate factual explanation tags from actual matched
data, for example: - "Matches your selected cuisine" - "Within your
budget" - "Located in your selected area" - "Rating meets your minimum"

Only display an explanation when the underlying data supports it. Never
produce unsupported statements such as "near you," "best in the city,"
"highly popular," or "allergy-safe" without evidence.

### 7.5 Optional secondary feature

If time permits, add a "Find restaurants similar to this one" feature
using restaurant content vectors and cosine similarity. Keep it
secondary to the required user-preference workflow.

## 8. Evaluation and validation

The assignment explicitly requires testing with sample user preferences
and evaluating recommendation quality.

### 8.1 Functional test scenarios

Create tests for at least: 1. Cuisine-only preference. 2. Location-only
preference. 3. Budget-only preference. 4. Minimum-rating preference. 5.
Combined cuisine + location + budget. 6. No preference submitted. 7.
Preference combination with no matching restaurants. 8. Dataset rows
with missing cuisine, cost, or rating. 9. Unknown cuisine/location
input. 10. Dataset with optional columns absent.

Tests must use actual dataset values when the dataset is available. If
synthetic fixtures are used for unit tests, label them as test fixtures
and never present them as real restaurants.

### 8.2 Quality evaluation

Do not invent a ground-truth relevance label. If no labeled
preference/restaurant relevance dataset exists, report that limitation.

Use transparent offline checks such as: - Constraint satisfaction rate:
proportion of results satisfying strict filters. - Result completeness:
proportion of returned rows with usable restaurant names. - Duplicate
recommendation rate. - Score ordering sanity: ranked scores should be
non-increasing. - Coverage: number/proportion of dataset restaurants
that can be recommended. - Diversity: number of distinct cuisines or
locations among top-k results, where supported.

For a small manually judged test set, create a CSV with user preference
cases and human relevance judgments, then compute Precision@K / Recall@K
only if relevance labels exist. Clearly label human judgments and sample
size.

Create `reports/evaluation.md` including: - Dataset and test-case
description. - Methodology and metrics. - Actual results produced by
running the application/tests. - Known limitations. - No fabricated
scores or claims.

### 8.3 Unit and integration tests

Test preprocessing, feature construction, ranking, filtering, routes,
and error handling. Use `pytest`. Include deterministic tests for score
calculations and missing-value behavior.

## 9. Web application requirements

Use **Python + Flask** for the web application, consistent with the
reference project style. Use Jinja2 templates and Bootstrap 5 (CDN or
local assets) for a responsive interface. Keep recommendation logic
independent from Flask routes.

### Required pages / states

**Home / preference form** - DineMind brand and concise description. -
Cuisine selector populated from cleaned dataset values. - Location
selector populated from dataset values. - Budget control reflecting
actual dataset units/currency. - Minimum rating control only if rating
exists. - Optional supported filters. - Submit button and reset
action. - Clear note when a preference is unavailable because the
dataset lacks that field.

**Results** - Display top-k recommendations as responsive cards or a
table. - Show restaurant name, cuisine, locality, rating, cost, and
other useful available attributes. - Show match score and factual
explanation tags. - Show a useful empty-state message if no restaurant
matches. - Provide "Edit preferences" action.

**About / methodology** - Explain that DineMind uses content-based
filtering. - Summarize the actual dataset and supported attributes. -
Explain match score at a high level. - State that results are
recommendations based on dataset attributes, not live availability.

### UI quality

-   Clean, modern, food-oriented design; professional and readable.
-   Responsive on desktop and mobile.
-   Accessible labels, keyboard-friendly controls, adequate contrast,
    and visible validation.
-   Do not use the Zomato name, logo, branding, or copied proprietary
    design.
-   Use DineMind consistently in page titles, headers, documentation,
    and screenshots.
-   Do not add fake restaurant photos. If no image URLs exist, use a
    neutral visual placeholder or omit images.

## 10. Backend design and routes

Suggested Flask routes:

  Route          Method   Responsibility
  -------------- -------- ------------------------------------------------
  `/`            GET      Render preference form
  `/recommend`   POST     Validate preferences and render ranked results
  `/about`       GET      Explain dataset and recommendation method
  `/health`      GET      Lightweight health check

Use a service/recommender module rather than implementing scoring inside
route handlers.

Requirements: - Validate all form input server-side. - Restrict numeric
inputs to sensible bounds. - Never trust client-provided column names or
file paths. - Handle malformed requests and missing data gracefully. -
Avoid loading and rebuilding the entire model on every request. Load
cleaned data and reusable feature artifacts once at startup where
practical. - Ensure the app can run from the documented project root. -
Keep debug mode disabled by default outside local development.

## 11. Configuration and reproducibility

Use a configuration module and `.env.example`.

Suggested configuration values: - `DATASET_PATH` -
`PROCESSED_DATA_PATH` - `TOP_K_DEFAULT` - `TOP_K_MAX` - `FLASK_HOST` -
`FLASK_PORT` - `FLASK_DEBUG`

Do not require API keys for the core system. If `.env` is used, add
`.env` to `.gitignore` and commit only `.env.example`.

Pin compatible dependency versions in `requirements.txt` after verifying
installation. Avoid adding unused libraries.

## 12. Suggested project structure

Adapt this structure to the existing repository rather than blindly
overwriting it:

``` text
DineMind/
├── app.py
├── config.py
├── requirements.txt
├── README.md
├── cogni.md
├── .env.example
├── .gitignore
├── data/
│   ├── raw/
│   │   └── .gitkeep
│   └── processed/
│       └── .gitkeep
├── src/
│   ├── __init__.py
│   ├── data_loader.py
│   ├── preprocessing.py
│   ├── feature_builder.py
│   ├── recommender.py
│   ├── explanations.py
│   └── validators.py
├── scripts/
│   ├── inspect_dataset.py
│   └── preprocess_data.py
├── templates/
│   ├── base.html
│   ├── index.html
│   ├── results.html
│   └── about.html
├── static/
│   ├── css/
│   │   └── style.css
│   ├── js/
│   │   └── app.js
│   └── images/
├── tests/
│   ├── conftest.py
│   ├── test_preprocessing.py
│   ├── test_recommender.py
│   └── test_routes.py
└── reports/
    ├── data_profile.md
    ├── recommendation_method.md
    └── evaluation.md
```

Keep modules focused: - `data_loader.py`: load and validate
source/processed data. - `preprocessing.py`: clean and normalize
records. - `feature_builder.py`: create encoded content features. -
`recommender.py`: filter, score, sort, and return results. -
`explanations.py`: produce factual match reasons. - `validators.py`:
validate and normalize user preferences. - `app.py`: Flask
initialization and route orchestration.

## 13. Implementation sequence --- execute in order

### Milestone 1: Inspect and plan

-   Inspect workspace and Drive dataset.
-   Profile the data.
-   Confirm the canonical field mapping.
-   Write `reports/data_profile.md`.
-   Record any missing fields or access blockers.

**Exit condition:** The agent can explain which actual columns will
power each supported preference.

### Milestone 2: Build the preprocessing pipeline

-   Implement loading, cleaning, missing-value handling, duplicate
    handling, parsing, and normalization.
-   Save the cleaned dataset separately.
-   Make the script safe to run more than once.
-   Add preprocessing tests.

**Exit condition:** Running the preprocessing command creates a valid
cleaned dataset and a report without modifying the raw file.

### Milestone 3: Build the recommendation engine

-   Implement feature preparation and preference validation.
-   Implement hard filters and weighted content-based ranking.
-   Implement deterministic sorting and explanation tags.
-   Add unit tests for each score component and edge case.
-   Document the formula and weights.

**Exit condition:** Given valid sample preferences, the engine returns
correctly filtered, ranked, explainable results.

### Milestone 4: Build the web application

-   Implement the preference form and dataset-driven dropdowns.
-   Implement Flask routes and server-side validation.
-   Implement responsive result cards/table.
-   Add empty states and user-friendly error messages.
-   Add the about/methodology page.

**Exit condition:** A user can complete the full
preference-to-recommendation journey in a browser.

### Milestone 5: Evaluate and improve

-   Run all functional scenarios.
-   Run unit and route tests.
-   Calculate supported quality metrics from actual outputs.
-   Review whether strict preferences are respected.
-   Check duplicates, missing fields, ranking order, and diversity.
-   Record actual results and limitations.

**Exit condition:** `reports/evaluation.md` contains reproducible, real
test results.

### Milestone 6: Final polish and handoff

-   Verify all setup commands from a clean environment.
-   Check mobile layout and form accessibility.
-   Remove unused files and debug prints.
-   Confirm `.gitignore` excludes virtual environments, caches, `.env`,
    and large generated artifacts where appropriate.
-   Update README with actual dataset details, screenshots if available,
    commands, architecture, algorithm, tests, and limitations.
-   Provide a concise completion summary with changed files and test
    commands/results.

**Exit condition:** Another developer can clone the repository, follow
README, preprocess the dataset, run the app, and reproduce the tests.

## 14. Commands and developer experience

Provide a reliable Windows-friendly setup. Verify exact commands against
the chosen Python version and dependencies.

Example workflow (adapt if the repository uses another supported setup):

``` powershell
# Create and activate a virtual environment
py -m venv .venv
.\.venv\Scripts\Activate.ps1

# Install dependencies
python -m pip install --upgrade pip
pip install -r requirements.txt

# Inspect the dataset
python scripts/inspect_dataset.py

# Preprocess
python scripts/preprocess_data.py

# Run tests
python -m pytest -q

# Start the web application
python app.py
```

Also document macOS/Linux activation:

``` bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
python scripts/inspect_dataset.py
python scripts/preprocess_data.py
python -m pytest -q
python app.py
```

The app should print the local URL, normally `http://127.0.0.1:5000`.
Confirm the actual configured port.

## 15. Minimum dependency guidance

Select only libraries actually used. A reasonable starting point is:

-   Flask --- web server and routing.
-   pandas --- data loading and cleaning.
-   numpy --- numeric operations.
-   scikit-learn --- preprocessing, encoders, TF-IDF, and cosine
    similarity where needed.
-   joblib --- optional persistence of fitted preprocessing artifacts.
-   python-dotenv --- optional environment configuration.
-   pytest --- tests.

Use Bootstrap for styling through templates. Visualization libraries
such as Matplotlib, Seaborn, or Plotly are optional and should be
included only if an actual analysis page/report needs them. Do not add
TensorFlow or PyTorch: this task does not require a neural network.

## 16. Security, privacy, and reliability

-   Treat the dataset as input, not executable content.
-   Do not use `eval`, unsafe deserialization, or shell commands built
    from user input.
-   Escape user-controlled text in templates; rely on Jinja2
    auto-escaping.
-   Validate all submitted values against known dataset choices or safe
    numeric ranges.
-   Do not expose local file paths or stack traces to end users.
-   Limit result count to a configured maximum.
-   Keep secrets out of Git.
-   Do not collect or store personal user information; preferences can
    be processed per request.
-   Add a clear error if the dataset is unavailable or empty.
-   Log actionable diagnostic information to the server console without
    exposing sensitive data in the UI.

## 17. Definition of done / acceptance checklist

The project is complete only when all applicable items below are
verified:

### Dataset and preprocessing

-   [ ] The supplied Drive folder has been inspected, or the access
    blocker is clearly documented.
-   [ ] The selected dataset and its schema are documented.
-   [ ] Raw data is preserved.
-   [ ] Missing values and duplicates are handled with documented rules.
-   [ ] Categorical fields are normalized/encoded appropriately.
-   [ ] Numeric fields are parsed and validated.
-   [ ] The preprocessing script is repeatable.

### Recommendation engine

-   [ ] Recommendations are driven by user preferences.
-   [ ] Cuisine, location, budget, and rating are supported when the
    dataset contains those fields.
-   [ ] Optional controls are shown only when supported.
-   [ ] Content-based scoring is implemented and documented.
-   [ ] Hard constraints behave as described in the UI.
-   [ ] Scores are bounded and sorted correctly.
-   [ ] Explanations are factual and traceable to dataset values.
-   [ ] Empty/no-match cases are handled.

### Application

-   [ ] DineMind branding is consistent.
-   [ ] Preference form works.
-   [ ] Results page displays actual dataset records.
-   [ ] Responsive layout is usable on desktop and mobile.
-   [ ] Server-side validation and friendly error handling work.
-   [ ] About/methodology information is available.

### Testing and delivery

-   [ ] Unit tests pass.
-   [ ] Flask route/integration tests pass.
-   [ ] Sample preference scenarios have been tested.
-   [ ] Evaluation report uses actual measured results.
-   [ ] README setup instructions have been verified.
-   [ ] `.gitignore` and `.env.example` are present.
-   [ ] The app starts successfully from the documented commands.

Do not mark an item complete unless it has actually been tested.

## 18. Final README requirements

Write a polished `README.md` for **DineMind --- Restaurant
Recommendation System**. Include: 1. Project overview and assignment
objective. 2. Features. 3. Dataset source and actual dataset
description. 4. Actual supported user preferences. 5. Preprocessing
steps. 6. Recommendation algorithm and score formula. 7. Tech stack. 8.
Project structure. 9. Installation and run instructions for Windows and
macOS/Linux. 10. Test commands and actual test status. 11. Sample
user-preference workflow using values that really exist in the dataset.
12. Screenshots, if captured from the working application. 13.
Limitations and future improvements. 14. Developer/author section only
with details supplied by the project owner; do not invent names,
credentials, or links.

Do not copy the reference README's author attribution or sample output.
Do not use the name Zomato anywhere in DineMind branding or project
documentation. Do not include made-up restaurant output.

## 19. Agent execution and final response format

Work autonomously through the milestones where access and environment
permit. Do not ask for confirmation for routine implementation choices.
Ask the user only when a genuine blocker exists, such as inaccessible
private Drive data or an ambiguous dataset that cannot be selected
safely.

At completion, report: - What was implemented. - Dataset file used and
its row/column counts. - Supported preference fields. - Recommendation
algorithm and final weights. - Commands to install, preprocess, test,
and run. - Actual test results. - Local app URL. - Any incomplete items
or limitations.

If blocked, report the exact blocker and the smallest action needed from
the user. Never claim the project is complete merely because code files
were generated.

------------------------------------------------------------------------

## Final instruction

**Build DineMind as a complete, functioning, testable application.**
Prioritize correctness, explainability, reproducibility, and a smooth
user experience. The main acceptance criterion is that a user can
express restaurant preferences and receive relevant, ranked
recommendations from the supplied dataset, with transparent explanations
for each result.
