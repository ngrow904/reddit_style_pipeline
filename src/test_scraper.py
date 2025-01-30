from scraper import ScraperEngine

# ✅ Initialize Scraper Engine (Web Scraping Mode)
scraper = ScraperEngine()

# ✅ Run the scraper and fetch posts
scraped_posts = scraper.run()

# ✅ Display results
for post in scraped_posts:
    print(f"[{post['Subreddit']}] {post['Title']} ({post['Upvotes']} upvotes, {post['Comments']} comments)")

