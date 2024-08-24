import snscrape.modules.twitter as sntwitter
import pandas as pd
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
import os

# Function to check if a proxy is working
def check_proxy(proxy):
    try:
        response = requests.get('https://httpbin.org/ip', proxies={"http": proxy, "https": proxy}, timeout=5)
        if response.status_code == 200:
            return proxy
    except:
        pass
    return None

# Read proxies from the file
with open('proxy_list.txt', 'r') as file:
    proxies = [line.strip() for line in file]

# Check proxies in parallel
working_proxy = None
with ThreadPoolExecutor(max_workers=10) as executor:
    future_to_proxy = {executor.submit(check_proxy, proxy): proxy for proxy in proxies}
    for future in as_completed(future_to_proxy):
        proxy = future_to_proxy[future]
        if future.result():
            working_proxy = future.result()
            break

if not working_proxy:
    raise Exception("No working proxy found")

# Set the proxy environment variables
os.environ['HTTP_PROXY'] = working_proxy
os.environ['HTTPS_PROXY'] = working_proxy

# Define the username and the number of tweets to scrape
username = "BarackObama"
max_tweets = 50

# Initialize an empty list to store tweets
tweets = []

# Use snscrape to scrape tweets with the working proxy
for i, tweet in enumerate(sntwitter.TwitterSearchScraper(f'from:{username}').get_items()):
    if i >= max_tweets:  # Limit the number of tweets to max_tweets
        break
    tweets.append([tweet.date, tweet.content, tweet.user.username])

# Convert the list to a pandas DataFrame
df = pd.DataFrame(tweets, columns=['Date', 'Content', 'Username'])

# Print the DataFrame
print(df)

# Optionally, save the DataFrame to a CSV file
df.to_csv('barackobama_tweets.csv', index=False)