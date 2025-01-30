import time
import os
import csv
import datetime
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

class TikTokScraper:
    def __init__(self):
        """Initialize TikTok Scraper"""
        self.data_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data", "tiktok_data.csv")
        
        # ✅ Ensure 'data/' directory exists
        data_directory = os.path.dirname(self.data_file)
        if data_directory and not os.path.exists(data_directory):
            os.makedirs(data_directory, exist_ok=True)

        # ✅ Ensure CSV file exists with headers
        if not os.path.exists(self.data_file):
            with open(self.data_file, mode='w', newline='', encoding="utf-8") as file:
                writer = csv.writer(file)
                writer.writerow(["Date", "Username", "Video URL", "Description", "Likes", "Comments", "Shares"])

    def setup_driver(self):
        """Setup the Chrome WebDriver for headless scraping"""
        options = Options()
        options.add_argument("--headless")  # Run in headless mode (no UI)
        options.add_argument("--disable-gpu")
        options.add_argument("--window-size=1920,1080")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_experimental_option("excludeSwitches", ["enable-logging"])
        
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
        return driver

    def scrape_trending_videos(self, limit=5):
        """Scrape trending TikTok videos"""
        print("🔍 Scraping TikTok trending videos...")

        driver = self.setup_driver()
        driver.get("https://www.tiktok.com/explore")

        time.sleep(5)  # Allow page to load
        
        videos = driver.find_elements(By.XPATH, '//div[@data-e2e="video-item"]')

        if not videos:
            print("❌ No videos found. TikTok may have blocked access.")
            driver.quit()
            return []

        all_videos = []
        for video in videos[:limit]:
            try:
                username = video.find_element(By.XPATH, './/a[@data-e2e="video-author-uniqueid"]').text
                video_url = video.find_element(By.TAG_NAME, "a").get_attribute("href")
                description = video.find_element(By.XPATH, './/div[@data-e2e="video-desc"]').text
                likes = video.find_element(By.XPATH, './/strong[@data-e2e="like-count"]').text
                comments = video.find_element(By.XPATH, './/strong[@data-e2e="comment-count"]').text
                shares = video.find_element(By.XPATH, './/strong[@data-e2e="share-count"]').text
                
                # Convert numbers
                likes = self.convert_numbers(likes)
                comments = self.convert_numbers(comments)
                shares = self.convert_numbers(shares)

                video_data = {
                    "Date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "Username": username,
                    "Video URL": video_url,
                    "Description": description,
                    "Likes": likes,
                    "Comments": comments,
                    "Shares": shares
                }

                all_videos.append(video_data)

                print(f"✅ Scraped: {username} - {description[:50]}... ({likes} Likes)")

            except Exception as e:
                print(f"❌ Error scraping a video: {e}")

        driver.quit()
        self.save_data(all_videos)
        return all_videos

    def convert_numbers(self, num_str):
        """Convert TikTok number strings like '1.2M' into integers"""
        if 'K' in num_str:
            return int(float(num_str.replace('K', '')) * 1000)
        elif 'M' in num_str:
            return int(float(num_str.replace('M', '')) * 1000000)
        try:
            return int(num_str.replace(',', ''))
        except ValueError:
            return 0

    def save_data(self, videos):
        """Save scraped TikTok videos to CSV"""
        if not videos:
            print("⚠️ No new videos to save. Skipping CSV write.")
            return

        try:
            with open(self.data_file, mode='a', newline='', encoding="utf-8") as file:
                writer = csv.writer(file)
                for video in videos:
                    writer.writerow([video["Date"], video["Username"], video["Video URL"], video["Description"],
                                     video["Likes"], video["Comments"], video["Shares"]])
            print("✅ Scraped data saved to data/tiktok_data.csv")
        except IOError as e:
            print(f"❌ Failed to save data to CSV (Error: {e})")

    def run(self):
        """Runs the TikTok scraper"""
        return self.scrape_trending_videos()


# Run TikTok scraper if executed directly
if __name__ == "__main__":
    scraper = TikTokScraper()
    scraper.run()
