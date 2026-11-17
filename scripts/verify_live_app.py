import urllib.request
import urllib.parse
import json
import time
import subprocess
import sys

def verify_live():
    print("Launching DineMind Flask server on 127.0.0.1:5000...")
    proc = subprocess.Popen([sys.executable, "app.py"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    
    # Retry loop waiting for server to bind port
    connected = False
    for attempt in range(15):
        time.sleep(1)
        try:
            with urllib.request.urlopen("http://127.0.0.1:5000/health", timeout=2) as res:
                if res.status == 200:
                    connected = True
                    break
        except Exception:
            continue
            
    if not connected:
        proc.terminate()
        stdout, _ = proc.communicate(timeout=3)
        print("Server output:\n", stdout)
        raise RuntimeError("Server failed to respond on 127.0.0.1:5000")
        
    try:
        # 1. Health check
        print("Testing GET /health...")
        with urllib.request.urlopen("http://127.0.0.1:5000/health", timeout=5) as res:
            assert res.status == 200
            data = json.loads(res.read().decode())
            print(f"  [OK] Health check: status={data['status']}, total_restaurants={data['total_restaurants']}")
            
        # 2. Home page (Hero, Design Language, and Layout)
        print("Testing GET / (Homepage Hero & Luxury Theme)...")
        with urllib.request.urlopen("http://127.0.0.1:5000/", timeout=5) as res:
            assert res.status == 200
            html = res.read().decode()
            assert "DineMind" in html
            assert "Discover restaurants" in html
            assert "you'll love." in html
            assert "Find My Restaurant" in html
            assert "Explore Restaurants" in html
            assert "Personalized Recommendations" in html
            assert "Explore Global Cuisines" in html
            assert "Smart Budget Matching" in html
            assert "9,551" in html
            assert "146" in html
            assert "140" in html
            assert "hero_dish.jpg" in html
            print("  [OK] Homepage: Hero, 3 feature cards, stats (9,551/146/140), and dish visual verified")

        # 3. Find Restaurants page
        print("Testing GET /find (Preference Form)...")
        with urllib.request.urlopen("http://127.0.0.1:5000/find", timeout=5) as res:
            assert res.status == 200
            html = res.read().decode()
            assert "Preferred Cuisines" in html
            assert "Destination & Locality" in html
            print("  [OK] Find Restaurants page verified")

        # 4. Explore Restaurants page
        print("Testing GET /explore (Venue Discovery)...")
        with urllib.request.urlopen("http://127.0.0.1:5000/explore", timeout=5) as res:
            assert res.status == 200
            html = res.read().decode()
            assert "Explore Verified Restaurants" in html
            print("  [OK] Explore Restaurants page verified")

        # 5. Explore Cuisines page
        print("Testing GET /cuisines (146 Cuisines Directory)...")
        with urllib.request.urlopen("http://127.0.0.1:5000/cuisines", timeout=5) as res:
            assert res.status == 200
            html = res.read().decode()
            assert "Global Cuisines Catalog" in html
            assert "North Indian" in html
            print("  [OK] Cuisines Directory page verified")

        # 6. About page
        print("Testing GET /about (Methodology)...")
        with urllib.request.urlopen("http://127.0.0.1:5000/about", timeout=5) as res:
            assert res.status == 200
            print("  [OK] About page verified")

        # 7. Recommend POST
        print("Testing POST /recommend...")
        post_data = urllib.parse.urlencode({
            "cuisines": "Italian, Pizza",
            "city": "New Delhi",
            "price_range": "2",
            "min_rating": "3.5",
            "top_k": "5",
            "strict_location": "true"
        }).encode("utf-8")
        req = urllib.request.Request("http://127.0.0.1:5000/recommend", data=post_data, method="POST")
        with urllib.request.urlopen(req, timeout=5) as res:
            assert res.status == 200
            html = res.read().decode()
            assert "Curated Dining Matches" in html
            print("  [OK] Recommend POST returned ranked matches")

        # 8. Similar venues endpoint
        print("Testing GET /similar/6317637...")
        with urllib.request.urlopen("http://127.0.0.1:5000/similar/6317637", timeout=5) as res:
            assert res.status == 200
            print("  [OK] Similar venues endpoint verified")
            
        print("\nAll 8 live HTTP endpoints & navigation actions VERIFIED SUCCESSFULLY!")
    finally:
        print("Stopping Flask server...")
        proc.terminate()
        try:
            proc.wait(timeout=3)
        except Exception:
            proc.kill()

if __name__ == "__main__":
    verify_live()
