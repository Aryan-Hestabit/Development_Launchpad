import pandas as pd
import requests

# 1. Fetch JSON from API
response = requests.get("https://dummyjson.com/products?limit=0")
data = response.json()

df = pd.DataFrame(data['products'])
df.to_excel("Data1.xlsx", index=False)
print(df)
