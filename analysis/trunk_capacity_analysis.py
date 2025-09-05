import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv('data/raw/car_details.csv')
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)


# Trunk capacity analysis
print("Trunk capacity statistics:")
print(f"Missing trunk capacity: {df['trunk_capacity'].isna().sum()} ({df['trunk_capacity'].isna().sum()/len(df)*100:.1f}%)")


# Show extremes
print("\nSmallest trunks:")
print(df.nsmallest(5, 'trunk_capacity')[['manufacturer', 'model', 'body_type', 'trunk_capacity', 'year']])

print("\nLargest trunks:")
print(df.nlargest(20, 'trunk_capacity')[['manufacturer', 'model', 'body_type', 'trunk_capacity', 'year']])

# Remove missing values for analysis
trunk_data = df['trunk_capacity'].dropna()

# Create bins for better visualization
bins = [0, 100, 200, 300, 400, 500, 600, 700, 800, 1000, 2000, 5000, 70000]
labels = ['0-100', '100-200', '200-300', '300-400', '400-500', '500-600', 
         '600-700', '700-800', '800-1000', '1000-2000', '2000-5000', '5000+']
trunk_bins = pd.cut(trunk_data, bins=bins, labels=labels)

print("Trunk capacity distribution:")
print(trunk_bins.value_counts().sort_index())

# Plot
fig, axes = plt.subplots(1, 2, figsize=(15, 5))

# Plot 2: Normal range (0-1000L)
normal_range = trunk_data[trunk_data <= 1000]
axes[0].hist(normal_range, bins=50, edgecolor='black')
axes[0].set_xlabel('Trunk Capacity (L)')
axes[0].set_ylabel('Count')
axes[0].set_title('Normal Cars (0-1000L)')

# Plot 3: Outliers (>2000L)
outliers = trunk_data[trunk_data > 2000]
axes[1].hist(outliers, bins=100, edgecolor='black', color='orange')
axes[1].set_xlabel('Trunk Capacity (L)')
axes[1].set_ylabel('Count')
axes[1].set_title(f'Outliers (>2000L): {len(outliers)} cars')

plt.tight_layout()
plt.show()


# Body type vs trunk capacity analysis
trunk_by_body = df.groupby('body_type')['trunk_capacity'].agg(['mean', 'median', 'min', 'max', 'count']).round(0)
trunk_by_body = trunk_by_body.sort_values('mean', ascending=False)

print("Trunk Capacity by Body Type:")
print("-" * 60)
print(trunk_by_body)

# Explore largest trunks by specific body types
body_types_to_check = ['Pickup','Kombi', 'Ferdehátú', 'Sedan', 'Városi terepjáró (crossover)', 
                       'Terepjáró', 'Cabrio', 'Coupe', 'Egyterű', 'Egyéb', 'Buggy', 'Hot rod', 'Mopedautó', 'Sport', 'Lépcsőshátú']

for body_type in body_types_to_check:
   print(f"\n{'='*60}")
   print(f"Largest trunks for {body_type}:")
   print(f"{'='*60}")
   
   body_type_cars = df[df['body_type'] == body_type]
   if len(body_type_cars) > 0:
       print(body_type_cars.nlargest(30, 'trunk_capacity')[['id','manufacturer', 'model', 'trunk_capacity', 'year']])
       
       # Also show median for reference
       median_trunk = body_type_cars['trunk_capacity'].median()
       print(f"\nMedian for {body_type}: {median_trunk:.0f}L")
       print(f"5x median would be: {median_trunk * 5:.0f}L")