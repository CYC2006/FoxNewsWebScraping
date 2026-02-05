import os
import sys

# Ensure the script can find modules in the src directory
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

# Import functions from your existing modules
try:
    from fox_scraper import run_scraper  # Note: See step 2 below
    from keyword_analyzer import analyze_and_print
    from database_manager import (
        init_db,
        get_db_stats,
        clear_keyword_categories,
        export_to_json,
        search_articles_by_title
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


# Sub-menu for Database Operations
def database_ops_menu():
    while True:
        print("\n" + "-"*30)
        print("🛠️  DATABASE OPERATIONS CENTER")
        print("-"*30)
        print("1. 📈 View Summary Stats")
        print("2. 📦 Export Data to JSON")
        print("3. 🔎 Search Articles")
        print("4. 🧹 Clear Keyword Categories")
        print("5. 🔙 Back to Main Menu")
        print("-"*30)
        
        choice = input("Select an option (1-5): ").strip()
        
        if choice == '1':
            stats = get_db_stats()
            print(f"\n📂 Database Status:")
            print(f" • Total Articles: {stats['articles']}")
            print(f" • Categorized Keywords: {stats['keywords']}")
            
        elif choice == '2':
            print("\n📦 Exporting data...")
            export_to_json("fox_news_backup.json")
            
        elif choice == '3':
            query = input("Enter a keyword to search in titles: ").strip()
            if query:
                results = search_articles_by_title(query)
                print(f"\n🔍 Found {len(results)} matches:")
                for row in results:
                    print(f"   [{row[1]}] {row[0]}") # Date - Title
            else:
                print("Empty query.")

        elif choice == '4':
            print("\n⚠️  WARNING: This will delete all AI-categorized keyword mappings.")
            print("   You will need to re-run the Keyword Analyzer to regenerate them.")
            confirm = input("Are you sure you want to proceed? (yes/no): ").lower()
            
            if confirm == "yes":
                clear_keyword_categories()
            else:
                print("Operation cancelled.")
                
        elif choice == '5':
            break # Return to main loop
            
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
            print("\n🎧 Podcast module is under development...")
            
        elif choice == '5':
            print("\n👋 Goodbye, CYC! Closing dashboard...")
            break
        
        else:
            print("\n⚠️ Invalid choice. Please enter 1 to 5.")


if __name__ == "__main__":
    main()