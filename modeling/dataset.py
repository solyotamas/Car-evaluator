import torch
from torch.utils.data import Dataset

class CarPriceDataset(Dataset):
    """
        Handling numerical and categorical features seperately becausr
        they will be processed differently by the network
    """
    
    def __init__(self, X_numerical, X_categorical, y):
        """
            - Already np.arrays
            X_numerical - Scaled
            X_categorical - Labelencoded
            y - Log Transformed
            - Transforming to torch tensors
        """
        self.X_numerical = torch.tensor(X_numerical, dtype=torch.float32)
        self.X_categorical = torch.tensor(X_categorical, dtype=torch.int64) 
        self.y = torch.tensor(y, dtype=torch.float32) 
        
        assert len(self.X_numerical) == len(self.X_categorical) == len(self.y), 'All inputs must have the same number of samples'
    
    def __len__(self):
        return len(self.y)
    
    def __getitem__(self, idx):
        return self.X_numerical[idx], self.X_categorical[idx], self.y[idx]
        
