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

# 페이지 다운
def page_down(num):
    body = driver.find_element(By.CSS_SELECTOR, 'body')
    body.click()
    for i in range(num):
        body.send_keys(Keys.PAGE_DOWN)
# ✅ 가격 정보 추출 함수
def extract_menu_and_price():
    try:
        # '가격' 탭 클릭
        price_tab = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.XPATH, "//span[text()='가격']/ancestor::a"))
        )
        price_tab.click()
        time.sleep(2)

        # HTML 파싱
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        menu_list = soup.select("div.place_section_content ul.WBQHI > li.F7pMw ul.JToq_ > li")

        results = []
        for item in menu_list:
            try:
                menu_name = item.select_one("span.gqmxb").text.strip()
                menu_price = item.select_one("div.dELze em").text.strip()
                results.append({"메뉴": menu_name, "가격": menu_price})
            except Exception as e:
                continue

        return results

    except Exception as e:
        print(f"[가격탭 클릭 실패] {e}")
        return []

# ✅ 크롬 옵션 설정
options = Options()
options.add_argument('--start-maximized')
options.add_argument('--headless')
options.add_argument('--disable-gpu')

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
driver.get("https://map.naver.com/p/entry/place")
time.sleep(3)

# 검색어 입력
search_query = '광진구 미용'
search_input = WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.CSS_SELECTOR, "input.input_search"))
)
search_input.send_keys(search_query)
search_input.send_keys(Keys.ENTER)
time.sleep(3)

results = []
time.sleep(2)
driver.switch_to.frame("searchIframe")

page_down(40)
time.sleep(3)
# 페이지 크롤링 시작
try:
    while True:
        # 검색 결과 항목 가져오기
        items = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, "span.YwYLL"))
        )
        print(f"{len(items)}개 가게 발견")
        next_btn = driver.find_elements(By.CSS_SELECTOR, '.zRM9F> a')
    
        for idx, item in enumerate(items):
            try:
                print(f"{idx+1}번째 가게 크롤링 중...")

                # ✅ 부모 요소 클릭
                clickable_parent = item.find_element(By.XPATH, "./ancestor::a")
                driver.execute_script("arguments[0].click();", clickable_parent)
                time.sleep(2)
                

                # 오른쪽 상세 패널 iframe 전환
                driver.switch_to.default_content()
                entry_iframe = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "iframe#entryIframe"))
                )
                driver.switch_to.frame(entry_iframe)
                

                # 이름 추출
                shop_name = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "span.GHAhO"))
                ).text.strip()
                # 업종 추출
                shop_type = WebDriverWait(driver,10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "span.lnJFt"))
                ).text.strip()
                # 주소 추출
                address = driver.find_element(By.CSS_SELECTOR, "span.LDgIH").text.strip()

                # 메뉴/가격 추출
                menu_data = extract_menu_and_price()
                menu_str = ", ".join([f"{m['메뉴']}({m['가격']}원)" for m in menu_data]) if menu_data else ""

                # 결과 저장
                results.append((shop_name, shop_type, address, menu_str))

                # 다시 검색 결과 iframe 복귀
                driver.switch_to.default_content()
                search_iframe = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "iframe#searchIframe"))
                )
                driver.switch_to.frame(search_iframe)
                

            except Exception as e:
                print(f"가게 상세페이지 오류: {e}")
                driver.switch_to.default_content()
                search_iframe = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "iframe#searchIframe"))
                )
                driver.switch_to.frame(search_iframe)
                continue
        if not next_btn[-1].is_enabled():
            break
        if shop_name[-1]:
            next_btn[-1].click()
            time.sleep(2)   
        else:
            print('페이지 인식 못함')
            break   

        

except Exception as e:
    print(f"검색결과 로딩 실패: {e}")

# CSV 저장
df = pd.DataFrame(results, columns=["상호", '업종',"주소", "메뉴"])
df.to_csv(f"{search_query}.csv", index=False, encoding="utf-8-sig")
print("CSV 저장 완료!")

driver.quit()
