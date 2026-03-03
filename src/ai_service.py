import os
import json
import time
from dotenv import load_dotenv

# Import the NEW google genai SDK
from google import genai
from google.genai import types

# Load environment variables
load_dotenv()

api_key = os.getenv("GOOGLE_API_KEY")

if not api_key:
    raise ValueError("❌ Error: GOOGLE_API_KEY not found!")

# Initialize the new Client
client = genai.Client(api_key=api_key)

# Exponential Backoff
# a network error-handling strategy where the wait time between retries increases exponentially (e.g., 1s, 2s, 4s) after each failed attempt

def call_gemini_with_retry(prompt, model_name='gemini-2.5-flash', retries=3, initial_delay=5):
    # using Exponential Backoff to call Gemini
    delay = initial_delay
    for i in range(retries):
        try:
            response = client.models.generate_content(
                model=model_name,
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json"
                )
            )
            return json.loads(response.text)
        
        except Exception as e:
            error_msg = str(e)
            # retry errors like 503 or 429
            if ("503" in error_msg or "429" in error_msg) and i < retries - 1:
                print(f"⚠️ API Busy ({'503' if '503' in error_msg else '429'}). "
                      f"Retrying in {delay}s... (Attempt {i+1}/{retries})")
                time.sleep(delay)
                delay *= 2  # Exponontial
                continue
            else:
                print(f"❌ Gemini API Call Failed: {e}")
                return None

def analyze_tech_article(content):
    base_dir = os.path.dirname(os.path.abspath(__file__))
    prompt_path = os.path.join(base_dir, "prompts", "tech_p2.txt")

    try:
        with open(prompt_path, "r", encoding="utf-8") as f:
            prompt_template = f.read()
        final_prompt = prompt_template.replace("{content}", content[:10000])
    except Exception as e:
        print(f"❌ Error reading Prompt: {e}")
        return None

    # retry
    return call_gemini_with_retry(final_prompt)

def categorize_keywords_batch(keywords_list):
    if not keywords_list:
        return {}

    base_dir = os.path.dirname(os.path.abspath(__file__))
    prompt_path = os.path.join(base_dir, "prompts", "category_p2.txt")

    try:
        with open(prompt_path, "r", encoding="utf-8") as f:
            prompt_template = f.read()
        keywords_str = ", ".join(keywords_list)
        final_prompt = prompt_template.replace("{keywords_list}", keywords_str)
    except Exception as e:
        print(f"❌ Error reading Category Prompt: {e}")
        return {}

    # retry
    result = call_gemini_with_retry(final_prompt)
    return result if result else {}

def generate_podcast_script(article_data):
    base_dir = os.path.dirname(os.path.abspath(__file__))
    prompt_path = os.path.join(base_dir, "prompts", "podcast_p2.txt")

    try:
        with open(prompt_path, "r", encoding="utf-8") as f:
            prompt_template = f.read()

        final_prompt = prompt_template.replace("{title}", article_data['title'])
        final_prompt = final_prompt.replace("{summary}", article_data.get('summary', ''))
        final_prompt = final_prompt.replace("{tech_level}", str(article_data.get('tech_level', 5)))
        final_prompt = final_prompt.replace("{content}", article_data.get('content', '')[:15000])
    except Exception as e:
        print(f"❌ Error reading Podcast Prompt: {e}")
        return None

    # 使用重試機制呼叫
    return call_gemini_with_retry(final_prompt)