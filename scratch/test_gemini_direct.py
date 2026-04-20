import google.generativeai as genai
import PIL.Image
import io

# Test with first key
key = "AIzaSyDDt1cafaREiZx0qY6r2XEKiNjsOQgAtgA"
genai.configure(api_key=key)
model = genai.GenerativeModel('gemini-1.5-flash')

try:
    print("Testing Gemini connectivity...")
    # Just a simple text test first
    response = model.generate_content("Hello")
    print(f"Connectivity Success: {response.text}")
except Exception as e:
    print(f"Connectivity Failed: {e}")
