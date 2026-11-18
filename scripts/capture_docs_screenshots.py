import os
import subprocess
import shutil

os.makedirs('docs/screenshots', exist_ok=True)

chrome_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
scratch_dir = r"C:\Users\nisha\.gemini\antigravity\brain\c02b8a20-aff1-4275-b88f-af8967ecb7c1\scratch"

# Copy desktop and mobile hero
if os.path.exists(os.path.join(scratch_dir, 'rendered_desktop_v4.png')):
    shutil.copy(os.path.join(scratch_dir, 'rendered_desktop_v4.png'), 'docs/screenshots/01_homepage_hero.png')
if os.path.exists(os.path.join(scratch_dir, 'rendered_mobile_v2.png')):
    shutil.copy(os.path.join(scratch_dir, 'rendered_mobile_v2.png'), 'docs/screenshots/02_mobile_responsive.png')

# Capture Find, Explore, Cuisines, About
targets = [
    ('docs/screenshots/03_preference_search.png', 'http://127.0.0.1:5000/find'),
    ('docs/screenshots/04_explore_venues.png', 'http://127.0.0.1:5000/explore'),
    ('docs/screenshots/05_cuisines_catalog.png', 'http://127.0.0.1:5000/cuisines'),
    ('docs/screenshots/06_methodology_about.png', 'http://127.0.0.1:5000/about')
]

for out_path, url in targets:
    subprocess.run([
        chrome_path,
        "--headless=new",
        f"--screenshot={out_path}",
        "--window-size=1440,900",
        url
    ], check=True)

print("Screenshots captured successfully:")
for f in sorted(os.listdir('docs/screenshots')):
    p = os.path.join('docs/screenshots', f)
    print(f"  {f} ({os.path.getsize(p)} bytes)")
