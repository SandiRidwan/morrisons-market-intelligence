"""
run_analysis.py
===============
Orkestrator utama: jalankan pipeline analisis end-to-end dan simpan
SEMUA tabel insight ke reports/tables/, plus ringkasan JSON ke reports/.

Ini "satu perintah" yang menjalankan seluruh project:
    python src/run_analysis.py
"""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

import analysis as A

REPORTS = Path(__file__).resolve().parent.parent / "reports"


def run() -> dict:
    df, rpt = A.load_and_clean()

    tables = {
        "price_by_category": A.price_summary_by_category(df),
        "promo_by_category": A.promo_analysis(df),
        "brand_positioning": A.brand_positioning(df),
        "value_for_money": A.value_for_money(df),
        "category_portfolio": A.category_portfolio(df),
        "brand_leaderboard": A.brand_leaderboard(df),
        "own_brand_opportunity": A.own_brand_opportunity(df),
        "review_engagement": A.review_engagement(df),
        "content_completeness": A.description_completeness(df),
    }
    for name, t in tables.items():
        fp = A.save_table(t, name)
        print(f"  [table] {fp.name:32} ({len(t)} rows)")

    rp = A.rating_vs_price(df)
    rp["rating_by_price_quartile"].to_csv(
        REPORTS / "tables" / "rating_by_price_quartile.csv")

    summary = {
        "source": "Morrisons UK (groceries.morrisons.com)",
        "products_raw": rpt.rows_raw,
        "products_analyzed": rpt.rows_clean,
        "categories": int(df["cat1"].nunique()),
        "brands": int(df["brand"].nunique()),
        "price_min": round(float(df["effective_price"].min()), 2),
        "price_median": round(float(df["effective_price"].median()), 2),
        "price_max": round(float(df["effective_price"].max()), 2),
        "promo_rate_pct": round(float(df["is_promo"].mean() * 100), 1),
        "median_discount_pct": round(float(df["discount_pct"].median(skipna=True)), 1),
        "rated_products_pct": round(float(df["rating"].notna().mean() * 100), 1),
        "rating_vs_price_spearman": rp["spearman_corr"],
        "data_quality": rpt.as_dict(),
        "notes": rpt.notes,
    }
    (REPORTS / "summary.json").write_text(json.dumps(summary, indent=2),
                                          encoding="utf-8")
    print(f"\n  [json] summary.json")
    return summary


if __name__ == "__main__":
    print("=" * 72)
    print("RUNNING FULL ANALYSIS — MORRISONS UK MARKET INTELLIGENCE")
    print("=" * 72)
    s = run()
    print("\n=== RINGKASAN ===")
    for k, v in s.items():
        if k not in ("data_quality", "notes"):
            print(f"  {k:28}: {v}")
