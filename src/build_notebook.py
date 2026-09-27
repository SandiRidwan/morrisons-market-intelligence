"""
build_notebook.py
=================
Membangun notebooks/morrisons_market_intelligence.ipynb secara programatik
(agar reproducible & bisa di-diff di git, bukan sekadar file biner).

Jalankan: python src/build_notebook.py
"""

from __future__ import annotations

import json
from pathlib import Path

NB_PATH = Path(__file__).resolve().parent.parent / "notebooks" / \
    "morrisons_market_intelligence.ipynb"


def md(text: str) -> dict:
    return {"cell_type": "markdown", "metadata": {}, "source": text.splitlines(keepends=True)}


def code(text: str) -> dict:
    return {"cell_type": "code", "execution_count": None, "metadata": {},
            "outputs": [], "source": text.splitlines(keepends=True)}


CELLS = [
    md("""# 🛒 Morrisons UK — Grocery Market Intelligence

**Analisis kompetitif atas 18.100 produk ritel dari groceries.morrisons.com.**

Notebook ini menelusuri seluruh alur analisis, dari data mentah hasil scraping
hingga rekomendasi bisnis. Ringkasan lengkap tersedia di `REPORT.md`.

> Dibuat oleh **Sandi Ridwan** · portofolio data analyst / data automation engineer.
"""),

    md("""## 0. Setup

Kita mengimpor modul analisis yang sudah dibuat di `src/`. Logika inti
(parsing, cleaning, insight) dipisahkan ke modul agar notebook ini tetap
ringkas & dapat direproduksi.
"""),

    code("""import sys
from pathlib import Path

# agar bisa import modul dari src/
sys.path.insert(0, str(Path.cwd().parent / "src"))

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

import analysis as A
import morrisons_parser as mp

pd.set_option("display.width", 160)
pd.set_option("display.max_columns", 40)
%matplotlib inline
"""),

    md("""## 1. Dari Data Mentah ke Data Bersih

Output scraper menyimpan informasi penting **di dalam string** — harga dalam
format `"£3.20"`, rating dalam `"Rating: 4.6 (12 reviews)"`, dan promo dalam
`"Promotions: Now £1.75, Was £2"`. Parser mengekstrak semua ini menjadi kolom.

Ini adalah langkah *"bronze → silver"* yang menentukan kualitas seluruh analisis.
"""),

    code("""# Parse mentah -> bersih (idempoten; aman dijalankan berulang)
parsed = mp.parse_raw()
parsed.to_csv(Path.cwd().parent / "data" / "processed" / "morrisons_clean.csv", index=False)
print(f"Produk ter-parse: {len(parsed):,}")
parsed[["brand","name","price","promo_price","discount_pct","rating","reviews","unit_price"]].head(8)
"""),

    md("""### 2. Kualitas Data

Sebelum percaya angka apa pun, kita audit kualitas data — secara eksplisit,
bukan disembunyikan.
"""),

    code("""df, rpt = A.load_and_clean()
print("DATA QUALITY REPORT")
print("="*50)
for k, v in rpt.as_dict().items():
    print(f"  {k:32}: {v}")
print()
for n in rpt.notes:
    print("  -", n)
"""),

    md("""## 3. Q1 — Struktur Harga Antarkategori
"""),

    code("""A.price_summary_by_category(df)
"""),

    code("""from IPython.display import Image, display
display(Image(filename=str(Path.cwd().parent / "reports/figures/01_price_by_category.png")))
"""),

    md("""## 4. Q2 — Intensitas Promosi
"""),

    code("""A.promo_analysis(df)
"""),

    code("""display(Image(filename=str(Path.cwd().parent / "reports/figures/02_promo_rate.png")))
"""),

    md("""## 5. Q3 — Positioning Brand

Membandingkan harga brand lintas-kategori menyesatkan (biskuit vs sampanye).
Jadi kita pakai **price index** = harga brand ÷ median kategori-nya.
"""),

    code("""A.brand_positioning(df).head(10)   # paling premium
"""),

    code("""A.brand_positioning(df).tail(10)   # paling value
"""),

    code("""display(Image(filename=str(Path.cwd().parent / "reports/figures/03_brand_positioning.png")))
"""),

    md("""## 6. Q4 — Apakah Harga Mencerminkan Kualitas?
"""),

    code("""rp = A.rating_vs_price(df)
print(f"Spearman correlation (harga vs rating): {rp['spearman_corr']}")
print(rp['interpretation'])
rp['rating_by_price_quartile']
"""),

    code("""display(Image(filename=str(Path.cwd().parent / "reports/figures/07_rating_by_quartile.png")))
"""),

    md("""## 7. Q5 — Peluang Private-Label

Kategori di mana brand premium mendominasi rak = peluang terbesar untuk
private-label yang lebih murah.
"""),

    code("""A.own_brand_opportunity(df)
"""),

    code("""display(Image(filename=str(Path.cwd().parent / "reports/figures/04_own_brand_gap.png")))
"""),

    md("""## 8. Produk Value Terbaik untuk Konsumen
"""),

    code("""A.value_for_money(df).head(15)
"""),

    code("""display(Image(filename=str(Path.cwd().parent / "reports/figures/09_value_winners.png")))
"""),

    md("""## 9. Kesimpulan & Rekomendasi

1. **Private-label push** di Treats & Snacks, Baby & Toddler, Drinks
   (gap premium +8–10pp).
2. **Kelola agresivitas promo** di Alkohol & Fresh (60% & 55% SKU promo).
3. **Kampanye "value"** — harga tidak berkorelasi dengan rating (ρ=0.08),
   jadi cerita value sangat menjual.
4. **Perbaiki kelengkapan konten** di kategori dengan deskripsi rendah.
5. **Pantau kompetitor berkala** dengan pipeline yang sama.

Rekomendasi lengkap + keterbatasan ada di `REPORT.md`.
"""),
]


def main():
    nb = {
        "cells": CELLS,
        "metadata": {
            "kernelspec": {"display_name": "Python 3", "language": "python",
                           "name": "python3"},
            "language_info": {"name": "python", "version": "3.x"},
        },
        "nbformat": 4,
        "nbformat_minor": 5,
    }
    NB_PATH.parent.mkdir(parents=True, exist_ok=True)
    NB_PATH.write_text(json.dumps(nb, indent=1, ensure_ascii=False),
                       encoding="utf-8")
    print(f"[OK] Notebook dibuat: {NB_PATH} ({len(CELLS)} cells)")


if __name__ == "__main__":
    main()
