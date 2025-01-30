import time
import os
import csv
import datetime
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from webdriver_manager.chrome import ChromeDriverManager

class TikTokScraper:
    def __init__(self, username="scalingstories"):
        """Initialize TikTok Scraper for a specific user."""
        self.username = username
        self.data_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data", f"{self.username}_tiktok_data.csv")

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
        """Setup the Chrome WebDriver for scraping"""
        options = Options()

        # ❌ REMOVE Incognito mode (Now runs in a regular browser)
        # options.add_argument("--incognito")  # REMOVED

        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("--disable-infobars")
        options.add_argument("--window-size=1920,1080")
        options.add_argument("--disable-features=NetworkService,NetworkServiceInProcess")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option("useAutomationExtension", False)

        # ✅ Start WebDriver
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

        # ✅ Remove WebDriver detection (Tricks TikTok into thinking it's a normal browser)
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

        return driver

    def check_login(self, driver):
        """Detects if login is required & pauses for manual login."""
        time.sleep(5)  # Allow page to load

        # ✅ Check for "Log in" button
        login_elements = driver.find_elements(By.XPATH, '//button[contains(text(), "Log in")]')

        if login_elements:
            print("🔐 TikTok requires login. Please log in manually and press Enter to continue...")
            input("⏳ Press Enter after logging in...")  # Wait for user to log in
            return True
        return False

    def scroll_to_load_videos(self, driver, scrolls=3):
        """Scroll down to load more TikTok videos."""
        for _ in range(scrolls):
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(3)  # Allow videos to load

    def scrape_user_videos(self, limit=5):
        """Scrape videos from a specific TikTok user."""
        driver = self.setup_driver()
        if not driver:
            return []

        user_url = f"https://www.tiktok.com/@{self.username}"
        print(f"🔍 Scraping TikTok videos from user: @{self.username}...")

        try:
            driver.get(user_url)
            time.sleep(10)  # ✅ Ensure page loads

            # ✅ Handle login if required
            self.check_login(driver)

            # ✅ Scroll to load more videos
            self.scroll_to_load_videos(driver, scrolls=5)

            # ✅ Find video elements (try multiple methods)
            videos = driver.find_elements(By.XPATH, '//div[@data-e2e="user-post-item"]')

            if not videos:
                print("❌ No videos found. TikTok may have blocked access.")
                driver.quit()
                return []

            all_videos = []
            for video in videos[:limit]:
                try:
                    # ✅ Click the video to open details
                    ActionChains(driver).move_to_element(video).click().perform()
                    time.sleep(3)  # Allow popup to load

                    username = self.username
                    video_url = driver.current_url  # ✅ Get actual video URL
                    description = driver.find_element(By.XPATH, '//div[@data-e2e="video-desc"]').text
                    likes = driver.find_element(By.XPATH, '//strong[@data-e2e="like-count"]').text
                    comments = driver.find_element(By.XPATH, '//strong[@data-e2e="comment-count"]').text
                    shares = driver.find_element(By.XPATH, '//strong[@data-e2e="share-count"]').text

                    # ✅ Convert numbers (e.g., 1.2M → 1200000)
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

                    # ✅ Close popup & go back to the main page
                    driver.find_element(By.TAG_NAME, "body").send_keys(Keys.ESCAPE)
                    time.sleep(2)

                except Exception as e:
                    print(f"❌ Error scraping a video: {e}")

            driver.quit()
            self.save_data(all_videos)
            return all_videos

        except Exception as e:
            print(f"❌ Error loading TikTok page: {e}")
            driver.quit()
            return []

    def convert_numbers(self, num_str):
        """Convert TikTok number strings like '1.2M' into integers."""
        if 'K' in num_str:
            return int(float(num_str.replace('K', '')) * 1000)
        elif 'M' in num_str:
            return int(float(num_str.replace('M', '')) * 1000000)
        try:
            return int(num_str.replace(',', ''))
        except ValueError:
            return 0

    def save_data(self, videos):
        """Save scraped TikTok videos to CSV."""
        if not videos:
            print("⚠️ No new videos to save. Skipping CSV write.")
            return

        file_exists = os.path.exists(self.data_file)

        try:
            with open(self.data_file, mode='a', newline='', encoding="utf-8") as file:
                writer = csv.writer(file)
                if not file_exists:
                    writer.writerow(["Date", "Username", "Video URL", "Description", "Likes", "Comments", "Shares"])

                for video in videos:
                    writer.writerow([video["Date"], video["Username"], video["Video URL"], video["Description"], video["Likes"], video["Comments"], video["Shares"]])

            print(f"✅ Scraped data saved to {self.data_file}")

        except IOError as e:
            print(f"❌ Failed to save data to CSV (Error: {e})")

# ✅ Run TikTok scraper if executed directly
if __name__ == "__main__":
    scraper = TikTokScraper(username="scalingstories")  # ✅ Now without underscore
    scraper.scrape_user_videos()
