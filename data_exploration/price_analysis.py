import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

df = pd.read_csv('data/raw/car_details.csv')
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)

print(f"Cars with missing prices: {df['price'].isna().sum()}")
print(f"Cars under 300k: {len(df[df['price'] < 300000])}")
print(f"{len(df[df['price'] < 500000]) / len(df) * 100:.2f}% of the dataset")


print("\nPrice ranges:")
print(f"Under 100k: {len(df[df['price'] < 100000])}")
print(f"100k-300k: {len(df[(df['price'] >= 100000) & (df['price'] < 300000)])}")
print(f"300k-500k: {len(df[(df['price'] >= 300000) & (df['price'] < 500000)])}")
print(f"500k-1M: {len(df[(df['price'] >= 500000) & (df['price'] < 1000000)])}")
print(df[(df['price'] >= 100000) & (df['price'] < 300000)]['condition'].value_counts())

prices = [300000, 1000000, 5000000, 10000000, 50000000, 100000000]
log_prices = np.log(prices)

plt.figure(figsize=(12, 6))
plt.subplot(1,2,1)
plt.bar(range(len(prices)), prices)
plt.title('Original Prices')
plt.ylabel('Price (Ft)')

plt.subplot(1,2,2)  
plt.bar(range(len(log_prices)), log_prices)
plt.title('Log Prices')
plt.ylabel('Log(Price)')
plt.show()


thresholds = [30, 40, 50, 75, 100, 150]
for t in thresholds:
    count = len(df[df['price'] > t*1_000_000])
    percent = count / len(df) * 100
    print(f"Above {t}M: {count} cars ({percent:.2f}%)")


print("\nCars between 50-100M:")
print(df[(df['price'] > 50_000_000) & (df['price'] <= 100_000_000)]['manufacturer'].value_counts().head(10))

