import torch
import torch.nn as nn
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import matplotlib.gridspec as gridspec



def train_plot(history, skip_first_x = 1):
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4))

    # Loss curves
    ax1.plot(history['train_losses'][skip_first_x:], label='Train')
    ax1.plot(history['val_losses'][skip_first_x:], label='Validation')
    ax1.set_xlabel('Epoch')
    ax1.set_ylabel('Loss')
    ax1.set_title('Training Losses')
    ax1.legend()

    # Learning rate
    ax2.plot(history['learning_rates'])
    ax2.set_xlabel('Epoch')
    ax2.set_ylabel('Learning Rate')
    ax2.set_title('Learning Rate Schedule')

    plt.tight_layout()
    plt.show()

def train_metrics(history):
    best_epoch = history['best_epoch']
    best_val_loss = history['best_val_loss']

    metrics_data = [
        ('BEST EPOCH', best_epoch),
        ('BEST VAL LOSS', best_val_loss)
    ]

    df = pd.DataFrame(metrics_data, columns=['Metric', 'Value'])
    return df

def test_plot(results: dict):
    actual_prices = results['actual_prices']
    prediction_prices = results['prediction_prices']
    percent_errors = results['percent_errors']
    mape = results['metrics']['mape']


    fig = plt.figure(figsize=(10, 8))
    gs = gridspec.GridSpec(2, 2)

    ax1 = fig.add_subplot(gs[0, :])
    ax2 = fig.add_subplot(gs[1, 0])
    ax3 = fig.add_subplot(gs[1, 1])

    # ---------- Plot 1 (top full width) ----------
    ax1.scatter(actual_prices / 1_000_000, prediction_prices / 1_000_000, alpha=0.8, s=3)
    max_val = max(actual_prices.max(), prediction_prices.max()) / 1e6
    ax1.plot([0, max_val], [0, max_val], 'r--', linewidth=2, label='Perfect prediction')
    ax1.set_xlabel('Actual - Million')
    ax1.set_ylabel('Predicted - Million')
    ax1.set_title(f"MAPE: {mape:.1f}%")
    ax1.legend()

    # ---------- Plot 2 (bottom left) ----------
    ax2.hist(percent_errors, bins=30, color='purple', edgecolor='black')
    ax2.set_xlabel('Error (%)')
    ax2.set_ylabel('Count')
    ax2.set_title('Errors')

    # ---------- Plot 3 (bottom right) ----------
    high_errors = percent_errors[percent_errors > 50]
    ax3.hist(high_errors, bins=20, color='red', edgecolor='black')
    ax3.set_xlabel('Error (%)')
    ax3.set_ylabel('Count')
    ax3.set_title(f'High Errors (n={len(high_errors)})')

    plt.tight_layout()
    plt.show()

def test_metrics(results:dict):
    metrics = results['metrics']

    metrics_data = [
        ('MAE', f"{metrics['mae']/1e6:.2f}M Ft", "Average absolute error"),
        ('RMSE', f"{metrics['rmse']/1e6:.2f}M Ft", "Root mean squared error ~ penalizes outliers more"),
        ('Mean APE', f"{metrics['mape']:.2f}%", "Mean absolute percentage error ~ %"),
        ('Median APE', f"{metrics['median_ape']:.2f}%", "Median absolute percentage error ~ %"),
        ('Within 10%', f"{metrics['within_10']:.2f}%", "Predictions with < 10% error"),
        ('Within 20%', f"{metrics['within_20']:.2f}%", "Predictions with < 20% error"),
        ('Within 30%', f"{metrics['within_30']:.2f}%", "Predictions with < 30% error")
    ] 

    df = pd.DataFrame(metrics_data, columns=['Metric', 'Value', 'Description'])
    return df

def test_show_extreme_cases(results: dict, df_test, extreme_threshhold = 100):
    percent_errors = results['percent_errors']
    pred_prices = results['prediction_prices']

    analysis_df = df_test.copy().reset_index(drop=True)
    analysis_df['percent_error'] = percent_errors
    analysis_df['predicted_price'] = pred_prices
    outliers = analysis_df[analysis_df['percent_error'] > extreme_threshhold].copy()

    if len(outliers) > 0:
        return outliers[['price', 'predicted_price', 'percent_error', 'manufacturer', 'model', 'year', 'kw', 'kilometers']].sort_values('percent_error', ascending=False)
    else:
        return pd.DataFrame()
    

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def plot_outlier_years(results: dict, df_test, threshold=50):

    percent_errors = results['percent_errors']
    
    analysis_df = df_test.copy().reset_index(drop=True)
    analysis_df['percent_error'] = percent_errors
    outliers = analysis_df[analysis_df['percent_error'] > threshold].copy()
    
    # ~~~~~~~~~~~~~~~~~~~~~~~~~

    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    
    # ---------- Plot 1 ~ Outlier Count by Year ----------
    year_counts = outliers['year'].value_counts().sort_index()
    axes[0].bar(year_counts.index, year_counts.values, color='red')
    axes[0].set_xlabel('Year')
    axes[0].set_ylabel('Number of Outliers')
    axes[0].set_title('Outlier Count by Year')
    axes[0].grid(True, alpha=0.5)
    
    # ---------- Plot 2 ~ Outlier % by Year ----------
    outlier_by_year = outliers.groupby('year').size()
    total_by_year = analysis_df.groupby('year').size()
    outlier_pct = (outlier_by_year / total_by_year * 100).fillna(0)
    axes[1].plot(outlier_pct.index, outlier_pct.values, marker='o', color='darkred', linewidth=2)
    axes[1].set_xlabel('Year')
    axes[1].set_ylabel('Outlier Percentage (%)')
    axes[1].set_title('% of Cars that are Outliers by Year')
    axes[1].grid(True, alpha=0.5)
    axes[1].axhline(y=outlier_pct.mean(), color='red', linestyle='--', alpha=0.5, label=f'Average: {outlier_pct.mean():.1f}%')
    axes[1].legend()
    
    plt.suptitle(f'Year Analysis of Outliers (>{threshold}% error)', fontsize=14)
    plt.tight_layout()
    plt.show()

def plot_outlier_km(results: dict, df_test, threshold=50):

    percent_errors = results['percent_errors']
    analysis_df = df_test.copy().reset_index(drop=True)
    analysis_df['percent_error'] = percent_errors

    outliers = analysis_df[analysis_df['percent_error'] > threshold].copy()
    
    # ~~~~~~~~~~~~~~~~~~~~~~~~~

    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    
    # ---------- Plot 1 ~ Outlier Count by km ----------
    max_km = df_test['kilometers'].max()
    bin_size = 25_000
    km_bins = np.arange(0, max_km + bin_size, bin_size)

    outliers['km_bin'] = pd.cut(outliers['kilometers'], bins=km_bins)
    km_counts = outliers['km_bin'].value_counts().sort_index()
    
    axes[0].bar(range(len(km_counts)), km_counts.values, color='red')
    axes[0].set_xlabel('Kilometers')
    axes[0].set_ylabel('Number of Outliers')
    axes[0].set_title('Outlier Count by Kilometers')
    axes[0].set_xticks(range(0, len(km_counts), 4))
    axes[0].set_xticklabels([f'{i*25}k' for i in range(0, len(km_counts), 4)], rotation=45)
    axes[0].grid(True, alpha=0.5)
    
    # ---------- Plot 2 ~ Outlier % by km ----------
    km_bins_pct = np.arange(0, 500_000, bin_size)
    analysis_df['km_bin'] = pd.cut(analysis_df['kilometers'], bins=km_bins_pct)
    outlier_by_km = outliers.groupby(pd.cut(outliers['kilometers'], bins=km_bins_pct), observed=False).size()
    total_by_km = analysis_df.groupby('km_bin', observed = False).size()
    outlier_pct = (outlier_by_km / total_by_km * 100).fillna(0)
    
    axes[1].plot(range(len(outlier_pct)), outlier_pct.values, marker='o', color='darkred', linewidth=2)
    axes[1].set_xlabel('Kilometers')
    axes[1].set_ylabel('Outlier Percentage (%)')
    axes[1].set_title('% of Cars that are Outliers by Kilometers')
    axes[1].set_xticks(range(0, len(outlier_pct), 2))
    axes[1].set_xticklabels([f'{i*25}k' for i in range(0, len(outlier_pct), 2)], rotation=45)
    axes[1].axhline(y=outlier_pct.mean(), color='red', linestyle='--', alpha=0.5, label=f'Average: {outlier_pct.mean():.1f}%')
    axes[1].grid(True, alpha=0.5)
    axes[1].legend()
    
    plt.suptitle(f'Kilometer Analysis of Outliers (>{threshold}% error)', fontsize=14)
    plt.tight_layout()
    plt.show()

def plot_outlier_price(results: dict, df_test, price_range:str = '200K - 100M', threshold=50, ):

    percent_errors = results['percent_errors']
    analysis_df = df_test.copy().reset_index(drop=True)
    analysis_df['percent_error'] = percent_errors

    outliers = analysis_df[analysis_df['percent_error'] > threshold].copy()

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    fig, axes = plt.subplots(1, 2, figsize=(14, 6))

    # ---------- Plot 1 ~ Outlier Count by Price ----------
    if price_range == '200K - 100M':
        price_bins = [200_000, 500_000, 1_000_000, 2_000_000, 3_000_000, 5_000_000, 10_000_000, 20_000_000, 50_000_000, 100_000_000]
        price_labels = ['200K - 500K', '500K - 1M', '1M - 2M', '2M - 3M', '3M - 5M', '5M - 10M', '10M - 20M', '20M - 50M','50M - 100M']
    elif price_range == '1M - 50M':
        price_bins = [1_000_000, 1_500_000, 2_000_000, 3_000_000, 5_000_000, 10_000_000, 20_000_000, 50_000_000]
        price_labels = ['1M - 1.5M', '1.5M - 2M', '2M - 3M', '3M - 5M', '5M - 10M', '10M - 20M', '20M - 50M']
    elif price_range == '2M - 50M':
        price_bins = [2_000_000, 3_000_000, 5_000_000, 10_000_000, 20_000_000, 50_000_000]
        price_labels = ['2M - 3M', '3M - 5M', '5M - 10M', '10M - 20M', '20M - 50M']


    outliers['price_bin'] = pd.cut(outliers['price'], bins=price_bins, labels=price_labels)
    price_counts = outliers['price_bin'].value_counts().sort_index()

    axes[0].bar(range(len(price_counts)), price_counts.values, color='red')
    axes[0].set_xlabel('Price')
    axes[0].set_ylabel('Number of Outliers')
    axes[0].set_title('Outlier Count by Price Range')

    axes[0].set_xticks(range(len(price_counts)))
    axes[0].set_xticklabels(price_labels, rotation=45)
    axes[0].grid(True, alpha=0.5)

    # ---------- Plot 2 ~ Outlier % by Price ----------
    analysis_df['price_bin'] = pd.cut(analysis_df['price'], bins=price_bins, labels=price_labels)
    outlier_by_price = outliers.groupby('price_bin', observed=False).size()
    total_by_price = analysis_df.groupby('price_bin', observed=False).size()
    outlier_pct = (outlier_by_price / total_by_price * 100).fillna(0)
    
    axes[1].plot(range(len(outlier_pct)), outlier_pct.values, marker='o', color='darkred', linewidth=2)
    axes[1].set_xlabel('Price Range (Ft)')
    axes[1].set_ylabel('Outlier Percentage (%)')
    axes[1].set_title('% of Cars that are Outliers by Price')

    axes[1].set_xticks(range(len(outlier_pct)))
    axes[1].set_xticklabels(price_labels, rotation=45)

    axes[1].axhline(y=outlier_pct.mean(), color='red', linestyle='--', alpha=0.5, label=f'Average: {outlier_pct.mean():.1f}%')
    axes[1].grid(True, alpha=0.5)
    axes[1].legend()

    plt.suptitle(f'Price Analysis of Outliers (>{threshold}% error)', fontsize=14)
    plt.tight_layout()
    plt.show()
    
def plot_outlier_by_manufacturer(results: dict, df_test, threshold=50, min_listings = 10):

    percent_errors = results['percent_errors']
    analysis_df = df_test.copy().reset_index(drop=True)
    analysis_df['percent_error'] = percent_errors

    outliers = analysis_df[analysis_df['percent_error'] > threshold].copy()

    # ~~~~~~~~~~~~~~~~~~~~~~~~~

    total_counts = analysis_df['manufacturer'].value_counts()
    outlier_counts = outliers['manufacturer'].value_counts()
    outlier_rate = (outlier_counts / total_counts * 100).fillna(0)

    valid_manufacturers = total_counts[total_counts >= min_listings].index
    filtered_rate = outlier_rate.loc[valid_manufacturers]

    top_manufacturers = filtered_rate.nlargest(15)
    top_counts = outlier_counts.loc[top_manufacturers.index]

    fig, axes = plt.subplots(1, 2, figsize=(14, 6))

    # --- Plot 1: Outlier Count by Manufacturer ---
    axes[0].bar(top_counts.index, top_counts.values, color='red')
    axes[0].set_xlabel('Manufacturers')
    axes[0].set_ylabel('Number of Outliers')
    axes[0].set_title(f'Outlier Count for Top {15} Performers')

    axes[0].set_xticks(range(len(top_manufacturers)))
    axes[0].set_xticklabels(top_manufacturers.index, rotation=45, ha='right')

    axes[0].grid(True, alpha=0.5)

    # --- Plot 1: Outlier Percentage by Manufacturer ---
    axes[1].bar(top_manufacturers.index, top_manufacturers.values, color='darkred')
    axes[1].set_xlabel('Manufacturers')
    axes[1].set_ylabel('Outlier Percentage (%)')
    axes[1].set_title(f'Top {15} Manufacturers by Outlier Rate')
    
    axes[1].set_xticks(range(len(top_manufacturers)))
    axes[1].set_xticklabels(top_manufacturers.index, rotation=45, ha='right')

    axes[1].axhline(y=outlier_rate.mean(), color='red', linestyle='--', label=f'Average: {outlier_rate.mean():.1f}%')
    axes[1].grid(True, alpha=0.5)
    axes[1].legend()


    plt.suptitle(f'Manufacturer Analysis of Outliers (>{threshold}% error, min {min_listings} listings)', fontsize=14)
    plt.tight_layout()
    plt.show()

def plot_outlier_by_kw(results: dict, df_test, threshold=50):
    
    percent_errors = results['percent_errors']
    analysis_df = df_test.copy().reset_index(drop=True)
    analysis_df['percent_error'] = percent_errors

    outliers = analysis_df[analysis_df['percent_error'] > threshold].copy()

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    fig, axes = plt.subplots(1, 2, figsize=(14, 6))

    # ---------- Plot 1 ~ Outlier Count by kw ----------
    kw_bins = [0, 50, 75, 100, 125, 150, 200, 300, 500, 1000]
    kw_labels = ['<50', '50-75', '75-100', '100-125', '125-150', '150-200', '200-300', '300-500', '500+']
    
    outliers['kw_bin'] = pd.cut(outliers['kw'], bins=kw_bins, labels=kw_labels)
    kw_counts = outliers['kw_bin'].value_counts().sort_index()

    axes[0].bar(range(len(kw_counts)), kw_counts.values, color='red')
    axes[0].set_xlabel('kw / performance')
    axes[0].set_ylabel('Number of Outliers')
    axes[0].set_title('Outlier Count by kw / performance Range')

    axes[0].set_xticks(range(len(kw_counts)))
    axes[0].set_xticklabels(kw_labels, rotation=45)
    axes[0].grid(True, alpha=0.5)

    # ---------- Plot 2 ~ Outlier % by kw ----------
    analysis_df['kw_bin'] = pd.cut(analysis_df['kw'], bins=kw_bins, labels=kw_labels)
    outlier_by_price = outliers.groupby('kw_bin', observed=False).size()
    total_by_price = analysis_df.groupby('kw_bin', observed=False).size()
    outlier_pct = (outlier_by_price / total_by_price * 100).fillna(0)
    
    axes[1].plot(range(len(outlier_pct)), outlier_pct.values, marker='o', color='darkred', linewidth=2)
    axes[1].set_xlabel('Kw / performance Ranges')
    axes[1].set_ylabel('Outlier Percentage (%)')
    axes[1].set_title('% of Cars that are Outliers by kw / performance')

    axes[1].set_xticks(range(len(outlier_pct)))
    axes[1].set_xticklabels(kw_labels, rotation=45)

    axes[1].axhline(y=outlier_pct.mean(), color='red', linestyle='--', alpha=0.5, label=f'Average: {outlier_pct.mean():.1f}%')
    axes[1].grid(True, alpha=0.5)
    axes[1].legend()

    plt.suptitle(f'Kw / Performance Analysis of Outliers (>{threshold}% error)', fontsize=14)
    plt.tight_layout()
    plt.show()


