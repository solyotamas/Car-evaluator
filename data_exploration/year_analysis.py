import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


df = pd.read_csv('data/raw/car_details.csv')
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)


print(f"Cars with missing years: {df['year'].isna().sum()}")

print("\nYear statistics:")
print(df['year'].describe())

year_ranges = [
    (0, 1990),
    (1990, 2000),
    (2000, 2010),
    (2010, 2015),
    (2015, 2020),
    (2020, 2025),
    (2025, 3000)
]

print("\nCars by year range:")
for start, end in year_ranges:
    count = len(df[(df['year'] >= start) & (df['year'] < end)])
    if count > 0:
        pct = count / len(df) * 100
        print(f"{start}-{end}: {count} cars ({pct:.2f}%)")


print("\nOldest cars:")
print(df.nsmallest(10, 'year')[['manufacturer', 'model', 'year', 'price']])

print("\nNewest cars:")  
print(df.nlargest(10, 'year')[['manufacturer', 'model', 'year', 'price']])


#dist
plt.figure(figsize=(12, 4))
plt.hist(df['year'].dropna(), bins=50, edgecolor='black')
plt.xlabel('Year')
plt.ylabel('Count')
plt.title('Distribution of Car Years')
plt.show()
