import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
# 1. CSV 파일 읽기
df = pd.read_csv('통합.csv')  # 가게 이름이 들어있는 csv
df['지역화폐'] = ''  # 결과를 저장할 새 열 추가
# 크롬 설정
options = Options()
options.add_argument('--start-maximized')
options.add_argument('--headless')
options.add_argument('--disable-gpu')

# 2. 크롬 드라이버 열기
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
driver.get('https://www.zeropay.or.kr/UI_HP_009_03.act')
time.sleep(2)


# 3. 가게 이름 하나씩 검색
for idx, row in df.iterrows():
    store_name = row['가게명']  # CSV에 가게명 열이 있다고 가정
    print(f"검색 중: {store_name}")

    # (1) 검색창 찾아서 입력
    search_input = driver.find_element(By.ID, 'iptText')
    search_input.clear()
    search_input.send_keys(store_name)
    time.sleep(0.5)
    
    # (2) 검색 버튼 클릭
    search_button = driver.find_element(By.ID, 'btnSearch')
    search_button.click()
    WebDriverWait(driver, 20).until(
    EC.invisibility_of_element_located((By.CSS_SELECTOR, "aside.loading"))
)

# (3) 검색 결과 확인
    tbody = driver.find_element(By.ID, 'tbTbody')
    rows = tbody.find_elements(By.TAG_NAME, 'tr')
    found = False
    for row in rows:
        cells = row.find_elements(By.TAG_NAME, 'td')  # find_elements로 여러 개의 td 요소를 가져옵니다.
        if len(cells) > 0:  # 셀이 존재하는지 확인
            print('결과존재')
            if len(cells) > 2 and '광진구' in cells[2].text:  # cells[2]에서 텍스트를 가져옵니다.
                df.at[idx, '지역화폐'] = '가능'
                print('광진구존재')
                break
            else:
                df.at[idx,'지역화폐'] = '불가'
                print('광진구없음')
                break
        else:
            df.at[idx, '지역화폐'] = '불가'
            print('결과없음')
            break

            

# 4. 결과 저장
df = df[['가게명','지역화폐']]
df.to_csv('지역화폐_결과.csv', index=False, encoding = 'utf-8-sig')

print('완료!')

driver.quit()
