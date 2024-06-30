import random
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import time
import logging

# Set up logging
logging.basicConfig(filename='scraper.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

def load_proxies(filename):
    with open(filename, 'r') as f:
        return [line.strip() for line in f if line.strip()]

def scrape_tweets(username, num_tweets=50, proxies=None):
    if not proxies:
        logging.error("No proxies available. Exiting.")
        return []

    service = Service(ChromeDriverManager().install())
    
    for proxy in proxies:
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        options.add_argument('--window-size=1920x1080')
        options.add_argument(f'--proxy-server={proxy}')
        
        max_retries = 3
        for attempt in range(max_retries):
            driver = None
            try:
                logging.info(f"Attempt {attempt + 1} to scrape tweets for user {username} using proxy {proxy}")
                driver = webdriver.Chrome(service=service, options=options)
                url = f"https://twitter.com/{username}"
                driver.get(url)

                tweets = []
                last_height = driver.execute_script("return document.body.scrollHeight")

                while len(tweets) < num_tweets:
                    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                    time.sleep(5)

                    new_height = driver.execute_script("return document.body.scrollHeight")
                    if new_height == last_height:
                        logging.info("Reached end of page or no new content loaded")
                        break
                    last_height = new_height

                    soup = BeautifulSoup(driver.page_source, 'html.parser')
                    tweet_divs = soup.find_all('div', {'data-testid': 'tweet'})

                    for tweet in tweet_divs:
                        tweet_text = tweet.find('div', {'data-testid': 'tweetText'})
                        if tweet_text and tweet_text.get_text(strip=True) not in tweets:
                            tweets.append(tweet_text.get_text(strip=True))

                    logging.info(f"Scraped {len(tweets)} tweets so far...")

                if driver:
                    driver.quit()
                logging.info(f"Successfully scraped {len(tweets)} tweets for user {username}")
                return tweets[:num_tweets]

            except Exception as e:
                logging.error(f"Error during attempt {attempt + 1} with proxy {proxy}: {str(e)}", exc_info=True)
                if driver:
                    driver.quit()
                if attempt == max_retries - 1:
                    logging.error(f"Max retries reached for proxy {proxy}. Trying next proxy.")
                time.sleep(5)  # Wait before retrying

    logging.error("All proxies failed. Unable to scrape tweets.")
    return []

# Load proxies
proxy_list = load_proxies('proxy_list.txt')
random.shuffle(proxy_list)  # Randomize proxy order

# Example usage
username = 'elonmusk'
scraped_tweets = scrape_tweets(username, num_tweets=100, proxies=proxy_list)

# Store tweets in a file
try:
    with open(f"{username}_tweets.txt", "w", encoding="utf-8") as f:
        for i, tweet in enumerate(scraped_tweets, 1):
            f.write(f"Tweet {i}: {tweet}\n\n")
    logging.info(f"Saved {len(scraped_tweets)} tweets to {username}_tweets.txt")
except Exception as e:
    logging.error(f"Error while saving tweets to file: {str(e)}", exc_info=True)

print(f"Scraping completed. Check {username}_tweets.txt for results and scraper.log for detailed logs.")