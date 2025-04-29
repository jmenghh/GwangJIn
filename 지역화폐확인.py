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
df = df.iloc[1000:2000,:]
df['지역화폐'] = ''  # 결과를 저장할 새 열 추가
# 크롬 설정
options = Options()
options.add_argument('--start-maximized')
options.add_argument('--headless')
options.add_argument('--disable-gpu')

# 2. 크롬 드라이버 열기
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()),options=options)
driver.get('https://www.zeropay.or.kr/UI_HP_009_03.act')
time.sleep(2)

# 광진구 찾기
gwangjin = WebDriverWait(driver, 20).until(
    EC.visibility_of_element_located((By.XPATH, "//button[text()='광진구']"))
)
driver.execute_script('arguments[0].scrollIntoView(true);',gwangjin)
gwangjin.click()
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
    WebDriverWait(driver, 10).until(
        EC.invisibility_of_element((By.ID, 'comAlertPopup'))
    )
    search_button.click()
    WebDriverWait(driver, 20).until(
    EC.invisibility_of_element_located((By.CSS_SELECTOR, "aside.loading"))
)

# (3) 검색 결과 확인
    tbody = driver.find_element(By.ID, 'tbTbody')
    rows = tbody.find_elements(By.TAG_NAME, 'tr')
    for row in rows:
        cells = row.find_elements(By.TAG_NAME, 'td')
    if len(cells) > 2:  # 셀이 존재하는지 확인
        print('결과존재')
        df.at[idx, '지역화폐'] = 'O'
    else:
        print('결과없음')
        df.at[idx, '지역화폐'] = 'X'
           

            

# 4. 결과 저장
cols = list(df.columns)
cols.insert(cols.index('가게명')+1,cols.pop(cols.index('지역화폐')))
df = df[cols]
df.to_csv('지역화폐_결과.csv', index=False, encoding = 'utf-8-sig')

print('완료!')

driver.quit()
