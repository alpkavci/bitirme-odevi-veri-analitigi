"""E-ticaret örnek veri seti üretici (sentetik, seed sabit).

Platform yalnızca tablo/kolon adlarını verdiği için veri seti bu şemaya uygun
olarak üretilmiştir. Çıktı: data/customers.csv, data/orders.csv, ecommerce.db
"""
import sqlite3
from pathlib import Path

import numpy as np
import pandas as pd

rng = np.random.default_rng(42)
OUT = Path(__file__).parent / "data"
OUT.mkdir(exist_ok=True)

N_CUSTOMERS = 5000
N_ORDERS = 32000

cities = ["İstanbul", "Ankara", "İzmir", "Bursa", "Antalya", "Adana", "Konya", "Gaziantep", "Kocaeli", "Eskişehir"]
city_w = np.array([0.30, 0.14, 0.11, 0.07, 0.07, 0.06, 0.06, 0.05, 0.07, 0.07])
city_mult = {"İstanbul": 1.15, "Ankara": 1.08, "İzmir": 1.05, "Bursa": 0.98, "Antalya": 1.02,
             "Adana": 0.92, "Konya": 0.9, "Gaziantep": 0.9, "Kocaeli": 1.0, "Eskişehir": 0.95}
income_groups = ["Düşük", "Orta", "Yüksek"]
income_w = [0.30, 0.50, 0.20]
income_mult = {"Düşük": 0.75, "Orta": 1.0, "Yüksek": 1.55}

cust_id = np.arange(1, N_CUSTOMERS + 1)
signup = pd.to_datetime("2024-01-01") + pd.to_timedelta(rng.integers(0, 600, N_CUSTOMERS), unit="D")
customers = pd.DataFrame({
    "customer_id": cust_id,
    "signup_date": signup.strftime("%Y-%m-%d"),
    "city": rng.choice(cities, N_CUSTOMERS, p=city_w),
    "age": np.clip(rng.normal(34, 9, N_CUSTOMERS).round(), 18, 70).astype(int),
    "income_group": rng.choice(income_groups, N_CUSTOMERS, p=income_w),
    "gender": rng.choice(["Kadın", "Erkek"], N_CUSTOMERS, p=[0.54, 0.46]),
})

# Siparişleri tüm müşteriler arasında eşit olmayan dağıtıyoruz (bazı müşteriler hiç sipariş vermiyor).
weights = rng.gamma(0.9, 1.0, N_CUSTOMERS)
weights /= weights.sum()
order_cust = rng.choice(cust_id, N_ORDERS, p=weights)

categories = ["Elektronik", "Moda", "Ev & Yaşam", "Kozmetik", "Spor", "Kitap & Hobi", "Süpermarket"]
cat_w = [0.17, 0.24, 0.16, 0.12, 0.08, 0.08, 0.15]
cat_base = {"Elektronik": 1450, "Moda": 520, "Ev & Yaşam": 640, "Kozmetik": 310, "Spor": 480,
            "Kitap & Hobi": 190, "Süpermarket": 260}
cats = rng.choice(categories, N_ORDERS, p=cat_w)

# Saat dağılımı: akşam 20-23 yoğun, öğle ikinci tepe, gece düşük.
hour_w = np.array([2, 1, 1, 1, 1, 2, 3, 5, 8, 11, 12, 13, 14, 12, 11, 11, 12, 13, 15, 19, 26, 28, 20, 8], float)
hour_w /= hour_w.sum()
hours = rng.choice(np.arange(24), N_ORDERS, p=hour_w)
minutes = rng.integers(0, 60, N_ORDERS)

# Tarih: 2025-01-01 .. 2025-12-31, Kasım/Aralık kampanya etkisiyle daha yoğun.
days = pd.date_range("2025-01-01", "2025-12-31")
month_w = np.array([0.075, 0.07, 0.075, 0.075, 0.08, 0.075, 0.07, 0.07, 0.08, 0.085, 0.13, 0.115])
day_w = np.array([month_w[d.month - 1] / d.days_in_month for d in days])
day_w /= day_w.sum()
order_dates = rng.choice(days, N_ORDERS, p=day_w)

cmap = customers.set_index("customer_id")
amount = np.array([cat_base[c] for c in cats], float)
amount *= np.array([income_mult[cmap.at[i, "income_group"]] for i in order_cust])
amount *= np.array([city_mult[cmap.at[i, "city"]] for i in order_cust])
gender_mult = np.where(cmap.loc[order_cust, "gender"].to_numpy() == "Erkek", 1.12, 1.0)
amount *= gender_mult
amount *= rng.lognormal(0, 0.45, N_ORDERS)
amount = amount.round(2)

orders = pd.DataFrame({
    "order_id": np.arange(100001, 100001 + N_ORDERS),
    "customer_id": order_cust,
    "order_date": pd.to_datetime(order_dates).strftime("%Y-%m-%d"),
    "order_time": [f"{h:02d}:{m:02d}:00" for h, m in zip(hours, minutes)],
    "total_amount": amount,
    "category": cats,
}).sort_values(["order_date", "order_time"]).reset_index(drop=True)

customers.to_csv(OUT / "customers.csv", index=False)
orders.to_csv(OUT / "orders.csv", index=False)

db = Path(__file__).parent / "ecommerce.db"
if db.exists():
    db.unlink()
con = sqlite3.connect(db)
customers.to_sql("customers", con, index=False)
orders.to_sql("orders", con, index=False)
con.commit()
con.close()
print("customers", len(customers), "orders", len(orders), "ciro", round(orders.total_amount.sum()))
