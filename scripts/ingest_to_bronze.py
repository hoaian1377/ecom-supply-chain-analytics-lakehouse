import pandas as pd
import boto3
import os
import json
from dotenv import load_dotenv

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(os.path.join(BASE_DIR, ".env"))

def Connect_Minio():
    endpoint = os.getenv("MINIO_ENDPOINT")
    if not endpoint:
        endpoint = "http://minio:9000" if os.path.exists("/.dockerenv") else "http://localhost:9000"
    s3_client = boto3.client(
        's3',
        endpoint_url = endpoint,
        aws_access_key_id = os.getenv('MINIO_ROOT_USER'),
        aws_secret_access_key = os.getenv('MINIO_ROOT_PASSWORD'),
        region_name = 'us-east-1'
    )
    return s3_client

def Upload_to_minio():
    s3 = Connect_Minio()
    bucket_name = 'bronze-layer'
    raw_dir = os.path.join(BASE_DIR, "data", "raw")
    file_upload = [
        (os.path.join(raw_dir, "carriers.json"), "raw_carriers.json"),
        (os.path.join(raw_dir, "orders.json"), "raw_orders.json"),
        (os.path.join(raw_dir, "shipments.json"), "raw_shipments.json")
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

        