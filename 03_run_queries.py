"""02_queries.sql dosyasındaki '-- name:' etiketli sorguları çalıştırır, sonuçları results/*.csv olarak yazar."""
import re
import sqlite3
from pathlib import Path

import pandas as pd

base = Path(__file__).parent
res = base / "results"
res.mkdir(exist_ok=True)
sql = (base / "02_queries.sql").read_text(encoding="utf-8")

con = sqlite3.connect(base / "ecommerce.db")
# View oluşturma ifadesini çalıştır
view_sql = sql.split("-- 2a)")[0]
con.executescript(view_sql)

for m in re.finditer(r"-- name: (\w+)\n(.*?;)", sql, re.S):
    name, query = m.group(1), m.group(2)
    df = pd.read_sql_query(query, con)
    df.to_csv(res / f"{name}.csv", index=False)
    print(f"== {name}")
    print(df.to_string(index=False))
    print()
con.close()
