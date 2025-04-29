import pandas as pd

df = pd.read_csv('지역화폐_최종.csv')

df = df[df['지역화폐'] == 'O']

print(df)