import pandas as pd

df = pd.read_csv('data/raw/car_details.csv')
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)

# Engine capacity analysis
print("Engine capacity statistics:")
print(f"Missing engine capacity: {df['engine_capacity'].isna().sum()} ({df['engine_capacity'].isna().sum()/len(df)*100:.1f}%)")
print("\nBasic statistics:")
print(df['engine_capacity'].describe())

# Check distribution
print("\nEngine capacity ranges:")
ranges = [(0, 500), (500, 1000), (1000, 1500), (1500, 2000), (2000, 2500), 
         (2500, 3000), (3000, 4000), (4000, 5000), (5000, 10000), (10000, 50000)]

for low, high in ranges:
   count = len(df[(df['engine_capacity'] >= low) & (df['engine_capacity'] < high)])
   if count > 0:
       print(f"{low:5d} - {high:5d} cc: {count:6d} cars")

# Check extremes
print("\nExtreme values:")
print(f"Engine < 100cc: {len(df[df['engine_capacity'] < 100])}")
print(f"Engine > 10000cc: {len(df[df['engine_capacity'] > 10000])}")

print("\nSmallest engines:")
print(df.nsmallest(100, 'engine_capacity')[['manufacturer', 'model', 'engine_capacity', 'fuel_type', 'kw']])

print("\nLargest engines:")
print(df.nlargest(10, 'engine_capacity')[['manufacturer', 'model', 'engine_capacity', 'fuel_type', 'kw']])

# By fuel type
print("\nAverage engine capacity by fuel type:")
engine_by_fuel = df.groupby('fuel_type')['engine_capacity'].agg(['mean', 'median', 'count']).sort_values('mean', ascending=False)
print(engine_by_fuel)


# WTF

# Find electric cars with engine capacity > 0
electric_with_engine = df[(df['fuel_type'] == 'Elektromos') & (df['engine_capacity'] > 0)]

print(f"Electric cars with engine capacity > 0: {len(electric_with_engine)} cars")
print("\nDetails:")
print(electric_with_engine[['id','manufacturer', 'model', 'engine_capacity', 'fuel_type','kw', 'year']].to_string())


# Check correlations with engine capacity
print("Correlations with engine capacity:")

# Numerical correlations
numerical_corr = df[['engine_capacity', 'kw', 'price', 'year', 'trunk_capacity']].corr()['engine_capacity'].sort_values(ascending=False)
print("\nNumerical correlations:")
print(numerical_corr)

# By fuel type
print("\nEngine capacity by fuel type (CV = coefficient of variation):")
fuel_stats = df.groupby('fuel_type')['engine_capacity'].agg(['mean', 'std', 'median', 'count'])
fuel_stats['cv'] = fuel_stats['std'] / fuel_stats['mean']  # Lower = more consistent
print(fuel_stats.sort_values('cv'))


#================ What will be dropped ===============
print("\n" + "=" * 60)

missing_cc = df['engine_capacity'].isna().sum()
under = len(df[df['engine_capacity'] < 500])
over = len(df[df['engine_capacity'] > 10000])

print(f"Will be dropped:")
print(f"Cars under 500 cc: {under}")
print(f"Car over 10 000 cc: {over}")
print(f"Will be imputed:")
print(f"Cars: {missing_cc}")