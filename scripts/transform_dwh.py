import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(os.path.join(BASE_DIR, ".env"))

DB_USERNAME = os.getenv("POSTGRES_USERNAME")
DB_PASSWORD = os.getenv("POSTGRES_PASSWORD")
DB_HOST = os.getenv("POSTGRES_HOST")
DB_PORT = os.getenv("POSTGRES_PORT") 
DB_DATABASE = os.getenv("POSTGRES_DATABASE") or os.getenv("DB_DATABASE", "SupplyChain")

def build_data_warehouse():
    print("Starting DWH Star Schema transformation...")
    engine = create_engine(f"postgresql+psycopg2://{DB_USERNAME}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_DATABASE}")
    sql_file = os.path.join(BASE_DIR, "sql", "datawarehouse.sql")
    
    with open(sql_file, "r", encoding="utf-8") as f:
        sql_content = f.read()

    # Thực thi SQL script
    raw_conn = engine.raw_connection()
    try:
        with raw_conn.cursor() as cursor:
            cursor.execute(sql_content)
        raw_conn.commit()
        print("Data Warehouse (Dim/Fact) built successfully!")
    finally:
        raw_conn.close()

if __name__ == "__main__":
    build_data_warehouse()
    print("Build DWH success!")
