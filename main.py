import torch
from torch.utils.data import DataLoader
from sklearn.model_selection import train_test_split
from nn.dataset import CarPriceDataset
from nn.model import MLPCarPriceRegressionNet_V1
import pandas as pd
import pandas as pd
from preprocessing.preprocess import PreProcessor
from nn.model_functions import train_model, plot_training, plot_error_analysis, plot_outlier_years, plot_outlier_km


df = pd.read_csv('data/clean/car_details.csv')

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
df_train, df_temp = train_test_split(df, test_size=0.2, random_state=42)
df_val, df_test = train_test_split(df_temp, test_size=0.5, random_state=42)

preprocessor = PreProcessor()
preprocessor.fit(df_train)
preprocessor.save('config/preprocessor_config.pkl', 'config/preprocessor_config.json')

model = MLPCarPriceRegressionNet_V1('config/preprocessor_config.pkl')

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

'''
history, model = train_model(
    model=model,
    train_loader=dataloader_train,
    val_loader=dataloader_val,
    epochs=150,
    learning_rate=0.0005
)
torch.save(model.state_dict(), 'models/car_price_model.pt')
'''
#plot_training(history=history)

model.load_state_dict(torch.load('models/car_price_model.pt'))
#plot_error_analysis(model, dataloader_test)
plot_outlier_years(model, dataloader_test, df_test, threshold=50)
plot_outlier_km(model, dataloader_test, df_test, threshold=50)