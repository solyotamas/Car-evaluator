from torch.utils.data import DataLoader
from sklearn.model_selection import train_test_split
from nn.dataset import CarPriceDataset
from nn.model import MLPCarPriceRegressionNet
import pandas as pd
import pandas as pd
from data_preprocessing.preprocessor import PreProcessor


df = pd.read_csv('data/clean/car_details.csv')

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
df_train, df_temp = train_test_split(df, test_size=0.2, random_state=42)
df_val, df_test = train_test_split(df_temp, test_size=0.25, random_state=42)

preprocessor = PreProcessor()
preprocessor.fit(df_train)
preprocessor.save('config/preprocessor_config.pkl', 'config/preprocessor_config.json')

model = MLPCarPriceRegressionNet('config/preprocessor_config.pkl')

X_num_train, X_cat_train, y_train = preprocessor.transform(df_train, is_training = True, include_target = True)
X_num_val, X_cat_val, y_val = preprocessor.transform(df_val, is_training = False, include_target = True)
X_num_test, X_cat_test, y_test = preprocessor.transform(df_test, is_training = False, include_target = True)

train_dataset = CarPriceDataset(X_num_train, X_cat_train, y_train)
val_dataset = CarPriceDataset(X_num_val, X_cat_val, y_val)
test_dataset = CarPriceDataset(X_num_test, X_cat_test, y_test)

dataloader_train = DataLoader(dataset = train_dataset, batch_size = 64, shuffle = True)
dataloader_val = DataLoader(dataset = val_dataset, batch_size = 64, shuffle = True)
dataloader_test = DataLoader(dataset = test_dataset, batch_size = 64, shuffle = False)

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~