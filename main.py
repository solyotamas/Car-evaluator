from torch.utils.data import DataLoader
from sklearn.model_selection import train_test_split

# 1. PREPARE YOUR DATA
# Split your DataFrame into train/validation
df_train, df_val = train_test_split(df, test_size=0.2, random_state=42)

# 2. PREPROCESS AND CREATE DATASETS
# Training data (fit preprocessors)
X_num_train, X_cat_train, y_train, vocab_sizes = preprocess_car_data(df_train, is_training=True)
train_dataset = CarPriceDataset(X_num_train, X_cat_train, y_train)

# Validation data (use fitted preprocessors)
X_num_val, X_cat_val, y_val, _ = preprocess_car_data(df_val, is_training=False)
val_dataset = CarPriceDataset(X_num_val, X_cat_val, y_val)

# 3. CREATE DATALOADERS
train_loader = DataLoader(
    dataset=train_dataset,
    batch_size=64,           # Process 64 cars at once
    shuffle=True,            # Randomize order each epoch
    num_workers=2,           # Parallel data loading
    drop_last=True           # Drop incomplete final batch
)

val_loader = DataLoader(
    dataset=val_dataset,
    batch_size=128,          # Larger batch for validation (no gradients)
    shuffle=False,           # Consistent evaluation order
    num_workers=2,           # Parallel loading
    drop_last=False          # Keep all validation samples
)


# 5. INSPECT YOUR DATALOADERS
print(f"Training batches per epoch: {len(train_loader)}")
print(f"Validation batches per epoch: {len(val_loader)}")
print(f"Training samples: {len(train_dataset)}")
print(f"Validation samples: {len(val_dataset)}")

# Test a single batch
numerical, categorical, targets = next(iter(train_loader))
print(f"Batch shapes:")
print(f"  Numerical: {numerical.shape}")
print(f"  Categorical: {categorical.shape}")  
print(f"  Targets: {targets.shape}")
print(f"Vocabulary sizes for embeddings: {vocab_sizes}")