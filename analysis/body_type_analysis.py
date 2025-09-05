import pandas as pd

df = pd.read_csv('data/raw/car_details.csv')
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)

# Body type analysis
print("Body type statistics:")
print(f"Missing body types: {df['body_type'].isna().sum()}")
print(f"Unique body types: {df['body_type'].nunique()}")

print("\nBody type distribution:")
body_counts = df['body_type'].value_counts()
print(body_counts)

print("\nPercentage distribution:")
for body_type, count in body_counts.items():
   print(f"{body_type}: {count/len(df)*100:.1f}%")

# Price by body type
print("\nAverage price by body type:")
price_by_body = df.groupby('body_type')['price'].agg(['mean', 'median', 'count']).sort_values('mean', ascending=False)
print(price_by_body)

# Check year distribution by body type (to see if some are newer trends)
print("\nAverage year by body type:")
year_by_body = df.groupby('body_type')['year'].agg(['mean', 'median', 'min', 'max']).sort_values('mean', ascending=False)
print(year_by_body)