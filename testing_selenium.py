from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import logging
import os

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def test_selenium():
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')
    options.add_argument('--window-size=1920x1080')

    try:
        logging.info(f"Current working directory: {os.getcwd()}")
        logging.info(f"List of files in current directory: {os.listdir()}")
        
        logging.info("Initializing Chrome WebDriver")
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
        
        logging.info("Attempting to load Twitter homepage")
        driver.get("https://twitter.com")
        
        logging.info(f"Page title: {driver.title}")
        logging.info(f"Current URL: {driver.current_url}")
        
        # Wait for a specific element to be present
        try:
            element = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "input[name='text']"))
            )
            logging.info("Found the 'text' input element on the page")
        except Exception as e:
            logging.error(f"Timed out waiting for page element: {str(e)}")
        
        # Get page source
        logging.info(f"Page source length: {len(driver.page_source)}")
        
        logging.info("Test completed successfully")
    except Exception as e:
        logging.error(f"An error occurred: {str(e)}", exc_info=True)
    finally:
        if 'driver' in locals():
            driver.quit()
            logging.info("WebDriver closed")

if __name__ == "__main__":
    test_selenium()