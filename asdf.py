import pandas as pd
df = pd.read_csv('지역화폐_결과1~1000.csv')  # 가게 이름이 들어있는 csv
filtered_df = df[df['지역화폐'] == 'O']
print(filtered_df)

filtered_df.to_csv('지역화폐_1~1000_가능.csv', index=False, encoding = 'utf-8-sig')