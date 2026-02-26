# Fox News Tech Analyzer & Podcast Generator 🎙️🔍

An automated pipeline that scrapes technology news from Fox News, analyzes the content using **Google Gemini AI**, stores structured data in **SQLite**, and generates engaging **podcast scripts** featuring a dynamic duo: Alex (The Host) and Jamie (The Expert).


## Auto Scraper command
1. crontab -e
2. 0 8 * * * cd /Users/cyc/Projects/WebScraping && /Users/cyc/Projects/WebScraping/venv/bin/python auto_scrape.py >> scraper.log 2>&1

## 🚀 Features

- **Automated Scraping**: Periodically fetches the latest tech news from Fox News.
- **AI-Powered Insights**: Uses Gemini 2.5 Flash to generate summaries, extract technical keywords, and assign "Tech Levels" (1-10).
- **Persistent Storage**: Structured SQLite database for long-term data analysis and deduplication.
- **Smart Categorization**: Incremental keyword classification (Company, Technology, Person, etc.) to minimize API costs.
- **Podcast Engine**: Automatically transforms the most significant news of the day into a 1-minute conversational script.
- **Interactive Dashboard**: A centralized Command Line Interface (CLI) to manage all operations.

## 📂 Project Structure

```text
WebScraping/
├── main.py                # Central CLI Dashboard (Entry Point)
├── .env                   # Environment variables (API Keys)
├── fox_news.db            # SQLite database
├── requirements.txt       # Project dependencies
└── src/
    ├── fox_scraper.py     # Web scraping & AI initial analysis
    ├── ai_service.py      # Google Gemini API integration
    ├── database_manager.py# SQL CRUD operations & DB maintenance
    ├── keyword_analyzer.py# Frequency analysis & categorization
    ├── podcast_producer.py# Script generation logic
    └── prompts/           # Specialized AI prompt templates