from selenium import webdriver
from selenium.webdriver.common.by import By
import time
import threading

from selenium.webdriver.chrome.options import Options

# 웹 드라이버 초기화
driver = webdriver.Chrome()


# 웹페이지 열기
driver.get("https://x.com/elonmusk")

# 콘텐츠 저장소
content_storage = []

# 저장소 락
storage_lock = threading.Lock()

def getter():
    global content_storage, storage_lock

    # 페이지 끝까지 스크롤
    last_height = driver.execute_script("return document.body.scrollHeight")
    while True:
        # 페이지 끝까지 스크롤
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

        # 새로운 콘텐츠가 로드될 때까지 대기
        time.sleep(2)

        # 새로운 스크롤 높이 가져오기
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height

        # 새로운 콘텐츠 가져오기
        content_items = driver.find_elements(By.CSS_SELECTOR, "div.content-item")

        # 콘텐츠 저장
        new_content = []
        for item in content_items:
            if item.text not in content_storage:
                new_content.append(item.text)

        # 새로운 콘텐츠가 있는 경우에만 저장
        if new_content:
            with storage_lock:
                content_storage.extend(new_content)

def printer():
    global content_storage, storage_lock

    while True:
        # 새로운 콘텐츠가 있는지 확인
        with storage_lock:
            if content_storage:
                # 새로운 콘텐츠 출력
                print(content_storage.pop(0))
        time.sleep(1)

# 스레드 생성 및 실행
getter_thread = threading.Thread(target=getter)
printer_thread = threading.Thread(target=printer)

getter_thread.start()
printer_thread.start()

# 메인 스레드 대기
getter_thread.join()
printer_thread.join()

# 웹페이지 텍스트 콘텐츠 출력
page_text = driver.find_element(By.TAG_NAME, "body").text
print(page_text)

# 웹 드라이버 종료
driver.quit()
