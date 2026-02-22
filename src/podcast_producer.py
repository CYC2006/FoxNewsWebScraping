import sqlite3
import json
import os
from src.ai_service import generate_podcast_script

DB_NAME = "fox_news.db"

def get_best_article_of_day(target_date):
    # Finds the article with the highest tech_level for a specific date.
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row # 讓我們可以用欄位名稱存取
    c = conn.cursor()

    print(f"🔍 Searching for top tech news on {target_date}...")
    
    # SQL Query: 選出日期符合，依照 tech_level 降序排列，只取第 1 筆
    c.execute('''
        SELECT title, summary, content, keyword_counts, tech_level, url 
        FROM articles 
        WHERE published_date = ? 
        ORDER BY tech_level DESC 
        LIMIT 1
    ''', (target_date,))
    
    row = c.fetchone()
    conn.close()

    if row:
        return dict(row)
    else:
        return None

def produce_script(target_date):
    # 1. Get the article
    article = get_best_article_of_day(target_date)
    
    if not article:
        print(f"⚠️ No articles found for date: {target_date}")
        print("   (Check if the date format is YYYY-MM-DD or if you scraped news for that day)")
        return

    print(f"✅ Found Top Article: {article['title']} (Level: {article['tech_level']})")
    
    # 2. Prepare data for AI (Convert JSON string back to dict)
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
        return

    # 4. Display Script nicely
    print("\n" + "="*50)
    print(f"🎧 PODCAST SCRIPT: {target_date}")
    print(f"📺 Topic: {article['title']}")
    print("="*50 + "\n")

    for line in script_json:
        speaker = line.get("speaker", "Unknown")
        emotion = line.get("emotion", "neutral")
        text = line.get("text", "")
        
        # Color coding for terminal (Optional visual effect)
        # Alex (Green), Jamie (Cyan)
        if speaker == "Alex":
            prefix = f"\033[92m[{speaker} ({emotion})]\033[0m" # Green
        else:
            prefix = f"\033[96m[{speaker} ({emotion})]\033[0m" # Cyan
            
        print(f"{prefix}: {text}\n")
    
    print("="*50)

    
    script_filename = f"podcast_scripts/script_{target_date}.json"
    try:
        with open(script_filename, "w", encoding="utf-8") as f:
            json.dump(script_json, f, indent=4, ensure_ascii=False)
        print(f"💾 Script successfully saved as {script_filename}")
        print("   (You can open this file and edit the text before generating audio)")
    except Exception as e:
        print(f"❌ Failed to save script: {e}")