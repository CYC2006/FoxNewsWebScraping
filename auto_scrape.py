import sys
from datetime import datetime

# Import the scraper function
try:
    from src.fox_scraper import run_scraper
except ImportError as e:
    print(f"❌ Initialization Error: {e}")
    sys.exit(1)

def main():
    # Record the start time
    start_time = datetime.now()
    time_str = start_time.strftime('%Y-%m-%d %H:%M:%S')
    
    print("=" * 60)
    print(f"[{time_str}] 🤖 Starting automated scraper job...")
    print("=" * 60)
    
    try:
        # Execute the scraping logic
        run_scraper()
        
        # Calculate execution duration
        end_time = datetime.now()
        duration = end_time - start_time
        print("=" * 60)
        print(f"[{end_time.strftime('%Y-%m-%d %H:%M:%S')}] ✅ Job completed successfully in {duration}.")
        
    except Exception as e:
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ❌ Job failed with error: {e}")
    
    print("=" * 60 + "\n")

if __name__ == "__main__":
    main()