from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time
import pandas as pd

# 크롬 옵션
options = Options()
options.add_argument('--start-maximized')

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
driver.get("https://map.kakao.com/")
time.sleep(2)

search_query = "광진구 한식"
search_input = driver.find_element(By.ID, "search.keyword.query")
search_input.send_keys(search_query)
search_input.send_keys(Keys.ENTER)

# dimmedLayer 사라질 때까지 대기
try:
    WebDriverWait(driver, 5).until(
        EC.invisibility_of_element_located((By.ID, "dimmedLayer"))
    )
except:
    pass

# 장소 탭 클릭
driver.find_element(By.XPATH, '//*[@id="info.main.options"]/li[2]/a').click()

results = []

# 페이지 그룹 기준 (1,6,11,16,...)
# 예시: base_page=6일 때 offset=1부터 돌면 current_page=7부터 시작함
for base_page in range(1, 36, 5):
    if base_page > 1:
        try:
            next_arrow = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.ID, "info.search.page.next"))
            )
            next_arrow.click()
            time.sleep(2)
        except Exception as e:
            print(f"{base_page}페이지 화살표 클릭 실패: {e}")
            break

    # ❗ base_page 그룹에서 첫 페이지는 이미 열려 있으니, offset을 0이 아닌 1부터 시작
    start_offset = 0 if base_page == 1 else 1

    for offset in range(start_offset, 5):  # 0~4면 5페이지 커버
        current_page = base_page + offset

        try:
            page_buttons = driver.find_elements(By.CSS_SELECTOR, "#info.search.page a")
            matched = False
            for btn in page_buttons:
                if btn.text == str(current_page):
                    btn.click()
                    matched = True
                    break
            if not matched:
                print(f"{current_page}페이지 버튼 없음")
                break

            print(f"{current_page}페이지 크롤링 중...")
            time.sleep(2)

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
        except Exception as e:
            print(f"{current_page}페이지 오류 발생: {e}")
            break

    # 6,11,... 진입 시 화살표 눌러서 다음 페이지 그룹으로 이동
    if base_page > 1:
        try:
            next_arrow = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.ID, "info.search.page.next"))
            )
            next_arrow.click()
            time.sleep(2)
        except Exception as e:
            print(f"{base_page}페이지 화살표 클릭 실패: {e}")
            break

    # base_page에서 한 번만 클릭하고, 그 이후는 offset 이용해서 그냥 넘어감
    for offset in range(5):
        current_page = base_page + offset

        # 페이지 그룹 넘어오면 바로 base_page는 클릭하지 말고 첫 번째 offset부터 시작하게 함
        try:
            # 페이지 버튼이 있을 때만 클릭
            page_buttons = driver.find_elements(By.CSS_SELECTOR, "#info.search.page a")
            matched = False
            for btn in page_buttons:
                if btn.text == str(current_page):
                    btn.click()
                    matched = True
                    break
            if not matched:
                print(f"{current_page}페이지 버튼 없음")
                break

            print(f"{current_page}페이지 크롤링 중...")
            time.sleep(2)

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
        except Exception as e:
            print(f"{current_page}페이지 오류 발생: {e}")
            break

    # base_page > 1이면 화살표 클릭해서 다음 페이지 그룹으로 이동
    if base_page > 1:
        try:
            next_arrow = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.ID, "info.search.page.next"))
            )
            next_arrow.click()
            time.sleep(2)
        except Exception as e:
            print(f"{base_page}페이지 화살표 클릭 실패: {e}")
            break

    for offset in range(5):  # 현재 페이지 그룹 내에서 순차 접근
        current_page = base_page + offset
        try:
            page_button = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.LINK_TEXT, str(current_page)))
            )
            page_button.click()
            print(f"{current_page}페이지 크롤링 중...")
            time.sleep(2)

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
        except Exception as e:
            print(f"{current_page}페이지 없음 또는 오류 발생: {e}")
            break

    for offset in range(5):
        current_page = base_page + offset
        try:
            page_button = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.LINK_TEXT, str(current_page)))
            )
            page_button.click()
            print(f"{current_page}페이지 크롤링 중...")
            time.sleep(2)

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
        except Exception as e:
            print(f"{current_page}페이지 없음 또는 오류 발생: {e}")
            break

driver.quit()

# 저장
df = pd.DataFrame(results, columns=["상호", "주소", "별점"])
df.to_csv("광진구한식집.csv", index=False, encoding="utf-8-sig")
print("csv로 저장 완료")
