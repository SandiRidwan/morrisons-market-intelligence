"""
make_charts.py
==============
Menghasilkan gambar (PNG) dari insight analisis data ASLI Morrisons UK.
Output -> reports/figures/*.png

Dijalankan setelah morrisons_parser.py + analysis.py siap.
"""

from __future__ import annotations

from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
from matplotlib.patches import Patch
import numpy as np
import pandas as pd

import analysis as A

FIG_DIR = Path(__file__).resolve().parent.parent / "reports" / "figures"

C = {
    "primary": "#1F5C3D", "accent": "#E4A11B", "dark": "#22303C",
    "grey": "#8B9AA6", "red": "#C0392B", "blue": "#2E6F95",
}
PALETTE = [C["primary"], C["accent"], C["blue"], C["red"], C["grey"],
           "#6A4C93", "#2A9D8F", "#E76F51", "#264653", "#A4262C",
           "#457B9D", "#E9C46A", "#F4A261", "#2A9D8F", "#9B5DE5"]

plt.rcParams.update({
    "figure.dpi": 130, "savefig.dpi": 130, "font.size": 10,
    "axes.titlesize": 12, "axes.titleweight": "bold",
    "axes.spines.top": False, "axes.spines.right": False,
    "axes.edgecolor": "#CCCCCC", "axes.grid": True,
    "grid.color": "#EEEEEE", "grid.linewidth": 0.8,
    "figure.facecolor": "white",
})


def _save(fig, name):
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    fp = FIG_DIR / f"{name}.png"
    fig.tight_layout()
    fig.savefig(fp, bbox_inches="tight")
    plt.close(fig)
    print(f"  [fig] {fp.name}")
    return fp


def _short(s, n=24):
    return s if len(s) <= n else s[: n - 1] + "…"


def chart_price_by_category(df):
    t = A.price_summary_by_category(df).sort_values("median_price")
    fig, ax = plt.subplots(figsize=(9.5, 6))
    bars = ax.barh([_short(i) for i in t.index], t["median_price"],
                   color=C["primary"], zorder=3)
    ax.errorbar(t["median_price"], range(len(t)),
                xerr=[t["median_price"] - t["p10"], t["p90"] - t["median_price"]],
                fmt="none", ecolor=C["dark"], elinewidth=1.2, capsize=3, zorder=4)
    for b, v in zip(bars, t["median_price"]):
        ax.text(v + 0.3, b.get_y() + b.get_height()/2, f"£{v:.2f}",
                va="center", fontsize=8.5, fontweight="bold", color=C["dark"])
    ax.set_xlabel("Median effective price (£) — whisker = P10–P90")
    ax.set_title(f"Median Price by Category — Morrisons UK\n(real scraped data, n={len(df):,} products)")
    ax.grid(axis="y", visible=False)
    return _save(fig, "01_price_by_category")


def chart_promo_rate(df):
    t = A.promo_analysis(df).sort_values("promo_rate_pct")
    fig, ax = plt.subplots(figsize=(9.5, 6))
    colors = [C["accent"] if v == t["promo_rate_pct"].max() else C["grey"]
              for v in t["promo_rate_pct"]]
    bars = ax.barh([_short(i) for i in t.index], t["promo_rate_pct"],
                   color=colors, zorder=3)
    for b, v, d in zip(bars, t["promo_rate_pct"], t["avg_discount_pct"]):
        ax.text(v + 0.7, b.get_y() + b.get_height()/2,
                f"{v:.1f}%" + (f"  (avg −{d:.0f}%)" if d else ""),
                va="center", fontsize=8.2, color=C["dark"])
    ax.set_xlabel("% of SKUs on promotion")
    ax.set_title("Promotion Intensity by Category")
    ax.set_xlim(0, t["promo_rate_pct"].max()*1.28)
    ax.grid(axis="y", visible=False)
    return _save(fig, "02_promo_rate")


def chart_brand_positioning(df):
    pos = A.brand_positioning(df)
    # ambil 10 premium tertinggi + 10 value terendah agar chart terbaca
    show = pd.concat([pos.head(10), pos.tail(10)]).drop_duplicates()
    show = show.sort_values("price_index")
    fig, ax = plt.subplots(figsize=(9.5, 8))
    cmap = {"Premium": C["red"], "Mainstream": C["grey"], "Value": C["primary"]}
    colors = [cmap[p] for p in show["positioning"]]
    bars = ax.barh([_short(i, 22) for i in show.index], show["price_index"],
                   color=colors, zorder=3)
    ax.axvline(1.0, color=C["dark"], lw=1.4, ls="--", zorder=4)
    for b, v in zip(bars, show["price_index"]):
        ax.text(v + 0.04, b.get_y() + b.get_height()/2, f"{v:.2f}",
                va="center", fontsize=8, color=C["dark"])
    ax.set_xlabel("Price index (brand price ÷ category median)")
    ax.set_title("Brand Price Positioning — 10 Most Premium vs 10 Most Value\n"
                 "(1.0 = at category median)")
    ax.grid(axis="y", visible=False)
    ax.legend(handles=[Patch(color=v, label=k) for k, v in cmap.items()],
              loc="lower right", frameon=False, fontsize=9)
    return _save(fig, "03_brand_positioning")


def chart_own_brand(df):
    t = A.own_brand_opportunity(df).sort_values("own_brand_gap")
    fig, ax = plt.subplots(figsize=(9.5, 6))
    y = np.arange(len(t)); w = 0.4
    ax.barh(y + w/2, t["premium_share_pct"], height=w, color=C["red"],
            label="Premium-brand share", zorder=3)
    ax.barh(y - w/2, t["value_share_pct"], height=w, color=C["primary"],
            label="Value-brand share", zorder=3)
    ax.set_yticks(y); ax.set_yticklabels([_short(i) for i in t.index])
    for i, gap in enumerate(t["own_brand_gap"]):
        ax.text(max(t["premium_share_pct"].iloc[i], t["value_share_pct"].iloc[i]) + 1,
                i, f"gap {gap:+.1f}pp", va="center", fontsize=8, color=C["dark"])
    ax.set_xlabel("% of SKUs")
    ax.set_xlim(0, t["premium_share_pct"].max()*1.25)
    ax.set_title("Own-Brand Opportunity\n(categories where premium brands dominate shelf)")
    ax.legend(loc="lower right", frameon=False, fontsize=8.5)
    ax.grid(axis="y", visible=False)
    return _save(fig, "04_own_brand_gap")


def chart_portfolio(df):
    t = A.category_portfolio(df)
    fig, axes = plt.subplots(1, 2, figsize=(13, 6))
    t10 = t.head(10)
    ax = axes[0]
    ax.pie(t10["sku_count"], labels=[_short(i, 16) for i in t10.index],
           autopct=lambda p: f"{p:.1f}%", startangle=90,
           colors=PALETTE[:len(t10)], textprops={"fontsize": 7.5},
           wedgeprops={"edgecolor": "white", "linewidth": 1})
    ax.set_title("Assortment Share (top 10 categories by SKU)")
    ax = axes[1]
    t2 = t[t["brand_count"] >= 5].sort_values("brand_density").tail(12)
    bars = ax.barh([_short(i) for i in t2.index], t2["brand_density"],
                   color=C["primary"], zorder=3)
    for b, v in zip(bars, t2["brand_density"]):
        ax.text(v + 0.2, b.get_y() + b.get_height()/2, f"{v:.1f}",
                va="center", fontsize=8, color=C["dark"])
    ax.set_xlabel("SKUs per brand")
    ax.set_title("Brand Density")
    ax.grid(axis="y", visible=False)
    fig.suptitle("Category Portfolio Composition", fontsize=14, fontweight="bold")
    return _save(fig, "05_portfolio")


def chart_rating_vs_price(df):
    sub = df.dropna(subset=["rating"]).copy()
    fig, ax = plt.subplots(figsize=(9.5, 6))
    hb = ax.hexbin(sub["effective_price"].clip(0, 30), sub["rating"],
                   gridsize=35, cmap="YlGn", mincnt=1, bins="log")
    fig.colorbar(hb, ax=ax, label="number of products (log)")
    ax.axhline(sub["rating"].median(), color=C["red"], ls="--", lw=1.2)
    rp = A.rating_vs_price(df)
    ax.set_xlabel("Effective price (£, clipped at 30)")
    ax.set_ylabel("Customer rating (1–5)")
    ax.set_title(f"Rating vs Price — Spearman ρ = {rp['spearman_corr']}\n"
                 f"({rp['interpretation']})")
    return _save(fig, "06_rating_vs_price")


def chart_rating_by_quartile(df):
    rp = A.rating_vs_price(df)
    byq = rp["rating_by_price_quartile"]
    fig, ax = plt.subplots(figsize=(8, 5))
    bars = ax.bar(range(len(byq)), byq["median"],
                  color=[C["grey"], C["blue"], C["primary"], C["accent"]], zorder=3)
    for b, (v, c) in zip(bars, zip(byq["median"], byq["count"])):
        ax.text(b.get_x()+b.get_width()/2, v+0.03, f"{v:.2f}\n(n={c:,})",
                ha="center", fontsize=9, color=C["dark"])
    ax.set_xticks(range(len(byq)))
    ax.set_xticklabels(byq.index, fontsize=9)
    ax.set_ylim(0, 5.4)
    ax.set_ylabel("Median rating")
    ax.set_title("Median Rating by Price Quartile")
    return _save(fig, "07_rating_by_quartile")


def chart_leaderboard(df):
    t = A.brand_leaderboard(df, top_n=20).sort_values("sku_count")
    fig, ax = plt.subplots(figsize=(9.5, 7))
    bars = ax.barh([_short(i, 22) for i in t.index], t["sku_count"],
                   color=C["primary"], zorder=3)
    for b, v, c, rt in zip(bars, t["sku_count"], t["categories"], t["avg_rating"]):
        lbl = f"{v} SKUs · {c} cats" + (f" · R{rt:.1f}" if rt == rt else "")
        ax.text(v + 1.5, b.get_y() + b.get_height()/2, lbl,
                va="center", fontsize=7.5, color=C["dark"])
    ax.set_xlabel("Number of SKUs (shelf presence)")
    ax.set_title("Brand Leaderboard — Top 20 by SKU Count")
    ax.set_xlim(0, t["sku_count"].max()*1.5)
    ax.grid(axis="y", visible=False)
    return _save(fig, "08_brand_leaderboard")


def chart_value_winners(df):
    t = A.value_for_money(df).head(15).sort_values("value_score")
    fig, ax = plt.subplots(figsize=(9.5, 7))
    bars = ax.barh([_short(i, 30) for i in t["name"]], t["value_score"],
                   color=C["accent"], zorder=3)
    for b, sc, pp, rt in zip(bars, t["value_score"], t["price_per_100g"], t["rating"]):
        ax.text(sc + 0.003, b.get_y() + b.get_height()/2,
                f"{sc:.2f} · £{pp:.2f}/100g · R{rt:.1f}",
                va="center", fontsize=7.5, color=C["dark"])
    ax.set_xlabel("Value score (60% rating + 40% low price-per-100g)")
    ax.set_xlim(0, 1.15)
    ax.set_title("Top 15 Value-for-Money Products\n(high rating, low unit price — min 10 reviews)")
    ax.grid(axis="y", visible=False)
    return _save(fig, "09_value_winners")


def chart_description_completeness(df):
    t = A.description_completeness(df).sort_values("with_description_pct").tail(14)
    fig, ax = plt.subplots(figsize=(9.5, 6))
    bars = ax.barh([_short(i) for i in t.index], t["with_description_pct"],
                   color=C["blue"], zorder=3)
    for b, v, ln in zip(bars, t["with_description_pct"], t["avg_desc_len"]):
        ax.text(v + 0.5, b.get_y() + b.get_height()/2,
                f"{v:.0f}%  (avg {ln:.0f} chars)",
                va="center", fontsize=8, color=C["dark"])
    ax.set_xlabel("% of products with a description")
    ax.set_xlim(0, 108)
    ax.set_title("Content Completeness by Category\n(product descriptions captured)")
    ax.grid(axis="y", visible=False)
    return _save(fig, "10_content_completeness")


def build_all():
    df, _ = A.load_and_clean()
    print(f"Membuat visualisasi dari {len(df):,} produk...")
    figs = [
        chart_price_by_category(df), chart_promo_rate(df),
        chart_brand_positioning(df), chart_own_brand(df),
        chart_portfolio(df), chart_rating_vs_price(df),
        chart_rating_by_quartile(df), chart_leaderboard(df),
        chart_value_winners(df), chart_description_completeness(df),
    ]
    print(f"\n[OK] {len(figs)} gambar dibuat di {FIG_DIR}")
    return figs


if __name__ == "__main__":
    build_all()
