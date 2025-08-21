from pandas import DataFrame
import numpy as np
from sklearn.preprocessing import LabelEncoder, StandardScaler
import pickle

# Define features
numerical_features = ['year', 'kilometers', 'kw', 'engine_capacity']
categorical_features = ['manufacturer', 'model', 'fuel_type', 'condition', 
                       'body_type', 'color', 'drive_type', 'transmission_type']

def preprocess_car_data(df : DataFrame, is_training=True):
    if is_training:
        print("🔧 Training mode: Fitting and saving preprocessors...")
        

        scaler = StandardScaler()
        X_numerical = scaler.fit_transform(df[numerical_features])
        with open('preprocessors/scaler.pkl', 'wb') as f:
            pickle.dump(scaler, f)
        print("✅ Scaler saved to preprocessors/scaler.pkl")
        

        # Fit categorical encoders
        X_categorical = []
        encoders = {}
        vocab_sizes = []
        
        for col in categorical_features:
            categories = ['<UNK>'] + df[col].astype(str).unique().tolist()

            encoder = LabelEncoder()
            encoder.fit(categories)
            encoded = encoder.transform(df[col].astype(str))
            
            X_categorical.append(encoded)
            encoders[col] = encoder
            vocab_sizes.append(len(encoder.classes_))
            
            print(f"{col}: {len(categories)} unique values (including <UNK>)")
        
        X_categorical = np.column_stack(X_categorical)
        

        with open('preprocessors/encoders.pkl', 'wb') as f:
            pickle.dump(encoders, f)
        with open(f'preprocessors/vocab_sizes.pkl', 'wb') as f:
            pickle.dump(vocab_sizes, f)
        
        print(f"✅ Encoders saved to preprocessors/encoders.pkl")
        print(f"✅ Vocab sizes saved to save_path/vocab_sizes.pkl")
        
    else:
        print("📂 Inference mode: Loading preprocessors...")
    

        with open(f'preprocessors/scaler.pkl', 'rb') as f:
            scaler = pickle.load(f)
        X_numerical = scaler.transform(df[numerical_features])
        print(f"✅ Scaler loaded from preprocessors/scaler.pkl")
        
        with open('preprocessors/encoders.pkl', 'rb') as f:
            encoders = pickle.load(f)
        with open('preprocessors/vocab_sizes.pkl', 'rb') as f:
            vocab_sizes = pickle.load(f)
        
        print(f"✅ Encoders loaded from preprocessors/encoders.pkl")
        
        # Apply encoders
        X_categorical = []
        for col in categorical_features:
            # Map unknown categories to <UNK> before encoding
            known_categories = set(encoders[col].classes_)
            values = df[col].astype(str).apply(
                lambda x: x if x in known_categories else '<UNK>'
            )
            encoded = encoders[col].transform(values)
            X_categorical.append(encoded)
        
        X_categorical = np.column_stack(X_categorical)
    
    #target
    y = np.log1p(df['price'].values)


    return X_numerical.astype(np.float32), X_categorical.astype(np.int64), y, vocab_sizes
