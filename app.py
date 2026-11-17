import os
import sys
from pathlib import Path
from flask import Flask, render_template, request, jsonify, redirect, url_for, abort

# Ensure root directory is on sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from config import Config
from src.data_loader import load_processed_data, load_raw_data
from src.preprocessing import preprocess_dataframe
from src.recommender import RestaurantRecommender

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # 1. Load or prepare processed data
    try:
        if not Config.PROCESSED_DATA_PATH.exists():
            print(f"[DineMind] Cleaned data not found. Auto-preprocessing from {Config.RAW_DATA_PATH}...")
            df_raw = load_raw_data()
            df_clean, _ = preprocess_dataframe(df_raw)
            Config.PROCESSED_DATA_PATH.parent.mkdir(parents=True, exist_ok=True)
            df_clean.to_csv(Config.PROCESSED_DATA_PATH, index=False, encoding="utf-8")
        else:
            df_clean = load_processed_data()
    except Exception as e:
        print(f"[DineMind] Warning: Could not initialize dataset: {e}")
        df_clean = None

    # 2. Initialize Recommender engine
    recommender = RestaurantRecommender(df_clean) if df_clean is not None else None
    app.recommender = recommender
    app.df = df_clean

    @app.route("/", methods=["GET"])
    def index():
        if app.recommender is None:
            return render_template(
                "error.html",
                error_code="500",
                error_title="Dataset Not Initialized",
                error_message="The restaurant dataset could not be loaded. Please run 'python scripts/preprocess_data.py'."
            ), 500
        options = app.recommender.get_filter_options()
        try:
            top_rec = app.recommender.recommend({})
            featured_restaurants = top_rec.get("recommendations", [])[:4]
        except Exception:
            featured_restaurants = []
        return render_template(
            "index.html",
            options=options,
            featured_restaurants=featured_restaurants,
            active_page="home"
        )

    @app.route("/find", methods=["GET"])
    def find_page():
        if app.recommender is None:
            abort(500)
        options = app.recommender.get_filter_options()
        return render_template("find.html", options=options, active_page="find")

    @app.route("/explore", methods=["GET"])
    def explore_page():
        if app.df is None or app.recommender is None:
            abort(500)
            
        city = request.args.get("city", "").strip()
        rating_str = request.args.get("rating", "0.0").strip()
        q = request.args.get("q", "").strip().lower()
        
        try:
            min_rating = float(rating_str)
        except ValueError:
            min_rating = 0.0
            
        sub_df = app.df.copy()
        
        if city:
            sub_df = sub_df[sub_df["city_clean"].str.lower() == city.lower()]
            
        if min_rating > 0:
            sub_df = sub_df[sub_df["aggregate_rating"] >= min_rating]
            
        if q:
            name_match = sub_df["restaurant_name"].str.lower().str.contains(q, na=False)
            cuisine_match = sub_df["cuisines_clean"].str.lower().str.contains(q, na=False)
            sub_df = sub_df[name_match | cuisine_match]
            
        # Sort by rating and votes
        sub_df = sub_df.sort_values(by=["aggregate_rating", "votes"], ascending=[False, False])
        sample_venues = sub_df.head(30).to_dict(orient="records")
        
        return render_template(
            "explore.html",
            restaurants=sample_venues,
            cities=app.recommender.available_cities,
            selected_city=city,
            selected_rating=min_rating,
            search_query=q,
            active_page="explore"
        )

    @app.route("/cuisines", methods=["GET"])
    def cuisines_page():
        if app.df is None or app.recommender is None:
            abort(500)
            
        # Compute count per cuisine
        cuisine_counts = {}
        for c_str in app.df["cuisines_clean"].dropna():
            parts = [p.strip() for p in c_str.split(",") if p.strip() and p.strip() != "Not Specified"]
            for part in parts:
                cuisine_counts[part] = cuisine_counts.get(part, 0) + 1
                
        sorted_cuisines = [
            {"name": k, "count": v}
            for k, v in sorted(cuisine_counts.items(), key=lambda x: -x[1])
        ]
        
        return render_template("cuisines.html", cuisine_data=sorted_cuisines, active_page="cuisines")

    @app.route("/recommend", methods=["POST"])
    def recommend():
        if app.recommender is None:
            abort(500)
            
        raw_prefs = {
            "cuisines": request.form.get("cuisines", ""),
            "city": request.form.get("city", ""),
            "locality": request.form.get("locality", ""),
            "price_range": request.form.get("price_range", ""),
            "max_cost": request.form.get("max_cost", ""),
            "min_rating": request.form.get("min_rating", ""),
            "online_delivery": request.form.get("online_delivery", "any"),
            "table_booking": request.form.get("table_booking", "any"),
            "strict_location": "strict_location" in request.form,
            "strict_budget": "strict_budget" in request.form,
            "strict_rating": "strict_rating" in request.form,
            "top_k": request.form.get("top_k", Config.TOP_K_DEFAULT),
        }
        
        result = app.recommender.recommend(raw_prefs)
        return render_template("results.html", result=result, active_page="find")

    @app.route("/similar/<int:restaurant_id>", methods=["GET"])
    def similar(restaurant_id):
        if app.recommender is None or app.df is None:
            abort(500)
            
        matches = app.df[app.df["restaurant_id"] == restaurant_id]
        if matches.empty:
            return render_template(
                "error.html",
                error_code="404",
                error_title="Restaurant Not Found",
                error_message=f"No venue found with Restaurant ID {restaurant_id} in the dataset."
            ), 404
            
        target_venue = matches.iloc[0].to_dict()
        similar_venues = app.recommender.get_similar_restaurants(restaurant_id, top_k=6)
        
        return render_template(
            "similar.html",
            target=target_venue,
            similar_results=similar_venues,
            active_page="find"
        )

    @app.route("/about", methods=["GET"])
    def about():
        return render_template("about.html", active_page="about")

    @app.route("/health", methods=["GET"])
    def health():
        is_ready = app.recommender is not None
        count = len(app.df) if app.df is not None else 0
        return jsonify({
            "status": "healthy" if is_ready else "degraded",
            "recommender_ready": is_ready,
            "total_restaurants": count,
            "version": "1.0.0"
        }), 200 if is_ready else 503

    @app.errorhandler(404)
    def handle_404(e):
        return render_template(
            "error.html",
            error_code="404",
            error_title="Page Not Found",
            error_message="The requested page or restaurant does not exist."
        ), 404

    @app.errorhandler(500)
    def handle_500(e):
        return render_template(
            "error.html",
            error_code="500",
            error_title="Internal Server Error",
            error_message="An unexpected server error occurred while processing recommendations."
        ), 500

    return app

if __name__ == "__main__":
    app = create_app()
    print(f"\n* DineMind Recommender running on http://{Config.FLASK_HOST}:{Config.FLASK_PORT}")
    app.run(
        host=Config.FLASK_HOST,
        port=Config.FLASK_PORT,
        debug=Config.FLASK_DEBUG
    )
