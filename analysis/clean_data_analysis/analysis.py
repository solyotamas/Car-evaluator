import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats

df = pd.read_csv('data/clean/car_details.csv')
pd.set_option('display.max_columns', None)

print("=== PRICE ANALYSIS ON CLEANED DATA ===\n")
print(f"Dataset shape: {df.shape}")
print(f"Price column: {df['price'].dtype}")

# ==================== PRICE DISTRIBUTION ====================
print("\n1. PRICE DISTRIBUTION")
print("-" * 50)

print("Basic statistics:")
print(df['price'].describe())

print(f"\nPrice range: {df['price'].min():,.0f} - {df['price'].max():,.0f} Ft")
print(f"Mean: {df['price'].mean():,.0f} Ft")
print(f"Median: {df['price'].median():,.0f} Ft")
print(f"Std: {df['price'].std():,.0f} Ft")

skewness = stats.skew(df['price'])
print(f"Skewness: {skewness:.2f} {'(right-skewed)' if skewness > 0 else '(left-skewed)'}")

ranges = [
    (0, 1_000_000, "Under 1M"),
    (1_000_000, 3_000_000, "1M-3M"), 
    (3_000_000, 5_000_000, "3M-5M"),
    (5_000_000, 10_000_000, "5M-10M"),
    (10_000_000, 20_000_000, "10M-20M"),
    (20_000_000, 50_000_000, "20M-50M"),
    (50_000_000, float('inf'), "50M- ")
]

print("\nPrice ranges:")
for low, high, label in ranges:
    count = len(df[(df['price'] >= low) & (df['price'] < high)])
    pct = count / len(df) * 100
    print(f"{label}: {count:,} cars ({pct:.1f}%)")

# ==================== LOG TRANSFORMATION ANALYSIS ====================
print("\n2. LOG TRANSFORMATION ANALYSIS")
print("-" * 50)

# Log transformation for neural networks
df['log_price'] = np.log(df['price'])

print("Original vs Log-transformed:")
print(f"Original - Mean: {df['price'].mean():,.0f}, Std: {df['price'].std():,.0f}")
print(f"Log - Mean: {df['log_price'].mean():.3f}, Std: {df['log_price'].std():.3f}")
print(f"Log skewness: {stats.skew(df['log_price']):.3f}")

# ==================== PRICE BY CATEGORICAL FEATURES ====================
print("\n3. PRICE BY CATEGORICAL FEATURES")
print("-" * 50)

categorical_features = ['manufacturer','model','fuel_type', 'condition', 'body_type', 'transmission_type', 'drive_type', 'color']

for feature in categorical_features:
    print(f"\n{feature.upper()}:")
    price_stats = df.groupby(feature)['price'].agg(['count', 'mean', 'median']).round(0)
    price_stats = price_stats.sort_values('mean', ascending=False)
    print(price_stats)

# ==================== PRICE CORRELATIONS ====================
print("\n4. PRICE CORRELATIONS WITH NUMERICAL FEATURES")
print("-" * 50)

numerical_features = ['year', 'kilometers', 'kw', 'engine_capacity', 'trunk_capacity', 'seats', 'number_of_gears']
correlations = df[numerical_features + ['price']].corr()['price'].sort_values(ascending=False)

print("Correlations with price:")
for feature, corr in correlations.items():
    if feature != 'price':
        strength = "strong" if abs(corr) > 0.5 else "moderate" if abs(corr) > 0.3 else "weak"
        print(f"{feature:20}: {corr:6.3f} ({strength})")

# ==================== OUTLIER ANALYSIS ====================
print("\n5. OUTLIER ANALYSIS")
print("-" * 50)

Q1 = df['price'].quantile(0.25)
Q3 = df['price'].quantile(0.75)
IQR = Q3 - Q1
lower_bound = Q1 - 1.5 * IQR
upper_bound = Q3 + 1.5 * IQR

outliers = df[(df['price'] < lower_bound) | (df['price'] > upper_bound)]
print(f"IQR outliers: {len(outliers):,} cars ({len(outliers)/len(df)*100:.1f}%)")
print(f"Upper bound: {upper_bound:,.0f} Ft")

# Most expensive cars
print("\nTop 10 most expensive cars:")
expensive = df.nlargest(10, 'price')[['manufacturer', 'model', 'year', 'price', 'condition']]
print(expensive.to_string(index=False))

# ==============================
categorical_features = ['manufacturer','model','fuel_type', 'condition', 'body_type', 'transmission_type', 'drive_type', 'color']

for col in categorical_features:
    if "Unknown" in df[col].unique():
        print(f"{col}: Has 'Unknown' category ✓")
    else:
        print(f"{col}: No 'Unknown' category")


print(f"Unique manufacturers: {df['manufacturer'].nunique()}")
print(f"Unique models: {df['model'].nunique()}")