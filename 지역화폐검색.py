import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

try:
    # CSV 파일 읽기
    df = pd.read_csv('총점수가게명중복제거.csv')
    df = df.iloc[1200:]
    df['지역화폐'] = ''

    options = Options()
    options.add_argument('--start-maximized')
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    driver.get('https://www.zeropay.or.kr/UI_HP_009_03.act')
    time.sleep(2)

    gwangjin = WebDriverWait(driver, 20).until(
        EC.visibility_of_element_located((By.XPATH, "//button[text()='광진구']"))
    )
    driver.execute_script('arguments[0].scrollIntoView(true);', gwangjin)
    gwangjin.click()

    for idx, row in df.iterrows():
        try:
            store_name = row['가게명']
            print(f"검색 중: {store_name}")

            search_input = driver.find_element(By.ID, 'iptText')
            search_input.clear()
            search_input.send_keys(store_name)
            time.sleep(0.5)

            search_button = driver.find_element(By.ID, 'btnSearch')
            WebDriverWait(driver, 20).until(
                EC.invisibility_of_element((By.ID, 'comAlertPopup'))
            )
            search_button.click()
            WebDriverWait(driver, 30).until(
                EC.invisibility_of_element_located((By.CSS_SELECTOR, "aside.loading"))
            )

            tbody = driver.find_element(By.ID, 'tbTbody')
            rows = tbody.find_elements(By.TAG_NAME, 'tr')
            has_result = False
            for row in rows:
                cells = row.find_elements(By.TAG_NAME, 'td')
                if len(cells) > 2:
                    has_result = True
                    break

            df.at[idx, '지역화폐'] = 'O' if has_result else 'X'
            print('결과존재' if has_result else '결과없음')

            # 진행된 결과 저장
            temp_df = df.copy()
            cols = list(temp_df.columns)
            cols.insert(cols.index('가게명') + 1, cols.pop(cols.index('지역화폐')))
            temp_df = temp_df[cols]
            temp_df.to_csv('지역화폐_결과_임시저장.csv', index=False, encoding='utf-8-sig')

        except Exception as inner_e:
            print(f'개별 가게 처리 중 에러 발생: {store_name}, 에러: {inner_e}')
            break  # 여기서 멈추고 저장된 부분까지만 결과 확인할 수 있도록

except Exception as e:
    print(f'전체 실행 중 에러 발생: {e}')

finally:
    try:
        driver.quit()
    except:
        pass
    input('아무 키나 누르십시오')
