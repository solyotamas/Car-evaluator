import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv('data/raw/car_details.csv')
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)



print("Kilometer statistics:")
print(df['kilometers'].describe())

print(f"\nMissing kilometers: {df['kilometers'].isna().sum()}")

# Check suspicious values
print(f"\nCars with 0 km: {len(df[df['kilometers'] == 0])}")
print(f"Cars >500k km: {len(df[df['kilometers'] > 500000])}")
print(f"Cars >750k km: {len(df[df['kilometers'] > 750000])}")
print(f"Cars >1M km: {len(df[df['kilometers'] > 1000000])}")

# Better distribution plots
plt.figure(figsize=(12, 4))

# Plot 1: Normal cars (<500k km)
plt.subplot(1,2,1)
plt.hist(df[df['kilometers'] < 500000]['kilometers'], bins=50, edgecolor='black')
plt.xlabel('Kilometers')
plt.title('Normal Cars (<500k km)')

# Plot 2: High mileage cars (≥500k km)
plt.subplot(1,2,2)
high_km = df[df['kilometers'] >= 500000]['kilometers']
if len(high_km) > 0:
   plt.hist(high_km, bins=30, edgecolor='black', color='orange')
   plt.xlabel('Kilometers')
   plt.title(f'High Mileage Cars (≥500k km) - {len(high_km)} cars')
else:
   plt.text(0.5, 0.5, 'No cars ≥500k km', ha='center', va='center')
   plt.title('High Mileage Cars (≥500k km)')

plt.tight_layout()
plt.show()
