from pandas import DataFrame
import numpy as np
from sklearn.preprocessing import LabelEncoder, StandardScaler
import joblib
import json


CATEGORICAL_FEATURES = ['manufacturer', 'fuel_type', 'condition', 'body_type', 'color', 'drive_type', 'transmission_type']
NUMERICAL_FEATURES = ['year', 'kilometers', 'kw', 'engine_capacity', 'metallic', 'km_imputed']
TARGET = 'price'

class PreProcessor:
    def __init__(self):
        self.numerical_features = []
        self.scaler = None
        self.categorical_features = {}

        self.scaler_readable = None
        self.categorical_features_readable = {}

    def fit(self, df : DataFrame):
        self.numerical_features = NUMERICAL_FEATURES

        self.scaler = StandardScaler()
        self.scaler.fit(df[NUMERICAL_FEATURES])

        self.scaler_readable = type(self.scaler).__name__

        for col in CATEGORICAL_FEATURES:
            original_values = df[col].unique().tolist()
            unique_values = ['<UNK>'] + original_values

            encoder = LabelEncoder()
            encoder.fit(unique_values)

            vocab_size = len(unique_values)
            embed_dim = self.calculate_embed_dim(vocab_size = vocab_size)

            self.categorical_features[col] = {
                'encoder' : encoder,
                'vocab_size' : vocab_size,
                'embed_dim' : embed_dim,
            }

            self.categorical_features_readable[col] = {
                'encoder' : type(encoder).__name__,
                'vocab_size' : vocab_size,
                'embed_dim' : embed_dim,
                'unique_value_names' : unique_values
            }

        return self
    
    def save(self, filepath_joblib, filepath_json):
        config = {
            'numerical_features': self.numerical_features,
            'scaler': self.scaler,
            'categorical_features': self.categorical_features
        }
        joblib.dump(config, filepath_joblib)

        config_readable = {
            'numerical_features': self.numerical_features,
            'scaler': self.scaler_readable,
            'categorical_features': self.categorical_features_readable
        }
        with open(filepath_json, 'w') as f:
            json.dump(config_readable, f, indent = 4)
        

    def transform(self, df : DataFrame, is_training, include_target):
        X_numerical = None
        X_categorical = None
        y = None

        X_numerical = self.scaler.transform(df[self.numerical_features])
        
        X_categorical = []
        for col in CATEGORICAL_FEATURES:
            encoder = self.categorical_features[col]['encoder']
            
            if is_training:
                encoded = encoder.transform(df[col])
            else:
                values = df[col].apply(
                    lambda x: x if x in encoder.classes_ else '<UNK>'
                )
                encoded = encoder.transform(values)
            
            X_categorical.append(encoded)
        X_categorical = np.column_stack(X_categorical)

        if include_target:
            y = np.log1p(df[TARGET].values)
            return X_numerical, X_categorical, y

        return X_numerical, X_categorical

    @staticmethod
    def calculate_embed_dim(vocab_size):
        return min(50, (vocab_size + 1) // 2)

        
