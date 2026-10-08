import pandas as pd
import boto3
import os
import json
from dotenv import load_dotenv

load_dotenv()
def Connect_Minio():
    s3_client = boto3.client(
        's3',
        endpoint_url = "http://localhost:9000",
        aws_access_key_id = os.getenv('MINIO_ROOT_USER'),
        aws_secret_access_key = os.getenv('MINIO_ROOT_PASSWORD'),
        region_name = 'us-east-1'
    )
    return s3_client

def Upload_to_minio():
    s3 = Connect_Minio()
    bucket_name = 'bronze-layer'
    file_upload = [
        (r"C:\duan\DE\E-Commerce Supply Chain Analytics Lakehouse\data\raw\carriers.json","raw_carriers.json"),
        (r"C:\duan\DE\E-Commerce Supply Chain Analytics Lakehouse\data\raw\orders.json","raw_orders.json"),
        (r"C:\duan\DE\E-Commerce Supply Chain Analytics Lakehouse\data\raw\shipments.json","raw_shipments.json")
    ]

    for local_path, object_name in file_upload:
        if not os.path.exists(local_path):
            print(f"File {local_path} không tồn tại")
            continue
        try:
            s3.upload_file(
                Filename=local_path,
                Bucket=bucket_name,
                Key=object_name,
                ExtraArgs={'ContentType': 'application/json'}
            )
            print(f'Upload thành công: {local_path} -> [{bucket_name}/{object_name}]"')
        except Exception as e:
            print(f"Lỗi khi upload {local_path}: {e}")

if __name__ == "__main__":
    Upload_to_minio()
    print("Upload success!")

        