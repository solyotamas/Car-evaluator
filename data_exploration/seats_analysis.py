import pandas as pd

df = pd.read_csv('data/raw/car_details.csv')
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)

# Seats analysis
print("Seats statistics:")
print(f"Missing seats: {df['seats'].isna().sum()} ({df['seats'].isna().sum()/len(df)*100:.1f}%)")

print("\nSeat distribution:")
seat_counts = df['seats'].value_counts().sort_index()
print(seat_counts)

# Check extremes
print("\nExtreme values:")
print(f"Cars with 1 seat: {len(df[df['seats'] == 1])}")
print(f"Cars with 2 seats: {len(df[df['seats'] == 2])}")
print(f"Cars with >9 seats: {len(df[df['seats'] > 9])}")
print(f"Cars with >15 seats: {len(df[df['seats'] > 15])}")

# Show outliers
print("\nCars with unusual seat counts (>9):")
unusual_seats = df[df['seats'] > 9].sort_values('seats', ascending=False)
print(unusual_seats[['manufacturer', 'model', 'body_type', 'seats', 'year']].head(20))

# Seats by body type
print("\nAverage seats by body type:")
seats_by_body = df.groupby('body_type')['seats'].agg(['mean', 'median', 'min', 'max', 'count']).sort_values('mean', ascending=False)
print(seats_by_body)