from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import TimeoutException, StaleElementReferenceException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import time
import logging
import requests
import random
from CloudflareBypasser import CloudflareBypasser

# Set up logging
logging.basicConfig(filename='scraper.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')



def is_proxy_valid(proxy):
    try:
        response = requests.get('https://www.google.com', proxies={'http': proxy, 'https': proxy}, timeout=10)
        return response.status_code == 200
    except:
        return False


def load_proxies(filename):
    with open(filename, 'r') as f:
        return [line.strip() for line in f if line.strip()]

def scrape_tweets(username, num_tweets=50, proxies=None):
    if not proxies:
        logging.error("No proxies available. Exiting.")
        print("No proxies available. Exiting.")
        return []

    service = Service(ChromeDriverManager().install())
    
    for proxy_index, proxy in enumerate(proxies, 1):
        
        if not is_proxy_valid(proxy):
            print(f"  Proxy {proxy} is not valid, skipping")
            continue
        
        print(f"\nTrying proxy {proxy_index}/{len(proxies)}: {proxy}")
        logging.info(f"Trying proxy {proxy_index}/{len(proxies)}: {proxy}")
        
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        options.add_argument('--window-size=1920x1080')
        options.add_argument(f'--proxy-server={proxy}')
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        
        max_retries = 3
        for attempt in range(max_retries):
            driver = None
            try:
                print(f"  Attempt {attempt + 1}/{max_retries} to scrape tweets for user {username}")
                logging.info(f"Attempt {attempt + 1}/{max_retries} to scrape tweets for user {username}")
                driver = webdriver.Chrome(service=service, options=options)
                driver.execute_cdp_cmd('Network.setUserAgentOverride', {"userAgent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.53 Safari/537.36'})
                
                url = f"https://twitter.com/{username}"
                driver.get(url)
                time.sleep(random.uniform(5, 10))  # Random wait time

                tweets = []
                last_height = driver.execute_script("return document.body.scrollHeight")
                
                while len(tweets) < num_tweets:
                    # Scroll down to bottom
                    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                    
                    # Wait to load page
                    time.sleep(random.uniform(2, 5))
                    
                    # Calculate new scroll height and compare with last scroll height
                    new_height = driver.execute_script("return document.body.scrollHeight")
                    if new_height == last_height:
                        # If heights are the same it will exit the function
                        break
                    last_height = new_height

                    # Extract tweets
                    soup = BeautifulSoup(driver.page_source, 'html.parser')
                    tweet_divs = soup.find_all('article', {'data-testid': 'tweet'})
                    
                    for tweet in tweet_divs:
                        tweet_text = tweet.find('div', {'data-testid': 'tweetText'})
                        if tweet_text and tweet_text.get_text(strip=True) not in tweets:
                            tweets.append(tweet_text.get_text(strip=True))
                    
                    print(f"  Scraped {len(tweets)} tweets so far...")
                    logging.info(f"Scraped {len(tweets)} tweets so far...")

                    # Break if we've collected enough tweets
                    if len(tweets) >= num_tweets:
                        break

                if driver:
                    driver.quit()
                
                if tweets:
                    print(f"Successfully scraped {len(tweets)} tweets for user {username}")
                    logging.info(f"Successfully scraped {len(tweets)} tweets for user {username}")
                    return tweets[:num_tweets]
                else:
                    print("  No tweets scraped, trying next attempt or proxy")
                    logging.info("No tweets scraped, trying next attempt or proxy")

            except Exception as e:
                print(f"  Error during attempt {attempt + 1} with proxy {proxy}: {str(e)}")
                logging.error(f"Error during attempt {attempt + 1} with proxy {proxy}: {str(e)}", exc_info=True)
                if driver:
                    driver.quit()
                if attempt == max_retries - 1:
                    print(f"  Max retries reached for proxy {proxy}. Trying next proxy.")
                    logging.error(f"Max retries reached for proxy {proxy}. Trying next proxy.")
                time.sleep(random.uniform(3, 7))  # Random wait before retrying

    print("All proxies failed. Unable to scrape tweets.")
    logging.error("All proxies failed. Unable to scrape tweets.")
    return []

# Load proxies
proxy_list = load_proxies('proxy_list.txt')
random.shuffle(proxy_list)  # Randomize proxy order

# Example usage
username = 'BarackObama'
print(f"Starting to scrape tweets for user: {username}")
print(f"Total proxies to try: {len(proxy_list)}")
scraped_tweets = scrape_tweets(username, num_tweets=100, proxies=proxy_list)

# Store tweets in a file
if scraped_tweets:
    try:
        with open(f"{username}_tweets.txt", "w", encoding="utf-8") as f:
            for i, tweet in enumerate(scraped_tweets, 1):
                f.write(f"Tweet {i}: {tweet}\n\n")
        print(f"Saved {len(scraped_tweets)} tweets to {username}_tweets.txt")
        logging.info(f"Saved {len(scraped_tweets)} tweets to {username}_tweets.txt")
    except Exception as e:
        print(f"Error while saving tweets to file: {str(e)}")
        logging.error(f"Error while saving tweets to file: {str(e)}", exc_info=True)
else:
    print("No tweets were scraped.")
    logging.info("No tweets were scraped.")

print(f"Scraping completed. Check {username}_tweets.txt for results and scraper.log for detailed logs.")