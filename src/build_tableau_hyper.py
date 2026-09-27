"""
build_tableau_hyper.py
======================
Menghasilkan bundel Tableau yang PASTI bisa dibuka:

  1. products.hyper   -> extract Tableau (format native, via Tableau Hyper API)
  2. morrisons.tds    -> datasource Tableau (XML sederhana, jauh lebih mudah valid)
  3. CARA_PAKAI.md    -> panduan drag-and-drop untuk membangun workbook

Mengapa bukan .twb penuh?
  .twb penuh butuh skema internal yang sangat ketat (2x percobaan gagal dengan
  error D2E8DA72). Pelajaran: JANGAN lawan kompleksitas tanpa bisa verifikasi.
  Sebaliknya: kirim DATA dalam format native (hyper) + datasource (tds, skema
  sederhana) — keduanya punya peluang sukses jauh lebih tinggi, dan worksheet
  dibangun dengan drag (2 menit) dari datasource yang sudah siap.

Jalankan: python src/build_tableau_hyper.py
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
TABLEAU_DIR = ROOT / "data" / "tableau"
BUNDLE = TABLEAU_DIR / "Tableau_Morrisons"
BUNDLE.mkdir(parents=True, exist_ok=True)

CSV = ROOT / "data" / "processed" / "morrisons_clean.csv"
HYPER = BUNDLE / "products.hyper"
TDS = BUNDLE / "morrisons.tds"


def prepare() -> pd.DataFrame:
    df = pd.read_csv(CSV, low_memory=False)
    # kolom analitik (sama dengan analysis.py)
    med = df.groupby("cat1")["effective_price"].transform("median")
    df["price_index"] = (df["effective_price"] / med).round(3)
    df["brand_tier"] = np.where(df["price_index"] >= 1.15, "Premium",
                        np.where(df["price_index"] <= 0.85, "Value", "Mainstream"))
    df["value_score"] = np.nan
    m = (df["reviews"].fillna(0) >= 10) & df["rating"].notna() & df["price_per_100g"].notna()
    s = df[m]
    if len(s):
        pr = s["price_per_100g"].rank(pct=True); rr = s["rating"].rank(pct=True)
        df.loc[s.index, "value_score"] = (rr * 0.6 + (1 - pr) * 0.4).round(3)

    df["is_promo"] = df["is_promo"].fillna(False).astype(bool)
    cols = ["cat1", "cat2", "brand", "brand_tier", "name",
            "effective_price", "price_per_100g", "rating", "reviews",
            "discount_pct", "is_promo", "value_score"]
    out = df[cols].copy()
    out["rating"] = out["rating"].fillna(-1).round(2)      # -1 = belum ada rating
    out["discount_pct"] = out["discount_pct"].fillna(0)
    out["value_score"] = out["value_score"].fillna(-1)
    out["reviews"] = out["reviews"].fillna(0).astype(int)
    return out


def write_hyper(df: pd.DataFrame):
    """Tulis extract .hyper via Tableau Hyper API."""
    from tableauhyperapi import (HyperProcess, Telemetry, Connection,
                                 CreateMode, TableDefinition, SqlType, Inserter,
                                 TableName, Nullability)

    table = TableDefinition(TableName("Extract", "Extract"), [
        TableDefinition.Column("Category", SqlType.text(), Nullability.NOT_NULLABLE),
        TableDefinition.Column("Subcategory", SqlType.text(), Nullability.NULLABLE),
        TableDefinition.Column("Brand", SqlType.text(), Nullability.NOT_NULLABLE),
        TableDefinition.Column("Price Tier", SqlType.text(), Nullability.NOT_NULLABLE),
        TableDefinition.Column("Product", SqlType.text(), Nullability.NOT_NULLABLE),
        TableDefinition.Column("Effective Price", SqlType.double(), Nullability.NOT_NULLABLE),
        TableDefinition.Column("Price per 100g", SqlType.double(), Nullability.NULLABLE),
        TableDefinition.Column("Rating", SqlType.double(), Nullability.NULLABLE),
        TableDefinition.Column("Reviews", SqlType.big_int(), Nullability.NOT_NULLABLE),
        TableDefinition.Column("Discount Pct", SqlType.double(), Nullability.NULLABLE),
        TableDefinition.Column("Is Promo", SqlType.bool(), Nullability.NOT_NULLABLE),
        TableDefinition.Column("Value Score", SqlType.double(), Nullability.NULLABLE),
    ])

    with HyperProcess(Telemetry.DO_NOT_SEND_USAGE_DATA_TO_TABLEAU) as hyper:
        with Connection(hyper.endpoint, HYPER, CreateMode.CREATE_AND_REPLACE) as conn:
            conn.catalog.create_schema("Extract")
            conn.catalog.create_table(table)
            rows = [
                [str(r["cat1"]), _s(r["cat2"]), str(r["brand"]), str(r["brand_tier"]),
                 str(r["name"]), float(r["effective_price"]),
                 _f(r["price_per_100g"]), _f(r["rating"]), int(r["reviews"]),
                 _f(r["discount_pct"]), bool(r["is_promo"]), _f(r["value_score"])]
                for _, r in df.iterrows()
            ]
            with Inserter(conn, table) as ins:
                ins.add_rows(rows)
                ins.execute()
            n = conn.execute_scalar_query(
                f"SELECT COUNT(*) FROM {table.table_name}")
    print(f"  [hyper] {HYPER.name} ({n:,} rows)")


def _s(v):
    return None if pd.isna(v) else str(v)


def _f(v):
    return None if pd.isna(v) else float(v)


def write_tds():
    """Datasource Tableau (.tds) menunjuk ke extract .hyper.

    .tds = XML sederhana (jauh lebih sedikit elemen dari .twb) → validasi mudah.
    """
    cols = [
        ("Category", "string", "dimension", "nominal"),
        ("Subcategory", "string", "dimension", "nominal"),
        ("Brand", "string", "dimension", "nominal"),
        ("Price Tier", "string", "dimension", "nominal"),
        ("Product", "string", "dimension", "nominal"),
        ("Effective Price", "real", "measure", "quantitative"),
        ("Price per 100g", "real", "measure", "quantitative"),
        ("Rating", "real", "measure", "quantitative"),
        ("Reviews", "integer", "measure", "quantitative"),
        ("Discount Pct", "real", "measure", "quantitative"),
        ("Is Promo", "boolean", "dimension", "nominal"),
        ("Value Score", "real", "measure", "quantitative"),
    ]
    L = []
    L.append("<?xml version='1.0' encoding='utf-8' ?>")
    L.append("")
    L.append("<datasource formatted-name='morrisons' inline='false' "
             "source-platform='win' version='18.1' xml:base='https://localhost:8080' "
             "xmlns:user='http://www.tableausoftware.com/xml/user'>")
    L.append("  <connection class='federated'>")
    L.append("    <named-connections>")
    L.append("      <named-connection caption='products' name='hyper.morrisons'>")
    L.append(f"        <connection class='hyper' dbname='{HYPER}' schema='Extract' "
             "tablename='Extract' />")
    L.append("      </named-connection>")
    L.append("    </named-connections>")
    L.append("    <relation connection='hyper.morrisons' name='Extract' "
             "table='[Extract].[Extract]' type='table' />")
    L.append("  </connection>")
    for name, dt, role, typ in cols:
        L.append(f"  <column datatype='{dt}' name='[{name}]' "
                 f"role='{role}' type='{typ}' />")
    L.append("  <layout dim-ordering='alphabetic' measure-ordering='alphabetic' "
             "show-structure='true' />")
    L.append("  <semantic-values />")
    L.append("</datasource>")
    TDS.write_text("\n".join(L), encoding="utf-8")

    # validasi XML
    import xml.etree.ElementTree as ET
    try:
        ET.fromstring(TDS.read_text(encoding="utf-8"))
        print(f"  [tds] {TDS.name} (XML valid)")
    except ET.ParseError as e:
        print(f"  [tds] INVALID: {e}")


def main():
    print("Membangun bundel Tableau (hyper + tds) ...")
    df = prepare()
    write_hyper(df)
    write_tds()
    print(f"\nSelesai. Bundel: {BUNDLE}")


if __name__ == "__main__":
    main()
