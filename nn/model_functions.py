import torch
import torch.nn as nn
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

def train_model(model, train_loader, val_loader, 
    epochs = 100, learning_rate = 0.001, weight_decay = 0.00001, gradient_clip = 1.0
):
    
    # i have amd so its always cpu
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    model = model.to(device)
    print(f"Training on: {device}")

    optimizer = torch.optim.Adam(model.parameters(), lr=learning_rate, weight_decay=weight_decay)
    scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(
        optimizer, mode='min', factor=0.5
    )
    mse_loss_fn = nn.MSELoss()
    

    # History tracking
    train_losses = []
    val_losses = []
    val_mapes = []
    learning_rates = []

    # Early stopping
    best_val_loss = float('inf')
    best_model = None
    best_epoch = 0
    early_stopping_patience =40
    early_stopping_patience_counter = 0
    min_delta = 0.0001


    for epoch in range(epochs):

        current_lr = optimizer.param_groups[0]['lr']
        learning_rates.append(current_lr)

        # ============ TRAINING ============
        model.train()
        train_batch_each_loss = []
        
        for X_num, X_cat, y in train_loader:
            X_num, X_cat, y = X_num.to(device), X_cat.to(device), y.to(device)
            
            optimizer.zero_grad()
            predictions = model(X_num, X_cat).squeeze()
            loss = mse_loss_fn(predictions, y)
            loss.backward()

            if gradient_clip > 0:
                torch.nn.utils.clip_grad_norm_(model.parameters(), gradient_clip)
            
            optimizer.step()
            train_batch_each_loss.append(loss.item())
        
        # avg train loss for the epoch
        avg_train_loss = np.mean(train_batch_each_loss)
        train_losses.append(avg_train_loss)


        # ============ VALIDATION ============
        model.eval()
        val_batch_each_loss = []
        val_predictions = []
        val_targets = []
        
        with torch.no_grad():
            for X_num, X_cat, y in val_loader:
                X_num, X_cat, y = X_num.to(device), X_cat.to(device), y.to(device)
                
                predictions = model(X_num, X_cat).squeeze()
                loss = mse_loss_fn(predictions, y)
                
                # Track loss
                val_batch_each_loss.append(loss.item())
                val_predictions.extend(predictions.cpu().numpy())
                val_targets.extend(y.cpu().numpy())
        
        # avg val loss for the epoch
        avg_val_loss = np.mean(val_batch_each_loss)
        val_losses.append(avg_val_loss)

        # Calculate MAPE on actual prices
        val_predictions = np.array(val_predictions)
        val_targets = np.array(val_targets)
        actual_prices = np.expm1(val_targets)
        pred_prices = np.expm1(val_predictions)
        mape = np.mean(np.abs((actual_prices - pred_prices) / actual_prices)) * 100
        val_mapes.append(mape)
        
        print(f"\nEpoch [{epoch+1}/{epochs}] (LR: {current_lr:.6f})")
        print(f"  Train Loss: {avg_train_loss:.4f}")
        print(f"  Val Loss:   {avg_val_loss:.4f}")
        print(f"  Val MAPE:   {mape:.2f}%")


        scheduler.step(avg_val_loss)

        # Check if this is the best model
        if avg_val_loss < best_val_loss - min_delta:
            best_val_loss = avg_val_loss
            best_model = model.state_dict().copy()
            best_epoch = epoch + 1
            early_stopping_patience_counter = 0  
            
        else:
            early_stopping_patience_counter += 1
            print(f"  Early stopping counter: {early_stopping_patience_counter}/{early_stopping_patience}")
            
            # Early stopping check
            if early_stopping_patience_counter >= early_stopping_patience:
                print(f"\n✋ Early stopping triggered at epoch {epoch+1}")
                print(f"Best model was from epoch {best_epoch}")
                break
    
    # Load best model
    model.load_state_dict(best_model)

    print("\n" + "="*60)
    print("TRAINING COMPLETED!")
    print(f"Best epoch: {best_epoch}")
    print(f"Best val loss: {best_val_loss:.6f}")
    print(f"Best val MAPE: {val_mapes[best_epoch-1]:.2f}%")



    return {
        'train_losses': train_losses,
        'val_losses': val_losses,
        'val_mapes' : val_mapes,
        'learning_rates' : learning_rates,
        'best_val_loss' : best_val_loss,
        'best_epoch' : best_epoch,
    }, model

def plot_training(history):
    
    # Simple plot
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4))

    # Loss curves - THE MOST IMPORTANT PLOT
    ax1.plot(history['train_loss'], label='Train')
    ax1.plot(history['val_loss'], label='Validation')
    ax1.set_xlabel('Epoch')
    ax1.set_ylabel('Loss')
    ax1.set_title('Training Progress')
    ax1.legend()

    # Learning rate
    ax2.plot(history['learning_rate'])
    ax2.set_xlabel('Epoch')
    ax2.set_ylabel('Learning Rate')
    ax2.set_title('Learning Rate Schedule')

    plt.tight_layout()
    plt.show()

def test_model(model, test_loader):
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

    model.eval()
    model = model.to(device)
    
    predictions = []
    actuals = []
    
    # Get all predictions
    with torch.no_grad():
        for X_num, X_cat, y in test_loader:
            X_num = X_num.to(device)
            X_cat = X_cat.to(device)
            y = y.to(device)
            
            preds = model(X_num, X_cat).squeeze()
            
            predictions.extend(preds.cpu().numpy())
            actuals.extend(y.cpu().numpy())
    
    # Convert to numpy arrays
    predictions = np.array(predictions)
    actuals = np.array(actuals)
    
    # Convert from log to actual prices
    actual_prices = np.expm1(actuals)
    pred_prices = np.expm1(predictions)
    
    # Calculate metrics
    errors = pred_prices - actual_prices
    abs_errors = np.abs(errors)
    percent_errors = abs_errors / actual_prices * 100
    
    # Calculate key metrics
    mae = np.mean(abs_errors)
    mape = np.mean(percent_errors)
    rmse = np.sqrt(np.mean(errors**2))
    median_ape = np.median(percent_errors)
    
    # Accuracy within thresholds
    within_10 = (percent_errors < 10).sum() / len(percent_errors) * 100
    within_20 = (percent_errors < 20).sum() / len(percent_errors) * 100
    within_30 = (percent_errors < 30).sum() / len(percent_errors) * 100
    
    # Print results
    print("\n" + "="*60)
    print("MODEL TEST RESULTS")
    print("="*60)
    print(f"Test set size: {len(predictions):,} cars")
    print("\nError Metrics:")
    print(f"  MAE:  {mae/1e6:.2f}M Ft")
    print(f"  RMSE: {rmse/1e6:.2f}M Ft")
    print(f"  MAPE: {mape:.2f}%")
    print(f"  Median APE: {median_ape:.2f}%")
    print("\nAccuracy:")
    print(f"  Within 10%: {within_10:.1f}%")
    print(f"  Within 20%: {within_20:.1f}%")
    print(f"  Within 30%: {within_30:.1f}%")
    print("\nPrediction Bias:")
    print(f"  Mean error: {errors.mean():.2f} Ft")
    print(f"  Overpredictions: {(errors > 0).sum()/len(errors)*100:.1f}%")
    print(f"  Underpredictions: {(errors < 0).sum()/len(errors)*100:.1f}%")
    print("="*60)

    return pred_prices, actual_prices, errors, percent_errors, {
            'mae': mae,
            'rmse': rmse,
            'mape': mape,
            'median_ape': median_ape,
            'within_10': within_10,
            'within_20': within_20,
            'within_30': within_30
        }
    
def plot_test(actual_prices, prediction_prices, percent_errors, mape):
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))


    ax1.scatter(actual_prices, prediction_prices, alpha=0.5)
    ax1.plot([min, max], [min, max], 'r--') 
    ax1.set_xlabel('Actual')
    ax1.set_ylabel('Predicted')
    ax1.set_title(f'MAPE: {mape:.1f}%')


    ax2.hist(percent_errors, bins=30)
    ax2.set_xlabel('Error (%)')
    ax2.set_ylabel('Count')
    ax2.set_title('How wrong are we?')

    plt.tight_layout()
    plt.show()




def plot_outlier_years(model, test_loader, df_test, device='cpu', threshold=50):
    """Plot year distribution of outliers"""
    
    model.eval()
    predictions = []
    actuals = []
    
    with torch.no_grad():
        for X_num, X_cat, y in test_loader:
            X_num, X_cat, y = X_num.to(device), X_cat.to(device), y.to(device)
            preds = model(X_num, X_cat).squeeze()
            predictions.extend(preds.cpu().numpy())
            actuals.extend(y.cpu().numpy())
    
    # Calculate errors
    actual_prices = np.expm1(actuals)
    pred_prices = np.expm1(predictions)
    percent_errors = np.abs(pred_prices - actual_prices) / actual_prices * 100
    
    # Create analysis df
    analysis_df = df_test.copy().reset_index(drop=True)
    analysis_df['percent_error'] = percent_errors
    
    outliers = analysis_df[analysis_df['percent_error'] > threshold]
    # Plot
    fig, axes = plt.subplots(1, 2, figsize=(18, 6))
    
    year_counts = outliers['year'].value_counts().sort_index()
    axes[0].bar(year_counts.index, year_counts.values, color='red', alpha=0.7)
    axes[0].set_xlabel('Year')
    axes[0].set_ylabel('Number of Outliers')
    axes[0].set_title('Outlier Count by Year')
    axes[0].grid(True, alpha=0.3)
    
    outlier_by_year = outliers.groupby('year').size()
    total_by_year = analysis_df.groupby('year').size()
    outlier_pct = (outlier_by_year / total_by_year * 100).fillna(0)
    
    axes[1].plot(outlier_pct.index, outlier_pct.values, marker='o', color='darkred', linewidth=2)
    axes[1].set_xlabel('Year')
    axes[1].set_ylabel('Outlier Percentage (%)')
    axes[1].set_title('% of Cars that are Outliers by Year')
    axes[1].grid(True, alpha=0.3)
    axes[1].axhline(y=outlier_pct.mean(), color='red', linestyle='--', alpha=0.5, label=f'Average: {outlier_pct.mean():.1f}%')
    axes[1].legend()
    
    plt.suptitle(f'Year Analysis of Outliers (>{threshold}% error)', fontsize=14)
    plt.tight_layout()
    plt.show()

def plot_outlier_km(model, test_loader, df_test, device='cpu', threshold=50):
    """Plot kilometer distribution of outliers"""
    
    model.eval()
    predictions = []
    actuals = []
    
    with torch.no_grad():
        for X_num, X_cat, y in test_loader:
            X_num, X_cat, y = X_num.to(device), X_cat.to(device), y.to(device)
            preds = model(X_num, X_cat).squeeze()
            predictions.extend(preds.cpu().numpy())
            actuals.extend(y.cpu().numpy())
    
    # Calculate errors
    actual_prices = np.expm1(actuals)
    pred_prices = np.expm1(predictions)
    percent_errors = np.abs(pred_prices - actual_prices) / actual_prices * 100
    
    # Create analysis df
    analysis_df = df_test.copy().reset_index(drop=True)
    analysis_df['percent_error'] = percent_errors
    
    outliers = analysis_df[analysis_df['percent_error'] > threshold]
    
    # Plot
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    
    # 1. Outlier count by km bins
    km_bins = np.arange(0, 500000, 20000)
    outliers['km_bin'] = pd.cut(outliers['kilometers'], bins=km_bins)
    km_counts = outliers['km_bin'].value_counts().sort_index()
    
    axes[0].bar(range(len(km_counts)), km_counts.values, color='red', alpha=0.7)
    axes[0].set_xlabel('Kilometers (bins of 20k)')
    axes[0].set_ylabel('Number of Outliers')
    axes[0].set_title('Outlier Count by Kilometers')
    axes[0].set_xticks(range(0, len(km_counts), 5))
    axes[0].set_xticklabels([f'{i*20}k' for i in range(0, len(km_counts), 5)], rotation=45)  # FIXED!
    axes[0].grid(True, alpha=0.3)
    
    # 2. Outlier percentage by km
    km_bins_pct = np.arange(0, 400000, 25000)
    analysis_df['km_bin'] = pd.cut(analysis_df['kilometers'], bins=km_bins_pct)
    outlier_by_km = outliers.groupby(pd.cut(outliers['kilometers'], bins=km_bins_pct)).size()
    total_by_km = analysis_df.groupby('km_bin').size()
    outlier_pct = (outlier_by_km / total_by_km * 100).fillna(0)
    
    axes[1].plot(range(len(outlier_pct)), outlier_pct.values, marker='o', color='darkred', linewidth=2)
    axes[1].set_xlabel('Kilometers')
    axes[1].set_ylabel('Outlier Percentage (%)')
    axes[1].set_title('% of Cars that are Outliers by Kilometers')
    axes[1].set_xticks(range(0, len(outlier_pct), 2))
    axes[1].set_xticklabels([f'{i*50}k' for i in range(0, len(outlier_pct), 2)], rotation=45)
    axes[1].axhline(y=outlier_pct.mean(), color='red', linestyle='--', alpha=0.5, label=f'Average: {outlier_pct.mean():.1f}%')
    axes[1].grid(True, alpha=0.3)
    axes[1].legend()
    
    plt.suptitle(f'Kilometer Analysis of Outliers (>{threshold}% error)', fontsize=14)
    plt.tight_layout()
    plt.show()










































