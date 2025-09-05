import pandas as pd

df = pd.read_csv('data/raw/car_details.csv')
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)

# Color analysis
print("Color statistics:")
print(f"Missing colors: {df['color'].isna().sum()} ({df['color'].isna().sum()/len(df)*100:.1f}%)")
print(f"Unique colors: {df['color'].nunique()}")

print("\nColors:")
color_counts = df['color'].value_counts()
print(color_counts)

print(f"\nTotal unique colors: {len(color_counts)}")

# Check for potential grouping patterns
print("\nColors with 'metál' (metallic):")
metal_colors = [c for c in df['color'].unique() if 'metál' in str(c).lower()]
print(f"Count: {len(metal_colors)}")
print(metal_colors[:10])  # Show first 10

print("\nColors with 'gyöngyház' (pearl):")
pearl_colors = [c for c in df['color'].unique() if 'gyöngyház' in str(c).lower()]
print(f"Count: {len(pearl_colors)}")

# Price by main color groups
print("\nAverage price by top 10 colors:")
top_colors = color_counts.head(10).index
price_by_color = df[df['color'].isin(top_colors)].groupby('color')['price'].agg(['mean', 'median', 'count'])
print(price_by_color.sort_values('mean', ascending=False))