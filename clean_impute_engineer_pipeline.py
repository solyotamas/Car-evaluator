import pandas as pd
from data_preprocessing.clean import (
    table_clean
)
from data_preprocessing.impute import (
    table_impute
)
from data_preprocessing.enginner import (
    table_engineer
)

df = pd.read_csv('data/raw/car_details.csv')

df_cleaned = table_clean(df=df)
df_imputed = table_impute(df=df_cleaned)
df_engineered = table_engineer(df=df_imputed)

df_engineered.to_csv('data/clean/car_details.csv', index=False)