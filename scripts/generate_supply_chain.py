import json
import random
from datetime import datetime, timedelta
from faker import Faker

# Khởi tạo Faker tiếng Việt
fake = Faker('vi_VN')

def generate_carriers():
    return [
        {"carrier_id": "CAR_001", "carrier_name": "Giao Hàng Tiết Kiệm (GHTK)", "code": "GHTK", "contact_phone": "1900 6092", "service_type": "Standard"},
        {"carrier_id": "CAR_002", "carrier_name": "Giao Hàng Nhanh (GHN)", "code": "GHN", "contact_phone": "1900 636677", "service_type": "Express"},
        {"carrier_id": "CAR_003", "carrier_name": "Viettel Post", "code": "VTP", "contact_phone": "1900 8095", "service_type": "Standard"},
        {"carrier_id": "CAR_004", "carrier_name": "VNPost / EMS", "code": "VNPOST", "contact_phone": "1900 545415", "service_type": "Economy"},
        {"carrier_id": "CAR_005", "carrier_name": "Ninja Van", "code": "NINJA", "contact_phone": "1900 886877", "service_type": "Express"}
    ]

def generate_supply_chain_dataset(num_records=100):
    warehouses = [
        {"warehouse_id": "WH_SGN", "warehouse_name": "Kho Tổng TP.HCM (Tân Bình)", "city": "TP. Hồ Chí Minh"},
        {"warehouse_id": "WH_HAN", "warehouse_name": "Kho Tổng Hà Nội (Long Biên)", "city": "Hà Nội"},
        {"warehouse_id": "WH_DAD", "warehouse_name": "Kho Trung Chuyển Đà Nẵng", "city": "Đà Nẵng"}
    ]
    
    carriers = generate_carriers()
    statuses = ["DELIVERED", "DELIVERED", "DELIVERED", "IN_TRANSIT", "DELAYED", "CANCELLED"]
    cities = ["Hà Nội", "TP. Hồ Chí Minh", "Đà Nẵng", "Cần Thơ", "Hải Phòng", "Bình Dương", "Đồng Nai"]
    
    orders = []
    shipments = []
    base_date = datetime.now()

    for i in range(1, num_records + 1):
        date_str = base_date.strftime("%Y%m%d")
        order_id = f"ORD-{date_str}-{i:03d}"
        order_date = base_date + timedelta(days=random.randint(0, 30), hours=random.randint(8, 20), minutes=random.randint(0, 59))
        warehouse = random.choice(warehouses)
        
        # 1. Bảng Đơn hàng (Orders)
        order = {
            "order_id": order_id,
            "customer": {
                "name": fake.name(),
                "phone": fake.phone_number(),
                "address": fake.address().replace("\n", ", "),
                "city": random.choice(cities)
            },
            "warehouse_id": warehouse["warehouse_id"],
            "order_date": order_date.strftime("%Y-%m-%d %H:%M:%S"),
            "total_items": random.randint(1, 5),
            "total_amount": float(round(random.uniform(150000, 3500000), -3)),
            "payment_method": random.choice(["COD", "MOMO", "BANK_TRANSFER", "CREDIT_CARD"])
        }
        orders.append(order)
        
        # 2. Bảng Vận chuyển (Shipments)
        carrier = random.choice(carriers)
        status = random.choice(statuses)
        pickup_date = order_date + timedelta(hours=random.randint(2, 12))
        estimated_delivery = order_date + timedelta(days=random.randint(2, 4))
        
        actual_delivery = None
        delay_reason = None
        
        if status == "DELIVERED":
            if random.random() < 0.8:  # 80% giao đúng hạn
                actual_delivery = estimated_delivery - timedelta(hours=random.randint(1, 12))
            else:  # 20% giao trễ
                actual_delivery = estimated_delivery + timedelta(days=random.randint(1, 3))
                delay_reason = random.choice(["Thời tiết xấu", "Kẹt xe/Tắc đường", "Không liên lạc được người nhận", "Sai địa chỉ"])
        elif status == "DELAYED":
            delay_reason = random.choice(["Kho quá tải", "Hàng hóa thất lạc tạm thời", "Phương tiện hư hỏng"])
        elif status == "CANCELLED":
            delay_reason = "Khách hàng hủy đơn"

        shipment = {
            "shipment_id": f"SHIP-{202609000 + i}",
            "order_id": order_id,
            "carrier_id": carrier["carrier_id"],
            "tracking_number": f"{carrier['code']}{random.randint(10000000, 99999999)}",
            "shipping_fee": float(round(random.uniform(15000, 60000), -3)),
            "status": status,
            "pickup_date": pickup_date.strftime("%Y-%m-%d %H:%M:%S"),
            "estimated_delivery_date": estimated_delivery.strftime("%Y-%m-%d"),
            "actual_delivery_date": actual_delivery.strftime("%Y-%m-%d %H:%M:%S") if actual_delivery else None,
            "delay_reason": delay_reason
        }
        shipments.append(shipment)

    # Xuất dữ liệu ra file JSON
    with open("carriers.json", "w", encoding="utf-8") as f:
        json.dump(carriers, f, ensure_ascii=False, indent=2)
        
    with open("orders.json", "w", encoding="utf-8") as f:
        json.dump(orders, f, ensure_ascii=False, indent=2)

    with open("shipments.json", "w", encoding="utf-8") as f:
        json.dump(shipments, f, ensure_ascii=False, indent=2)

    print(f" Đã tạo thành công {num_records} bản ghi ra 3 file JSON!")

if __name__ == "__main__":
    generate_supply_chain_dataset(num_records=100)