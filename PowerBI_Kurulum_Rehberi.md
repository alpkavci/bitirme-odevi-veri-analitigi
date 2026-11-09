# Power BI Dashboard Kurulum Rehberi (~15 dk)

`.pbix` dosyası yalnızca **Power BI Desktop** (Windows) ile üretilebilir. Aşağıdaki adımlar hazır CSV'lerden
raporda gösterilen dashboard'u birebir kurar. Sonunda **Dosya > Farklı Kaydet > `PowerBI_Dashboard.pbix`**.

## 1. Veriyi al
1. Giriş Yap > **Metin/CSV** > `data/customers.csv` > Yükle
2. Aynısını `data/orders.csv` için yap.
3. Veri Dönüştür (Power Query): `orders[total_amount]` = Ondalık sayı, `orders[order_date]` = Tarih,
   `orders[order_time]` = Saat, `customers[signup_date]` = Tarih.

## 2. Model sekmesi (1:N ilişki)
`customers[customer_id]` → `orders[customer_id]` sürükle. Kardinalite **Bire-çok (1:N)**, çapraz filtre yönü **Tek**.

## 3. DAX ölçüleri (Yeni Ölçü)
```
Toplam Ciro    = SUM(orders[total_amount])
Toplam Sipariş = COUNTROWS(orders)
Aktif Müşteri  = DISTINCTCOUNT(orders[customer_id])
```
Hesaplanmış sütun (orders tablosu): `Saat = HOUR(orders[order_time])`  ve  `Ay = FORMAT(orders[order_date], "MM")`

## 4. Görseller
| Görsel | Alanlar |
|---|---|
| Kart ×3 | Toplam Ciro, Toplam Sipariş, Aktif Müşteri |
| Çubuk grafik (yatay) | Eksen: customers[city] · Değer: Toplam Ciro · Filtre: İlk N = 5 (Toplam Ciro'ya göre) |
| Çizgi grafik (aylık) | X: orders[Ay] · Y: Toplam Ciro |
| Çizgi grafik (saatlik) | X: orders[Saat] · Y: Toplam Sipariş |
| Halka grafik #1 | Gösterim: customers[gender] · Değer: Toplam Ciro |
| Halka grafik #2 | Gösterim: customers[income_group] · Değer: Toplam Ciro |

## 5. Doğrulama (beklenen değerler)
Toplam Ciro **24.528.331,35 ₺**, Toplam Sipariş **32.000**, Aktif Müşteri **4.236**.
İlk 5 şehir: İstanbul, Ankara, İzmir, Antalya, Kocaeli. Bu değerler tutuyorsa model doğrudur.
Referans görünüm: `charts/dashboard.png`.
