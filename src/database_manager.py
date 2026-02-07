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
            content TEXT,
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
            (url, title, published_date, crawled_at, summary, content, tech_level, keyword_counts, impact_scope, ai_full_json)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            article_data["url"],
            article_data["title"],
            article_data["published_date"],
            article_data["crawled_at"],
            ai_result.get("summary", "N/A"),
            article_data["content"],
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


# ===== Database Operations from User =====

# opt1. Advanced search for the CLI dashboard
def search_articles_advanced(query=None, search_type="title"):

    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    
    if not query:
        # If no query, return the latest 20 articles
        c.execute("SELECT title, published_date, tech_level, url, summary FROM articles ORDER BY published_date DESC LIMIT 20")
    
    elif search_type == "date":
        # Search by exact date
        c.execute("SELECT title, published_date, tech_level, url, summary FROM articles WHERE published_date = ?", (query,))
        
    else:
        # Search by title keyword (Case insensitive)
        c.execute("SELECT title, published_date, tech_level, url, summary FROM articles WHERE title LIKE ?", (f'%{query}%',))
        
    results = c.fetchall()
    conn.close()
    return results

def delete_article(url):
    """Deletes a single article by its URL."""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    try:
        c.execute("DELETE FROM articles WHERE url = ?", (url,))
        conn.commit()
        return c.rowcount > 0
    except Exception as e:
        print(f"Error deleting article: {e}")
        return False
    finally:
        conn.close()

# opt2. Returns a dictionary containing database statistics
def get_db_stats():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM articles")
    article_count = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM keyword_metadata")
    keyword_count = c.fetchone()[0]
    conn.close()
    return {"articles": article_count, "keywords": keyword_count}


# opt3. Exports all articles from SQLite to a JSON file
def export_to_json(filename = "fox_news_export.json"):
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row # This allows accessing columns by name
    c = conn.cursor()
    
    c.execute("SELECT * FROM articles")
    rows = c.fetchall()
    
    # Convert SQLite rows to a list of dicts
    data = [dict(row) for row in rows]
    
    try:
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        print(f"📦 Export successful! Saved to {filename}")
    except Exception as e:
        print(f"❌ Export failed: {e}")
    finally:
        conn.close()


# opt4. Clear the keyword_metadata table (for re-run AI categorization with new prompt)
def clear_keyword_categories():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("DELETE FROM keyword_metadata")
    deleted_count = c.rowcount
    conn.commit()
    conn.close()
    print(f"🧹 Database Cleaned: Removed {deleted_count} keyword categories.")


'''
# Simple search function to find articles containing a specific keyword
def search_articles_by_title(keyword):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    
    # SQL LIKE query for partial matching
    c.execute("SELECT title, published_date, url, tech_level FROM articles WHERE title LIKE ?", (f'%{keyword}%',))
    results = c.fetchall()
    conn.close()
    return results
'''