import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv('data/raw/car_details.csv')
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)


# Power (kw/le) analysis
print("Power statistics:")
print(f"Missing kw: {df['kw'].isna().sum()} ({df['kw'].isna().sum()/len(df)*100:.1f}%)")
print(f"Missing le: {df['le'].isna().sum()} ({df['le'].isna().sum()/len(df)*100:.1f}%)")

# Check if they're always both missing or both present
both_missing = df['kw'].isna() & df['le'].isna()
one_missing = (df['kw'].isna() & df['le'].notna()) | (df['kw'].notna() & df['le'].isna())
print(f"\nBoth missing: {both_missing.sum()}")
print(f"Only one missing: {one_missing.sum()}")

# Correlation between kw and le
correlation = df[['kw', 'le']].corr()
print(f"\nCorrelation:\n{correlation}")


# ==========================
# KW

print("KW Statistics:")
print(df['kw'].describe())

# extreme values
print(f"\nExtreme values:")
print(f"Cars with kw < 30: {len(df[df['kw'] < 30])}")
print(f"Cars with kw > 500: {len(df[df['kw'] > 500])}")
print(f"Cars with kw > 700: {len(df[df['kw'] > 700])}")

# Show extremes
print("\nLowest power cars:")
print(df.nsmallest(10, 'kw')[['manufacturer', 'model', 'year', 'kw', 'le', 'price']])

print("\nHighest power cars:")
print(df.nlargest(10, 'kw')[['manufacturer', 'model', 'year', 'kw', 'le', 'price']])




# Visualize
plt.figure(figsize=(10, 5))

plt.subplot(1,3,1)
plt.hist(df['kw'].dropna(), bins=50, edgecolor='black')
plt.xlabel('KW')
plt.ylabel('Count')
plt.title('KW Distribution (All)')

plt.subplot(1,3,2)
plt.hist(df[df['kw'] < 300]['kw'], bins=50, edgecolor='black')
plt.xlabel('KW')
plt.ylabel('Count')
plt.title('KW Distribution (<300 kw)')

plt.tight_layout()
plt.show()


print("Cars by KW range:")

ranges = [(0, 20), (0,30) ,(20, 40), (40, 60), (60, 80), (80, 100), 
          (100,120), (120,140), (140, 160), (160,180), (180,200),
          (200,220), (220,240), (240, 260), (260,280), (280,300)
         ]

for low, high in ranges:
   count = len(df[(df['kw'] >= low) & (df['kw'] < high)])
   print(f"{low} - {high} kw: {count} cars")


print(f"300+ kw: {len(df[df['kw'] >= 300])} cars")


print("\nDetailed 0-20 kw breakdown:")
print(f"  0-10 kw:  {len(df[(df['kw'] >= 0) & (df['kw'] < 10)])} cars")
print(f"  10-20 kw: {len(df[(df['kw'] >= 10) & (df['kw'] < 20)])} cars")


#================ What will be dropped ===============
print("\n" + "=" * 60)

missing_kw = df['kw'].isna().sum()
under = len(df[df['kw'] < 30])
over = len(df[df['kw'] > 1000])

print(f"Will be dropped:")
print(f"Cars with missing kw: {missing_kw}")
print(f"Cars with <30 kw: {under}")
print(f"Cars with >1000 kw: {over}")