import google.generativeai as genai
import json
import os

# 建議將 API KEY 設為環境變數，或者暫時填入這裡
# os.environ["GEMINI_API_KEY"] = "你的_API_KEY"

api_key = os.getenv("GOOGLE_API_KEY")
genai.configure(api_key="AIzaSyBV9gulGAwE90lhTAAtItq_du65-zkGlH4") 

def analyze_tech_article(content):
    #  input: aritcle cotent (str)
    # output: analyzed Dict (json)

    model = genai.GenerativeModel("gemini-2.5-flash")

    prompt = f"""
    You are an expert Tech News Analyst.
    Analyze the following article and return the output strictly in JSON format.
    
    Output Schema:
    - summary: A concise summary of the article (max 50 words).
    - keywords: A list of 5-10 technical keywords (e.g., ["LLM", "NVIDIA", "GPU"]).
    - tech_level: An integer from 1 (General Public) to 10 (Expert Engineer).
    (tech_level is for allowing readers to choose articles that suit their level of knowledge)

    Other Precautions:
    - don't mention anything about Fox News
    - don't reply with political stances
    
    Article Content:
    {content[:80000]}
    """

    try:
        response = model.generate_content(
            prompt,
            generation_config={"response_mime_type": "application/json"}
        )
        return json.loads(response.text)
    except Exception as e:
        print(f"AI analysis Failed: {e}")
        return None