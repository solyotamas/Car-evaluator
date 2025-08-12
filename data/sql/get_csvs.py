from sqlalchemy import create_engine
from dotenv import load_dotenv
import pandas as pd
import os

load_dotenv("shhh.env")
engine_connection = os.getenv("SQL_ENGINE")

engine = create_engine(engine_connection)

# Car Details Table
car_details_df = pd.read_sql_query("SELECT * FROM car_details", engine)
car_details_df.to_csv('data/car_details.csv', index=False)

# Car Data Table
car_data_df = pd.read_sql_query("SELECT * FROM car_data", engine)
car_data_df.to_csv('data/car_data.csv', index=False)