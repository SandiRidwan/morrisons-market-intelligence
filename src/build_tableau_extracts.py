"""
build_tableau_extracts.py
=========================
Menyiapkan file khusus untuk Tableau:

1. data/tableau/tableau_products.csv
   -> dataset utama + KOLOM CALCULATED siap pakai (price_index, brand_tier,
      value_score, price_clipped) supaya tidak perlu bikin Calculated Field
      manual di Tableau.

2. data/tableau/tableau_kpi.csv
   -> 5 baris KPI untuk "KPI BAND" di dashboard.

3. data/tableau/tableau_brand_positioning.csv
   -> versi brand-level (scatter lebih ringan & bersih).

Jalankan: python src/build_tableau_extracts.py
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

import analysis as A

OUT = Path(__file__).resolve().parent.parent / "data" / "tableau"


def build_products(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    # kolom siap-Tableau (duplikat logika analysis.py agar mandiri)
    out["price_index"] = out["price_index"].round(3)
    out["price_clipped"] = out["effective_price"].clip(upper=30)
    out["has_rating"] = out["rating"].notna()
    out["has_description"] = out["desc_len"] > 0

    # value score
    sub_mask = out["reviews"].fillna(0) >= 10
    out["value_score"] = np.nan
    sub = out[sub_mask & out["rating"].notna() & out["price_per_100g"].notna()]
    if len(sub):
        price_r = sub["price_per_100g"].rank(pct=True)
        rating_r = sub["rating"].rank(pct=True)
        out.loc[sub.index, "value_score"] = (
            rating_r * 0.6 + (1 - price_r) * 0.4).round(3)

    cols = [
        "product_id", "name", "brand", "cat1", "cat2",
        "effective_price", "price_clipped", "list_price", "unit_price",
        "price_per_100g", "price_index", "brand_tier",
        "is_promo", "discount_pct", "promo_type",
        "rating", "reviews", "has_rating",
        "desc_len", "has_description", "value_score",
    ]
    return out[cols]


def build_kpi(df: pd.DataFrame) -> pd.DataFrame:
    rows = [
        ("Total Products", len(df), "count"),
        ("Median Price", round(float(df["effective_price"].median()), 2), "£"),
        ("Promo Rate", round(float(df["is_promo"].mean() * 100), 1), "%"),
        ("Median Discount", round(float(df["discount_pct"].median(skipna=True)), 1), "%"),
        ("Unique Brands", int(df["brand"].nunique()), "count"),
    ]
    return pd.DataFrame(rows, columns=["kpi", "value", "unit"])


def build_brand_positioning(df: pd.DataFrame, min_products: int = 10) -> pd.DataFrame:
    g = df.groupby("brand")
    out = pd.DataFrame({
        "products": g.size(),
        "price_index": g["price_index"].median().round(3),
        "median_rating": g["rating"].median().round(2),
        "median_price": g["effective_price"].median().round(2),
        "promo_rate_pct": (g["is_promo"].mean() * 100).round(1),
        "categories": g["cat1"].nunique(),
    })
    out = out[out["products"] >= min_products].reset_index()
    out["brand_tier"] = np.where(
        out["price_index"] >= 1.15, "Premium",
        np.where(out["price_index"] <= 0.85, "Value", "Mainstream"))
    return out.sort_values("price_index", ascending=False)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    df, rpt = A.load_and_clean()

    prod = build_products(df)
    prod.to_csv(OUT / "tableau_products.csv", index=False)
    print(f"[OK] tableau_products.csv          {prod.shape}")

    kpi = build_kpi(df)
    kpi.to_csv(OUT / "tableau_kpi.csv", index=False)
    print(f"[OK] tableau_kpi.csv               {kpi.shape}")

    bp = build_brand_positioning(df)
    bp.to_csv(OUT / "tableau_brand_positioning.csv", index=False)
    print(f"[OK] tableau_brand_positioning.csv {bp.shape}")

    print(f"\nSemua file Tableau di: {OUT}")
    print("\nKPI:")
    print(kpi.to_string(index=False))


if __name__ == "__main__":
    main()
