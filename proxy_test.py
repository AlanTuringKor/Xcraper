from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def test_with_proxy(proxy):
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument(f'--proxy-server={proxy}')

    try:
        logging.info(f"Initializing Chrome WebDriver with proxy: {proxy}")
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
        
        logging.info("Setting page load timeout")
        driver.set_page_load_timeout(30)  # 30 seconds timeout
        
        logging.info("Attempting to load a test page")
        driver.get("http://httpbin.org/ip")  # This page will show the IP being used
        
        logging.info(f"Page title: {driver.title}")
        logging.info(f"Current URL: {driver.current_url}")
        
        # Wait for the pre element to be present (contains the IP info)
        try:
            element = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "pre"))
            )
            logging.info(f"Page content: {element.text}")
        except Exception as e:
            logging.error(f"Timed out waiting for page element: {str(e)}")
        
        logging.info("Test completed successfully")
    except Exception as e:
        logging.error(f"An error occurred: {str(e)}", exc_info=True)
    finally:
        if 'driver' in locals():
            driver.quit()
            logging.info("WebDriver closed")

if __name__ == "__main__":
    # List of proxies to try
    proxies = [
        "166.0.235.5:30149",
        "202.159.30.9:443",
        "103.19.10.245:POR4153T",
        "43.153.55.205:443",
        "198.24.170.122:35333",
        "113.74.26.116:4145",
        "45.63.70.67:29313",
        "1.234.28.160:80",
        "103.82.11.237:4153",
        "66.171.186.47:1080",
        "202.159.35.97:443",
        "162.214.121.11:46504",
        "95.111.91.50:10801",
        "47.241.238.217:1080",
    ]
    
    for proxy in proxies:
        test_with_proxy(proxy)
        time.sleep(5)  # Wait a bit before trying the next proxy