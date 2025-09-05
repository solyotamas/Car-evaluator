import torch
import numpy as np

def test_model(model, test_loader):
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

    model.eval()
    model = model.to(device)
    
    predictions = []
    actuals = []
    

    with torch.no_grad():
        for X_num, X_cat, y in test_loader:
            X_num = X_num.to(device)
            X_cat = X_cat.to(device)
            y = y.to(device)
            
            preds = model(X_num, X_cat).squeeze()
            
            predictions.extend(preds.cpu().numpy())
            actuals.extend(y.cpu().numpy())
    
    predictions = np.array(predictions)
    actuals = np.array(actuals)
    
    # convert back from log
    actual_prices = np.expm1(actuals)
    pred_prices = np.expm1(predictions)
    
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    errors = pred_prices - actual_prices
    abs_errors = np.abs(errors)
    percent_errors = abs_errors / actual_prices * 100
    
    mae = np.mean(abs_errors)
    mape = np.mean(percent_errors)
    rmse = np.sqrt(np.mean(errors**2))
    median_ape = np.median(percent_errors)
    
    within_10 = (percent_errors < 10).sum() / len(percent_errors) * 100
    within_20 = (percent_errors < 20).sum() / len(percent_errors) * 100
    within_30 = (percent_errors < 30).sum() / len(percent_errors) * 100
    

    return {
        'actual_prices' : actual_prices,
        'prediction_prices' : pred_prices,
        'percent_errors' : percent_errors,
        'metrics' : {
            'mae': mae,
            'rmse': rmse,
            'mape': mape,
            'median_ape': median_ape,
            'within_10': within_10,
            'within_20': within_20,
            'within_30': within_30
        }
    }