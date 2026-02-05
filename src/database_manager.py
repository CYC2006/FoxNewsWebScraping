import sqlite3
import json
import os

DB_NAME = "fox_news.db"

def init_db():
    # Initialize the SQLite database and create the 'articles' table if it doesn't exist.
    # Ensure the database file is created in the same directory as the script or project root
    # Here we use relative path, assuming running from project root.
    
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    
    # Create table with flattened fields for easy querying
    # 'url' is the PRIMARY KEY to prevent duplicate entries
    c.execute('''
        CREATE TABLE IF NOT EXISTS articles (
            url TEXT PRIMARY KEY,
            title TEXT,
            published_date TEXT,    -- Format: YYYY-MM-DD
            crawled_at TEXT,
            summary TEXT,
            tech_level INTEGER,
            keyword_counts TEXT,    -- Stored as JSON string
            impact_scope TEXT,      -- Stored as JSON string
            ai_full_json TEXT       -- Backup of full AI response
        )
    ''')

    # Create table for persistent keyword categories
    c.execute('''
        CREATE TABLE IF NOT EXISTS keyword_metadata (
            keyword TEXT PRIMARY KEY,
            category TEXT
        )
    ''')
    
    conn.commit()
    conn.close()
    print(f"[Database] Initialized {DB_NAME} successfully.")


def is_article_exists(url):
    # Check if an article URL already exists in the database
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    # Query for the existence of the URL
    c.execute("SELECT 1 FROM articles WHERE url = ?", (url,))
    result = c.fetchone()
    
    conn.close()

    # Returns True if exists, False otherwise
    return result is not None


def save_article_to_db(article_data):
    # Save a single article to the database.
    # Ignores the insert if the URL already exists (Deduplication).

    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    try:
        # Extract AI analysis data
        ai_result = article_data.get("ai_analysis", {})
        
        # Prepare data for insertion
        # Convert List/Dict objects to JSON strings for SQLite storage
        keyword_counts_str = json.dumps(ai_result.get("keyword_counts", {}), ensure_ascii=False)
        impact_scope_str = json.dumps(ai_result.get("impact_scope", []), ensure_ascii=False)
        full_json_str = json.dumps(ai_result, ensure_ascii=False)

        # INSERT OR IGNORE: The magic command for deduplication based on Primary Key (url)
        c.execute('''
            INSERT OR IGNORE INTO articles 
            (url, title, published_date, crawled_at, summary, tech_level, keyword_counts, impact_scope, ai_full_json)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            article_data["url"],
            article_data["title"],
            article_data["published_date"],
            article_data["crawled_at"],
            ai_result.get("summary", "N/A"),
            ai_result.get("tech_level", 0),
            keyword_counts_str,
            impact_scope_str,
            full_json_str
        ))
        
        conn.commit()
        
        # Check if the row was actually inserted
        if c.rowcount > 0:
            print(f"✅ [Database] Saved: {article_data['title'][:30]}...")
            return True
        else:
            print(f"⚠️ [Database] Skipped duplicate: {article_data['title'][:30]}...")
            return False

    except Exception as e:
        print(f"❌ [Database] Insert Error: {e}")
        return False
    finally:
        conn.close()


def clear_categories():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    
    # 清除所有已儲存的關鍵字分類，強迫下次重新分析
    print("🧹 Cleaning keyword_metadata table...")
    c.execute("DELETE FROM keyword_metadata")
    
    conn.commit()
    conn.close()
    print("✅ Database cleaned! You can now run the analyzer again.")