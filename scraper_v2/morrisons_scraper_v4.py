"""
morrisons_scraper_v4.py
========================
Scraper BARU untuk Morrisons (2026) — hasil reverse engineering endpoint baru.

LATAR BELAKANG (kenapa scraper lama tidak jalan lagi):
  Endpoint lama  : GET /api/webproductpagews/v6/product-pages
                   -> KINI mengembalikan decoratedProducts: [] (kosong).
  Endpoint baru  : PUT /api/webproductpagews/v6/products
                   -> body: JSON list of product UUIDs
                   -> response: {products:[{productId, retailerProductId, name,
                      brand, packSizeDescription, price, unitPrice, promotions,
                      promoPrice, available, ...}]}
  Header wajib   : x-csrf-token, client-route-id, page-view-id
                   (dibuat oleh JS browser; nilainya berubah tiap sesi).
  Pemicu         : PUT dipanggil saat infinite-scroll (tiap ~24 produk).

STRATEGI (paling andal): biarkan BROWSER melakukan pemuatan, kita hanya
MENYADAP (intercept) setiap response PUT /v6/products. Tidak perlu menebak
token/parameter — browser yang menghitungnya, kita cukup membaca hasilnya.

Output: CSV lokal (TANPA Google Sheets). Format kolom DIPERKAYA dari respons
        baru, lalu dipetakan agar kompatibel dengan pipeline analisis lama.

Jalankan:
    python morrisons_scraper_v4.py test     # 1 kategori, debug
    python morrisons_scraper_v4.py          # scrape semua kategori
"""

from __future__ import annotations

import csv
import json
import random
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

from playwright.sync_api import sync_playwright, TimeoutError as PWTimeout

# ---------------------------------------------------------------------------
# KONFIGURASI
# ---------------------------------------------------------------------------
BASE = "https://groceries.morrisons.com"
OUT_DIR = Path(__file__).resolve().parent / "output"
OUT_CSV = OUT_DIR / "morrisons_products_latest.csv"
OUT_JSON = OUT_DIR / "morrisons_raw_latest.json"

# 10 kategori (id kategori dari riset; URL memakai /categories/{slug}/{retailerId})
CATEGORIES = {
    "Food Cupboard":                 "food-cupboard/102705",
    "Treats & Snacks":               "treats-snacks/193648",
    "Dietary & Lifestyle Foods":     "dietary-lifestyle-foods/192319",
    "World Foods":                   "world-foods/182137",
    "Drinks":                        "drinks/103644",
    "Beer, Wines & Spirits":         "beer-wines-spirits/103120",
    "Toiletries & Beauty":           "toiletries-beauty/102838",
    "Health, Wellbeing & Medicines": "health-wellbeing-medicines/103497",
    "Baby & Toddler":                "baby-toddler/177598",
    "Household":                     "household/102063",
}

SCROLL_STEPS = 60          # banyak scroll per kategori
SCROLL_WAIT_MS = 1800      # jeda antar scroll
IDLE_STOP = 4              # berhenti bila N scroll berturut tanpa produk baru
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36")

# ---------------------------------------------------------------------------
# OUTPUT COLUMNS (diperkaya + kompatibel pipeline lama)
# ---------------------------------------------------------------------------
COLUMNS = [
    "crawl_timestamp", "shop_id", "shop_name", "shop_country", "shop_language",
    "shop_currency", "shop_product_id", "retailer_product_id",
    "Brand", "Name", "pack_size",
    "Price", "promo_price", "on_promo", "promo_description",
    "unit_price_amount", "unit_price_unit",
    "rating", "reviews",
    "available", "product_type",
    "cat1", "cat2", "cat3", "cat4", "category_path",
    "dietary_tags",
    "Product_URL", "image_url",
]


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


# ---------------------------------------------------------------------------
# INTI: sadap PUT /v6/products selama scroll satu kategori
# ---------------------------------------------------------------------------
def scrape_category(page, cat_name: str, slug: str, verbose: bool = True) -> list[dict]:
    """Muat satu kategori & sadap semua produk dari response PUT."""
    url = f"{BASE}/categories/{slug}"
    products: dict[str, dict] = {}

    def on_response(resp):
        if "/api/webproductpagews/v6/products" not in resp.url:
            return
        if resp.request.method != "PUT":
            return
        try:
            data = resp.json()
        except Exception:
            return
        for p in (data.get("products") or []):
            pid = p.get("productId")
            if pid:
                products[pid] = p

    page.on("response", on_response)

    if verbose:
        print(f"  [{cat_name}] buka {url}")
    try:
        page.goto(url, wait_until="domcontentloaded", timeout=60000)
    except PWTimeout:
        print(f"  [{cat_name}] TIMEOUT saat buka — skip")
        return []
    page.wait_for_timeout(3500)

    idle = 0
    last = len(products)
    for i in range(SCROLL_STEPS):
        page.mouse.wheel(0, random.randint(4000, 6000))
        page.wait_for_timeout(SCROLL_WAIT_MS)
        now = len(products)
        if now == last:
            idle += 1
            if idle >= IDLE_STOP:
                break
        else:
            idle = 0
        last = now
        if verbose and (i % 5 == 0):
            print(f"     scroll {i+1:>2}: {now} produk")

    page.remove_listener("response", on_response)
    if verbose:
        print(f"  [{cat_name}] SELESAI: {len(products)} produk unik")
    return list(products.values())


# ---------------------------------------------------------------------------
# MAP produk mentah -> baris CSV
# ---------------------------------------------------------------------------
def to_row(p: dict, cat: str, ts: str) -> dict:
    price = (p.get("price") or {}).get("amount")
    promo = (p.get("promoPrice") or {})
    promo_amt = promo.get("amount") if isinstance(promo, dict) else None
    up = (p.get("unitPrice") or {})
    up_price = (up.get("price") or {}).get("amount") if isinstance(up, dict) else None
    promos = p.get("promotions") or []
    promo_desc = promos[0].get("description") if promos else None
    rpid = p.get("retailerProductId") or ""

    # rating & review count (ada di ratingSummary)
    rs = p.get("ratingSummary") or {}
    rating = rs.get("overallRating") if isinstance(rs, dict) else None
    reviews = rs.get("count") if isinstance(rs, dict) else None

    # kategori lengkap (categoryPath = list nama)
    cpath = p.get("categoryPath") or []
    def cp(i):
        return cpath[i] if len(cpath) > i else ""

    # dietary/lifestyle (iconAttributes)
    icons = p.get("iconAttributes") or []
    dietary = ", ".join(
        str(i.get("label")) for i in icons
        if isinstance(i, dict) and i.get("label")) if icons else ""

    # gambar
    img = ""
    imgs = p.get("images") or []
    if imgs and isinstance(imgs[0], dict):
        img = imgs[0].get("src") or ""
    if not img:
        img = (p.get("image") or {}).get("src") if isinstance(p.get("image"), dict) else ""

    return {
        "crawl_timestamp": ts,
        "shop_id": "morrisons-uk-001",
        "shop_name": "Morrisons",
        "shop_country": "United Kingdom",
        "shop_language": "en-GB",
        "shop_currency": "GBP",
        "shop_product_id": p.get("productId"),
        "retailer_product_id": rpid,
        "Brand": p.get("brand") or "",
        "Name": p.get("name") or "",
        "pack_size": p.get("packSizeDescription") or "",
        "Price": price,
        "promo_price": promo_amt,
        "on_promo": bool(promo_amt),
        "promo_description": promo_desc or "",
        "unit_price_amount": up_price,
        "unit_price_unit": up.get("unitName") if isinstance(up, dict) else "",
        "rating": rating,
        "reviews": reviews,
        "available": p.get("available"),
        "product_type": p.get("type") or "",
        "cat1": cp(0) or cat,
        "cat2": cp(1),
        "cat3": cp(2),
        "cat4": cp(3),
        "category_path": " > ".join(str(x) for x in cpath),
        "dietary_tags": dietary,
        "Product_URL": f"{BASE}/products/{rpid}" if rpid else "",
        "image_url": img or (f"{BASE}/productimages/540/{rpid}.jpg" if rpid else ""),
    }


# ---------------------------------------------------------------------------
# ORKESTRASI
# ---------------------------------------------------------------------------
def run(categories: dict[str, str], headless: bool = True) -> list[dict]:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    ts = utc_now()
    all_rows: list[dict] = []
    raw: dict[str, list] = {}

    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=headless)
        ctx = browser.new_context(locale="en-GB", user_agent=UA,
                                  viewport={"width": 1400, "height": 1000})
        page = ctx.new_page()
        for cat, slug in categories.items():
            prods = scrape_category(page, cat, slug)
            raw[cat] = prods
            for p in prods:
                all_rows.append(to_row(p, cat, ts))
            # simpan progres
            with open(OUT_CSV, "w", newline="", encoding="utf-8-sig") as f:
                w = csv.DictWriter(f, fieldnames=COLUMNS)
                w.writeheader()
                w.writerows(all_rows)
        browser.close()

    OUT_JSON.write_text(json.dumps(raw, ensure_ascii=False), encoding="utf-8")
    return all_rows


def regen_from_json():
    """Bangun ulang CSV dari JSON mentah yang sudah tersimpan (tanpa scrape ulang)."""
    if not OUT_JSON.exists():
        raise SystemExit(f"JSON tidak ada: {OUT_JSON}")
    raw = json.loads(OUT_JSON.read_text(encoding="utf-8"))
    ts = utc_now()
    rows = []
    for cat, prods in raw.items():
        for p in prods:
            rows.append(to_row(p, cat, ts))
    # dedup by product_id (produk unik; produk bisa muncul di >1 kategori)
    seen = {}
    for r in rows:
        pid = r["shop_product_id"]
        if pid not in seen:
            seen[pid] = r
    deduped = list(seen.values())
    with open(OUT_CSV, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=COLUMNS)
        w.writeheader()
        w.writerows(deduped)
    print(f"regen: {len(rows)} baris -> {len(deduped)} produk unik")
    print(f"CSV: {OUT_CSV}")
    # ringkas
    import statistics
    ratings = [float(r["rating"]) for r in deduped if r.get("rating")]
    print(f"rating tersedia: {len(ratings)} ({len(ratings)/len(deduped)*100:.1f}%)")
    promos = sum(1 for r in deduped if r["on_promo"])
    print(f"promo: {promos} ({promos/len(deduped)*100:.1f}%)")
    return deduped


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else "all"
    if mode == "from-json":
        print("=== RE-GENERATE CSV dari JSON mentah ===")
        regen_from_json()
        return
    if mode == "test":
        cats = {"Food Cupboard": CATEGORIES["Food Cupboard"]}
        print("=== MODE TEST (1 kategori) ===")
        rows = run(cats, headless=True)
    else:
        print("=== MODE FULL (10 kategori) ===")
        rows = run(CATEGORIES, headless=True)

    print(f"\n{'='*60}")
    print(f"TOTAL: {len(rows)} produk")
    print(f"CSV : {OUT_CSV}")
    print(f"JSON: {OUT_JSON}")
    if rows:
        cats = {}
        for r in rows:
            cats[r["cat1"]] = cats.get(r["cat1"], 0) + 1
        print("\nPer kategori:")
        for c, n in cats.items():
            print(f"  {c:<32} {n:>5}")
        promos = sum(1 for r in rows if r["on_promo"])
        print(f"\nPromo: {promos} ({promos/len(rows)*100:.1f}%)")
        with_price = sum(1 for r in rows if r["Price"])
        print(f"Punya harga: {with_price} ({with_price/len(rows)*100:.1f}%)")
        with_brand = sum(1 for r in rows if r["Brand"])
        print(f"Punya brand: {with_brand} ({with_brand/len(rows)*100:.1f}%)")


if __name__ == "__main__":
    main()
