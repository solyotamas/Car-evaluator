import torch
from torch.utils.data import Dataset

class CarPriceDataset(Dataset):
    """
    PyTorch Dataset for car price prediction with mixed data types.
    
    Handles both numerical and categorical features separately since
    they'll be processed differently by the neural network.
    """
    
    def __init__(self, X_numerical, X_categorical, y):
        """
        Args:
            X_numerical (np.ndarray): Standardized numerical features [n_samples, n_numerical_features]
            X_categorical (np.ndarray): Label-encoded categorical features [n_samples, n_categorical_features]
            y (np.ndarray): Target values (log-transformed prices) [n_samples]
        """

        self.X_numerical = torch.tensor(X_numerical, dtype=torch.float32)
        self.X_categorical = torch.tensor(X_categorical, dtype=torch.int64) 
        self.y = torch.tensor(y, dtype=torch.float32) 
        
        assert len(self.X_numerical) == len(self.X_categorical) == len(self.y), "All inputs must have the same number of samples"
    
    def __len__(self):
        return len(self.y)
    
    def __getitem__(self, idx):
        """
        Get a single sample from the dataset.
        
        Args:
            idx (int): Index of the sample to retrieve
            
        Returns:
            tuple: (numerical_features, categorical_features, target)
                - numerical_features: torch.FloatTensor [n_numerical_features]
                - categorical_features: torch.LongTensor [n_categorical_features] 
                - target: torch.FloatTensor (scalar)
        """
        return self.X_numerical[idx], self.X_categorical[idx], self.y[idx]
        
