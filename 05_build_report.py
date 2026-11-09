"""Ana raporu (DOCX) üretir: proje yönetim planı + SQL + Power BI/dashboard + veri hikayesi."""
from pathlib import Path

import pandas as pd
from docx import Document
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor

base = Path(__file__).parent
res, ch = base / "results", base / "charts"
AUTHOR = "Alp Eren Kavcı"

kpi = pd.read_csv(res / "kpis.csv").iloc[0]
cities = pd.read_csv(res / "top5_cities.csv")
hourly = pd.read_csv(res / "hourly_orders.csv")
monthly = pd.read_csv(res / "monthly_revenue.csv")
gender = pd.read_csv(res / "by_gender.csv").set_index("gender")
income = pd.read_csv(res / "by_income.csv").set_index("income_group")
cats = pd.read_csv(res / "avg_by_category.csv").set_index("category")
orders = pd.read_csv(base / "data" / "orders.csv")


def n(v, d=0):
    return f"{v:,.{d}f}".replace(",", "X").replace(".", ",").replace("X", ".")


def mn(v):
    return n(v / 1e6, 2) + " Mn ₺"


total = kpi.total_revenue
top_city = cities.iloc[0]
top5_share = cities.total_revenue.sum() / total * 100
ist_share = top_city.total_revenue / total * 100
peak_h = hourly.sort_values("order_count", ascending=False).head(3).order_hour.tolist()
eve = hourly[hourly.order_hour.between(20, 22)].order_count.sum() / hourly.order_count.sum() * 100
eve19 = hourly[hourly.order_hour.between(19, 22)].order_count.sum() / hourly.order_count.sum() * 100
night = hourly[hourly.order_hour.between(1, 4)].order_count.sum() / hourly.order_count.sum() * 100
nov = monthly.set_index("order_month").loc["2025-11", "revenue"]
dec = monthly.set_index("order_month").loc["2025-12", "revenue"]
base_avg = monthly[~monthly.order_month.isin(["2025-11", "2025-12"])].revenue.mean()
nov_lift = (nov / base_avg - 1) * 100
nd_share = (nov + dec) / total * 100
cat_rev = orders.groupby("category").total_amount.sum().sort_values(ascending=False)
elec_share = cat_rev["Elektronik"] / total * 100
moda_share = cat_rev["Moda"] / total * 100
male_share = gender.loc["Erkek", "revenue"] / total * 100
fem_share = gender.loc["Kadın", "revenue"] / total * 100
male_avg, fem_avg = gender.loc["Erkek", "avg_order_value"], gender.loc["Kadın", "avg_order_value"]
inc_share = {k: income.loc[k, "revenue"] / total * 100 for k in income.index}
hi_avg, lo_avg = income.loc["Yüksek", "avg_order_value"], income.loc["Düşük", "avg_order_value"]
aov = total / kpi.total_orders
active_pct = kpi.active_customers / 5000 * 100
cat_top, cat_low = cats.index[0], cats.index[-1]

doc = Document()
sec = doc.sections[0]
sec.left_margin = sec.right_margin = Cm(2.2)
sec.top_margin = sec.bottom_margin = Cm(2)
st = doc.styles["Normal"]
st.font.name = "Calibri"
st.font.size = Pt(11)
st.element.rPr.rFonts.set(qn("w:eastAsia"), "Calibri")
for lvl, size in [(1, 18), (2, 14), (3, 12)]:
    h = doc.styles[f"Heading {lvl}"]
    h.font.name = "Calibri"
    h.font.size = Pt(size)
    h.font.color.rgb = RGBColor(0x1E, 0x40, 0xAF)


def shade(cell, color):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:color"), "auto")
    shd.set(qn("w:fill"), color)
    tcPr.append(shd)


def table(headers, rows, widths=None, font=10):
    t = doc.add_table(rows=1, cols=len(headers))
    t.style = "Table Grid"
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    for i, h in enumerate(headers):
        c = t.rows[0].cells[i]
        c.text = ""
        r = c.paragraphs[0].add_run(h)
        r.bold, r.font.size = True, Pt(font)
        r.font.color.rgb = RGBColor(255, 255, 255)
        shade(c, "1E40AF")
    for row in rows:
        cells = t.add_row().cells
        for i, v in enumerate(row):
            cells[i].text = ""
            r = cells[i].paragraphs[0].add_run(str(v))
            r.font.size = Pt(font)
    if widths:
        for row in t.rows:
            for i, w in enumerate(widths):
                row.cells[i].width = Cm(w)
    doc.add_paragraph()
    return t


def code(text):
    p = doc.add_paragraph()
    p.paragraph_format.left_indent = Cm(0.4)
    r = p.add_run(text)
    r.font.name = "Consolas"
    r._element.rPr.rFonts.set(qn("w:eastAsia"), "Consolas")
    r.font.size = Pt(9)
    pPr = p._p.get_or_add_pPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:fill"), "F1F5F9")
    pPr.append(shd)


def para(text, bold=False, italic=False):
    p = doc.add_paragraph()
    r = p.add_run(text)
    r.bold, r.italic = bold, italic
    return p


def bullets(items):
    for it in items:
        doc.add_paragraph(it, style="List Bullet")


def pic(name, width=15.5):
    doc.add_picture(str(ch / name), width=Cm(width))
    doc.paragraphs[-1].alignment = WD_ALIGN_PARAGRAPH.CENTER


# ---------------- Kapak ----------------
t = doc.add_paragraph()
t.alignment = WD_ALIGN_PARAGRAPH.CENTER
t.paragraph_format.space_before = Pt(120)
r = t.add_run("Veri Analitiği ve Proje Yönetimi\nBitirme Ödevi")
r.bold, r.font.size = True, Pt(28)
r.font.color.rgb = RGBColor(0x1E, 0x40, 0xAF)
s = doc.add_paragraph()
s.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = s.add_run("E-Ticaret Platformu Satış ve Müşteri Davranışları Analizi")
r.font.size = Pt(16)
doc.add_paragraph()
for line in [AUTHOR, "Akbank Gençlik Akademisi – Teknoloji Okuryazarlığı Programı", "Kasım 2026"]:
    p = doc.add_paragraph(line)
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
doc.add_page_break()

# ---------------- İçerik özeti ----------------
doc.add_heading("İçindekiler ve Teslim Paketi", 1)
bullets([
    "1. Proje Yönetimi ve Agile Planlama (Project Charter, Backlog, Sprint planı, Scrum rolleri)",
    "2. SQL ile Veri Yönetimi ve Sorgulama (View + 3 analiz sorgusu)",
    "3. Power BI ile Veri Modelleme ve Görselleştirme (model, DAX ölçüleri, dashboard)",
    "4. Veri Okuryazarlığı ve Veri Hikayeleştirme (grafik yorumları, stratejik öneriler)",
    "Ek: Veri seti hakkında not ve dosya listesi",
])
para("Teslim paketi: Alp_Eren_Kavci_Bitirme_Odevi (ana rapor, SQL sorguları, veri seti, dashboard görselleri ve Power BI kurulum rehberi; Power BI .pbix dosyası pakete dahil değildir, dashboard görseli ve kurulum adımları sağlanmıştır).", italic=True)

# ---------------- 1. Proje yönetimi ----------------
doc.add_heading("1. Proje Yönetimi ve Agile Temelleri – Planlama", 1)
doc.add_heading("1.1 Proje Başlatma Belgesi (Project Charter)", 2)
table(["Başlık", "İçerik"], [
    ["Proje adı", "E-Ticaret Satış ve Müşteri Davranışları Analizi"],
    ["Amaç", "Müşteri ve sipariş verisini analiz ederek ciroyu en çok etkileyen şehir, zaman, kategori ve müşteri "
             "segmentlerini belirlemek; yönetime veriye dayalı aksiyon önerileri sunmak."],
    ["Kapsam (dahil)", "customers ve orders tablolarının SQL ile birleştirilmesi, 3 temel analiz sorgusu, Power BI "
                       "modeli ve dashboard'u, yöneticiler için veri hikayesi ve öneri raporu."],
    ["Kapsam (hariç)", "Canlı veri entegrasyonu, tahminleme/makine öğrenmesi modelleri, stok ve lojistik analizi."],
    ["Ana paydaşlar", "Genel Müdür / Yönetim Kurulu (karar verici), Pazarlama Müdürü (kampanya ve zamanlama), "
                      "Satış ve Kategori Yöneticileri, Veri/BI ekibi (geliştirici), Müşteri Deneyimi ekibi."],
    ["Başarı kriterleri", "(1) 3 SQL sorusunun doğru ve tekrarlanabilir yanıtlanması, (2) Dashboard'da 3 KPI kartı, "
                          "bar, çizgi ve 2 donut grafiğinin bulunması, (3) Her grafik için iş yorumu, (4) En az 2 "
                          "uygulanabilir aksiyon önerisi, (5) Sprint süresi olan 5 iş gününde teslim."],
    ["Varsayımlar", "Veri temizdir ve tek para birimindedir (₺); siparişlerde tutar KDV dahildir; analiz dönemi 2025 takvim yılıdır."],
    ["Riskler", "Veri kalitesi sorunları (eksik/yinelenen kayıt), tarih/saat biçim farkları, Power BI Desktop erişimi. "
                "Önlem: kontrol sorguları, standart tarih formatı, CSV tabanlı yedek akış."],
], widths=[3.5, 12.5])

doc.add_heading("1.2 Product Backlog (User Story'ler)", 2)
table(["ID", "User Story", "Öncelik", "Puan"], [
    ["US-1", "Bir veri analisti olarak, müşteri ve sipariş tablolarını tek bir analitik view'da görmek istiyorum ki tüm analizleri tek kaynaktan yapabileyim.", "Yüksek", "3"],
    ["US-2", "Bir yönetici olarak, en çok ciro getiren şehirleri görmek istiyorum ki bölgesel yatırımı yönlendirebileyim.", "Yüksek", "2"],
    ["US-3", "Bir pazarlama müdürü olarak, siparişlerin günün hangi saatlerinde yoğunlaştığını bilmek istiyorum ki kampanya zamanını planlayabileyim.", "Yüksek", "2"],
    ["US-4", "Bir kategori yöneticisi olarak, kategori bazında ortalama sepet tutarını görmek istiyorum ki fiyat ve çapraz satış stratejisi belirleyebileyim.", "Orta", "2"],
    ["US-5", "Bir BI geliştiricisi olarak, Power BI'da 1:N ilişkili bir veri modeli kurmak istiyorum ki rapor dinamik ve doğru çalışsın.", "Yüksek", "3"],
    ["US-6", "Bir yönetici olarak, KPI kartları, trend ve kırılım grafikleri olan tek sayfalık bir dashboard istiyorum ki durumu bir bakışta anlayayım.", "Yüksek", "5"],
    ["US-7", "Bir yönetici olarak, her grafiğin iş yorumunu ve öneriyi okumak istiyorum ki teknik bilgi olmadan karar verebileyim.", "Orta", "3"],
    ["US-8", "Bir proje sahibi olarak, tüm çıktıların tek klasörde paylaşılmasını istiyorum ki ekip kolayca erişebilsin.", "Düşük", "1"],
], widths=[1.4, 10.6, 2.0, 1.4], font=9.5)

doc.add_heading("1.3 Sprint Planı (1 haftalık Sprint – 21 puan)", 2)
para("Sprint hedefi: Ham veriden yönetici dashboard'una ve öneri raporuna uçtan uca çalışan bir analiz teslim etmek.")
table(["Gün", "Çalışma", "User Story", "Çıktı"], [
    ["Pzt", "Sprint planlama, Project Charter, veri setinin hazırlanması", "US-1", "Charter, ecommerce.db, customers/orders"],
    ["Sal", "SQL view ve 3 analiz sorgusu, sonuç doğrulama", "US-1, US-2, US-3, US-4", "02_queries.sql, results/*.csv"],
    ["Çar", "Power BI veri modeli (1:N), DAX ölçüleri", "US-5", "Model + ölçüler"],
    ["Per", "Dashboard tasarımı (KPI, bar, çizgi, donut)", "US-6", "Dashboard"],
    ["Cum", "Veri hikayesi, öneriler, Sprint Review ve Retrospektif, teslim klasörü", "US-7, US-8", "Ana rapor, Drive klasörü"],
], widths=[1.4, 7.0, 3.6, 4.4], font=9.5)
para("Günlük Scrum (15 dk) ile ilerleme takip edilir; Definition of Done: sorgular çalışır ve doğrulanmıştır, grafikler "
     "verideki rakamlarla birebir tutarlıdır, her grafiğin yorumu yazılmıştır, klasör paylaşım izni doğrudur.")

doc.add_heading("1.4 Scrum Rol Dağılımı", 2)
table(["Rol", "Bu projedeki sorumluluk"], [
    ["Product Owner", "İş hedefini (ciroyu artırma) ve önceliklendirilmiş backlog'u yönetir; hangi analizlerin önce geleceğine karar verir, "
                      "yönetici ihtiyaçlarını temsil eder ve sprint sonunda çıktıyı kabul eder."],
    ["Scrum Master", "Scrum olaylarını (planlama, günlük, review, retrospektif) yürütür, engelleri (veri erişimi, lisans vb.) kaldırır "
                     "ve ekibin süreçlere uymasını sağlar; ürün kararı vermez."],
    ["Geliştirici Takım", "Veriyi hazırlar, SQL sorgularını yazar, Power BI modelini ve dashboard'u geliştirir, veri hikayesini hazırlar; "
                          "kalite ve doğrulamadan birlikte sorumludur."],
], widths=[3.5, 12.5])
doc.add_page_break()

# ---------------- 2. SQL ----------------
doc.add_heading("2. SQL ile Veri Yönetimi ve Sorgulama", 1)
para("Veri iki tablodan oluşur: customers (5.000 müşteri) ve orders (32.000 sipariş, 2025 yılı). "
     "Sorgular SQLite üzerinde çalıştırılmış ve sonuçları aşağıya yazılmıştır.")
doc.add_heading("2.1 Veri ilişkilendirme – analitik görünüm (View)", 2)
code("""CREATE VIEW vw_order_analytics AS
SELECT
    o.order_id, o.order_date, o.order_time,
    CAST(strftime('%H', o.order_time) AS INTEGER) AS order_hour,
    strftime('%Y-%m', o.order_date)               AS order_month,
    o.total_amount, o.category,
    c.customer_id, c.signup_date, c.city, c.age, c.income_group, c.gender
FROM orders o
JOIN customers c ON c.customer_id = o.customer_id;""")

doc.add_heading("2.2 Analiz sorguları", 2)
doc.add_heading("Soru 1 – En yüksek ciro getiren ilk 5 şehir", 3)
code("""SELECT city, ROUND(SUM(total_amount), 2) AS total_revenue, COUNT(*) AS order_count
FROM vw_order_analytics
GROUP BY city
ORDER BY total_revenue DESC
LIMIT 5;""")
table(["Şehir", "Toplam ciro (₺)", "Sipariş sayısı"],
      [[r.city, n(r.total_revenue, 2), n(r.order_count)] for r in cities.itertuples()], widths=[5, 5.5, 5])

doc.add_heading("Soru 2 – Günün saatlerine göre sipariş yoğunluğu", 3)
code("""SELECT order_hour, COUNT(*) AS order_count
FROM vw_order_analytics
GROUP BY order_hour
ORDER BY order_hour;""")
half = len(hourly) // 2
rows = []
for i in range(half):
    a, b = hourly.iloc[i], hourly.iloc[i + half]
    rows.append([f"{int(a.order_hour):02d}:00", n(a.order_count), f"{int(b.order_hour):02d}:00", n(b.order_count)])
table(["Saat", "Sipariş", "Saat", "Sipariş"], rows, widths=[3.5, 4, 3.5, 4], font=9.5)

doc.add_heading("Soru 3 – Kategorilere göre ortalama harcama tutarı", 3)
code("""SELECT category, ROUND(AVG(total_amount), 2) AS avg_order_value, COUNT(*) AS order_count
FROM vw_order_analytics
GROUP BY category
ORDER BY avg_order_value DESC;""")
table(["Kategori", "Ortalama harcama (₺)", "Sipariş sayısı"],
      [[k, n(r.avg_order_value, 2), n(r.order_count)] for k, r in cats.iterrows()], widths=[5, 5.5, 5])
doc.add_page_break()

# ---------------- 3. Power BI ----------------
doc.add_heading("3. Power BI ile Veri Modelleme ve Görselleştirme", 1)
doc.add_heading("3.1 Veri modeli (Model sekmesi)", 2)
para("customers ve orders tabloları Power BI'a CSV/SQL kaynağından aktarılır. Model sekmesinde tablolar customer_id alanı "
     "üzerinden bire-çok (1:N) ilişkiyle bağlanır:")
table(["İlişki", "Kardinalite", "Filtre yönü"], [
    ["customers[customer_id]  →  orders[customer_id]", "Bire-çok (1:N)  (bir müşteri, birden çok sipariş)", "Tek yön (customers → orders)"],
], widths=[6.5, 6, 3.5])
para("Tarih bazlı analiz için orders[order_date] alanına bağlı bir Takvim tablosu eklenebilir (Takvim[Tarih] 1 → orders[order_date] N).")
doc.add_heading("3.2 DAX ölçüleri", 2)
code("""Toplam Ciro        = SUM(orders[total_amount])
Toplam Sipariş     = COUNTROWS(orders)
Aktif Müşteri      = DISTINCTCOUNT(orders[customer_id])
Ortalama Sepet     = DIVIDE([Toplam Ciro], [Toplam Sipariş])
Sipariş Saati      = HOUR(orders[order_time])   -- hesaplanmış sütun""")
doc.add_heading("3.3 Dashboard", 2)
para("Dashboard'da istenen tüm görsel unsurlar bulunmaktadır: üç KPI kartı (Toplam Ciro, Toplam Sipariş Sayısı, Aktif Müşteri "
     "Sayısı), şehir bazlı bar grafik, aylık satış trendi ve saatlik sipariş çizgi grafikleri, cinsiyete ve gelir grubuna göre "
     "harcama dağılımı için iki donut grafik.")
pic("dashboard.png", 16.2)
doc.add_page_break()

# ---------------- 4. Veri hikayesi ----------------
doc.add_heading("4. Veri Okuryazarlığı ve Veri Hikayeleştirme", 1)
doc.add_heading("Yönetici özeti", 2)
para(f"2025 yılında {n(kpi.total_orders)} sipariş ve {mn(total)} ciro elde edildi; {n(kpi.active_customers)} müşteri "
     f"(kayıtlı müşterilerin %{n(active_pct, 0)}'i) en az bir sipariş verdi. Ortalama sepet tutarı {n(aov, 0)} ₺. "
     f"Cironun %{n(top5_share, 0)}'i ilk 5 şehirden, %{n(ist_share, 0)}'i yalnızca İstanbul'dan geliyor; siparişler akşam "
     f"saatlerinde, ciro ise yıl sonu kampanya döneminde yoğunlaşıyor.")

doc.add_heading("4.1 Grafik gözlemleri", 2)
items = [
    ("KPI kartları", "dashboard.png",
     f"Yıllık ciro {mn(total)}, sipariş sayısı {n(kpi.total_orders)} ve aktif müşteri sayısı {n(kpi.active_customers)}. "
     f"Kayıtlı müşterilerin yaklaşık %{n(100 - active_pct, 0)}'i hiç sipariş vermemiş; bu kitle yeniden etkinleştirme için hazır bir potansiyel."),
    ("Şehirlere göre ciro (bar grafik)", "bar_sehir.png",
     f"İstanbul {mn(top_city.total_revenue)} ile cironun %{n(ist_share, 0)}'ini üretiyor ve ikinci sıradaki Ankara'nın yaklaşık "
     f"{n(top_city.total_revenue / cities.iloc[1].total_revenue, 1)} katı. İlk 5 şehir toplam cironun %{n(top5_share, 0)}'ini taşıyor; "
     f"bu yoğunlaşma hem fırsat (lojistik/kampanya odağı) hem risk (tek şehre bağımlılık)."),
    ("Aylık satış trendi (çizgi grafik)", "cizgi_aylik.png",
     f"Ocak–Ekim döneminde aylık ciro {mn(base_avg)} civarında dengeli seyrediyor. Kasım ayı {mn(nov)} ile ortalamanın "
     f"%{n(nov_lift, 0)} üzerine çıkıyor ve Kasım–Aralık yıllık cironun %{n(nd_share, 0)}'ini oluşturuyor. Yaz aylarında (Temmuz–Ağustos) hafif bir durgunluk var."),
    ("Saatlik sipariş yoğunluğu (çizgi grafik)", "cizgi_saatlik.png",
     f"Siparişler 20:00–22:00 arasında zirve yapıyor (en yoğun saatler: {', '.join(str(int(h)) + ':00' for h in peak_h)}); bu üç saat "
     f"günlük siparişlerin %{n(eve, 0)}'ini, 19:00–22:00 arası ise %{n(eve19, 0)}'ini kapsıyor. Gece 01:00–05:00 arası sipariş payı "
     f"yalnızca %{n(night, 0)}. Müşteriler mesai sonrası, evde ve mobil cihazdan alışveriş yapıyor olabilir."),
    ("Cinsiyete göre harcama (donut)", "donut_cinsiyet.png",
     f"Harcamanın %{n(male_share, 0)}'i erkek, %{n(fem_share, 0)}'i kadın müşterilerden geliyor. Erkeklerin ortalama sepeti "
     f"{n(male_avg, 0)} ₺ ile kadınların {n(fem_avg, 0)} ₺ değerinin %{n((male_avg / fem_avg - 1) * 100, 0)} üzerinde; "
     f"farkın nedeni (kategori karması, kampanya duyarlılığı) ayrıca incelenmeli; bu veriyle kesin bir neden söylenemez."),
    ("Gelir grubuna göre harcama (donut)", "donut_gelir.png",
     f"Orta gelir grubu cironun %{n(inc_share['Orta'], 0)}'ini, yüksek gelir grubu %{n(inc_share['Yüksek'], 0)}'ini, düşük gelir "
     f"grubu %{n(inc_share['Düşük'], 0)}'ini oluşturuyor. Yüksek gelirli müşterilerin ortalama sepeti ({n(hi_avg, 0)} ₺) düşük gelirlilerin "
     f"({n(lo_avg, 0)} ₺) yaklaşık {n(hi_avg / lo_avg, 1)} katı; küçük bir segment orantısız büyük değer yaratıyor."),
    ("Kategoriye göre ortalama sepet (bar)", "bar_kategori.png",
     f"{cat_top} {n(cats.loc[cat_top, 'avg_order_value'], 0)} ₺ ile en yüksek sepet tutarına sahip ve cironun %{n(elec_share, 0)}'ini "
     f"oluşturuyor; {cat_low} ise {n(cats.loc[cat_low, 'avg_order_value'], 0)} ₺ ile en düşük. Moda sipariş adedinde birinci "
     f"(cironun %{n(moda_share, 0)}'i) ve düşük sepetli kategorilerle çapraz satış için uygun."),
]
for title, img, text in items:
    doc.add_heading(title, 3)
    if img != "dashboard.png":
        pic(img, 11 if "donut" not in img else 8)
    para(text)

doc.add_heading("4.2 Stratejik öneriler", 2)
table(["#", "Aksiyon", "Hedef kitle / zamanlama", "Gerekçe ve beklenen etki"], [
    ["1", "Akşam saatlerine özel mobil bildirim ve \"flaş fırsat\" kampanyaları",
     f"Tüm müşteriler, özellikle 19:00–22:00 arası; İstanbul ve Ankara öncelikli",
     f"Siparişlerin %{n(eve19, 0)}'i bu saatlerde veriliyor. Bildirim ve kampanyayı bu pencereye kaydırmak dönüşümü artırır; "
     f"bu saatlerdeki siparişlerde %5 artış bile yıllık sipariş sayısını yaklaşık {n(eve19 / 100 * kpi.total_orders * 0.05, 0)} adet yükseltir."],
    ["2", "Yüksek gelirli segmente elektronik odaklı premium paket ve sadakat programı",
     "Yüksek gelir grubu (özellikle erkek müşteriler), Kasım öncesi hazırlık",
     f"Yüksek gelirli müşterilerin sepeti düşük gelirlilerin {n(hi_avg / lo_avg, 1)} katı; elektronik cironun %{n(elec_share, 0)}'ini yaratıyor. "
     f"Bu segmentte sepet başına %10 artış cirodaki payı olan %{n(inc_share['Yüksek'], 0)}'lik dilimde doğrudan etki yaratır."],
    ["3", "Kasım–Aralık kampanya dönemi için stok ve reklam bütçesinin önceden planlanması; Temmuz–Ağustos'ta canlandırma kampanyası",
     "Tüm müşteriler; Ekim sonu hazırlık, yaz aylarında indirim/kupon",
     f"Kasım–Aralık yıllık cironun %{n(nd_share, 0)}'ini taşıyor. Yaz durgunluğunu kapatmak aylık cirodaki dalgalanmayı azaltır."],
    ["4", "Sipariş vermemiş kayıtlı müşteriler için yeniden etkinleştirme (ilk sipariş indirimi)",
     f"Kayıtlı ama pasif ~{n(5000 - kpi.active_customers)} müşteri; kayıt sonrası ilk 30 gün",
     "Pasif kitle zaten tanınan ve ulaşılabilir bir kitle; yeni müşteri kazanmaktan daha düşük maliyetli."],
], widths=[0.8, 4.8, 4.4, 6.0], font=9)

doc.add_heading("4.3 Sonuç", 2)
para("Analiz, ciro büyümesi için üç kaldıraç işaret ediyor: zaman (akşam saatleri ve yıl sonu), değer (yüksek gelirli segment ve "
     "elektronik) ve coğrafya (İstanbul'a bağımlılığı yönetirken Ankara-İzmir'i büyütmek). Öneriler küçük pilotlarla başlatılıp sonuçlar "
     "aynı dashboard üzerinden izlenerek ölçeklenebilir.")

doc.add_heading("Ek – Veri seti hakkında not", 1)
para("Ödev yönergesinde yalnızca tablo ve kolon adları verildiği için, customers ve orders tabloları bu şemaya uygun olarak, "
     "tekrarlanabilir (sabit tohumlu) bir betikle sentetik olarak üretilmiştir (01_generate_data.py). Veri gerçek bir şirkete "
     "ait değildir; rakamlar yöntemi göstermek içindir. Aynı SQL sorguları ve Power BI modeli gerçek veriyle değiştirilmeden çalışır.")
table(["Dosya", "Açıklama"], [
    ["Ana_Rapor.docx", "Proje yönetim planı, SQL sorguları ve veri hikayeleştirme raporu (bu belge)"],
    ["data/customers.csv, data/orders.csv", "Veri seti (Power BI'a doğrudan aktarılabilir)"],
    ["02_queries.sql", "View ve tüm analiz sorguları"],
    ["ecommerce.db", "SQLite veritabanı"],
    ["charts/*.png", "Dashboard ve tekil grafik görselleri"],
], widths=[5.5, 10.5])

out = base / "Ana_Rapor.docx"
doc.save(out)
print("saved", out, out.stat().st_size)
