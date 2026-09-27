"""
generate_sample_data.py
=======================
Membuat dataset SAMPEL realistis yang meniru output `morrisons-product-scraper`
(15.000+ produk, 57 kolom per produk).

KENAPA ADA FILE INI?
--------------------
Data asli hasil scraping bersifat klien/private dan tidak di-commit ke repo publik.
File ini memungkinkan siapa pun (recruiter, reviewer) menjalankan seluruh analisis
END-TO-END tanpa perlu akses data asli. Saat data asli tersedia, cukup ganti file
CSV-nya di data/raw/ dan notebook analisis langsung jalan tanpa perubahan kode.

Catatan: skema & distribusi dibuat mendekati realistis (harga grocery, brand UK,
kategori, nutrisi) agar insight yang dihasilkan bermakna secara statistik.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from pathlib import Path

RNG = np.random.default_rng(seed=42)

# ---------------------------------------------------------------------------
# Konfigurasi domain (supermarket grocery UK)
# ---------------------------------------------------------------------------
OUT_PATH = Path(__file__).resolve().parent.parent / "data" / "raw" / "morrisons_products_sample.csv"
N_PRODUCTS = 15_000

SHOP = {
    "shop_id": "morrisons-uk-001",
    "shop_name": "Morrisons",
    "shop_country": "United Kingdom",
    "shop_language": "en-GB",
    "shop_currency": "GBP",
}

# 10 kategori sesuai dokumentasi repo, dengan rentang harga khas & jumlah brand
CATEGORIES = {
    "Food Cupboard":                  {"cat_id": "c2fe6663-6cbf-4ed5-86f1-c306d0360dfb", "price": (0.45, 12.0), "weight": 0.22},
    "Treats & Snacks":                {"cat_id": "0a43d8e7-9ce4-47e2-880a-0dd5bbaa9b25", "price": (0.60, 8.0),  "weight": 0.14},
    "Dietary & Lifestyle Foods":      {"cat_id": "4850370a-3a5e-4956-ade7-00d0bf47783d", "price": (1.20, 15.0), "weight": 0.06},
    "World Foods":                    {"cat_id": "f4d47513-e02c-41a2-99bc-cc01763c3467", "price": (0.80, 14.0), "weight": 0.08},
    "Drinks":                         {"cat_id": "d36e4c96-e988-4e43-84e3-f1fd513f4778", "price": (0.50, 25.0), "weight": 0.13},
    "Beer, Wines & Spirits":          {"cat_id": "b182dd9d-bdfe-487e-b583-74007e5b1e69", "price": (2.50, 45.0), "weight": 0.09},
    "Toiletries & Beauty":            {"cat_id": "c1fea557-544f-4111-945b-eb8a72a99d2e", "price": (0.90, 20.0), "weight": 0.09},
    "Health, Wellbeing & Medicines":  {"cat_id": "eccda9dc-19b2-482c-bf43-e833bf5c1c0d", "price": (1.00, 18.0), "weight": 0.05},
    "Baby & Toddler":                 {"cat_id": "a5f0280a-acd2-42f9-873d-6478fac6522d", "price": (1.50, 22.0), "weight": 0.05},
    "Household":                      {"cat_id": "2bbf0ff7-f6f8-4a03-9f01-940174963086", "price": (1.00, 16.0), "weight": 0.09},
}

# Brand: sebagian "premium" (harga lebih tinggi), sebagian "value/economy"
PREMIUM_BRANDS = ["M&S", "Waitrose Own", "Bonne Maman", "Kellogg's", "Cadbury",
                  "Heinz", "Ferrero", "Nestlé", "Lurpak", "Twinings"]
VALUE_BRANDS = ["Morrisons Savers", "Everyday Value", "Stockwell", "Greens",
                "Just Essentials", "Smart Price", "Growers Select", "Woodside Farms"]
MAINSTREAM_BRANDS = ["Tesco", "Asda", "Sainsbury's", "Co-op", "Aldi", "Lidl",
                     "Walkers", "McVitie's", "Robinsons", "Yeo Valley",
                     "Rachel's", "Nairn's", "Quorn", "Ben & Jerry's"]

BRAND_TIER = (
    [(b, "premium") for b in PREMIUM_BRANDS]
    + [(b, "value") for b in VALUE_BRANDS]
    + [(b, "mainstream") for b in MAINSTREAM_BRANDS]
)

# Kata benda per kategori untuk membentuk nama produk realistis
PRODUCT_NOUNS = {
    "Food Cupboard": ["Baked Beans", "Pasta Sauce", "Cereal", "Rice", "Olive Oil",
                      "Tinned Tomatoes", "Peanut Butter", "Honey", "Flour", "Sugar",
                      "Stock Cubes", "Cous Cous", "Lentils", "Tuna", "Coffee"],
    "Treats & Snacks": ["Crisps", "Chocolate Bar", "Biscuits", "Popcorn", "Nuts",
                        "Gummy Sweets", "Cake Bars", "Crackers", "Rice Cakes", "Ice Lollies"],
    "Dietary & Lifestyle Foods": ["Oat Milk", "Gluten-Free Bread", "Vegan Cheese",
                                  "Protein Bars", "Keto Mix", "Low-Sugar Jam",
                                  "Almond Flour", "Coconut Yogurt", "Seitan", "Tofu"],
    "World Foods": ["Curry Paste", "Tortillas", "Soy Sauce", "Coconut Milk",
                    "Noodles", "Harissa", "Kimchi", "Miso Paste", "Falafel Mix", "Ramen"],
    "Drinks": ["Orange Juice", "Cola", "Sparkling Water", "Energy Drink",
               "Coffee Pods", "Green Tea", "Smoothie", "Lemonade", "Oat Drink", "Cordial"],
    "Beer, Wines & Spirits": ["Lager", "IPA", "Red Wine", "White Wine", "Gin",
                              "Vodka", "Cider", "Prosecco", "Whisky", "Rum"],
    "Toiletries & Beauty": ["Shampoo", "Conditioner", "Body Wash", "Toothpaste",
                            "Deodorant", "Face Cream", "Razor Blades", "Hand Soap",
                            "Lip Balm", "Sunscreen"],
    "Health, Wellbeing & Medicines": ["Vitamin C", "Paracetamol", "Ibuprofen",
                                      "Multivitamins", "Cough Syrup", "Antihistamine",
                                      "Omega 3", "Magnesium", "Plasters", "Probiotics"],
    "Baby & Toddler": ["Baby Wipes", "Nappies", "Baby Food Pouch", "Formula Milk",
                       "Baby Cereal", "Teething Gel", "Baby Lotion", "Bottle Steriliser",
                       "Puree", "Toddler Snacks"],
    "Household": ["Washing Up Liquid", "Laundry Pods", "Bleach", "Kitchen Roll",
                  "Bin Bags", "Surface Spray", "Toilet Roll", "Fabric Softener",
                  "Sponges", "Dishwasher Tablets"],
}

QUANTITY_RANGES = ["1 pack", "2 pack", "3 pack", "4 pack", "6 pack", "12 pack"]
DIETARY_TAGS = ["vegetarian", "vegan", "gluten-free", "organic", "low-fat",
                "sugar-free", "high-protein", "halal", "kosher"]
ALLERGENS = ["milk", "eggs", "soya", "wheat", "nuts", "peanuts", "sesame",
             "fish", "shellfish", "celery", "mustard", "sulphites"]


def _make_name(category: str, brand: str, rng) -> str:
    noun = rng.choice(PRODUCT_NOUNS[category])
    variant = rng.choice(["", "Original", "Classic", "Premium", "Light",
                          "Extra", "Organic", "Chunky", "Smooth", "400g"])
    return f"{brand} {noun} {variant}".strip()


def generate(seed: int = 42) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    cat_names = list(CATEGORIES.keys())
    weights = np.array([CATEGORIES[c]["weight"] for c in cat_names])
    weights = weights / weights.sum()
    counts = rng.multinomial(N_PRODUCTS, weights)

    rows = []
    pid = 1
    for cat, n in zip(cat_names, counts):
        meta = CATEGORIES[cat]
        lo, hi = meta["price"]
        for _ in range(int(n)):
            brand, tier = BRAND_TIER[rng.integers(0, len(BRAND_TIER))]
            # base price log-normal-ish lalu di-scale ke rentang kategori
            base = float(rng.uniform(lo, hi))
            tier_mult = {"premium": rng.uniform(1.15, 1.45),
                         "mainstream": rng.uniform(0.95, 1.12),
                         "value": rng.uniform(0.55, 0.85)}[tier]
            price = round(base * tier_mult, 2)
            # promosi acak ~18% produk
            on_promo = bool(rng.random() < 0.18)
            promo_price = round(price * rng.uniform(0.6, 0.85), 2) if on_promo else np.nan
            name = _make_name(cat, brand, rng)
            weight_g = int(rng.choice([100, 250, 400, 500, 750, 1000, 1500, 2000]))

            # nutrisi (per 100g), hanya relevan untuk makanan/minuman
            is_food = cat not in ("Toiletries & Beauty", "Household",
                                  "Health, Wellbeing & Medicines")
            def maybe(x):
                return round(float(x), 1) if is_food else np.nan

            rows.append({
                "shop_product_id": f"MRN{pid:07d}",
                "shop_id": SHOP["shop_id"],
                "shop_name": SHOP["shop_name"],
                "shop_country": SHOP["shop_country"],
                "shop_language": SHOP["shop_language"],
                "shop_currency": SHOP["shop_currency"],
                "Name": name,
                "Brand": brand,
                "Price": price,
                "promo_price": promo_price,
                "on_promo": on_promo,
                "Product_URL": f"https://groceries.morrisons.com/products/{pid:07d}",
                "category_path": f"{cat} > {rng.choice(PRODUCT_NOUNS[cat])}",
                "cat1": cat,
                "cat2": str(rng.choice(PRODUCT_NOUNS[cat])),
                "cat3": "", "cat4": "", "cat5": "",
                "Image1": f"https://cdn.morrisons.com/v3/{pid:07d}_1280x1280.jpg",
                "qty_range": str(rng.choice(QUANTITY_RANGES)),
                "min_qty": 1, "max_qty": int(rng.integers(1, 12)),
                "unit_price": round(price / (weight_g / 100), 3),  # per 100g
                "weight_g": weight_g,
                "dietary_tags": ", ".join(rng.choice(DIETARY_TAGS, size=int(rng.integers(0, 3)), replace=False)[:2]) if is_food else "",
                "allergens": ", ".join(rng.choice(ALLERGENS, size=int(rng.integers(0, 4)), replace=False)[:3]) if is_food else "",
                "energy_kcal_per_100g": maybe(rng.uniform(50, 550)),
                "fat_per_100g": maybe(rng.uniform(0.2, 30)),
                "saturates_per_100g": maybe(rng.uniform(0.1, 12)),
                "carbs_per_100g": maybe(rng.uniform(2, 75)),
                "sugars_per_100g": maybe(rng.uniform(0.5, 45)),
                "fibre_per_100g": maybe(rng.uniform(0.3, 9)),
                "protein_per_100g": maybe(rng.uniform(0.5, 25)),
                "salt_per_100g": maybe(rng.uniform(0.05, 2.5)),
                "is_organic": bool(rng.random() < 0.12),
                "country_of_origin": str(rng.choice(["UK", "UK", "UK", "EU", "EU", "Non-EU"])),
                "rating": round(float(rng.uniform(1.0, 5.0)), 1),
                "reviews_count": int(rng.integers(0, 1200)),
                "in_stock": True,
                "others1": brand if not np.isnan(price) else "",
            })
            pid += 1

    df = pd.DataFrame(rows)

    # Inject data quality issues secara sengaja (realistis!) supaya analisis
    # cleaning di notebook punya sesuatu untuk dibersihkan.
    # 1) sebagian kecil harga kosong -> akan di-drop
    null_idx = rng.choice(df.index, size=45, replace=False)
    df.loc[null_idx, "Price"] = np.nan
    # 2) rating di luar skala (data-entry error)
    df.loc[rng.choice(df.index, size=20, replace=False), "rating"] = 9.9
    # 3) brand duplikat beda kapitalisasi
    df.loc[df.sample(60, random_state=1).index, "Brand"] = df["Brand"].str.upper()
    # 4) spasi berlebih di nama
    df.loc[df.sample(30, random_state=2).index, "Name"] = (
        df["Name"].str.replace(" ", "  ", n=1)
    )
    return df


def main() -> None:
    df = generate(seed=42)
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUT_PATH, index=False)
    print(f"[OK] Sample dataset dibuat: {OUT_PATH}")
    print(f"     Baris  : {len(df):,}")
    print(f"     Kolom  : {df.shape[1]}")
    print(f"     Kategori: {df['cat1'].nunique()}")
    print(f"     Brand  : {df['Brand'].nunique()}")
    print(f"     Harga  : £{df['Price'].min():.2f} - £{df['Price'].max():.2f} "
          f"(median £{df['Price'].median():.2f})")


if __name__ == "__main__":
    main()
