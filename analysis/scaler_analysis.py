import pandas as pd
import numpy as np
from sklearn.preprocessing import RobustScaler, StandardScaler
import matplotlib.pyplot as plt

# Load your data
df = pd.read_csv('data/clean/car_details.csv')


numerical_features = [
    'year', 'kilometers', 'kw', 'trunk_capacity', 
    'seats', 'engine_capacity', 'number_of_gears'
]
numerical_features = [
    'year', 'kilometers', 'kw','engine_capacity', 'metallic', 'km_imputed'
]

sample_df = df[numerical_features]

print("BEFORE SCALING:")
print("=" * 50)
print(sample_df.describe())

standard_scaler = StandardScaler()
standard_scaled_data = standard_scaler.fit_transform(sample_df)
standard_scaled_df = pd.DataFrame(standard_scaled_data, columns=numerical_features)
print("\nAFTER STANDARD SCALING:")
print("=" * 50)
print(standard_scaled_df.describe())

robust_scaler = RobustScaler()
robust_scaled_data = robust_scaler.fit_transform(sample_df)
robust_scaled_df = pd.DataFrame(robust_scaled_data, columns=numerical_features)
print("\nAFTER ROBUST SCALING:")
print("=" * 50)
print(robust_scaled_df.describe())

# Compare scaler parameters
print("\nSCALER PARAMETERS COMPARISON:")
print("=" * 50)
for i, feature in enumerate(numerical_features):
    print(f"\n{feature}:")
    print(f"  StandardScaler - Mean: {standard_scaler.mean_[i]:.2f}, Std: {standard_scaler.scale_[i]:.2f}")
    print(f"  RobustScaler   - Median: {robust_scaler.center_[i]:.2f}, IQR: {robust_scaler.scale_[i]:.2f}")

# Visualize the comparison
fig, axes = plt.subplots(3, len(numerical_features), figsize=(20, 12))

for i, feature in enumerate(numerical_features):
    # Original data
    axes[0, i].hist(sample_df[feature], bins=30, alpha=0.7, color='blue')
    axes[0, i].set_title(f'{feature}\n(Original)', fontsize=10)
    axes[0, i].tick_params(axis='x', rotation=45)
    
    # StandardScaler
    axes[1, i].hist(standard_scaled_df[feature], bins=30, alpha=0.7, color='green')
    axes[1, i].set_title(f'{feature}\n(StandardScaler)', fontsize=10)
    axes[1, i].tick_params(axis='x', rotation=45)
    
    # RobustScaler
    axes[2, i].hist(robust_scaled_df[feature], bins=30, alpha=0.7, color='red')
    axes[2, i].set_title(f'{feature}\n(RobustScaler)', fontsize=10)
    axes[2, i].tick_params(axis='x', rotation=45)

plt.tight_layout()
plt.suptitle('Original vs StandardScaler vs RobustScaler', fontsize=16, y=1.02)
plt.show()
