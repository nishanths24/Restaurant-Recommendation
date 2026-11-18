import urllib.request
import urllib.parse
import json
import time
import subprocess
import sys

def verify_live():
    # Check if server is already running on port 5000
    already_running = False
    try:
        with urllib.request.urlopen("http://127.0.0.1:5000/health", timeout=2) as res:
            if res.status == 200:
                already_running = True
                print("DineMind server is already running on 127.0.0.1:5000.")
    except Exception:
        pass

    proc = None
    if not already_running:
        print("Launching DineMind Flask server on 127.0.0.1:5000...")
        proc = subprocess.Popen([sys.executable, "app.py"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
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
            if proc:
                proc.terminate()
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
            assert "Where Every Taste" in html
            assert "Finds Its Place" in html
            assert "Discover Restaurants" in html
            assert "Explore Cuisines" in html
            assert "Tonight's Discoveries" in html
            assert "hero_dish.jpg" in html
            print("  [OK] Homepage: Editorial Hero, Tonights Discoveries, and dish visual verified")

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
        if proc:
            print("Stopping Flask server...")
            proc.terminate()
            try:
                proc.wait(timeout=3)
            except Exception:
                proc.kill()

if __name__ == "__main__":
    verify_live()
