import pandas as pd
import boto3
import json
import ast
import os
import io
from dotenv import load_dotenv
load_dotenv()

def Connect_Minio():
    s3_client = boto3.client(
        's3',
        endpoint_url = 'http://localhost:9000',
        aws_access_key_id = os.getenv('MINIO_ROOT_USER'),
        aws_secret_access_key=os.getenv('MINIO_ROOT_PASSWORD'),
        region_name = 'us-east-1'
    )
    return s3_client


def clean_carriers_data():
    file_path = r"C:\duan\DE\E-Commerce Supply Chain Analytics Lakehouse\data\raw\carriers.json"

    df = pd.read_json(file_path)

    return df


def clean_orders_data():
    file_path = r"C:\duan\DE\E-Commerce Supply Chain Analytics Lakehouse\data\raw\orders.json"

    df = pd.read_json(file_path)

    if 'customer' in df.columns:
        customer_df = pd.json_normalize(df['customer'])
        df = df.drop(columns=['customer']).join(customer_df)

    df['order_date'] = pd.to_datetime(df['order_date']).dt.normalize()

    df['total_amount'] = pd.to_numeric(
        df['total_amount'],
        errors='coerce'
    ).astype('Float64')

    return df


def clean_shipments_data():
    file_path = r"C:\duan\DE\E-Commerce Supply Chain Analytics Lakehouse\data\raw\shipments.json"

    df = pd.read_json(file_path)

    df['delay_reason'] = df['delay_reason'].fillna('N/A')

    datetime_cols = [
        'pickup_date',
        'estimated_delivery_date',
        'actual_delivery_date'
    ]

    for col in datetime_cols:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col])

    return df

def Upload_Minio(file_path,object_name):
    s3 = Connect_Minio()
    bucket_name = 'silver-layer'
    s3.upload_file(
        Filename=file_path,
        Bucket=bucket_name,
        Key=object_name
    )
    print(f"Uploaded: {object_name}")

def main():

    print("Đang xử lý dữ liệu...")

    df_carriers = clean_carriers_data()
    df_orders = clean_orders_data()
    df_shipments = clean_shipments_data()
    print(f"Clean Carriers hoàn tất: {df_carriers.shape}")
    print(f"Clean Orders hoàn tất: {df_orders.shape}")
    print(f"Clean Shipments hoàn tất: {df_shipments.shape}")
    print("\nMẫu dữ liệu Orders sau khi bung JSON & ép kiểu:")
    print(df_orders.head())
    output_dir = r"C:\duan\DE\E-Commerce Supply Chain Analytics Lakehouse\data\cleaned"
    os.makedirs(output_dir, exist_ok=True)
    carriers_file = os.path.join(output_dir,"carriers_clean.parquet")
    orders_file = os.path.join( output_dir,"orders_clean.parquet")
    shipments_file = os.path.join(output_dir,"shipments_clean.parquet")
    df_carriers.to_parquet(carriers_file,index=False)
    df_orders.to_parquet(orders_file,index=False)
    df_shipments.to_parquet(shipments_file,index=False)
    print("\nĐã tạo 3 file Parquet.")
    print("\nĐang upload lên MinIO...")
    Upload_Minio(carriers_file,"carriers/carriers_clean.parquet")
    Upload_Minio(orders_file,"orders/orders_clean.parquet")
    Upload_Minio(shipments_file, "shipments/shipments_clean.parquet")
    print("\nUpload MinIO hoàn tất!")

if __name__ == "__main__":
    main()
