import sqlite3
import json
from collections import Counter
from ai_service import categorize_keywords_batch

DB_NAME = "fox_news.db"

def get_persisted_categories():
    """Fetch all previously categorized keywords from the database."""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT keyword, category FROM keyword_metadata")
    mapping = dict(c.fetchall())
    conn.close()
    return mapping

def save_new_categories(category_dict):
    """Save newly identified keyword categories to the database."""
    if not category_dict:
        return
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    # Using INSERT OR IGNORE to ensure no conflicts with existing keys
    data = [(kw, cat) for kw, cat in category_dict.items()]
    c.executemany("INSERT OR IGNORE INTO keyword_metadata (keyword, category) VALUES (?, ?)", data)
    conn.commit()
    conn.close()

def analyze_and_print():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    # 1. Extraction: Get all keyword counts (JSON strings) from articles
    print("📥 Reading data from database...")
    c.execute("SELECT keyword_counts FROM articles")
    rows = c.fetchall()
    conn.close()

    if not rows:
        print("No articles found in database.")
        return

    # 2. Aggregation: Sum up frequencies using Counter
    total_counter = Counter()
    for row in rows:
        json_str = row[0]
        if json_str:
            try:
                k_dict = json.loads(json_str)
                total_counter.update(k_dict)
            except json.JSONDecodeError:
                continue

    unique_keywords = list(total_counter.keys())
    print(f"📊 Total unique keywords found: {len(unique_keywords)}")

    # 3. Incremental Categorization Logic
    # Load existing categories from DB
    existing_categories = get_persisted_categories()
    
    # Identify keywords that have never been categorized by AI
    new_keywords = [kw for kw in unique_keywords if kw not in existing_categories]

    if new_keywords:
        print(f"🤖 Found {len(new_keywords)} new keywords. Asking AI to categorize...")
        # Only send the NEW keywords to Gemini to save tokens
        new_category_map = categorize_keywords_batch(new_keywords)
        
        # Persist new findings to the database
        save_new_categories(new_category_map)
        
        # Update local mapping for the current report
        existing_categories.update(new_category_map)
    else:
        print("✨ All keywords are already categorized in the database.")

    # 4. Grouping and Visualization
    grouped_results = {}
    for kw, count in total_counter.most_common():
        cat = existing_categories.get(kw, "Uncategorized")
        if cat not in grouped_results:
            grouped_results[cat] = []
        grouped_results[cat].append((kw, count))

    # 5. Formatted CLI Output
    print("\n" + "="*50)
    print("🔥 AGGREGATED KEYWORDS REPORT (Persistent) 🔥")
    print("="*50)

    preferred_order = ["Technology", "Company", "Person", "Economy", "Product", "Location", "Other"]
    all_categories = preferred_order + [k for k in grouped_results.keys() if k not in preferred_order]

    for cat in all_categories:
        if cat in grouped_results:
            print(f"\n📂 [{cat}]")
            print("-" * 30)
            # Show top 10 items per category
            for kw, count in grouped_results[cat][:10]: 
                print(f" • {kw:<25} : {count} times")

    print("\n" + "="*50)

if __name__ == "__main__":
    analyze_and_print()