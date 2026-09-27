"""
morrisons_parser.py
====================
Mengubah output MENTAH scraper Morrisons (60 kolom mentah, banyak nilai
ter-embed dalam string) menjadi DataFrame bersih siap-analisis.

KENAPA PARSER TERPISAH?
-----------------------
Data mentah menyimpan informasi penting di dalam STRING, bukan kolom:
  Price          -> "£3.20"                          (mata uang disematkan)
  others1        -> "Unit Price: £8.00 per kg"       (harga satuan)
  others2        -> "Rating: 4.6 (12 reviews)"       (rating + jumlah review)
  others3/4/5    -> "Promotions: Now £1.75, Was £2"  (promo multi-tipe)
  product_description1 -> HTML deskripsi

Menaruh logika parsing di SATU modul teruji membuat seluruh pipeline
analisis dapat dikonsumsi ulang & di-unit-test. Ini pola "bronze -> silver".

Jalankan langsung untuk smoke test:
    python src/morrisons_parser.py
"""

from __future__ import annotations

import html
import re
from pathlib import Path

import numpy as np
import pandas as pd

RAW_PATH = Path(__file__).resolve().parent.parent / "data" / "raw" / "morrisons_products.csv"
PROC_DIR = Path(__file__).resolve().parent.parent / "data" / "processed"

# ---------------------------------------------------------------------------
# Regex (dikompilasi sekali -> lebih cepat untuk 36k baris)
# ---------------------------------------------------------------------------
RE_PRICE = re.compile(r"£\s*([0-9]+(?:\.[0-9]+)?)")
RE_RATING = re.compile(r"Rating:\s*([0-9](?:\.[0-9])?)\s*\((\d+)\s*reviews?\)", re.I)
RE_UNIT_PRICE = re.compile(r"Unit Price:\s*£\s*([0-9]+(?:\.[0-9]+)?)\s*per\s*(\w+)", re.I)
# "Now £1.75, Was £2"  atau  "Was £2, Now £1.75"
RE_NOW_WAS = re.compile(r"Now\s*£\s*([0-9.]+)\s*,?\s*Was\s*£\s*([0-9.]+)", re.I)
RE_BUY_N_FOR = re.compile(r"Buy\s*(\d+)\s*for\s*£\s*([0-9.]+)", re.I)
RE_TAG = re.compile(r"<[^>]+>")
RE_WS = re.compile(r"\s+")


def _to_float(s: str) -> float:
    m = RE_PRICE.search(s) or RE_NOW_WAS.search(s)
    if not m:
        return np.nan
    return float(m.group(1))


def parse_price(v) -> float:
    """'£3.20' -> 3.20 ; NaN bila kosong."""
    if pd.isna(v):
        return np.nan
    m = RE_PRICE.search(str(v))
    return float(m.group(1)) if m else np.nan


def parse_rating(s) -> float:
    """'Rating: 4.6 (12 reviews)' -> 4.6"""
    if pd.isna(s):
        return np.nan
    m = RE_RATING.search(str(s))
    return float(m.group(1)) if m else np.nan


def parse_review_count(s) -> float:
    if pd.isna(s):
        return np.nan
    m = RE_RATING.search(str(s))
    return float(m.group(2)) if m else np.nan


def parse_unit_price(s):
    """'Unit Price: £8.00 per kg' -> (8.00, 'kg')"""
    if pd.isna(s):
        return (np.nan, None)
    m = RE_UNIT_PRICE.search(str(s))
    if not m:
        return (np.nan, None)
    return (float(m.group(1)), m.group(2).lower())


def parse_promo(row) -> tuple[bool, float, float, str]:
    """
    Promosi tersebar di others3/others4/others5 dengan banyak format:
       'Promotions: Now £1.75, Was £2'    -> Now = harga BAYAR, Was = harga lama
       'Promotions: Buy 2 for £4'         -> multi-buy
       'Promotions: Price Match'          -> tanpa angka

    PENTING: kolom `Price` utama pada data mentah = harga TAMPIL (sering = "Was").
    Jadi harga promo nyata diambil dari kata "Now".

    Mengembalikan: (is_promo, promo_price, was_price, promo_type)
    """
    texts = [str(row.get(f"others{i}")) for i in range(3, 6)]
    blob = " | ".join(t for t in texts if t and t != "nan")
    if "Promotions:" not in blob:
        return (False, np.nan, np.nan, "")

    if m := RE_NOW_WAS.search(blob):
        return (True, float(m.group(1)), float(m.group(2)), "price_cut")
    if m := RE_BUY_N_FOR.search(blob):
        n, tot = int(m.group(1)), float(m.group(2))
        return (True, round(tot / n, 2), np.nan, f"multibuy_{n}for")
    if "price match" in blob.lower():
        return (True, np.nan, np.nan, "price_match")
    return (True, np.nan, np.nan, "other")


def parse_dietary(row) -> str:
    """Ekstrak tag dietary dari others2..others5 (contoh 'Suitable for vegetarians')."""
    tags = []
    for i in range(2, 6):
        t = str(row.get(f"others{i}", ""))
        m = re.search(r"Dietary/Lifestyle:\s*([^|]+)", t, re.I)
        if m:
            tags.append(m.group(1).strip())
    return " | ".join(dict.fromkeys(tags))  # dedupe, jaga urutan


def clean_description(html_str) -> str:
    """Buang tag HTML + decode entity -> teks bersih."""
    if pd.isna(html_str):
        return ""
    txt = RE_TAG.sub(" ", str(html_str))
    txt = html.unescape(txt)
    return RE_WS.sub(" ", txt).strip()


# ---------------------------------------------------------------------------
# PIPELINE UTAMA
# ---------------------------------------------------------------------------
def parse_raw(path: Path | None = None) -> pd.DataFrame:
    """Baca CSV mentah -> DataFrame 'silver' dengan kolom hasil parsing."""
    path = path or RAW_PATH
    if not path.exists():
        raise FileNotFoundError(
            f"Data mentah tidak ditemukan: {path}\n"
            "Ekstrak dulu morrisons_products.rar ke data/raw/."
        )

    df = pd.read_csv(path, dtype=str, low_memory=False)
    df.columns = [c.strip() for c in df.columns]

    out = pd.DataFrame(index=df.index)
    # --- identitas & metadata ---
    out["product_id"] = df.get("shop_product_id", pd.Series(dtype=str))
    out["name"] = df.get("Name", pd.Series(dtype=str)).astype(str).str.strip()
    out["brand"] = df.get("Brand", pd.Series(dtype=str)).astype(str).str.strip()
    out["url"] = df.get("Product_URL", pd.Series(dtype=str))
    out["cat1"] = df.get("cat1", pd.Series(dtype=str)).astype(str).str.strip()
    out["cat2"] = df.get("cat2", pd.Series(dtype=str)).astype(str).str.strip()
    out["category_path"] = df.get("category_path", pd.Series(dtype=str))

    # --- harga ---
    out["price"] = df.get("Price", pd.Series(dtype=str)).map(parse_price)

    # --- others1 -> unit price + satuan ---
    if "others1" in df.columns:
        ups = df["others1"].map(parse_unit_price)
        out["unit_price"] = [u[0] for u in ups]
        out["unit_basis"] = [u[1] for u in ups]
    else:
        out["unit_price"] = np.nan
        out["unit_basis"] = None

    # --- others2 -> rating + reviews ---
    r2 = df.get("others2", pd.Series(dtype=str)).astype(str)
    out["rating"] = r2.map(parse_rating)
    out["reviews"] = r2.map(parse_review_count)

    # --- others3..5 -> promo ---
    promos = df.apply(parse_promo, axis=1)
    out["is_promo"] = [p[0] for p in promos]
    out["promo_price"] = [p[1] for p in promos]
    out["was_price"] = [p[2] for p in promos]
    out["promo_type"] = [p[3] for p in promos]

    # --- deskripsi ---
    out["description"] = df.get("product_description1",
                                pd.Series(dtype=str)).map(clean_description)
    out["desc_len"] = out["description"].str.len()
    out["dietary"] = df.apply(parse_dietary, axis=1)

    out["crawl_timestamp"] = df.get("crawl_timestamp", pd.Series(dtype=str))

    # ---------------- kolom turunan (golden) ----------------
    # effective_price = harga yang benar-benar dibayar konsumen.
    # Bila ada promo harga-turun, pakai promo_price; selain itu pakai price.
    out["effective_price"] = np.where(
        out["promo_price"].notna(), out["promo_price"], out["price"]
    )
    # baseline pembanding: was_price bila ada, jika tidak price
    out["list_price"] = np.where(
        out["was_price"].notna(), out["was_price"], out["price"]
    )
    out["discount_pct"] = np.where(
        out["is_promo"] & out["was_price"].notna() & (out["was_price"] > 0),
        ((out["was_price"] - out["effective_price"]) / out["was_price"] * 100).round(1),
        np.nan,
    )
    # price per unit ternormalisasi ke per-100g (kg -> /10) untuk value analysis
    out["price_per_100g"] = np.where(
        out["unit_basis"] == "kg", out["unit_price"] / 10,
        np.where(out["unit_basis"].isin(["100g", "g"]), out["unit_price"], np.nan),
    )
    return out


def save_processed(df: pd.DataFrame, name: str = "morrisons_clean.csv") -> Path:
    PROC_DIR.mkdir(parents=True, exist_ok=True)
    fp = PROC_DIR / name
    df.to_csv(fp, index=False)
    return fp


# ---------------------------------------------------------------------------
if __name__ == "__main__":
    print("Parsing data mentah Morrisons...")
    df = parse_raw()
    print(f"  Produk       : {len(df):,}")
    print(f"  Kolom output : {df.shape[1]}")
    print(f"  Harga valid  : {df['price'].notna().sum():,} "
          f"({df['price'].notna().mean()*100:.1f}%)")
    print(f"  Rating valid : {df['rating'].notna().sum():,} "
          f"({df['rating'].notna().mean()*100:.1f}%)")
    print(f"  Promo aktif  : {df['is_promo'].sum():,} "
          f"({df['is_promo'].mean()*100:.1f}%)")
    print(f"  Unit price   : {df['unit_price'].notna().sum():,}")
    print(f"  Deskripsi    : {(df['desc_len']>0).sum():,}")
    print(f"  Kategori     : {df['cat1'].nunique()}")
    print(f"  Brand        : {df['brand'].nunique()}")

    fp = save_processed(df)
    print(f"\n[OK] Disimpan: {fp}")

    print("\n=== Contoh hasil parsing ===")
    cols = ["brand", "name", "price", "promo_price", "discount_pct",
            "rating", "reviews", "unit_price", "unit_basis", "promo_type"]
    print(df[cols].head(8).to_string())
