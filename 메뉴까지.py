from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
from time import sleep
import pandas as pd
import time

# 메뉴 정보 함수
def getMenuInfo(i, driver):
    try:
        # 상세페이지로 이동
        detail_page_xpath = f'//*[@id="info.search.place.list"]/li[{i+1}]/div[5]/div[4]/a[1]'
        driver.find_element(By.XPATH, detail_page_xpath).send_keys(Keys.ENTER)
        driver.switch_to.window(driver.window_handles[-1])  # 상세 정보 탭으로 전환

        # 메뉴 섹션이 뜰 때까지 대기
        try:
            WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, '.info_goods'))
            )
        except:
            print(f"메뉴 섹션이 로드되지 않았습니다. 페이지 {i+1}에서 오류 발생.")
            driver.close()
            driver.switch_to.window(driver.window_handles[0])
            return []

        menuInfos = []
        menu_items = driver.find_elements(By.CSS_SELECTOR, '.info_goods .list_menu > li')

        for item in menu_items:
            try:
                # 메뉴명
                name = item.find_element(By.CSS_SELECTOR, '.loss_word').text.strip()
                # 가격
                try:
                    price = item.find_element(By.CSS_SELECTOR, '.price_menu').text.strip().split(' ')[1]
                except:
                    price = ""
                
                menuInfos.append([name, price])
            except Exception as e:
                print(f"메뉴 크롤링 실패: {e}")
                continue

        driver.close()
        driver.switch_to.window(driver.window_handles[0])  # 검색 탭으로 돌아가기
        return menuInfos
    except Exception as e:
        print(f"메뉴 크롤링 실패: {e}")
        try:
            driver.close()
            driver.switch_to.window(driver.window_handles[0])
        except:
            pass
        return []

    try:
        detail_page_xpath = f'//*[@id="info.search.place.list"]/li[{i+1}]/div[5]/div[4]/a[1]'
        driver.find_element(By.XPATH, detail_page_xpath).send_keys(Keys.ENTER)
        driver.switch_to.window(driver.window_handles[-1])
        sleep(1)

        menuInfos = []
        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')

        menuonlyType = soup.select('.cont_menu > .list_menu > .menuonly_type')
        nophotoType = soup.select('.cont_menu > .list_menu > .nophoto_type')
        photoType = soup.select('.cont_menu > .list_menu > .photo_type')

        if len(menuonlyType) != 0:
            for menu in menuonlyType:
                menuInfos.append(_getMenuInfo(menu))
        elif len(nophotoType) != 0:
            for menu in nophotoType:
                menuInfos.append(_getMenuInfo(menu))
        else:
            for menu in photoType:
                menuInfos.append(_getMenuInfo(menu))

        driver.close()
        driver.switch_to.window(driver.window_handles[0])
        return menuInfos
    except Exception as e:
        print(f"메뉴 크롤링 실패: {e}")
        try:
            driver.close()
            driver.switch_to.window(driver.window_handles[0])
        except:
            pass
        return []

def _getMenuInfo(menu):
    menuName = menu.select('.info_menu > .loss_word')[0].text
    menuPrices = menu.select('.info_menu > .price_menu')
    menuPrice = ''
    if len(menuPrices) != 0:
        menuPrice = menuPrices[0].text.split(' ')[1]
    return [menuName, menuPrice]

# 셀레니움 설정
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

WebDriverWait(driver, 5).until(EC.invisibility_of_element_located((By.ID, "dimmedLayer")))
driver.find_element(By.XPATH, '//*[@id="info.main.options"]/li[2]/a').click()

results = []

# 1~5페이지만 크롤링
for page in range(1, 6):
    try:
        page_button = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.LINK_TEXT, str(page)))
        )
        page_button.click()
        print(f"{page}페이지 크롤링 중...")
        time.sleep(2)

        items = driver.find_elements(By.CSS_SELECTOR, ".placelist .PlaceItem")
        for idx, item in enumerate(items):
            try:
                name = item.find_element(By.CSS_SELECTOR, ".head_item .link_name").text
                address = item.find_element(By.CSS_SELECTOR, ".addr p").text
                score_elem = item.find_elements(By.CSS_SELECTOR, ".rating .score em")
                score = score_elem[0].text if score_elem else "0.0"

                menus = getMenuInfo(idx, driver)
                menu_text = ", ".join([f"{m[0]}({m[1]})" if m[1] else m[0] for m in menus])

                results.append((name, address, score, menu_text))
            except Exception as e:
                print("식당 정보 오류:", e)
                continue
    except Exception as e:
        print(f"{page}페이지 오류 발생: {e}")
        break

driver.quit()

# 중복 제거
unique_results = list(set(results))

# CSV 저장
df = pd.DataFrame(unique_results, columns=["상호", "주소", "별점", "메뉴"])
df.to_csv('광진구한식집_메뉴포함.csv', index=False, encoding='utf-8-sig')
print("csv 저장 완료!")
