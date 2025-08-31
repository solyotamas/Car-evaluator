import torch
import torch.nn as nn
import joblib

class MLPCarPriceRegressionNet_V1(nn.Module):
    def __init__(self, preprocessor_path):
        super().__init__()
        
        config = joblib.load(preprocessor_path)
        self.numerical_features = config['numerical_features']
        self.categorical_features = config['categorical_features']
        self.categorical_order = list(self.categorical_features.keys())
        
        ''' 
        self.embed_manufacturer = nn.Embedding(72, 36)
        self.embed_fuel_type = nn.Embedding(8, 4)
        self.embed_condition = nn.Embedding(6, 3)
        self.embed_body_type = nn.Embedding(14, 7)
        self.embed_color = nn.Embedding(39, 20)
        self.embed_drive_type = nn.Embedding(7, 4)
        self.embed_transmission_type = nn.Embedding(7, 4)
        '''
        self.embeddings = nn.ModuleDict()
        embeddings_dim = 0
        for feature_name, feature_config in self.categorical_features.items():
            vocab_size = feature_config['vocab_size']
            embed_dim = feature_config['embed_dim']
            
            self.embeddings[feature_name] = nn.Embedding(vocab_size, embed_dim)
            embeddings_dim += embed_dim
            
        
        numerical_dims = len(self.numerical_features)
        input_dim = numerical_dims + embeddings_dim
        #print(input_dim)
        

        # MLP
        self.mlp = nn.Sequential(

            nn.Linear(input_dim, 256),
            nn.BatchNorm1d(256),
            nn.ReLU(),
            #nn.Dropout(0.2),

            nn.Linear(256, 192),
            nn.BatchNorm1d(192),
            nn.ReLU(),
            
            nn.Linear(192, 128),
            nn.BatchNorm1d(128),
            nn.ReLU(),
            #nn.Dropout(0.15),

            nn.Linear(128, 96),
            nn.BatchNorm1d(96),
            nn.ReLU(),

            nn.Linear(96, 64),
            nn.BatchNorm1d(64),
            nn.ReLU(),
            
            nn.Linear(64, 48),
            nn.BatchNorm1d(48),
            nn.ReLU(),
            #nn.Dropout(0.1),

            nn.Linear(48, 32),
            nn.BatchNorm1d(32),
            nn.ReLU(),
            
            nn.Linear(32, 1)
        )

        
    def forward(self, X_numerical, X_categorical):
        """
        Args:
            X_numerical: (batch_size, n_numerical_features)
            X_categorical: (batch_size, n_categorical_features)
        
        Returns:
            (batch_size, 1) - log(price) predictions
        """
        
        '''
        embedded_features = [
            self.embed_manufacturer(X_categorical[:, 0]),
            self.embed_fuel_type(X_categorical[:, 1]),
            self.embed_condition(X_categorical[:, 2]),
            self.embed_body_type(X_categorical[:, 3]),
            self.embed_color(X_categorical[:, 4]),
            self.embed_drive_type(X_categorical[:, 5]),
            self.embed_transmission_type(X_categorical[:, 6])
        ]
        '''
        embedded_features = []
        for i, feature_name in enumerate(self.categorical_order):
            embedded = self.embeddings[feature_name](X_categorical[:, i])
            embedded_features.append(embedded)
        
        combined = torch.cat([X_numerical] + embedded_features, dim=1)

        output = self.mlp(combined)
        return output
    

if __name__ == "__main__":
    model = MLPCarPriceRegressionNet_V1('config/preprocessor_config.pkl')

    print(f"{sum(p.numel() for p in model.parameters())} parameters")
    

