CREATE TABLE IF NOT EXISTS Dim_Carriers 
(
	dim_carrierID int generated always as identity Primary key,
	carrier_id varchar(255),
	carrier_name varchar(250),
	code varchar(255),
	contact_phone varchar(20),
	service_type varchar(255)
);

CREATE TABLE IF NOT EXISTS Dim_Customers
(
	dim_customerID int generated always as identity primary key,
	name varchar(255),
	phone varchar(20),
	address text,
	city varchar(255)
);

CREATE TABLE IF NOT EXISTS Dim_Orders
(
	dim_orderID int generated always as identity primary key,
	order_id varchar(255),
	warehouse_id varchar(255),
	payment_method varchar(255)
);

CREATE TABLE IF NOT EXISTS Dim_Date
(
	dim_dateID int generated always as identity primary key,
	order_date date,
	pickup_date date,
	estimated_delivery_date date,
	actual_delivery_date date
);

CREATE TABLE IF NOT EXISTS Dim_Shipments
(
	dim_shipmentID int generated always as identity primary key,
	shipment_id varchar(255),
	tracking_number varchar(255),
	status varchar(255),
	delay_reason varchar(255)
);

CREATE TABLE IF NOT EXISTS Fact_Shipments
(
	fact_shipmentID int generated always as identity primary key,
	dim_carrierID int,
	dim_customerID int,
	dim_orderID int,
	dim_dateID int,
	dim_shipmentID int,
	total_items int,
	total_amount float,
	shipping_fee int,
	CONSTRAINT fk_shipment_carrier Foreign Key (dim_carrierID) References Dim_Carriers(dim_carrierID),
	CONSTRAINT fk_shipment_customer Foreign Key (dim_customerID) References Dim_Customers(dim_customerID),
	CONSTRAINT fk_shipment_order Foreign Key (dim_orderID) References Dim_Orders(dim_orderID),
	CONSTRAINT fk_shipment_date Foreign Key (dim_dateID) References Dim_Date(dim_dateID),
	CONSTRAINT fk_shipment_shipment Foreign Key (dim_shipmentID) References Dim_Shipments(dim_shipmentID)
);

-- Xóa dữ liệu cũ trước khi nạp mới (Full Refresh Mart)
TRUNCATE TABLE Fact_Shipments, Dim_Carriers, Dim_Customers, Dim_Orders, Dim_Date, Dim_Shipments RESTART IDENTITY CASCADE;

-- 1. Nạp Dim_Carriers
INSERT INTO Dim_Carriers (carrier_id, carrier_name, code, contact_phone, service_type)
SELECT DISTINCT
    cc.carrier_id,
    cc.carrier_name,
    cc.code,
    cc.contact_phone,
    cc.service_type
FROM carriers_clean cc
WHERE cc.carrier_id IS NOT NULL;

-- 2. Nạp Dim_Customers
INSERT INTO Dim_Customers (name, phone, address, city)
SELECT DISTINCT
    oc.name,
    oc.phone,
    oc.address,
    oc.city
FROM orders_clean oc
WHERE oc.name IS NOT NULL;

-- 3. Nạp Dim_Orders
INSERT INTO Dim_Orders (order_id, warehouse_id, payment_method)
SELECT DISTINCT
    oc.order_id,
    oc.warehouse_id,
    oc.payment_method
FROM orders_clean oc
WHERE oc.order_id IS NOT NULL;

-- 4. Nạp Dim_Date
INSERT INTO Dim_Date (order_date, pickup_date, estimated_delivery_date, actual_delivery_date)
SELECT DISTINCT
    oc.order_date,
    sc.pickup_date,
    sc.estimated_delivery_date,
    sc.actual_delivery_date
FROM orders_clean oc
JOIN shipments_clean sc ON oc.order_id = sc.order_id;

-- 5. Nạp Dim_Shipments
INSERT INTO Dim_Shipments (shipment_id, tracking_number, status, delay_reason)
SELECT DISTINCT
    sc.shipment_id,
    sc.tracking_number,
    sc.status,
    sc.delay_reason
FROM shipments_clean sc
WHERE sc.shipment_id IS NOT NULL;

-- 6. Nạp Fact_Shipments
INSERT INTO Fact_Shipments (
    dim_carrierid,
    dim_customerid,
    dim_orderid,
    dim_dateid,
    dim_shipmentid,
    total_items,
    total_amount,
    shipping_fee
)
SELECT 
    d_car.dim_carrierid,
    d_cust.dim_customerid,
    d_ord.dim_orderid,
    d_dt.dim_dateid,
    d_shp.dim_shipmentid,
    oc.total_items,
    oc.total_amount,
    sc.shipping_fee
FROM orders_clean oc
JOIN shipments_clean sc 
    ON TRIM(oc.order_id) = TRIM(sc.order_id)
LEFT JOIN Dim_Carriers d_car 
    ON TRIM(sc.carrier_id) = TRIM(d_car.carrier_id)
LEFT JOIN Dim_Customers d_cust 
    ON TRIM(oc.name) = TRIM(d_cust.name) 
   AND TRIM(oc.phone) = TRIM(d_cust.phone)
LEFT JOIN Dim_Orders d_ord 
    ON TRIM(oc.order_id) = TRIM(d_ord.order_id)
LEFT JOIN Dim_Shipments d_shp 
    ON TRIM(sc.shipment_id) = TRIM(d_shp.shipment_id)
LEFT JOIN Dim_Date d_dt 
    ON oc.order_date::date = d_dt.order_date
   AND sc.pickup_date::date = d_dt.pickup_date;