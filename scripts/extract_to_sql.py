import pandas as pd
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(os.path.join(BASE_DIR, ".env"))

cleaned_dir = os.path.join(BASE_DIR, "data", "cleaned")

DB_USERNAME = os.getenv("POSTGRES_USERNAME")
DB_PASSWORD = os.getenv("POSTGRES_PASSWORD")
DB_HOST = os.getenv("POSTGRES_HOST")
DB_PORT = os.getenv("POSTGRES_PORT")
DB_DATABASE = os.getenv("POSTGRES_DATABASE")

def Load_to_sql():
    engine = create_engine(f"postgresql+psycopg2://{DB_USERNAME}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_DATABASE}")
    df_carriers_clean = pd.read_parquet(os.path.join(cleaned_dir, "carriers_clean.parquet"))
    df_orders_clean = pd.read_parquet(os.path.join(cleaned_dir, "orders_clean.parquet"))
    df_shipments_clean = pd.read_parquet(os.path.join(cleaned_dir, "shipments_clean.parquet"))
    df_carriers_clean.to_sql('carriers_clean', con=engine, if_exists='replace', index=False)
    df_orders_clean.to_sql('orders_clean', con=engine, if_exists='replace', index=False)
    df_shipments_clean.to_sql('shipments_clean', con=engine, if_exists='replace', index=False)
    return df_carriers_clean, df_orders_clean, df_shipments_clean

if __name__ == "__main__":
    Load_to_sql()
    print("Load database success!")