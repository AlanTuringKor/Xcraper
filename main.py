from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import time

def scrape_tweets(username, num_tweets=50):
    # Set up the Selenium WebDriver
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')  # Run in headless mode (no GUI)
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)

    url = f"https://twitter.com/{username}"
    driver.get(url)

    tweets = []
    last_height = driver.execute_script("return document.body.scrollHeight")

    while len(tweets) < num_tweets:
        # Scroll down to the bottom
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

        # Wait for new content to load
        time.sleep(2)

        # Calculate new scroll height and compare with last scroll height
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height

        # Parse the page source with BeautifulSoup
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        tweet_divs = soup.find_all('div', {'data-testid': 'tweet'})

        for tweet in tweet_divs:
            tweet_text = tweet.find('div', {'data-testid': 'tweetText'})
            if tweet_text and tweet_text.get_text(strip=True) not in tweets:
                tweets.append(tweet_text.get_text(strip=True))

        print(f"Scraped {len(tweets)} tweets so far...")

    driver.quit()
    return tweets[:num_tweets]

# Example usage
username = 'example_user'
scraped_tweets = scrape_tweets(username, num_tweets=100)

# Store tweets in a file
with open(f"{username}_tweets.txt", "w", encoding="utf-8") as f:
    for i, tweet in enumerate(scraped_tweets, 1):
        f.write(f"Tweet {i}: {tweet}\n\n")

print(f"Scraped {len(scraped_tweets)} tweets and saved them to {username}_tweets.txt")