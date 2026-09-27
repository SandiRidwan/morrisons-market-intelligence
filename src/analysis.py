"""
analysis.py
===========
Modul analisis pasar untuk dataset produk Morrisons UK (data asli).

Input: data/processed/morrisons_clean.csv (hasil morrisons_parser.py).

Desain:
- Setiap fungsi mengembalikan DataFrame/skalar siap-pakai (bisa dipanggil
  dari notebook, CLI, atau report generator).
- Tidak ada plotting di sini -> analisis & presentasi dipisah.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import numpy as np
import pandas as pd

PROC_CSV = Path(__file__).resolve().parent.parent / "data" / "processed" / "morrisons_clean.csv"

# Hanya kategori berisi barang konsumen (buang bagian korporat/non-produk)
RETAIL_CATS = [
    "Food Cupboard", "Toiletries & Beauty", "Treats & Snacks",
    "Beer, Wines & Spirits", "World Foods", "Household",
    "Health, Wellbeing & Medicines", "Baby & Toddler", "Drinks",
    "Fresh & Chilled Foods", "Dietary & Lifestyle Foods", "Frozen Food",
    "Bakery & Cakes", "Meat & Fish", "Fruit, Veg & Flowers",
]


# ===========================================================================
# 1. INGESTION + DATA QUALITY
# ===========================================================================
@dataclass
class DataQualityReport:
    rows_raw: int = 0
    rows_clean: int = 0
    null_prices: int = 0
    duplicate_products: int = 0
    missing_rating_pct: float = 0.0
    missing_brand_pct: float = 0.0
    notes: list[str] = field(default_factory=list)

    def as_dict(self) -> dict:
        return {
            "rows_raw": self.rows_raw,
            "rows_clean": self.rows_clean,
            "rows_dropped": self.rows_raw - self.rows_clean,
            "duplicate_products_dropped": self.duplicate_products,
            "missing_rating_pct": self.missing_rating_pct,
            "missing_brand_pct": self.missing_brand_pct,
        }


def load_and_clean(path: Path | None = None) -> tuple[pd.DataFrame, DataQualityReport]:
    """
    Muat data terparse & jalankan pembersihan akhir.

    Langkah:
      1. Drop produk tanpa harga valid (tidak bisa dianalisis harga).
      2. Drop duplikat berdasarkan product_id.
      3. Batasi ke kategori retail (buang halaman korporat).
      4. Normalisasi nama brand & buat tier harga.
      5. Buat kolom analitik turunan.
    """
    path = path or PROC_CSV
    if not path.exists():
        raise FileNotFoundError(
            f"Data bersih tidak ditemukan: {path}\n"
            "Jalankan dulu: python src/morrisons_parser.py"
        )
    df = pd.read_csv(path, low_memory=False)
    rpt = DataQualityReport(rows_raw=len(df))

    # 1. harga valid
    rpt.null_prices = int(df["price"].isna().sum())
    df = df[df["price"].notna()].copy()

    # 2. dedupe
    before = len(df)
    df = df.drop_duplicates(subset="product_id").copy()
    rpt.duplicate_products = before - len(df)

    # 3. fokus kategori retail
    df = df[df["cat1"].isin(RETAIL_CATS)].copy()

    # 4. brand
    df["brand"] = (df["brand"].astype(str).str.strip()
                   .str.replace(r"\s+", " ", regex=True))
    df.loc[df["brand"].isin(["", "nan", "None"]), "brand"] = "Unbranded"
    rpt.missing_brand_pct = round(
        (df["brand"] == "Unbranded").mean() * 100, 1)

    # 5. metrik turunan
    df["price"] = df["price"].astype(float)
    df["effective_price"] = df["effective_price"].astype(float)
    # tier harga relatif terhadap median kategori
    cat_med = df.groupby("cat1")["effective_price"].transform("median")
    df["price_index"] = (df["effective_price"] / cat_med).round(3)
    df["brand_tier"] = np.where(
        df["price_index"] >= 1.15, "Premium",
        np.where(df["price_index"] <= 0.85, "Value", "Mainstream"))

    # nilai ekonomis: harga per 100g dari unit price
    df["value_band"] = pd.cut(
        df["price_per_100g"],
        bins=[0, 0.5, 1.0, 2.0, 5.0, np.inf],
        labels=["<£0.50/100g", "£0.50-1", "£1-2", "£2-5", ">£5/100g"])

    rpt.rows_clean = len(df)
    rpt.missing_rating_pct = round(df["rating"].isna().mean() * 100, 1)

    rpt.notes.append(
        f"{rpt.duplicate_products} produk duplikat (SKU sama) dihapus.")
    rpt.notes.append(
        f"{rpt.missing_rating_pct}% produk belum punya rating "
        "(analisis rating memakai subset yang tersedia).")
    rpt.notes.append(
        "Harga promo & diskon dipulihkan dari field teks 'others3/4/5'.")
    return df, rpt


# ===========================================================================
# 2. INSIGHT: PRICING
# ===========================================================================
def price_summary_by_category(df: pd.DataFrame) -> pd.DataFrame:
    g = df.groupby("cat1")["effective_price"]
    out = pd.DataFrame({
        "products": g.count(),
        "median_price": g.median().round(2),
        "mean_price": g.mean().round(2),
        "p10": g.quantile(0.10).round(2),
        "p90": g.quantile(0.90).round(2),
    })
    out["price_spread_pct"] = (
        (out["p90"] - out["p10"]) / out["median_price"] * 100).round(0)
    return out.sort_values("median_price", ascending=False)


def promo_analysis(df: pd.DataFrame) -> pd.DataFrame:
    g = df.groupby("cat1")
    out = pd.DataFrame({
        "products": g.size(),
        "promo_count": g["is_promo"].sum(),
        "promo_rate_pct": (g["is_promo"].mean() * 100).round(1),
        "avg_discount_pct": g["discount_pct"].apply(
            lambda s: round(s.dropna().mean(), 1) if s.notna().any() else 0.0),
    })
    return out.sort_values("promo_rate_pct", ascending=False)


def brand_positioning(df: pd.DataFrame, min_products: int = 10) -> pd.DataFrame:
    """Price index brand vs median kategori-nya (>1 premium, <1 value)."""
    g = df.groupby("brand")["price_index"]
    out = pd.DataFrame({"products": g.count(),
                        "price_index": g.median().round(3)})
    out = out[out["products"] >= min_products]
    out["positioning"] = np.where(
        out["price_index"] >= 1.15, "Premium",
        np.where(out["price_index"] <= 0.85, "Value", "Mainstream"))
    out["avg_rating"] = df.groupby("brand")["rating"].median().round(2)
    return out.sort_values("price_index", ascending=False)


def value_for_money(df: pd.DataFrame, min_reviews: int = 10) -> pd.DataFrame:
    """
    Produk dengan rating tinggi TAPI harga-per-100g murah = 'value winners'.
    Metrik inti untuk rekomendasi konsumen / private-label.
    """
    sub = df[df["reviews"] >= min_reviews].dropna(
        subset=["price_per_100g", "rating"]).copy()
    # skor: rating tinggi & harga rendah -> tinggi
    price_r = sub["price_per_100g"].rank(pct=True)
    rating_r = sub["rating"].rank(pct=True)
    sub["value_score"] = ((rating_r * 0.6) + ((1 - price_r) * 0.4)).round(3)
    cols = ["brand", "name", "cat1", "effective_price", "price_per_100g",
            "rating", "reviews", "value_score"]
    return sub.sort_values("value_score", ascending=False)[cols].head(25)


# ===========================================================================
# 3. INSIGHT: ASSORTMENT
# ===========================================================================
def category_portfolio(df: pd.DataFrame) -> pd.DataFrame:
    g = df.groupby("cat1")
    out = pd.DataFrame({
        "sku_count": g.size(),
        "brand_count": g["brand"].nunique(),
        "avg_price": g["effective_price"].mean().round(2),
    })
    out["sku_share_pct"] = (out["sku_count"]/out["sku_count"].sum()*100).round(1)
    out["brand_density"] = (out["sku_count"]/out["brand_count"]).round(1)
    return out.sort_values("sku_count", ascending=False)


def brand_leaderboard(df: pd.DataFrame, top_n: int = 20) -> pd.DataFrame:
    g = df.groupby("brand")
    out = pd.DataFrame({
        "sku_count": g.size(),
        "categories": g["cat1"].nunique(),
        "avg_price": g["effective_price"].mean().round(2),
        "avg_rating": g["rating"].median().round(2),
        "promo_rate_pct": (g["is_promo"].mean()*100).round(1),
    })
    return out.sort_values("sku_count", ascending=False).head(top_n)


def own_brand_opportunity(df: pd.DataFrame, top_n: int = 12) -> pd.DataFrame:
    """
    Kategori di mana brand premium mendominasi (share SKU tinggi) TAPI
    ada brand value -> peluang Morrisons own-brand menekan harga.
    """
    df = df.assign(is_prem=df["brand_tier"] == "Premium",
                   is_val=df["brand_tier"] == "Value")
    g = df.groupby("cat1")
    out = pd.DataFrame({
        "skus": g.size(),
        "premium_share_pct": (g["is_prem"].mean()*100).round(1),
        "value_share_pct": (g["is_val"].mean()*100).round(1),
        "median_price": g["effective_price"].median().round(2),
    })
    out["own_brand_gap"] = (out["premium_share_pct"]
                            - out["value_share_pct"]).round(1)
    return out.sort_values("own_brand_gap", ascending=False).head(top_n)


# ===========================================================================
# 4. INSIGHT: PRODUCT / RATING SIGNALS
# ===========================================================================
def rating_vs_price(df: pd.DataFrame) -> dict:
    sub = df.dropna(subset=["rating"]).copy()
    sub["quartile"] = pd.qcut(sub["effective_price"], 4,
                              labels=["Q1 termurah", "Q2", "Q3", "Q4 termahal"],
                              duplicates="drop")
    by_q = sub.groupby("quartile", observed=True)["rating"].agg(
        ["median", "count"]).round(2)
    corr = sub["effective_price"].corr(sub["rating"], method="spearman")
    return {
        "spearman_corr": round(float(corr), 3),
        "rating_by_price_quartile": by_q,
        "interpretation": (
            "Tidak ada hubungan kuat antara harga & rating"
            if abs(corr) < 0.15 else
            ("Produk lebih mahal cenderung dinilai lebih baik"
             if corr > 0 else "Produk lebih mahal cenderung dinilai lebih buruk")),
    }


def review_engagement(df: pd.DataFrame, top_n: int = 15) -> pd.DataFrame:
    """Brand dengan total review terbanyak = brand awareness tertinggi."""
    g = df.groupby("brand")
    out = pd.DataFrame({
        "total_reviews": g["reviews"].sum(),
        "rated_skus": g["rating"].count(),
        "avg_rating": g["rating"].median().round(2),
    })
    out = out[out["total_reviews"] > 0]
    return out.sort_values("total_reviews", ascending=False).head(top_n)


def description_completeness(df: pd.DataFrame) -> pd.DataFrame:
    """Kelengkapan konten per kategori (SEO/konversi signal)."""
    g = df.groupby("cat1")
    out = pd.DataFrame({
        "products": g.size(),
        "with_description_pct": (g["desc_len"].apply(lambda s: (s > 0).mean()*100)).round(1),
        "avg_desc_len": g["desc_len"].mean().round(0),
    })
    return out.sort_values("with_description_pct")


# ===========================================================================
# 5. EXPORT
# ===========================================================================
def save_table(df: pd.DataFrame, name: str) -> Path:
    out = Path(__file__).resolve().parent.parent / "reports" / "tables"
    out.mkdir(parents=True, exist_ok=True)
    fp = out / f"{name}.csv"
    df.to_csv(fp)
    return fp


if __name__ == "__main__":
    pd.set_option("display.width", 160)
    df, rpt = load_and_clean()
    print("=" * 72)
    print("MORRISONS UK — MARKET INTELLIGENCE SNAPSHOT")
    print("=" * 72)
    print(f"\n[Data Quality]")
    for k, v in rpt.as_dict().items():
        print(f"   {k:28}: {v}")
    for n in rpt.notes:
        print(f"   - {n}")

    print("\n[Pricing by Category]")
    print(price_summary_by_category(df).to_string())

    print("\n[Promo Rate by Category]")
    print(promo_analysis(df).to_string())

    print("\n[Brand Positioning — Top 8 Premium]")
    print(brand_positioning(df).head(8).to_string())

    print("\n[Own-Brand Opportunity]")
    print(own_brand_opportunity(df).to_string())

    print("\n[Rating vs Price]")
    rp = rating_vs_price(df)
    print(f"   Spearman = {rp['spearman_corr']} ({rp['interpretation']})")
    print(rp["rating_by_price_quartile"].to_string())

    print("\n[Top Value-for-Money Products]")
    print(value_for_money(df).head(8).to_string())
