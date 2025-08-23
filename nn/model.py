import torch
import torch.nn as nn
import joblib

class MLPCarPriceRegressionNet(nn.Module):
    def __init__(self, preprocessor_path):
        super().__init__()
        
        # Load preprocessor config
        config = joblib.load(preprocessor_path)
        self.numerical_features = config['numerical_features']
        self.categorical_features = config['categorical_features']
        
        # Build embedding layers from config
        self.embeddings = nn.ModuleDict()
        total_embed_dim = 0
        
        for feat_name, feat_config in self.categorical_features.items():
            vocab_size = feat_config['vocab_size']
            embed_dim = feat_config['embed_dim']
            
            self.embeddings[feat_name] = nn.Embedding(vocab_size, embed_dim)
            total_embed_dim += embed_dim
            
            #print(f"{feat_name}: vocab={vocab_size}, embed={embed_dim}")
        
        # Calculate input dimension
        num_numerical = len(self.numerical_features)
        input_dim = num_numerical + total_embed_dim
        
        print(f"\nTotal input dim: {num_numerical} numerical + {total_embed_dim} embedding = {input_dim}")
        
        # Build MLP
        self.mlp = nn.Sequential(
            nn.Linear(input_dim, 256),
            nn.BatchNorm1d(256),
            nn.ReLU(),
            nn.Dropout(0.3),
            
            nn.Linear(256, 128),
            nn.BatchNorm1d(128),
            nn.ReLU(),
            nn.Dropout(0.3),
            
            nn.Linear(128, 64),
            nn.BatchNorm1d(64),
            nn.ReLU(),
            nn.Dropout(0.3),
            
            nn.Linear(64, 1)
        )
        
        # Store feature order for forward pass
        self.categorical_order = list(self.categorical_features.keys())
        
    def forward(self, X_numerical, X_categorical):
        """
        Args:
            X_numerical: (batch_size, n_numerical_features)
            X_categorical: (batch_size, n_categorical_features)
        
        Returns:
            (batch_size, 1) - log(price) predictions
        """
        # Process embeddings in the correct order
        embedded_features = []
        for i, feat_name in enumerate(self.categorical_order):
            embedded = self.embeddings[feat_name](X_categorical[:, i])
            embedded_features.append(embedded)
        
        # Concatenate everything
        combined = torch.cat([X_numerical] + embedded_features, dim=1)
        
        # Pass through MLP
        output = self.mlp(combined)
        
        return output