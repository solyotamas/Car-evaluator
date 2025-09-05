from sqlalchemy import create_engine
from dotenv import load_dotenv
import pandas as pd
import os
from datetime import datetime

load_dotenv("shhh.env")
engine_connection = os.getenv("SQL_ENGINE")
engine = create_engine(engine_connection)

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~
date_str = datetime.now().strftime('%Y%m%d')

# Car Details Table
car_details_df = pd.read_sql_query("SELECT * FROM car_details", engine)
length = len(car_details_df)
filename = f'car_details_{length}_{date_str}.csv'
car_details_df.to_csv(f'data/raw/{filename}', index=False)

# Car Data Table
car_data_df = pd.read_sql_query("SELECT * FROM car_details", engine)
length = len(car_details_df)
filename = f'car_data_{length}_{date_str}.csv'
car_data_df.to_csv(f'data/raw/{filename}', index=False)
