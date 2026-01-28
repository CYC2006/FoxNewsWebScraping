import google.generativeai as genai
import json
import os
from dotenv import load_dotenv

# load environment variables in .env
load_dotenv()

# os.environ["GEMINI_API_KEY"] = "你的_API_KEY"
api_key = os.getenv("GOOGLE_API_KEY")

if not api_key:
    raise ValueError("❌ Error: GOOGLE_API_KEY not found!")

genai.configure(api_key=api_key) 

def analyze_tech_article(content):
    #  input: aritcle cotent (str)
    # output: analyzed Dict (json)

    model = genai.GenerativeModel("gemini-2.5-flash")

    # 1. Get path of ai_service.py (src/)
    base_dir = os.path.dirname(os.path.abspath(__file__))

    # 2. Combine the complete path of prompt.txt
    prompt_path = os.path.join(base_dir, "prompts", "tech_prompt2.txt")

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

    # ----- Feed AI -----
    try:
        response = model.generate_content(
            final_prompt,
            generation_config={"response_mime_type": "application/json"}
        )
        return json.loads(response.text)
    
    except Exception as e:
        print(f"AI analysis Failed: {e}")
        return None