#!/usr/bin/env python3
"""Regenerate the fake CSV files used by POC-02. No Azure SDK is required."""
from pathlib import Path
import csv

ROOT = Path(__file__).resolve().parents[1]

DATASETS = {
    ROOT / "sample_data/phase1/raw/orders/orders_batch_001.csv": [
        ["order_id","customer_id","product_id","product_name","product_category","quantity","unit_price","status","order_ts","updated_at"],
        ["O1001","C001","P001","USB-C Cable","Accessories","2","19.99","CREATED","2026-08-30 09:00:00","2026-08-30 09:00:00"],
        ["O1002","C002","P002","Wireless Mouse","Accessories","1","29.50","CREATED","2026-08-30 09:05:00","2026-08-30 09:05:00"],
        ["O1002","C002","P002","Wireless Mouse","Accessories","1","29.50","SHIPPED","2026-08-30 09:05:00","2026-08-30 10:15:00"],
        ["O1003","C003","P003","Laptop Stand","Office","1","49.00","PROCESSING","2026-08-30 09:20:00","2026-08-30 09:30:00"],
        ["","C001","P004","Keyboard","Accessories","1","59.00","CREATED","2026-08-30 10:00:00","2026-08-30 10:00:00"],
        ["O1005","C002","P004","Keyboard","Accessories","0","59.00","CREATED","2026-08-30 10:10:00","2026-08-30 10:10:00"],
        ["O1006","C003","P005","Webcam","Electronics","1","-5.00","CREATED","2026-08-30 10:20:00","2026-08-30 10:20:00"],
        ["O1007","C003","P006","Desk Lamp","Office","1","25.00","UNKNOWN","2026-08-30 10:30:00","2026-08-30 10:30:00"],
        ["O1008_BAD_TS","C001","P006","Desk Lamp","Office","1","25.00","CREATED","not-a-date","2026-08-30 10:40:00"],
    ],
    ROOT / "sample_data/phase1/raw/customers/customers_batch_001.csv": [
        ["customer_id","customer_name","email","city","country","updated_at"],
        ["C001","Asha Khan","asha@example.com","Hyderabad","India","2026-08-30 08:00:00"],
        ["C002","Ravi Mehta","ravi@example.com","Mumbai","India","2026-08-30 08:05:00"],
        ["C003","Neha Singh","neha@example.com","Pune","India","2026-08-30 08:10:00"],
        ["","Invalid Customer","bad-email","Delhi","India","2026-08-30 08:20:00"],
    ],
    ROOT / "sample_data/phase2/raw/orders/orders_batch_002_schema_evolution.csv": [
        ["order_id","customer_id","product_id","product_name","product_category","quantity","unit_price","status","order_ts","updated_at","sales_channel"],
        ["O1001","C001","P001","USB-C Cable","Accessories","2","19.99","SHIPPED","2026-08-30 09:00:00","2026-08-31 08:00:00","WEB"],
        ["O1009","C002","P004","Mechanical Keyboard","Accessories","1","79.00","CREATED","2026-08-31 08:10:00","2026-08-31 08:10:00","MOBILE"],
        ["O1010","C004","P007","Noise Cancelling Headphones","Electronics","1","149.00","CREATED","2026-08-31 08:20:00","2026-08-31 08:20:00","PARTNER"],
    ],
    ROOT / "sample_data/phase2/raw/customers/customers_batch_002_customer_change.csv": [
        ["customer_id","customer_name","email","city","country","updated_at"],
        ["C002","Ravi Mehta","ravi@example.com","Bengaluru","India","2026-08-31 07:30:00"],
        ["C004","Imran Ali","imran@example.com","Chennai","India","2026-08-31 07:40:00"],
    ],
}

for path, rows in DATASETS.items():
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        csv.writer(f).writerows(rows)
    print(f"wrote {path.relative_to(ROOT)}")
