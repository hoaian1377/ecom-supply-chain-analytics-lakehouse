from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
import sys
import os

# Thêm đường dẫn thư mục scripts vào hệ thống của Airflow
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../scripts')))

from generate_supply_chain import generate_supply_chain_dataset
from ingest_to_bronze import Upload_to_minio
from cleaning_data import main as clean_silver_main
from extract_to_sql import Load_to_sql
from transform_dwh import build_data_warehouse

default_args = {
    'owner': 'data_engineer',
    'depends_on_past': False,
    'email_on_failure': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

with DAG(
    'ecommerce_supply_chain_lakehouse',
    default_args=default_args,
    description='End-to-end automated pipeline for E-Commerce Supply Chain Lakehouse',
    schedule_interval='@daily',
    start_date=datetime(2026, 1, 1),
    catchup=False,
) as dag:

    # Task 1: Tạo dữ liệu giả lập ban đầu
    task_generate = PythonOperator(
        task_id='generate_raw_data',
        python_callable=generate_supply_chain_dataset,
        op_kwargs={'num_records': 100}
    )

    # Task 2: Đẩy dữ liệu thô lên MinIO (Bronze Layer)
    task_bronze = PythonOperator(
        task_id='upload_to_bronze_minio',
        python_callable=Upload_to_minio,
    )

    # Task 3: Làm sạch dữ liệu và đẩy sang Parquet / Silver MinIO (Silver Layer)
    task_silver = PythonOperator(
        task_id='clean_and_transform_silver',
        python_callable=clean_silver_main,
    )

    # Task 4: Load dữ liệu sạch từ Parquet vào PostgreSQL (Gold Staging Layer)
    task_gold = PythonOperator(
        task_id='load_to_postgresql',
        python_callable=Load_to_sql,
    )

    # Task 5: Mô hình hóa dữ liệu sang Star Schema Data Warehouse (Dim / Fact)
    task_dwh = PythonOperator(
        task_id='transform_to_dwh_star_schema',
        python_callable=build_data_warehouse,
    )

    # Thứ tự thực thi khép kín toàn bộ luồng
    task_generate >> task_bronze >> task_silver >> task_gold >> task_dwh