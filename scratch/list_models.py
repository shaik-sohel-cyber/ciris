import google.generativeai as genai

key = "AIzaSyDDt1cafaREiZx0qY6r2XEKiNjsOQgAtgA"
genai.configure(api_key=key)

try:
    print("Available models:")
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            print(m.name)
except Exception as e:
    print(f"Failed to list models: {e}")
