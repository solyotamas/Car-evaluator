import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

df = pd.read_csv('data/raw/car_details.csv')
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)

# Check missing values
print(f"Missing manufacturer: {df['manufacturer'].isna().sum()}")
print(f"Missing model: {df['model'].isna().sum()}")

# Top manufacturers
print("\nTop 20 manufacturers:")
print(df['manufacturer'].value_counts().head(20))


manufacturer_counts = df['manufacturer'].value_counts()
print(f"Manufacturers with only 1 car: {len(manufacturer_counts[manufacturer_counts == 1])}")
print("\nRare manufacturers (≤5 cars):")
print(manufacturer_counts[manufacturer_counts <= 5])


print("Cars with missing models:")
print(df[df['model'].isna()][['manufacturer', 'model', 'year', 'price']])


print("\nPotential duplicates/typos in manufacturers:")
manufacturers = df['manufacturer'].unique()
for m in manufacturers:
    if 'MERCEDES' in str(m):
        print(f"  {m}: {len(df[df['manufacturer'] == m])} cars")

print("\nMercedes variants price comparison:")
for variant in ['MERCEDES-BENZ', 'MERCEDES-AMG', 'MERCEDES-MAYBACH']:
    if variant in df['manufacturer'].values:
        avg_price = df[df['manufacturer'] == variant]['price'].mean()
        print(f"{variant}: avg price {avg_price:,.0f} Ft")


# Threshold to drop manufacturers from
print("Distribution of manufacturer counts:")
print(f"1 car: {len(manufacturer_counts[manufacturer_counts == 1])} manufacturers")
print(f"2-5 cars: {len(manufacturer_counts[(manufacturer_counts >= 2) & (manufacturer_counts <= 5)])} manufacturers")
print(f"6-10 cars: {len(manufacturer_counts[(manufacturer_counts >= 6) & (manufacturer_counts <= 10)])} manufacturers")
print(f"11-20 cars: {len(manufacturer_counts[(manufacturer_counts >= 11) & (manufacturer_counts <= 20)])} manufacturers")
print(f"21-50 cars: {len(manufacturer_counts[(manufacturer_counts >= 21) & (manufacturer_counts <= 50)])} manufacturers")
print(f"50+ cars: {len(manufacturer_counts[manufacturer_counts > 50])} manufacturers")

print(df['manufacturer'].value_counts())

# Data from your distribution
categories = ['1 car', '2-5 cars', '6-10 cars', '11-20 cars', '21-50 cars', '50+ cars']
counts = [34, 22, 13, 15, 9, 55]

# Calculate cumulative removal impact
thresholds = [1, 5, 10, 20, 50]
cars_removed = []
for t in thresholds:
   removed = manufacturer_counts[manufacturer_counts <= t].sum()
   cars_removed.append(removed)

# Create subplots
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

# Plot 1: Manufacturer distribution
ax1.bar(categories, counts, color='steelblue', edgecolor='black')
ax1.set_xlabel('Number of Cars per Manufacturer')
ax1.set_ylabel('Number of Manufacturers')
ax1.set_title('Distribution of Manufacturers by Car Count')
ax1.grid(axis='y', alpha=0.3)

# Add value labels on bars
for i, v in enumerate(counts):
   ax1.text(i, v + 0.5, str(v), ha='center', fontweight='bold')

# Plot 2: Impact of different thresholds
ax2.bar(['≤1', '≤5', '≤10', '≤20', '≤50'], cars_removed, color='coral', edgecolor='black')
ax2.set_xlabel('Threshold (remove manufacturers with ≤X cars)')
ax2.set_ylabel('Total Cars Removed')
ax2.set_title('Impact of Different Thresholds')
ax2.grid(axis='y', alpha=0.3)

# Add value labels
for i, v in enumerate(cars_removed):
   ax2.text(i, v + 10, f'{v} cars', ha='center', fontweight='bold')
   ax2.text(i, v/2, f'{v/len(df)*100:.2f}%', ha='center', color='white', fontweight='bold')

plt.tight_layout()
plt.show()

