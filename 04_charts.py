"""SQL sonuçlarından dashboard görselleri üretir (charts/*.png)."""
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

base = Path(__file__).parent
res = base / "results"
out = base / "charts"
out.mkdir(exist_ok=True)

plt.rcParams.update({"font.family": "DejaVu Sans", "axes.spines.top": False, "axes.spines.right": False})
BLUE, ORANGE, GREEN, GRAY = "#2563eb", "#f59e0b", "#10b981", "#64748b"
PALETTE = ["#2563eb", "#f59e0b", "#10b981", "#ef4444", "#8b5cf6"]


def tl(v, digits=1):
    """Milyon TL biçimi."""
    return f"{v / 1e6:.{digits}f}".replace(".", ",") + " Mn ₺"


kpi = pd.read_csv(res / "kpis.csv").iloc[0]
cities = pd.read_csv(res / "top5_cities.csv")
hourly = pd.read_csv(res / "hourly_orders.csv")
monthly = pd.read_csv(res / "monthly_revenue.csv")
gender = pd.read_csv(res / "by_gender.csv")
income = pd.read_csv(res / "by_income.csv")
cats = pd.read_csv(res / "avg_by_category.csv")


def draw_kpi(ax, title, value):
    ax.axis("off")
    ax.add_patch(plt.Rectangle((0, 0), 1, 1, transform=ax.transAxes, color="#eff6ff", ec="#bfdbfe"))
    ax.text(0.5, 0.68, value, ha="center", va="center", fontsize=22, fontweight="bold", color=BLUE, transform=ax.transAxes)
    ax.text(0.5, 0.25, title, ha="center", va="center", fontsize=11, color=GRAY, transform=ax.transAxes)


def bar_cities(ax):
    d = cities.sort_values("total_revenue")
    ax.barh(d.city, d.total_revenue / 1e6, color=BLUE)
    for i, v in enumerate(d.total_revenue / 1e6):
        ax.text(v + 0.1, i, f"{v:.1f}", va="center", fontsize=9)
    ax.set_title("En Fazla Ciro Getiren 5 Şehir (Mn ₺)", loc="left", fontweight="bold")
    ax.set_xlim(0, d.total_revenue.max() / 1e6 * 1.15)


def line_trend(ax):
    ax.plot(monthly.order_month.str[5:], monthly.revenue / 1e6, marker="o", color=BLUE, lw=2)
    ax.fill_between(range(len(monthly)), monthly.revenue / 1e6, color=BLUE, alpha=0.08)
    ax.set_title("Aylık Satış Trendi 2025 (Mn ₺)", loc="left", fontweight="bold")
    ax.set_xlabel("Ay")
    ax.grid(axis="y", alpha=0.25)
    peak = monthly.revenue.idxmax()
    ax.annotate("Kasım (kampanya)", (peak, monthly.revenue[peak] / 1e6), xytext=(peak - 4, monthly.revenue[peak] / 1e6 - 0.1),
                arrowprops=dict(arrowstyle="->", color=GRAY), fontsize=9, color=GRAY)


def line_hourly(ax):
    ax.plot(hourly.order_hour, hourly.order_count, marker="o", color=ORANGE, lw=2)
    ax.fill_between(hourly.order_hour, hourly.order_count, color=ORANGE, alpha=0.1)
    ax.set_xticks(range(0, 24, 2))
    ax.set_title("Saatlik Sipariş Sayısı", loc="left", fontweight="bold")
    ax.set_xlabel("Saat")
    ax.grid(axis="y", alpha=0.25)
    ax.axvspan(20, 22, color=ORANGE, alpha=0.12)


def donut(ax, labels, values, title):
    wedges, _ = ax.pie(values, colors=PALETTE, startangle=90, wedgeprops=dict(width=0.38, edgecolor="white"))
    total = sum(values)
    ax.set_title(title, fontweight="bold")
    ax.legend(wedges, [f"{l}  %{v / total * 100:.0f}" for l, v in zip(labels, values)], loc="upper center",
              bbox_to_anchor=(0.5, 0.02), ncol=3, frameon=False, fontsize=9)


# Tek tek görseller
for name, fn, size in [("bar_sehir", bar_cities, (7, 4)), ("cizgi_aylik", line_trend, (7, 4)), ("cizgi_saatlik", line_hourly, (7, 4))]:
    fig, ax = plt.subplots(figsize=size)
    fn(ax)
    fig.tight_layout()
    fig.savefig(out / f"{name}.png", dpi=160)
    plt.close(fig)

for name, df, col, title in [("donut_cinsiyet", gender, "gender", "Cinsiyete Göre Harcama Dağılımı"),
                             ("donut_gelir", income, "income_group", "Gelir Grubuna Göre Harcama Dağılımı")]:
    fig, ax = plt.subplots(figsize=(5, 4.4))
    donut(ax, df[col].tolist(), df.revenue.tolist(), title)
    fig.tight_layout()
    fig.savefig(out / f"{name}.png", dpi=160)
    plt.close(fig)

fig, ax = plt.subplots(figsize=(7, 4))
d = cats.sort_values("avg_order_value")
ax.barh(d.category, d.avg_order_value, color=GREEN)
for i, v in enumerate(d.avg_order_value):
    ax.text(v + 20, i, f"{v:,.0f} ₺".replace(",", "."), va="center", fontsize=9)
ax.set_title("Kategoriye Göre Ortalama Sepet Tutarı (₺)", loc="left", fontweight="bold")
ax.set_xlim(0, d.avg_order_value.max() * 1.18)
fig.tight_layout()
fig.savefig(out / "bar_kategori.png", dpi=160)
plt.close(fig)

# Birleşik dashboard
fig = plt.figure(figsize=(16, 10), facecolor="white")
gs = fig.add_gridspec(3, 6, height_ratios=[0.6, 1.5, 1.6], hspace=0.55, wspace=0.7)
fig.suptitle("E-Ticaret Satış ve Müşteri Davranışları Dashboard (2025)", fontsize=18, fontweight="bold", x=0.05, ha="left")
draw_kpi(fig.add_subplot(gs[0, 0:2]), "Toplam Ciro", tl(kpi.total_revenue))
draw_kpi(fig.add_subplot(gs[0, 2:4]), "Toplam Sipariş Sayısı", f"{int(kpi.total_orders):,}".replace(",", "."))
draw_kpi(fig.add_subplot(gs[0, 4:6]), "Aktif Müşteri Sayısı", f"{int(kpi.active_customers):,}".replace(",", "."))
bar_cities(fig.add_subplot(gs[1, 0:3]))
line_trend(fig.add_subplot(gs[1, 3:6]))
donut(fig.add_subplot(gs[2, 0:2]), gender.gender.tolist(), gender.revenue.tolist(), "Cinsiyete Göre Harcama")
donut(fig.add_subplot(gs[2, 2:4]), income.income_group.tolist(), income.revenue.tolist(), "Gelir Grubuna Göre Harcama")
line_hourly(fig.add_subplot(gs[2, 4:6]))
fig.savefig(out / "dashboard.png", dpi=140, bbox_inches="tight")
plt.close(fig)
print(sorted(p.name for p in out.glob("*.png")))
