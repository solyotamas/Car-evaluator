import pandas as pd

df = pd.read_csv('data/raw/car_details.csv')
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)

# Transmission analysis
print("Transmission statistics:")
print(f"Missing transmission_type: {df['transmission_type'].isna().sum()} ({df['transmission_type'].isna().sum()/len(df)*100:.1f}%)")
print(f"Missing number_of_gears: {df['number_of_gears'].isna().sum()} ({df['number_of_gears'].isna().sum()/len(df)*100:.1f}%)")
print(f"Missing transmission_subtype: {df['transmission_subtype'].isna().sum()} ({df['transmission_subtype'].isna().sum()/len(df)*100:.1f}%)")

print("\nTransmission type distribution:")
trans_counts = df['transmission_type'].value_counts()
print(trans_counts)

print("\nNumber of gears distribution:")
gears_counts = df['number_of_gears'].value_counts().sort_index()
print(gears_counts)


print(f"Total unique subtypes: {df['transmission_subtype'].nunique()}")

# Price by transmission
print("\nAverage price by transmission type:")
price_by_trans = df.groupby('transmission_type')['price'].agg(['mean', 'median', 'count']).sort_values('mean', ascending=False)
print(price_by_trans)


tiptronic_cars = df[df['transmission_subtype'] == 'tiptronic']
print("\nTransmission types with tiptronic subtype:")
print(tiptronic_cars['transmission_type'].value_counts())



print("\n" + "="*60)
print("FOKOZATMENTES (CVT) ANALYSIS:")
cvt_cars = df[df['transmission_type'].str.contains('Fokozatmentes', na=False)]
if cvt_cars['number_of_gears'].notna().sum() > 0:
   print("\nGear values for CVT cars:")
   print(cvt_cars['number_of_gears'].value_counts().sort_index())



print("Detailed gear analysis by transmission type:")
print("="*60)

# For each transmission type, show gear distribution
for trans_type in df['transmission_type'].unique():
   if pd.notna(trans_type):
       trans_data = df[df['transmission_type'] == trans_type]
       print(f"\n{trans_type}:")
       print(f"  Total cars: {len(trans_data)}")
       print(f"  With gear data: {trans_data['number_of_gears'].notna().sum()}")
       print(f"  Missing gear data: {trans_data['number_of_gears'].isna().sum()}")
       
       if trans_data['number_of_gears'].notna().sum() > 0:
           print(f"  Gear distribution:")
           gear_counts = trans_data['number_of_gears'].value_counts().sort_index()
           for gear, count in gear_counts.items():
               print(f"    {gear:.0f} gears: {count} cars")
           print(f"  Mean: {trans_data['number_of_gears'].mean():.1f}")
           print(f"  Median: {trans_data['number_of_gears'].median():.0f}")
