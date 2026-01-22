import requests
import time # avoid DDoS detection
import json
from bs4 import BeautifulSoup

# import AI module
from src.ai_service import analyze_tech_article

# Collecting results in an array
all_articles_data = []

# Cmd + Shift + C on the web to check every objects' code
url = "https://www.foxnews.com/tech"

headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"
}

res = requests.get(url, headers=headers)
res.raise_for_status()

soup = BeautifulSoup(res.text, "html.parser")

# Fox News <article> tag
articles = soup.find_all("article")


print("-" * 82)
article_count = 0

for a in articles:
    # Find Tech Articles within a day -----------------

    # 1. Find time tag (in class="meta")
    meta_tag = a.find("div", class_="meta")

    is_today = False
    time_debug_msg = "No time Info"

    if meta_tag:
        time_text = meta_tag.get_text(separator=" ", strip=True).lower()
        time_debug_msg = time_text
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

        while (not str.isdigit(time_text_arr[0])):
            category += (time_text_arr[0].capitalize() + " ")
            del time_text_arr[0]

        print(f"Article {article_count+1}", end=" | ")
        print(category + "| ", end="")
        print(time_text_arr[0] + " " + time_text_arr[1] + " " + time_text_arr[2], end=" | ")

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
                # 4. Request article page
                detail_res = requests.get(full_url, headers=headers, timeout=10)
                detail_soup = BeautifulSoup(detail_res.text, "html.parser")

                # 5. Record Published Date
                date_info = ["", 0, 0]

                date_span = detail_soup.find("span", class_="article-date")

                if date_span:
                    time_tag = date_span.find("time")
                    if time_tag:
                        raw_time_text = time_tag.get_text(strip=True)

                        time_parts = raw_time_text.split(' ')
                        if len(time_parts) >= 3:
                            date_info[0] = time_parts[0]
                            date_info[1] = time_parts[1]
                            date_info[2] = time_parts[2]
                        else:
                            print("Fail to fetch Published Date.")
                
                # 6. Search for Content Block (.article-body)
                body = detail_soup.find("div", class_="article-body")
                
                if body:
                    # 7. Grab all paragraphs <p>
                    paragraphs = body.find_all("p")
                    content = "\n".join([p.get_text(strip=True) for p in paragraphs])
                    print(f"Length: {len(content.split())}")
                    
                    # 8. using Google AI API to analyze
                    print("----- AI analysis ... -----")
                    ai_result = analyze_tech_article(content)
                    article_data = {
                        "title": title,
                        "url": full_url,
                        "published_date": date_info,
                        "crawled_at": time.strftime("%Y-%m-%d %H:%M:%S"), # fetch time
                        "content": content, # original content
                        "ai_analysis": ai_result # JSON (Dict) returned from AI
                    }

                    print(f"Title: {title}")
                    # print("Content: " + content[:50] + "...") # preview

                    all_articles_data.append(article_data)
                    article_count += 1
                    print("Analyzed Report Added")

                # 9. stop to avoid DDoS detection
                time.sleep(1)
                
            except Exception as e:
                print(f"Fail to fetch Article Content: {full_url}, Error: {e}")

    # -------------------------------------------------        

    print("-" * 82)

if all_articles_data:
    output_file = "data.json"
    print(f"Writing to file: {output_file} ...")

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(
            all_articles_data,
            f,
            ensure_ascii=False,
            indent=4
        )

    print("Finish Writing! Please check data.json for results.")

else:
    print("Tech News Fetch Failed")