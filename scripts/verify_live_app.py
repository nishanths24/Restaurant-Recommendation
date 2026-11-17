import urllib.request
import urllib.parse
import json
import time
import subprocess
import sys

def verify_live():
    print("Launching DineMind Flask server on 127.0.0.1:5000...")
    proc = subprocess.Popen([sys.executable, "app.py"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    time.sleep(3) # Wait for startup
    
    try:
        # 1. Health check
        print("Testing GET /health...")
        with urllib.request.urlopen("http://127.0.0.1:5000/health", timeout=5) as res:
            assert res.status == 200
            data = json.loads(res.read().decode())
            print(f"  Health OK: status={data['status']}, total_restaurants={data['total_restaurants']}")
            
        # 2. Home page
        print("Testing GET /...")
        with urllib.request.urlopen("http://127.0.0.1:5000/", timeout=5) as res:
            assert res.status == 200
            html = res.read().decode()
            assert "DineMind" in html
            print("  Home page OK (DineMind found)")

        # 3. About page
        print("Testing GET /about...")
        with urllib.request.urlopen("http://127.0.0.1:5000/about", timeout=5) as res:
            assert res.status == 200
            print("  About page OK")

        # 4. Recommend POST
        print("Testing POST /recommend...")
        post_data = urllib.parse.urlencode({
            "cuisines": "North Indian, Mughlai",
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
            assert "Recommended Dining Options" in html
            print("  Recommend POST OK: Returned ranked results")
            
        print("\nAll live HTTP endpoint verifications PASSED!")
    finally:
        print("Stopping Flask test server...")
        proc.terminate()
        try:
            proc.wait(timeout=3)
        except Exception:
            proc.kill()

if __name__ == "__main__":
    verify_live()
