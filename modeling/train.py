import torch
import torch.nn as nn
import numpy as np


def train_model(model, train_loader, val_loader, 
    epochs = 100, learning_rate = 0.001, learning_rate_decay_factor = 0.5, weight_decay = 0.00001, gradient_clip = 1.0, 
):
    
    # rip amds
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    model = model.to(device)
    print(f"Training on: {device}")

    
    optimizer = torch.optim.Adam(model.parameters(), lr=learning_rate, weight_decay=weight_decay)
    scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(
        optimizer, mode='min', factor=learning_rate_decay_factor, min_lr=0.000001
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
            loss = mse_loss_fn(predictions.squeeze(), y)
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
                
                # loss
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

        # best model?
        if avg_val_loss < best_val_loss - min_delta:
            best_val_loss = avg_val_loss
            best_model = model.state_dict().copy()
            best_epoch = epoch + 1
            early_stopping_patience_counter = 0  
            
        else:
            early_stopping_patience_counter += 1
            print(f"  Early stopping counter: {early_stopping_patience_counter}/{early_stopping_patience}")
            
            # early stop check
            if early_stopping_patience_counter >= early_stopping_patience:
                print(f"\nEarly stopping triggered at epoch {epoch+1}")
                print(f"Best model was from epoch {best_epoch}")
                break
    
    # loading best model
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
        'best_val_mape' : val_mapes[best_epoch-1]
    }, model