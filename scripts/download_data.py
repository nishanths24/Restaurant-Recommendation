import urllib.request
import os

def download_file(file_id, dest_path):
    print(f"Downloading {file_id} to {dest_path}...")
    url = f"https://drive.usercontent.google.com/download?id={file_id}&export=download"
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    try:
        with urllib.request.urlopen(req) as resp, open(dest_path, 'wb') as out:
            data = resp.read()
            out.write(data)
            print(f"Saved {dest_path} ({len(data)} bytes)")
    except Exception as e:
        print(f"Direct download failed: {e}. Trying uc?export=download...")
        url2 = f"https://drive.google.com/uc?export=download&id={file_id}"
        req2 = urllib.request.Request(url2, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req2) as resp, open(dest_path, 'wb') as out:
            data = resp.read()
            out.write(data)
            print(f"Saved {dest_path} ({len(data)} bytes)")

download_file("15ZOqfBTam2MlGjQ8HF1NVrH8UaOnZoay", "data/raw/Dataset .csv")
download_file("1RsEES4Ffttkhoq9blByPdBHyIn3690N2", "reports/Machine Learning.pdf")

