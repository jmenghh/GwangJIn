from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import time
import pandas as pd

# ✅ 메뉴 + 가격 추출 함수
def extract_menu_and_price():
    try:
        # '메뉴' 탭 클릭
        menu_tab = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.LINK_TEXT, "메뉴"))
        )
        menu_tab.click()
        time.sleep(0.5)

        # HTML 파싱
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        menu_items = soup.select("div.wrap_goods ul.list_goods li")

        results = []
        for item in menu_items:
            try:
                name = item.select_one("strong.tit_item").text.strip()
                price = item.select_one("p.desc_item").text.strip()
                results.append({"메뉴": name, "가격": price})
            except:
                continue

        return results

    except Exception as e:
        print(f"[메뉴 추출 실패] {e}")
        return []

# ✅ 크롬 옵션 설정
options = Options()
options.add_argument('--start-maximized')

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
driver.get("https://map.kakao.com/")
time.sleep(2)

# 검색어 입력
search_query = input('검색어를 입력하세요: ')
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

# 페이지 그룹 기준 (1,6,11,...)
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

                    # ✅ 상세보기 링크 클릭 (새 탭 열림)
                    detail_btn = item.find_element(By.CSS_SELECTOR, ".moreview")
                    driver.execute_script("arguments[0].click();", detail_btn)
                    time.sleep(2)

                    # 탭 전환
                    driver.switch_to.window(driver.window_handles[-1])

                    # 메뉴 + 가격 크롤링
                    menu_data = extract_menu_and_price()
                    menu_str = ", ".join([f"{m['메뉴']}({m['가격']})" for m in menu_data]) if menu_data else ""

                    # 결과 저장
                    results.append((name, address, score, menu_str))

                    # 탭 닫고 복귀
                    driver.close()
                    driver.switch_to.window(driver.window_handles[0])
                    time.sleep(1)

                except Exception as e:
                    print(f"장소 상세페이지 오류: {e}")
                    if len(driver.window_handles) > 1:
                        driver.close()
                        driver.switch_to.window(driver.window_handles[0])
                    continue

        except Exception as e:
            print(f"{current_page}페이지 없음 또는 오류 발생: {e}")
            break

driver.quit()

# CSV 저장
df = pd.DataFrame(results, columns=["상호", "주소", "별점", "메뉴"])
df.to_csv("{}.csv".format(search_query), index=False, encoding="utf-8-sig")
print("CSV 저장 완료!")
