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


#================ What will be dropped ===============

print("\n" + "=" * 60)

cheap_cars = df[df['price'] < 200000]
print(cheap_cars.groupby('condition')['price'].count())
print("\nSample of <200k cars:")
print(cheap_cars[['manufacturer', 'model', 'year', 'price', 'condition']].sort_values('price'))

print("\n" + "=" * 60)

over150m = df[df['price'] > 150000000]
print("\nCars over 150m:")
print(over150m[['manufacturer', 'model', 'year', 'price']].sort_values('price'))

print("\n" + "=" * 60)

over_500m = df[df['price'] > 500000000]
print("\nCars over 500m:")
print(over_500m[['manufacturer', 'model', 'year', 'price']].sort_values('price'))

print("\n" + "=" * 60)

missing_price = df['price'].isna().sum()
under_200k = len(df[df['price'] < 200000])
over500m = len(df[df['price'] > 500000000])


print(f"\nWill be dropped:")
print(f"Missing prices: {missing_price} cars")
print(f"Under 200k: {under_200k} cars")
print(f"Over 500m: {over500m} cars")
print(f"TOTAL: {missing_price + under_200k + over500m} cars")



