import pandas as pd

df = pd.read_csv('data/raw/car_details.csv')
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)

# Drive type analysis
print("Drive type statistics:")
print(f"Missing drive types: {df['drive_type'].isna().sum()} ({df['drive_type'].isna().sum()/len(df)*100:.1f}%)")
print(f"Unique drive types: {df['drive_type'].nunique()}")

print("\nDrive type distribution:")
drive_counts = df['drive_type'].value_counts()
print(drive_counts)

print("\nPercentage distribution:")
for drive_type, count in drive_counts.items():
   print(f"{drive_type}: {count/len(df)*100:.1f}%")

# Price by drive type
print("\nAverage price by drive type:")
price_by_drive = df.groupby('drive_type')['price'].agg(['mean', 'median', 'count']).sort_values('mean', ascending=False)
print(price_by_drive)
