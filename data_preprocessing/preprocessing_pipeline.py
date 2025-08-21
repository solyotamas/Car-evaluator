import pandas as pd
from clean import (
    table_clean
)
from impute import (
    table_impute
)
from enginner import (
    table_engineer
)

df = pd.read_csv('data/raw/car_details.csv')

df_cleaned = table_clean(df=df)
df_imputed = table_impute(df=df_cleaned)
df_engineered = table_engineer(df=df_imputed)

df_engineered.to_csv('data/clean/car_details.csv', index=False)