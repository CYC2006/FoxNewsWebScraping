import os
import sys

# Ensure the script can find modules in the src directory
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

# Import functions from your existing modules
try:
    from fox_scraper import run_scraper  # Note: See step 2 below
    from keyword_analyzer import analyze_and_print
    from database_manager import init_db
    from database_manager import clear_categories
except ImportError as e:
    print(f"❌ Initialization Error: {e}")

def display_menu():
    print("\n" + "="*40)
    print("TECH NEWS ANALYSIS DASHBOARD")
    print("="*40)
    print("1. Fetch & Analyze Daily News")
    print("2. Generate Keyword Analysis Report")
    print("3. View Database Summary Stats")
    print("4. Generate Podcast Script (Coming Soon)")
    print("5. Clear all categories in Database")
    print("6. Exit")
    print("="*40)

# Show Database Stats
def view_db_summary():
    import sqlite3
    conn = sqlite3.connect("fox_news.db")
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM articles")
    article_count = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM keyword_metadata")
    keyword_count = c.fetchone()[0]
    conn.close()
    
    print(f"\n📂 Database Status:")
    print(f"   • Total Articles: {article_count}")
    print(f"   • Categorized Keywords: {keyword_count}")

def main():
    init_db()

    while True:
        display_menu()
        choice = input("Select an option (1-5): ").strip()

        if choice == '1':
            print("\n📡 Starting Fox News Scraper...")
            # We wrap your scraper logic into a function for better control
            run_scraper() 
        
        elif choice == '2':
            print("\n🔄 Running Keyword Analyzer...")
            analyze_and_print()
            
        elif choice == '3':
            view_db_summary()
            
        elif choice == '4':
            print("\n🎧 Podcast module is under development...")
            # You can call your upcoming podcast_producer script here
            
        elif choice == '5':
            clear_categories()
            
        elif choice == '6':
            print("\n👋 Goodbye! Closing dashboard...")
            break
        
        else:
            print("\n⚠️ Invalid choice. Please enter 1 to 5.")
        
        input("\nPress Enter to return to menu...")

if __name__ == "__main__":
    main()