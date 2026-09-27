"""
adapt_new_data.py
=================
Mengubah output scraper BARU (morrisons_products_latest.csv) menjadi skema
yang dipakai pipeline analisis (`morrisons_clean.csv`), sehingga seluruh
analisis/chart/dashboard/Tableau bisa dijalankan dari data TERBARU tanpa
mengubah modul lain.

PERBEDAAN SKEMA:
  Lama (parser HTML)  : price "£3.20" (string), promo/rating di field teks
  Baru (API v6)       : price & promoPrice sudah angka terpisah, unit price
                        terpisah, promotions[] terstruktur  -> lebih bersih.

Karena data baru SUDAH bersih, adapter ini langsung MEMETAKAN kolom, bukan
mem-parse string seperti morrisons_parser (dipertahankan untuk kompatibilitas).

Jalankan: python src/adapt_new_data.py <path_csv_baru>
          (tanpa argumen -> pakai path default)
"""

from __future__ import annotations

import shutil
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_SRC = ROOT.parent / "_scraper-work" / "new" / "output" / "morrisons_products_latest.csv"
OUT = ROOT / "data" / "processed" / "morrisons_clean.csv"


def adapt(src: Path) -> pd.DataFrame:
    df = pd.read_csv(src, dtype=str, low_memory=False)
    out = pd.DataFrame(index=df.index)

    out["product_id"] = df.get("shop_product_id")
    out["name"] = df.get("Name", pd.Series(dtype=str)).fillna("").str.strip()
    out["brand"] = df.get("Brand", pd.Series(dtype=str)).fillna("").str.strip()
    out["url"] = df.get("Product_URL", pd.Series(dtype=str)).fillna("")
    out["cat1"] = df.get("cat1", pd.Series(dtype=str)).fillna("").str.strip()
    out["cat2"] = df.get("cat2", pd.Series(dtype=str)).fillna("").str.strip()
    out["category_path"] = df.get("category_path", pd.Series(dtype=str)).fillna("")

    # harga
    out["price"] = pd.to_numeric(df.get("Price"), errors="coerce")
    promo = pd.to_numeric(df.get("promo_price"), errors="coerce")
    out["effective_price"] = promo.where(promo.notna(), out["price"])
    out["list_price"] = out["price"]
    out["discount_pct"] = np.where(
        promo.notna() & (out["price"] > 0),
        ((out["price"] - promo) / out["price"] * 100).round(1), np.nan)

    # promo
    out["is_promo"] = df.get("on_promo", pd.Series(dtype=str)).map(
        lambda v: str(v).strip().lower() in ("true", "1", "yes"))
    out["promo_price"] = promo
    out["was_price"] = np.where(promo.notna(), out["price"], np.nan)
    out["promo_type"] = df.get("promo_description", pd.Series(dtype=str)).fillna("")

    # unit price
    out["unit_price"] = pd.to_numeric(df.get("unit_price_amount"), errors="coerce")
    unit_raw = df.get("unit_price_unit", pd.Series(dtype=str)).fillna("")
    out["unit_basis"] = unit_raw.str.replace("PER_1", "", regex=False).str.lower()
    out["unit_basis"] = out["unit_basis"].replace("", np.nan)
    out["price_per_100g"] = np.where(
        out["unit_basis"] == "kg", out["unit_price"] / 10,
        np.where(out["unit_basis"].isin(["100g", "g"]), out["unit_price"], np.nan))

    # RATING — tersedia di endpoint baru (ratingSummary)
    out["rating"] = pd.to_numeric(df.get("rating"), errors="coerce")
    out["reviews"] = pd.to_numeric(df.get("reviews"), errors="coerce")

    # deskripsi tidak dikirim endpoint listing; dietary tags ADA
    out["description"] = ""
    out["desc_len"] = 0
    out["dietary"] = df.get("dietary_tags", pd.Series(dtype=str)).fillna("")
    out["crawl_timestamp"] = df.get("crawl_timestamp", pd.Series(dtype=str)).fillna("")

    before = len(out)
    out = out[out["price"].notna()].copy()
    print(f"  Baris tanpa harga dibuang: {before - len(out)}")
    rated = out["rating"].notna().mean() * 100
    print(f"  Rating tersedia: {rated:.1f}%")
    return out


def main():
    src = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_SRC
    if not src.exists():
        raise SystemExit(f"Sumber tidak ada: {src}")
    print(f"Mengadaptasi data baru: {src}")
    df = adapt(src)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUT, index=False)
    print(f"  [OK] {OUT}  ({len(df):,} baris, {df.shape[1]} kolom)")
    print(f"  Kategori: {df['cat1'].nunique()} | Brand: {df['brand'].nunique():,}")
    print(f"  Harga: £{df['effective_price'].min():.2f} – £{df['effective_price'].max():.2f} "
          f"(median £{df['effective_price'].median():.2f})")
    print(f"  Promo: {df['is_promo'].mean()*100:.1f}%")


if __name__ == "__main__":
    main()
