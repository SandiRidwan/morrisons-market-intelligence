"""
build_twb.py  (v5 — skeleton LENGKAP, semua section wajib)
===========================================================
Menghasilkan .twb yang BENAR-BENAR terbuka di Tableau Public 2026.2.

SEJARAH (semua pelajaran):
  v1-v2: ~120 error skema. v3-v4: error turun ke 2 jenis lalu 0 di log,
  TAPI Tableau tetap menutup sendiri saat `upgrade-dom` — karena SECTION WAJIB
  HILANG. Workbook asli (yang terbuka bersih) punya section yang v4 tidak punya:
      document-format-change-manifest, repository-location, preferences,
      datasources, shared-views, actions, worksheets, dashboards, windows,
      datagraph, external
  v5 menambahkan SEMUA section wajib itu.

FAKTA FORMAT (diverifikasi dari workbook asli):
  - <rows>/<cols> berisi TEKS: [ds].[none:field:nk] / [ds].[sum:field:qk]
  - <column-instance> HANYA di <datasource-dependencies>
  - derivation enum: None | Sum | Attribute | User | Day-Trunc | Month-Trunc
    (rata-rata/hitung = calculated field, bukan derivation)
  - Tableau 2026.2 TIDAK mengenal <simple-id>  -> dihilangkan
  - <layout> butuh dim-percentage & measure-percentage
  - urutan <table>: view -> style -> panes -> rows -> cols -> tooltip-style
"""

from __future__ import annotations

import xml.etree.ElementTree as ET
from pathlib import Path
from xml.sax.saxutils import quoteattr

ROOT = Path(__file__).resolve().parent.parent
BUNDLE = ROOT / "data" / "tableau" / "Tableau_Morrisons"
OUT = BUNDLE / "morrisons_market_intelligence.twb"
HYPER = BUNDLE / "products.hyper"

DS = "federated.morrisons"
DS_CAP = "Morrisons Products"
CONN = "hyper.morrisons"

DIMS = ["Category", "Subcategory", "Brand", "Price Tier", "Product", "Is Promo"]
MEAS = ["Effective Price", "Price per 100g", "Rating", "Reviews",
        "Discount Pct", "Value Score"]
CALCS = {
    "AvgPrice": ("Avg Price", "AVG([Effective Price])", "real"),
    "AvgRating": ("Avg Rating", "AVG([Rating])", "real"),
    "AvgUnit": ("Avg Unit Price", "AVG([Price per 100g])", "real"),
    "AvgDiscount": ("Avg Discount", "AVG([Discount Pct])", "real"),
    "Products": ("Products", "COUNTD([Product])", "integer"),
    "AvgValue": ("Avg Value Score", "AVG([Value Score])", "real"),
}


def dt(f: str) -> str:
    if f == "Reviews":
        return "integer"
    if f == "Is Promo":
        return "boolean"
    if f in DIMS:
        return "string"
    return "real"


class X:
    """Writer XML dengan indentasi 2-spasi yang benar (tanpa trik replace)."""

    def __init__(self):
        self.p = ["<?xml version='1.0' encoding='utf-8' ?>", ""]
        self.d = 0

    def _ind(self):
        return "  " * self.d

    def o(self, tag, **a):
        self.p.append(f"{self._ind()}<{tag}{self._a(a)}>")
        self.d += 1

    def c(self, tag):
        self.d -= 1
        self.p.append(f"{self._ind()}</{tag}>")

    def e(self, tag, **a):
        self.p.append(f"{self._ind()}<{tag}{self._a(a)} />")

    def raw(self, s):
        self.p.append(f"{self._ind()}{s}")

    @staticmethod
    def _a(a):
        # Tableau menulis atribut dengan PETIK TUNGGAL. Beberapa build menolak
        # petik ganda pada atribut, jadi kita pakai ' dan escape bila perlu.
        return "".join(
            f" {k}='{str(v).replace(chr(39), '&apos;')}'" for k, v in a.items()
        )

    def t(self):
        return "\n".join(self.p)


# ---------------------------------------------------------------------------
def write_datasource(x: X):
    x.o("datasources")
    x.o("datasource", hasconnection="true", inline="true",
        name=DS, caption=DS_CAP, version="18.1")
    x.o("connection", **{"class": "federated"})
    x.o("named-connections")
    # PENTING: <connection class='hyper'> harus BERADA DI DALAM
    # <named-connection> (bukan di luar sebagai self-closing). Ini pemicu
    # utama Tableau menutup sendiri (gagal konek ke extract).
    x.o("named-connection", caption=DS_CAP, name=CONN)
    x.e("connection", **{"class": "hyper",
                         "dbname": str(HYPER).replace("\\", "/"),
                         "schema": "Extract", "tablename": "Extract"})
    x.c("named-connection")
    x.c("named-connections")
    x.e("relation", connection=CONN, name="Extract",
        table="[Extract].[Extract]", type="table")
    x.c("connection")
    for f in DIMS + MEAS:
        x.e("column", datatype=dt(f), name=f"[{f}]",
            role=("dimension" if f in DIMS else "measure"),
            type=("nominal" if f in DIMS else "quantitative"))
    # calculation HARUS self-closing <calculation ... />
    for fld, (cap, formula, typ) in CALCS.items():
        x.o("column", caption=cap, datatype=typ, name=f"[{fld}]",
            role="measure", type="quantitative")
        x.e("calculation", **{"class": "tableau", "formula": formula})
        x.c("column")
    x.e("layout", **{"dim-percentage": "0.5", "measure-percentage": "0.5",
                     "dim-ordering": "alphabetic",
                     "measure-ordering": "alphabetic",
                     "show-structure": "true"})
    x.o("semantic-values")
    x.e("semantic-value", key="[Category].[none:Category:nk]",
        value='"Food Cupboard"')
    x.c("semantic-values")
    x.c("datasource")
    x.c("datasources")


def write_worksheet(x: X, name: str, dim: str | None, calcf: str, mark="Bar"):
    ci_dim = f"[none:{dim}:nk]" if dim else None
    ci_calc = f"[usr:{calcf}:qk]"
    row_ref = f"[{DS}].{ci_dim}" if dim else None
    col_ref = f"[{DS}].{ci_calc}"

    x.o("worksheet", name=name)
    x.o("table")
    x.o("view")
    x.o("datasources")
    x.e("datasource", caption=DS_CAP, name=DS)
    x.c("datasources")
    x.o("datasource-dependencies", datasource=DS)
    if dim:
        x.e("column", datatype=dt(dim), name=f"[{dim}]",
            role="dimension", type="nominal")
        x.e("column-instance", column=f"[{dim}]", derivation="None",
            name=ci_dim, pivot="key", type="nominal")
    cap, formula, typ = CALCS[calcf]
    x.e("column", caption=cap, datatype=typ, name=f"[{calcf}]",
        role="measure", type="quantitative")
    x.e("column-instance", column=f"[{calcf}]", derivation="User",
        name=ci_calc, pivot="key", type="quantitative")
    x.c("datasource-dependencies")
    x.e("aggregation", value="true")
    x.c("view")
    x.e("style")
    x.o("panes")
    x.o("pane", **{"selection-relaxation-option": "selection-relaxation-allow"})
    x.o("view")
    x.e("breakdown", value="auto")
    x.c("view")
    x.e("mark", **{"class": mark})
    if mark == "Text":
        x.o("encodings")
        x.e("text", column=f"[{DS}].{ci_calc}")
        x.c("encodings")
    x.c("pane")
    x.c("panes")
    x.raw(f"<rows>{row_ref}</rows>" if row_ref else "<rows />")
    x.raw("<cols />" if mark == "Text" else f"<cols>{col_ref}</cols>")
    x.e("tooltip-style", **{"tooltip-mode": "none"})
    x.c("table")
    x.c("worksheet")


def build():
    print("Membangun .twb v5 (skeleton lengkap) ...")
    if not HYPER.exists():
        raise SystemExit("products.hyper tidak ada.")

    x = X()
    x.o("workbook", **{"original-version": "18.1",
                       "source-build": "2025.2.2 (20252.25.0818.1050)",
                       "source-platform": "win", "version": "18.1",
                       "xml:base": "https://localhost:8080"})

    # 1) document-format-change-manifest
    x.o("document-format-change-manifest")
    for t in ["AccessibleZoneTabOrder", "DatagraphCoreV1",
              "ObjectModelEncapsulateLegacy", "ObjectModelTableType"]:
        x.e(t)
    x.c("document-format-change-manifest")

    # 2) repository-location
    x.e("repository-location", **{"derived-from": "", "id": "MorrisonsMI",
                                  "path": "/workbooks", "revision": "1.0"})

    # 3) preferences (SATU preference — sesuai workbook minimal yang terbukti jalan)
    x.o("preferences")
    x.e("preference", name="ui.shelf.height", value="26")
    x.c("preferences")

    # 4) datasources
    write_datasource(x)

    # 5) shared-views + actions — pakai SELF-CLOSING (seperti workbook minimal
    #    yang terbukti terbuka). Bentuk ber-pair kosong memicu error content model.
    x.e("shared-views")
    x.e("actions")

    # 7) worksheets — WAJIB berisi minimal 1 <worksheet> (tidak boleh kosong)
    x.o("worksheets")
    specs = [
        ("Median Price by Category", "Category", "AvgPrice"),
        ("Avg Rating by Category", "Category", "AvgRating"),
        ("Avg Unit Price by Category", "Category", "AvgUnit"),
        ("Products by Price Tier", "Price Tier", "Products"),
        ("Avg Discount by Tier", "Price Tier", "AvgDiscount"),
        ("Top Brands", "Brand", "Products"),
        ("Avg Value by Tier", "Price Tier", "AvgValue"),
    ]
    for nm, d, c in specs:
        write_worksheet(x, nm, d, c, "Bar")
    for nm, c in [("KPI Products", "Products"),
                  ("KPI Avg Price", "AvgPrice"),
                  ("KPI Avg Rating", "AvgRating")]:
        write_worksheet(x, nm, None, c, "Text")
    x.c("worksheets")

    # 8) dashboards — WAJIB berisi minimal 1
    x.o("dashboards")
    x.o("dashboard", name="Morrisons — Market Intelligence")
    x.e("style")
    x.e("size", maxheight="900", maxwidth="1400",
        minheight="900", minwidth="1400", **{"sizing-mode": "fixed"})
    x.o("zones")
    x.e("zone", h="100000", id="1", w="100000", x="0", y="0")
    x.c("zones")
    x.c("dashboard")
    x.c("dashboards")

    # 9) windows — WAJIB berisi minimal 1 window (cards + viewpoint)
    x.o("windows")
    x.o("window", **{"class": "dashboard",
                     "name": "Morrisons — Market Intelligence"})
    x.e("cards")
    x.o("viewpoint")
    x.e("zoom")
    x.c("viewpoint")
    x.c("window")
    x.c("windows")

    # 10) datagraph — content model wajib lengkap
    x.o("datagraph")
    x.o("graph")
    x.o("properties")
    x.e("default-execution-subgraph-guid",
        value="3a12a248-46b9-4663-94bf-7d3171377f6d")
    x.c("properties")
    x.e("node-execution-subgraphs")
    x.e("nodes")
    x.e("edges")
    x.e("pin-values")
    x.c("graph")
    x.c("datagraph")

    # 11) external (kosong)
    x.o("external")
    x.o("shapes")
    x.c("shapes")
    x.c("external")

    x.c("workbook")

    xml = x.t()
    try:
        ET.fromstring(xml)
        ok = "XML-OK"
    except ET.ParseError as e:
        ok = f"XML-INVALID: {e}"
    OUT.write_text(xml, encoding="utf-8")
    print(f"  [twb] {OUT.name} ({len(xml):,} chars) {ok}")
    return OUT


if __name__ == "__main__":
    build()
