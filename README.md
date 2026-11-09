# Veri Analitiği ve Proje Yönetimi Bitirme Ödevi
**E-Ticaret Platformu Satış ve Müşteri Davranışları Analizi** — Alp Eren Kavcı
Akbank Gençlik Akademisi · Teknoloji Okuryazarlığı Programı

## İçerik
| Dosya / Klasör | Açıklama |
|---|---|
| `Ana_Rapor.docx` | Proje yönetim planı (Charter, backlog, sprint, Scrum rolleri), SQL sorguları ve veri hikayeleştirme raporu |
| `02_queries.sql` | Analitik view ve tüm analiz sorguları |
| `data/customers.csv`, `data/orders.csv` | Veri seti (sentetik, ödev şemasına uygun) |
| `ecommerce.db` | SQLite veritabanı |
| `charts/` | Dashboard ve tekil grafik görselleri (`dashboard.png`) |
| `PowerBI_Kurulum_Rehberi.md` | Power BI modeli (1:N), DAX ölçüleri ve görsel kurulumu |
| `01_…05_*.py` | Veri üretimi, sorgu çalıştırma, grafik ve rapor üretim betikleri |

## Yeniden üretme
```bash
python -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt
python 01_generate_data.py && python 03_run_queries.py && python 04_charts.py && python 05_build_report.py
```

## Not
Ödev yönergesinde yalnızca tablo ve kolon adları verildiği için veri seti bu şemaya uygun olarak sabit tohumlu bir betikle
sentetik üretilmiştir. Power BI dashboard'unun `.pbix` dosyası bu repoya eklenmemiştir; kurulum adımları
`PowerBI_Kurulum_Rehberi.md` içinde, görünüm `charts/dashboard.png` içindedir.
