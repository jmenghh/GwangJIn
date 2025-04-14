from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager  # 수정된 부분
import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# 크롬 옵션
options = Options()
options.add_argument('--start-maximized')

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

# 카카오맵 열기
driver.get("https://map.kakao.com/")
time.sleep(2)

# 검색
search_query = "광진구 한식"
search_input = driver.find_element(By.ID, "search.keyword.query")
search_input.send_keys(search_query)
search_input.send_keys(Keys.ENTER)

try:
    # dimmedLayer가 뜨면 사라질 때까지 기다림 (최대 5초)
    WebDriverWait(driver, 5).until(
        EC.invisibility_of_element_located((By.ID, "dimmedLayer"))
    )
except:
    # dimmedLayer가 없거나 이미 사라졌다면 그냥 통과
    pass

# 장소 탭 클릭
driver.find_element(By.XPATH, '//*[@id="info.main.options"]/li[2]/a').click()

results = []

# 1~5페이지 자동 크롤링
for page in range(1, 6):  # 1페이지부터 5페이지까지 자동 크롤링
    print(f"{page} 페이지 크롤링 중...")
    
    # 페이지 로딩 대기
    time.sleep(2)
    
    # 데이터 크롤링
    items = driver.find_elements(By.CSS_SELECTOR, ".placelist .PlaceItem")
    for item in items:
        try:
            name = item.find_element(By.CSS_SELECTOR, ".head_item .link_name").text
            address = item.find_element(By.CSS_SELECTOR, ".addr p").text
            score_elem = item.find_elements(By.CSS_SELECTOR, ".rating .score em")
            score = score_elem[0].text if score_elem else "0.0"
            results.append((name, address, score))
        except Exception as e:
            print("오류 발생:", e)
            continue
    
    # 5페이지까지 크롤링 완료 후, 6페이지로 넘어가는 화살표를 수동으로 클릭하도록 유도
    if page == 5:
        print("5페이지까지 크롤링 완료. 6페이지로 넘어가는 화살표를 수동으로 클릭한 후 Enter를 눌러주세요.")
        input("수동으로 6페이지로 넘기고 Enter 키를 눌러주세요.")  # 수동으로 화살표를 클릭한 후 Enter로 넘어가도록 유도

# 이후 페이지들 자동 크롤링 (6, 7, 8, 9, 10...)
page_number = 6  # 6페이지부터 시작

while True:
    print(f"{page_number} 페이지 크롤링 중...")

    # 페이지 로딩 대기
    time.sleep(2)
    
    # 데이터 크롤링
    items = driver.find_elements(By.CSS_SELECTOR, ".placelist .PlaceItem")
    for item in items:
        try:
            name = item.find_element(By.CSS_SELECTOR, ".head_item .link_name").text
            address = item.find_element(By.CSS_SELECTOR, ".addr p").text
            score_elem = item.find_elements(By.CSS_SELECTOR, ".rating .score em")
            score = score_elem[0].text if score_elem else "0.0"
            results.append((name, address, score))
        except Exception as e:
            print("오류 발생:", e)
            continue
    
    # 6페이지 이후부터는 자동으로 다음 페이지로 넘기기
    try:
        next_button = driver.find_element(By.XPATH, '//*[@id="info.search.page.next"]')
        if next_button.is_enabled():
            next_button.click()  # 페이지가 넘겨지면 계속 진행
            time.sleep(2)  # 페이지 로딩 대기
        else:
            print("다음 페이지로 이동할 수 없습니다.")
            break
    except Exception as e:
        print(f"다음 페이지로 이동 실패: {e}")
        break

    page_number += 1  # 페이지 번호 1씩 증가 (6, 7, 8, 9, 10...)

driver.quit()

# 결과 출력
for name, address, score in results:
    print(f"{name} / {address} / {score}")

import pandas as pd

df = pd.DataFrame(results, columns=["상호","주소","별점"])

df.to_csv('광진구한식집.csv', index=False, encoding='utf-8-sig')
print('csv로 저장 완료')
