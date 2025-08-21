import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv('data/raw/car_details.csv')
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)

print("Fuel type statistics:")
print(f"Missing fuel types: {df['fuel_type'].isna().sum()}")
print(f"Unique fuel types: {df['fuel_type'].nunique()}")

print("\nFuel type distribution:")
fuel_counts = df['fuel_type'].value_counts()
print(fuel_counts)

# Price by fuel type
print("\nAverage price by fuel type:")
price_by_fuel = df.groupby('fuel_type')['price'].agg(['mean', 'median', 'count']).sort_values('mean', ascending=False)
print(price_by_fuel)

# Visualization
plt.figure(figsize=(12, 5))

fuel_counts.plot(kind='bar')
plt.title('Fuel Types by Count')
plt.xlabel('Fuel Type')
plt.ylabel('Count')
plt.xticks(rotation=45)

plt.tight_layout()
plt.show()