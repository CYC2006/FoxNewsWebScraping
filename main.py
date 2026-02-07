import os
import sys

# Import functions from your existing modules
try:
    from src.fox_scraper import run_scraper  # Note: See step 2 below
    from src.keyword_analyzer import analyze_and_print
    from src.podcast_producer import produce_script
    from src.database_manager import (
        init_db,
        search_articles_advanced,
        delete_article,
        get_db_stats,
        export_to_json,
        clear_keyword_categories
    )
except ImportError as e:
    print(f"❌ Initialization Error: {e}")


def display_menu():
    print("\n" + "="*40)
    print("🚀 TECH NEWS ANALYSIS DASHBOARD")
    print("="*40)
    print("1. 🔍 Fetch & Analyze Daily News")
    print("2. 📊 Generate Keyword Analysis Report")
    print("3. 🗄️  Database Operations")
    print("4. 🎙️  Generate Podcast Script (Coming Soon)")
    print("5. 🚪 Exit")
    print("="*40)


# main.py

def manage_articles_ui():
    """
    Interactive UI for Searching, Viewing, and Deleting articles.
    Flow: Search -> List with IDs -> Select ID -> Action
    """
    while True:
        print("\n" + "-"*30)
        print("🔎 ARTICLE MANAGER")
        print("-" * 30)
        print("1. 📅 List by Date")
        print("2. ⌨️  Search by Keyword")
        print("3. 🆕 Show Recent Articles")
        print("4. 🔙 Back")
        
        search_choice = input("Select search method (1-4): ").strip()
        
        results = []
        
        # --- PHASE 1: SEARCH ---
        if search_choice == '1':
            date_query = input("Enter Date (YYYY-MM-DD): ").strip()
            results = search_articles_advanced(date_query, search_type="date")
            
        elif search_choice == '2':
            keyword = input("Enter Keyword (e.g., AI, Apple): ").strip()
            results = search_articles_advanced(keyword, search_type="title")
            
        elif search_choice == '3':
            results = search_articles_advanced(query=None) # Get recent
            
        elif search_choice == '4':
            return # Back to DB menu
            
        else:
            print("❌ Invalid choice.")
            continue

        # --- PHASE 2: LIST & SELECT ---
        if not results:
            print("❌ No articles found.")
            continue
            
        print(f"\n✅ Found {len(results)} articles:")
        print(f"{'ID':<3} | {'Date':<12} | {'Level':<5} | {'Title'}")
        print("-" * 60)
        
        # Enumerate creates a temporary index (1, 2, 3...) for the user
        for idx, row in enumerate(results, 1):
            # row = (title, date, level, url, summary)
            print(f"{idx:<4} | {row[1]:<12} | {row[2]:<5} | {row[0][:40]}...")

        # --- PHASE 3: ACTION ---
        try:
            selection = input("\nSelect ID to manage (or Press Enter to cancel): ").strip()
            if not selection:
                continue
                
            sel_idx = int(selection) - 1
            
            if 0 <= sel_idx < len(results):
                target_article = results[sel_idx]
                # Unpack the tuple
                title, date, level, url, summary = target_article
                
                print("\n" + "="*40)
                print(f"📄 SELECTED: {title}")
                print(f"🔗 URL: {url}")
                print(f"📝 Summary: {summary[:100]}...")
                print("="*40)
                
                action = input("Actions: (D)Delete / (V)View Full / (C)Cancel: ").upper().strip()
                
                if action == 'D':
                    confirm = input(f"⚠️ Are you sure you want to delete this article? (y/n): ").lower()
                    if confirm == 'y':
                        if delete_article(url):
                            print("🗑️  Article Deleted Successfully.")
                        else:
                            print("❌ Deletion Failed.")
                            
                elif action == 'V':
                    print("\n--- Full Summary ---")
                    print(summary)
                    input("\nPress Enter to continue...")
                    
                else:
                    print("Operation Cancelled.")
            else:
                print("❌ Invalid ID Number.")
                
        except ValueError:
            print("❌ Please enter a valid number.")


def database_ops_menu():
    """Main Database Operations Menu"""
    while True:
        print("\n" + "="*40)
        print("🛠️  DATABASE OPERATIONS CENTER")
        print("="*40)
        print("1. 🔎 Search & Manage Articles (Delete/View)")  # Unified Entry
        print("2. 📈 View Summary Stats")
        print("3. 📦 Export Data to JSON")
        print("4. 🧹 Clear Keyword Categories")
        print("5. 🔙 Back to Main Menu")
        print("="*40)
        
        choice = input("Select option (1-5): ").strip()
        
        if choice == '1':
            manage_articles_ui() # Enter the new interactive UI
            
        elif choice == '2':
            stats = get_db_stats()
            print(f"\n📂 Database Status:")
            print(f"   • Total Articles: {stats['articles']}")
            print(f"   • Categorized Keywords: {stats['keywords']}")
            
        elif choice == '3':
            export_to_json()
            
        elif choice == '4':
            confirm = input("⚠️ Clear all AI categories? (y/n): ").lower()
            if confirm == 'y':
                clear_keyword_categories()
                
        elif choice == '5':
            break
        else:
            print("Invalid choice.")


def main():
    init_db()

    while True:
        display_menu()
        choice = input("Select an option (1-5): ").strip()

        if choice == '1':
            print("\n📡 Starting Fox News Scraper...")
            run_scraper() 
        
        elif choice == '2':
            print("\n🔄 Running Keyword Analyzer...")
            analyze_and_print()
            
        elif choice == '3':
            database_ops_menu()

        elif choice == '4':
            print("\n🎧 Podcast Generator")
            date_input = input("Enter the date (YYYY-MM-DD) to generate script: ").strip()
            
            # Use datetime.strptime for strict validation
            from datetime import datetime
            try:
                # This checks both format and logical date validity
                valid_date = datetime.strptime(date_input, "%Y-%m-%d")
                
                # If valid, proceed to generate script
                produce_script(date_input)
                
            except ValueError:
                # This catches cases like '2026-13-01' or '2026-02-30' or 'abc'
                print(f"❌ Invalid date or format: '{date_input}'")
                print("   Please use the standard YYYY-MM-DD format (e.g., 2026-02-07)")
            
        elif choice == '5':
            print("\n👋 Goodbye, CYC! Closing dashboard...")
            break
        
        else:
            print("\n⚠️ Invalid choice. Please enter 1 to 5.")


if __name__ == "__main__":
    main()