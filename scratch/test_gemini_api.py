import requests
import os

url = "http://127.0.0.1:8000/api/ocr/gemini"
# Find any image in the current dir or subdirs to test
image_path = None
for root, dirs, files in os.walk("."):
    for file in files:
        if file.endswith((".png", ".jpg", ".jpeg")):
            image_path = os.path.join(root, file)
            break
    if image_path: break

if not image_path:
    print("No image found to test with.")
else:
    print(f"Testing with image: {image_path}")
    with open(image_path, "rb") as f:
        files = {"file": f}
        try:
            response = requests.post(url, files=files)
            print(f"Status Code: {response.status_code}")
            print(f"Response: {response.text}")
        except Exception as e:
            print(f"Request failed: {e}")
