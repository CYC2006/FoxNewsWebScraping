import sqlite3
import json
import os
from src.ai_service import generate_podcast_script

DB_NAME = "fox_news.db"

def get_article_by_url(url):
    # Fetches a specific article by its exact URL
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row 
    c = conn.cursor()

    c.execute('''
        SELECT title, summary, content, keyword_counts, tech_level, url 
        FROM articles 
        WHERE url = ?
    ''', (url,))
    
    row = c.fetchone()
    conn.close()

    return dict(row) if row else None


def produce_script_by_url(target_url, target_date):
    # Generates a podcast script for a specifically selected article
    # 1. Get the specific article
    article = get_article_by_url(target_url)
    
    if not article:
        print("❌ Error: Article not found in database.")
        return False

    print(f"✅ Selected Article: {article['title']} (Level: {article['tech_level']})")
    
    # 2. Prepare data for AI 
    try:
        keywords_dict = json.loads(article['keyword_counts'])
    except:
        keywords_dict = {}

    article_data = {
        "title": article['title'],
        "summary": article['summary'],
        "content": article['content'],
        "tech_level": article['tech_level']
    }

    # 3. Generate Script
    print("🎙️ Generating Podcast Script with AI...")
    script_json = generate_podcast_script(article_data)

    if not script_json:
        print("❌ Failed to generate script.")
        return False

    # 4. Display Script nicely
    print("\n" + "="*50)
    print(f"🎧 PODCAST SCRIPT: {target_date}")
    print(f"📺 Topic: {article['title']}")
    print("="*50 + "\n")

    for line in script_json:
        speaker = line.get("speaker", "Unknown")
        emotion = line.get("emotion", "neutral")
        text = line.get("text", "")
        
        if speaker == "Alex":
            prefix = f"\033[92m[{speaker} ({emotion})]\033[0m" # Green
        else:
            prefix = f"\033[96m[{speaker} ({emotion})]\033[0m" # Cyan
            
        print(f"{prefix}: {text}\n")
    
    print("="*50)
    
    # 5. Save to JSON file
    os.makedirs("podcast_scripts", exist_ok=True)
    script_filename = f"podcast_scripts/script_{target_date}.json"
    
    try:
        with open(script_filename, "w", encoding="utf-8") as f:
            json.dump(script_json, f, indent=4, ensure_ascii=False)
        print(f"💾 Script successfully saved to: {script_filename}")
        print("   (You can open this file and edit the text before generating audio)")
        return True
    except Exception as e:
        print(f"❌ Failed to save script: {e}")
        return False