import requests
from bs4 import BeautifulSoup
import csv
import os
import datetime
import time
from requests.exceptions import RequestException

class ScraperEngine:
    def __init__(self):
        """Initializes the scraper engine for web scraping mode."""
        self.data_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data", "scraped_data.csv")
        self.subreddits = ["AskReddit", "nosleep", "AmItheAsshole"]  # List of subreddits
        self.existing_urls = self.load_existing_urls()  # ✅ Load already scraped URLs

        # ✅ Ensure the 'data/' directory exists
        data_directory = os.path.dirname(self.data_file)
        if data_directory and not os.path.exists(data_directory):
            os.makedirs(data_directory, exist_ok=True)

        # ✅ Ensure CSV file exists with headers
        if not os.path.exists(self.data_file):
            with open(self.data_file, mode='w', newline='', encoding="utf-8") as file:
                writer = csv.writer(file)
                writer.writerow(["Date", "Subreddit", "Title", "Upvotes", "Comments", "URL"])

    def load_existing_urls(self):
        """Loads previously scraped URLs from the CSV to prevent duplicate scraping."""
        existing_urls = set()
        if os.path.exists(self.data_file):
            with open(self.data_file, mode='r', encoding="utf-8") as file:
                reader = csv.reader(file)
                next(reader, None)  # Skip header row
                for row in reader:
                    if len(row) > 5:  # Ensure it's a valid row with a URL
                        existing_urls.add(row[5])  # URL is stored in the 6th column
        return existing_urls

    def scrape_reddit_web(self, limit=10):
        """Scrapes Reddit's website for trending posts, avoiding duplicates."""
        all_posts = []
        scraped_urls = set()  # ✅ Track URLs within this session
        base_url = "https://old.reddit.com/r/{}/top/?t=day"

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36"
        }

        for subreddit_name in self.subreddits:
            print(f"Web scraping r/{subreddit_name}...")
            if not subreddit_name.isalnum():
                print(f"❌ Invalid subreddit name: {subreddit_name}. Skipping...")
                continue

            attempts = 3  # Retry up to 3 times
            for i in range(attempts):
                try:
                    response = requests.get(base_url.format(subreddit_name), headers=headers, timeout=10)
                    response.raise_for_status()  # Raise error for bad status codes (4xx, 5xx)
                    break  # Exit retry loop if successful
                except requests.exceptions.SSLError:
                    print(f"❌ SSL Error on r/{subreddit_name}, retrying... ({i+1}/{attempts})")
                    time.sleep(2)  # Wait before retrying
                except requests.exceptions.RequestException as e:
                    print(f"❌ Failed to fetch r/{subreddit_name} (Error: {e})")
                    return []  # Stop retrying on non-SSL errors

            # ✅ Process HTML after a successful request
            time.sleep(2)  # Delay to avoid bot detection
            soup = BeautifulSoup(response.text, "html.parser")

            # ✅ Check for CAPTCHA
            if soup.find("div", class_="g-recaptcha"):
                print(f"❌ CAPTCHA detected for r/{subreddit_name}. Skipping...")
                continue

            posts = soup.find_all("div", class_="thing", limit=limit * 2)  # Increase limit to find more unique posts

            if not posts:
                print(f"❌ No posts found for r/{subreddit_name}.")
                continue

            found_unique = False  # ✅ Track if we find at least one new post

            for post in posts:
                title_element = post.find("a", class_="title")
                title = title_element.text.strip() if title_element else "N/A"

                # 🛑 Skip posts with promotional words
                spam_keywords = ["crypto", "advertisement", "promote", "sponsored"]
                if any(word in title.lower() for word in spam_keywords):
                    print(f"🚨 Skipping possible ad/spam post: {title}")
                    continue

                url_element = post.find("a", class_="title")
                url = url_element["href"] if url_element else "N/A"
                if url.startswith('/'):
                    url = f"https://old.reddit.com{url}"
                elif not url.startswith('http'):
                    url = f"https://old.reddit.com{url}"

                # ✅ Skip duplicate posts already in CSV or scraped in this session
                if url in self.existing_urls or url in scraped_urls:
                    print(f"⚠️ Skipping duplicate post: {title}")
                    continue  # ✅ Skip duplicate, but keep checking for new ones

                # ✅ If we find a unique post, mark it
                found_unique = True

                upvotes_element = post.find("div", class_="score unvoted") or post.find("div", class_="score likes") or post.find("div", class_="score dislikes")
                upvotes = upvotes_element.text if upvotes_element else "0"

                try:
                    upvotes = self.convert_upvotes(upvotes)
                except ValueError:
                    upvotes = 0

                comments_element = post.find("a", text=lambda text: text and "comments" in text)
                comments = comments_element.text.split()[0] if comments_element else "0"

                try:
                    comments = int(comments.replace('k', '000').replace('.', '').replace(',', ''))
                except ValueError:
                    comments = 0

                post_data = {
                    "Date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "Subreddit": subreddit_name,
                    "Title": title,
                    "Upvotes": upvotes,
                    "Comments": comments,
                    "URL": url
                }

                all_posts.append(post_data)
                scraped_urls.add(url)  # ✅ Track URL in this session

                # ✅ Stop early if we reach the unique post limit
                if len(all_posts) >= limit:
                    break

            if not found_unique:
                print(f"⚠️ All posts in r/{subreddit_name} were duplicates. Moving on...")

        self.save_data(all_posts)

        # ✅ NEW: Show total posts scraped
        print(f"✅ Total unique posts scraped: {len(all_posts)}")

        return all_posts

    def convert_upvotes(self, upvotes):
        """Converts upvotes to an integer."""
        if not upvotes or upvotes in ["N/A", "•", ""]:
            return 0
        if 'k' in upvotes.lower():
            return int(float(upvotes[:-1]) * 1000)
        try:
            return int(upvotes.replace(',', ''))
        except ValueError:
            return 0

    def save_data(self, posts):
        """Saves scraped data to a CSV file."""
        if not posts:
            print("⚠️ No new posts to save. Skipping CSV write.")
            return

        try:
            with open(self.data_file, mode='a', newline='', encoding="utf-8") as file:
                writer = csv.writer(file)
                for post in posts:
                    writer.writerow([post["Date"], post["Subreddit"], post["Title"], post["Upvotes"], post["Comments"], post["URL"]])
            print("✅ Scraped data saved to data/scraped_data.csv")
        except IOError as e:
            print(f"❌ Failed to save data to CSV (Error: {e})")

    def run(self):
        """Runs the web scraper."""
        return self.scrape_reddit_web()
