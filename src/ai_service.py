import os
import json
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


def analyze_tech_article(content):
    # Input: article content (str)
    # Output: analyzed Dict (json)

    # 1. Get path of ai_service.py (src/)
    base_dir = os.path.dirname(os.path.abspath(__file__))

    # 2. Combine the complete path of prompt.txt
    prompt_path = os.path.join(base_dir, "prompts", "tech_p2.txt")

    # ----- Read Prompt -----
    try:
        # 3. Read file
        with open(prompt_path, "r", encoding="utf-8") as f:
            prompt_template = f.read()

        # 4. Fill in article content into prompt
        final_prompt = prompt_template.replace("{content}", content[:10000])

    except FileNotFoundError:
        print(f"❌ Error: Prompt file not found. Please check the path: {prompt_path}")
        return None
    except Exception as e:
        print(f"❌ Error: Failed to read Prompt: {e}")
        return None

    # ----- Feed AI (Updated Syntax) -----
    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=final_prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json"
            )
        )
        return json.loads(response.text)
    
    except Exception as e:
        print(f"❌ AI analysis Failed: {e}")
        return None
    

def categorize_keywords_batch(keywords_list):
    """
    Input: List of strings e.g. ["AI", "NVIDIA", "Musk"]
    Output: Dict e.g. {"AI": "Technology", "NVIDIA": "Company"}
    """
    if not keywords_list:
        return {}

    base_dir = os.path.dirname(os.path.abspath(__file__))
    prompt_path = os.path.join(base_dir, "prompts", "category_p2.txt")

    try:
        with open(prompt_path, "r", encoding="utf-8") as f:
            prompt_template = f.read()
        
        # Turn list into string
        keywords_str = ", ".join(keywords_list)
        final_prompt = prompt_template.replace("{keywords_list}", keywords_str)

        # Updated generation syntax
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=final_prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json"
            )
        )
        return json.loads(response.text)

    except Exception as e:
        print(f"❌ Keyword Categorization Failed: {e}")
        return {}
    

def generate_podcast_script(article_data):
    base_dir = os.path.dirname(os.path.abspath(__file__))
    prompt_path = os.path.join(base_dir, "prompts", "podcast_p1.txt")

    try:
        with open(prompt_path, "r", encoding="utf-8") as f:
            prompt_template = f.read()

        # Fill in variables
        final_prompt = prompt_template.replace("{title}", article_data['title'])
        final_prompt = final_prompt.replace("{summary}", article_data.get('summary', ''))
        final_prompt = final_prompt.replace("{tech_level}", str(article_data.get('tech_level', 5)))
        
        # Truncate content to 15,000 chars for safety
        final_prompt = final_prompt.replace("{content}", article_data.get('content', '')[:15000])

        # Updated generation syntax
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=final_prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json"
            )
        )
        return json.loads(response.text)

    except Exception as e:
        print(f"❌ Podcast Generation Failed: {e}")
        return None