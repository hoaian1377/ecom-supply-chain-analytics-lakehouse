import pandas as pd
from sqlalchemy import create_engine,text
from dotenv import load_dotenv
import os
load_dotenv()

DB_USERNAME= os.getenv("DB_USERNAME")
DB_PASSWORD=os.getenv("DB_PASSWORD")
DB_HOST=os.getenv("DB_HOST")
DB_PORT=os.getenv("DB_PORT")
DB_DATABASE=os.getenv("DB_DATABASE")
def Load_to_sql():
    engine = create_engine(f"postgresql+psycopg2://{DB_USERNAME}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_DATABASE}")
    df_carriers_clean = pd.read_parquet(r"C:\duan\DE\E-Commerce Supply Chain Analytics Lakehouse\data\cleaned\carriers_clean.parquet")
    df_orders_clean = pd.read_parquet(r"C:\duan\DE\E-Commerce Supply Chain Analytics Lakehouse\data\cleaned\orders_clean.parquet")
    df_shipments_clean = pd.read_parquet(r"C:\duan\DE\E-Commerce Supply Chain Analytics Lakehouse\data\cleaned\shipments_clean.parquet")
    df_carriers_clean.to_sql('carriers_clean',con=engine, if_exists='replace', index=False)
    df_orders_clean.to_sql('orders_clean',con=engine, if_exists='replace', index=False)
    df_shipments_clean.to_sql('shipments_clean',con=engine, if_exists='replace', index=False)
    return  df_carriers_clean, df_orders_clean, df_shipments_clean

if __name__ == "__main__":
    Load_to_sql()
    print("Load database success!")