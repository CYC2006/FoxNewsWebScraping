import google.generativeai as genai

API_KEY = "AIzaSyBV9gulGAwE90lhTAAtItq_du65-zkGlH4"
genai.configure(api_key=API_KEY)

print(f"Querying available models using Key: {API_KEY[:10]}...")
print("-" * 60)

try:
    # 列出所有模型
    found_any = False
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            print(f"✅ Model Name: {m.name}")
            found_any = True
            
    if not found_any:
        print("❌ Connection Successful, but no models supporting generateContent were found.")

except Exception as e:
    print(f"❌ Error: {e}")

print("-" * 60)