import pandas as pd

df = pd.read_csv('data/raw/car_details.csv')
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)
pd.set_option('display.max_colwidth', None)
pd.set_option('display.width', None) 

# Condition analysis
print("Condition statistics:")
print(f"Missing conditions: {df['condition'].isna().sum()}")
print(f"Unique conditions: {df['condition'].nunique()}")

print("\nCondition distribution:")
condition_counts = df['condition'].value_counts()
print(condition_counts)

print("\nPercentage distribution:")
for condition, count in condition_counts.items():
   print(f"{condition}: {count/len(df)*100:.1f}%")

# Check price by condition
print("\nAverage price by condition:")
price_by_condition = df.groupby('condition')['price'].agg(['mean', 'median', 'count']).sort_values('mean', ascending=False)
print(price_by_condition)