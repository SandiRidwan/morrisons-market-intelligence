"""
make_dashboard_mockup.py
========================
Membuat MOCKUP visual layout dashboard Tableau (1 gambar) sebagai referensi
desain. Bukan dashboard interaktif — ini "wireframe" high-fidelity agar
susunan panel & KPI terlihat sebelum dibangun di Tableau.

Output: reports/figures/00_dashboard_mockup.png
"""

from __future__ import annotations

from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Rectangle
import matplotlib.gridspec as gridspec
import numpy as np
import pandas as pd

import analysis as A

FIG = Path(__file__).resolve().parent.parent / "reports" / "figures"

C = {
    "primary": "#1F5C3D", "accent": "#E4A11B", "dark": "#22303C",
    "grey": "#8B9AA6", "red": "#C0392B", "blue": "#2E6F95",
    "bg": "#F5F6F7", "card": "#FFFFFF",
}


def _card(ax, title, accent=C["primary"]):
    """Beri bingkai 'card' ala dashboard."""
    ax.set_facecolor(C["card"])
    for s in ax.spines.values():
        s.set_color("#DDE1E4")
    ax.set_xticks([]); ax.set_yticks([])
    ax.set_title(title, fontsize=8.5, fontweight="bold",
                 color=C["dark"], loc="left", pad=6)


def build():
    df, _ = A.load_and_clean()

    fig = plt.figure(figsize=(16, 10.5), dpi=110)
    fig.patch.set_facecolor(C["bg"])

    gs = gridspec.GridSpec(
        4, 6, figure=fig,
        height_ratios=[0.5, 0.55, 1.0, 1.0],
        hspace=0.55, wspace=0.35,
        left=0.035, right=0.98, top=0.965, bottom=0.045)

    # ---------- HEADER ----------
    axh = fig.add_subplot(gs[0, :])
    axh.set_facecolor(C["primary"])
    axh.set_xticks([]); axh.set_yticks([])
    for s in axh.spines.values():
        s.set_visible(False)
    axh.text(0.012, 0.62, "Morrisons UK — Grocery Market Intelligence",
             fontsize=16, fontweight="bold", color="white", va="center")
    axh.text(0.012, 0.20, "Real scraped data  ·  n = 18,100 products  ·  15 categories  ·  2,600 brands",
             fontsize=9, color="#D7E4DC", va="center")
    axh.text(0.99, 0.5, "TABLEAU DASHBOARD  (layout mockup)",
             fontsize=9, color="#D7E4DC", va="center", ha="right", style="italic")

    # ---------- KPI BAND ----------
    kpis = [
        ("18,100", "Products", C["primary"]),
        ("£2.70", "Median price", C["dark"]),
        ("26.4%", "Promo rate", C["accent"]),
        ("−23.1%", "Median discount", C["red"]),
        ("2,600", "Unique brands", C["blue"]),
    ]
    for i, (val, lbl, col) in enumerate(kpis):
        ax = fig.add_subplot(gs[1, i:i+1] if i < 5 else gs[1, 5])
        # 6 kolom, 5 KPI -> ambil spasi; petakan i ke kolom i (0..4), kolom 5 diisi terakhir
        ax.axis("off")
    # ulang penempatan KPI secara manual (5 kotak merata)
    for i, (val, lbl, col) in enumerate(kpis):
        ax = fig.add_subplot(gs[1, i])
        ax.axis("off")
        box = FancyBboxPatch((0.02, 0.05), 0.96, 0.9,
                             boxstyle="round,pad=0.02,rounding_size=0.06",
                             linewidth=0, facecolor=C["card"],
                             transform=ax.transAxes, clip_on=False)
        ax.add_patch(box)
        ax.add_patch(Rectangle((0.02, 0.05), 0.03, 0.9, transform=ax.transAxes,
                               facecolor=col, clip_on=False))
        ax.text(0.11, 0.62, val, fontsize=20, fontweight="bold", color=col,
                transform=ax.transAxes, va="center")
        ax.text(0.11, 0.26, lbl, fontsize=8.5, color=C["dark"],
                transform=ax.transAxes, va="center")

    # ---------- ROW 2: price + promo ----------
    ax1 = fig.add_subplot(gs[2, 0:3])
    _card(ax1, "01 · Median Price by Category")
    t = A.price_summary_by_category(df)
    t = t[t.index.isin(df["cat1"].value_counts().head(10).index)].sort_values("median_price")
    ax1.barh(range(len(t)), t["median_price"], color=C["primary"], zorder=3)
    ax1.set_yticks(range(len(t)))
    ax1.set_yticklabels([x[:22] for x in t.index], fontsize=6.5)
    for i, v in enumerate(t["median_price"]):
        ax1.text(v + 0.2, i, f"£{v:.2f}", va="center", fontsize=6, color=C["dark"])
    ax1.tick_params(axis="x", labelsize=6.5)
    ax1.grid(axis="y", visible=False); ax1.grid(axis="x", color="#EEEEEE")
    ax1.set_xlim(0, t["median_price"].max()*1.18)

    ax2 = fig.add_subplot(gs[2, 3:6])
    _card(ax2, "02 · Promotion Rate by Category")
    t2 = A.promo_analysis(df)
    t2 = t2[t2.index.isin(df["cat1"].value_counts().head(10).index)].sort_values("promo_rate_pct")
    colors = [C["accent"] if v == t2["promo_rate_pct"].max() else C["grey"]
              for v in t2["promo_rate_pct"]]
    ax2.barh(range(len(t2)), t2["promo_rate_pct"], color=colors, zorder=3)
    ax2.set_yticks(range(len(t2)))
    ax2.set_yticklabels([x[:22] for x in t2.index], fontsize=6.5)
    for i, v in enumerate(t2["promo_rate_pct"]):
        ax2.text(v + 0.8, i, f"{v:.0f}%", va="center", fontsize=6, color=C["dark"])
    ax2.tick_params(axis="x", labelsize=6.5)
    ax2.grid(axis="y", visible=False); ax2.grid(axis="x", color="#EEEEEE")
    ax2.set_xlim(0, t2["promo_rate_pct"].max()*1.2)

    # ---------- ROW 3: brand positioning + own brand ----------
    ax3 = fig.add_subplot(gs[3, 0:3])
    _card(ax3, "03 · Brand Positioning  (price index vs rating)")
    bp = A.brand_positioning(df).dropna(subset=["avg_rating"])
    cmap = {"Premium": C["red"], "Value": C["primary"], "Mainstream": C["grey"]}
    for tier, g in bp.groupby("positioning"):
        ax3.scatter(g["price_index"], g["avg_rating"], s=g["products"]*1.5,
                    alpha=0.55, color=cmap[tier], label=tier, edgecolor="white", linewidth=0.4)
    ax3.axvline(1.0, color=C["dark"], ls="--", lw=1)
    ax3.set_xlabel("Price index (÷ category median)", fontsize=7)
    ax3.set_ylabel("Median rating", fontsize=7)
    ax3.tick_params(labelsize=6.5)
    ax3.set_xlim(0, min(bp["price_index"].max(), 5))
    ax3.legend(fontsize=6, frameon=False, loc="lower right")
    ax3.grid(color="#EEEEEE")

    ax4 = fig.add_subplot(gs[3, 3:6])
    _card(ax4, "04 · Own-Brand Opportunity  (premium vs value share)")
    ob = A.own_brand_opportunity(df).head(10).sort_values("premium_share_pct")
    y = np.arange(len(ob)); w = 0.4
    ax4.barh(y + w/2, ob["premium_share_pct"], height=w, color=C["red"], label="Premium", zorder=3)
    ax4.barh(y - w/2, ob["value_share_pct"], height=w, color=C["primary"], label="Value", zorder=3)
    ax4.set_yticks(y)
    ax4.set_yticklabels([x[:22] for x in ob.index], fontsize=6.5)
    ax4.tick_params(axis="x", labelsize=6.5)
    ax4.legend(fontsize=6, frameon=False, loc="lower right")
    ax4.grid(axis="y", visible=False); ax4.grid(axis="x", color="#EEEEEE")
    ax4.set_xlabel("% of SKUs", fontsize=7)

    fig.text(0.035, 0.012,
             "Blueprint lengkap: TABLEAU_DASHBOARD_BLUEPRINT.md  ·  "
             "Data source: data/tableau/tableau_products.csv  ·  "
             "Dibuat oleh Sandi Ridwan",
             fontsize=6.5, color=C["grey"])

    fp = FIG / "00_dashboard_mockup.png"
    fig.savefig(fp, bbox_inches="tight", facecolor=C["bg"])
    plt.close(fig)
    print(f"[OK] Mockup dashboard: {fp}")
    return fp


if __name__ == "__main__":
    build()
