import requests
import time # avoid DDoS detection
import json
from bs4 import BeautifulSoup
from datetime import datetime

# Import AI module
from ai_service import analyze_tech_article
# Import Database module
from database_manager import init_db, save_article_to_db

# Helper function to convert Fox News date to YYYY-MM-DD
def parse_fox_date(date_parts):
    try:
        raw_date_str = f"{date_parts[0]} {date_parts[1]} {date_parts[2]}"
        raw_date_str = raw_date_str.replace(",", "")

        # Parse and format
        dt_obj = datetime.strptime(raw_date_str, "%B %d %Y")
        return dt_obj.strftime("%Y-%m-%d")
    
    except Exception as e:
        print(f"⚠️ Date parsing failed: {date_parts} | Error: {e}")
        return datetime.now().strftime("%Y-%m-%d") # Fallback to today


# ----- Main Logic -----

# Initialize Database
init_db()

# Cmd + Shift + C on the web to check every objects' code
url = "https://www.foxnews.com/tech"
headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"
}

# request
try:
    res = requests.get(url, headers=headers)
    res.raise_for_status()
except Exception as e:
    print(f"❌ Connection Error: {e}")
    exit()

soup = BeautifulSoup(res.text, "html.parser")
articles = soup.find_all("article")

print("-" * 82)
article_count = 0


# Run for every fox news articles
for a in articles:
    # Find Tech Articles within a day -----------------

    # 1. Find time tag (in class="meta")
    meta_tag = a.find("div", class_="meta")
    is_today = False

    if meta_tag:
        time_text = meta_tag.get_text(separator=" ", strip=True).lower()
        # print(time_text)
        
        # 2. Filter out the news within a day
        if "min" in time_text or "hour" in time_text:
            is_today = True

        if "1 day ago" in time_text:
            is_today = True

        if "video" in time_text: # no video clip
            is_today = False

        if not is_today:
            continue

        time_text_arr = time_text.split(' ')
        category = ""

        while (time_text_arr and not str.isdigit(time_text_arr[0])):
            category += (time_text_arr[0].capitalize() + " ")
            del time_text_arr[0]

        print(f"Article {article_count+1}", end=" | ")

        # Handle case where time_text_arr might be empty after processing
        if len(time_text_arr) >= 3:
            print(category + "| ", end="")
            print(time_text_arr[0] + " " + time_text_arr[1] + " " + time_text_arr[2], end=" | ")
        else:
            print(category + "| Time Parsing format unexpected | \n")

    # -------------------------------------------------

    # Enter Article Content ---------------------------
    # 1. Find <title> tag in <article>
    title_header = a.find("h4", class_="title")
    if title_header:
        link_tag = title_header.find("a")
        if link_tag:
            title = link_tag.get_text(strip=True)

            # 2. Get article relative url
            relative_url = link_tag.get("href")
            # 3. Complete full Fox News url
            full_url = relative_url if relative_url.startswith("http") else f"https://www.foxnews.com{relative_url}"
            
            try:
                # 4. Request article detail page
                detail_res = requests.get(full_url, headers=headers, timeout=10)
                detail_soup = BeautifulSoup(detail_res.text, "html.parser")

                # 5. Record Published Date
                formatted_date = datetime.now().strftime("%Y-%m-%d")

                date_span = detail_soup.find("span", class_="article-date")
                if date_span:
                    time_tag = date_span.find("time")
                    if time_tag:
                        raw_time_text = time_tag.get_text(strip=True)
                        time_parts = raw_time_text.split(' ')
                        if len(time_parts) >= 3:
                            formatted_date = parse_fox_date(time_parts[:3])
                
                # 6. Extract Content (.article-body)
                body = detail_soup.find("div", class_="article-body")
                
                if body:
                    # 7. Grab all paragraphs <p>
                    paragraphs = body.find_all("p")
                    content = "\n".join([p.get_text(strip=True) for p in paragraphs])
                    print(f"Length: {len(content.split())}")
                    
                    # 8. Using Google AI API to analyze
                    print("----- Google AI analyzing ... -----")
                    ai_result = analyze_tech_article(content)

                    if ai_result:
                        article_data = {
                            "title": title,
                            "url": full_url,
                            "published_date": formatted_date,
                            "crawled_at": time.strftime("%Y-%m-%d %H:%M:%S"), # fetch time
                            "ai_analysis": ai_result # JSON (Dict) returned from AI
                        }

                        print(f"Title: {title}")

                        # 9. Save to Database directly
                        saved = save_article_to_db(article_data)
                        if saved:
                            article_count += 1
                    else:
                        print("❌ AI Analysis Failed (returned None)")

                time.sleep(1) # sleep to match human behavior
                
            except Exception as e:
                print(f"Fail to fetch Article Content: {full_url}, Error: {e}")       

    print("-" * 82)

print("All tasks finished. Check 'fox_news.db' for results.")