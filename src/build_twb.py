"""
build_twb.py  (v4 — struktur FINAL, diverifikasi baris-per-baris dari workbook asli)
====================================================================================
Menghasilkan .twb yang BENAR-BENAR terbuka di Tableau Public 2026.2.

RANGKUMAN SEMUA PELAJARAN (v1..v4):
  - <rows>/<cols> berisi TEKS referensi kolom, BUKAN elemen:
        <rows>[ds].[none:field:nk]</rows>
        <cols>[ds].[sum:field:qk]</cols>
  - <column-instance> HANYA boleh berada di dalam <datasource-dependencies>.
  - derivation enum yang SAH: None | Sum | Attribute | User | Day-Trunc | Month-Trunc.
    (TIDAK ada Avg/Cnt/Min/Max! -> rata-rata/median/hitung pakai CALCULATED FIELD.)
  - <simple-id uuid='{GUID}' /> ada DI DALAM <worksheet>, SETELAH </table>.
  - <layout> butuh: dim-percentage, measure-percentage, dim-ordering,
    measure-ordering, show-structure.
  - urutan <table>: view -> style -> panes -> rows -> cols -> tooltip-style.
  - agregasi (avg/count/median) dibuat sebagai <column> calculated di datasource
    dengan formula, mis. AVG([Effective Price]).
  - atribut 'class' ditulis apa adanya.

Output: data/tableau/Tableau_Morrisons/morrisons_market_intelligence.twb
"""

from __future__ import annotations

import hashlib
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

# calculated aggregations (karena derivation Avg/Cnt tidak ada)
# nama field kalkulasi -> (caption, formula, datatype)
CALCS = {
    "AvgPrice": ("Avg Price", "AVG([Effective Price])", "real"),
    "AvgRating": ("Avg Rating", "AVG([Rating])", "real"),
    "AvgUnit": ("Avg Unit Price", "AVG([Price per 100g])", "real"),
    "AvgDiscount": ("Avg Discount", "AVG([Discount Pct])", "real"),
    "Products": ("Products", "COUNTD([Product])", "integer"),
    "AvgValue": ("Avg Value Score", "AVG([Value Score])", "real"),
}


def guid(seed: str) -> str:
    h = hashlib.md5(seed.encode()).hexdigest().upper()
    return f"{{{h[:8]}-{h[8:12]}-{h[12:16]}-{h[16:20]}-{h[20:32]}}}"


def dt(f: str) -> str:
    if f == "Reviews":
        return "integer"
    if f == "Is Promo":
        return "boolean"
    if f in DIMS:
        return "string"
    return "real"


class X:
    def __init__(self):
        self.p = ["<?xml version='1.0' encoding='utf-8' ?>", ""]
        self.d = 0

    def o(self, tag, **a):
        self.p.append("  " * self.d + f"<{tag}{self._a(a)}>")
        self.d += 1

    def c(self, tag):
        self.d -= 1
        self.p.append("  " * self.d + f"</{tag}>")

    def e(self, tag, **a):
        self.p.append("  " * self.d + f"<{tag}{self._a(a)} />")

    def raw(self, s):
        self.p.append("  " * self.d + s)

    @staticmethod
    def _a(a):
        return "".join(f" {k}={quoteattr(str(v))}" for k, v in a.items())

    def t(self):
        return "\n".join(self.p)


# ---------------------------------------------------------------------------
def write_datasource(x: X):
    x.o("datasources")
    x.o("datasource", hasconnection="true", inline="true",
        name=DS, caption=DS_CAP, version="18.1")

    x.o("connection", **{"class": "federated"})
    x.o("named-connections")
    x.e("named-connection", caption=DS_CAP, name=CONN)
    x.c("named-connections")
    x.e("connection", **{"class": "hyper",
                         "dbname": str(HYPER).replace("\\", "/"),
                         "schema": "Extract", "tablename": "Extract"})
    x.e("relation", connection=CONN, name="Extract",
        table="[Extract].[Extract]", type="table")
    x.c("connection")  # federated

    # kolom fisik
    for f in DIMS + MEAS:
        x.e("column", datatype=dt(f), name=f"[{f}]",
            role=("dimension" if f in DIMS else "measure"),
            type=("nominal" if f in DIMS else "quantitative"))
    # calculated columns (agregasi)
    for fld, (cap, formula, typ) in CALCS.items():
        x.o("column", caption=cap, datatype=typ, name=f"[{fld}]",
            role="measure", type="quantitative")
        x.o("calculation", **{"class": "tableau",
                              "formula": formula})
        x.c("calculation")
        x.c("column")

    x.e("layout", **{"dim-percentage": "0.5", "measure-percentage": "0.5",
                     "dim-ordering": "alphabetic",
                     "measure-ordering": "alphabetic",
                     "show-structure": "true"})
    # semantic-values harus berisi minimal satu semantic-value
    x.o("semantic-values")
    x.e("semantic-value", key="[Category].[none:Category:nk]", value='"Food Cupboard"')
    x.c("semantic-values")
    x.c("datasource")
    x.c("datasources")


def ws_pane(x: X, mark: str, fields: list[tuple[str, str]]):
    """Tulis <panes><pane> dengan mark + encodings."""
    x.o("panes")
    x.o("pane", **{"selection-relaxation-option": "selection-relaxation-allow"})
    x.o("view")
    x.e("breakdown", value="auto")
    x.c("view")
    x.e("mark", **{"class": mark})
    if fields:
        x.o("encodings")
        for kind, ref in fields:
            x.e(kind, column=f"[{DS}].{ref}")
        x.c("encodings")
    x.c("pane")
    x.c("panes")


def write_worksheet(x: X, name: str, dim: str | None, calcf: str,
                    mark: str = "Bar"):
    """Worksheet valid. dim=None -> single-value KPI (mark Text)."""
    ci_dim = f"[none:{dim}:nk]" if dim else None
    # calculated field memakai derivation 'User' -> [usr:Nama:qk]
    ci_calc = f"[usr:{calcf}:qk]"
    # referensi teks di <rows>/<cols>: [ds].[NamaColumnInstance]  (SATU bracket)
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

    enc = [("text", ci_calc)] if mark == "Text" else []
    ws_pane(x, mark, enc)

    x.raw(f"<rows>{row_ref}</rows>" if row_ref else "<rows />")
    if mark == "Text":
        x.raw("<cols />")
    else:
        x.raw(f"<cols>{col_ref}</cols>")
    x.e("tooltip-style", **{"tooltip-mode": "none"})
    x.c("table")
    # CATATAN: Tableau Public 2026.2 TIDAK mengenal elemen <simple-id> -> dihilangkan.
    x.c("worksheet")


def build():
    print("Membangun .twb v4 ...")
    if not HYPER.exists():
        raise SystemExit("products.hyper belum ada.")

    x = X()
    x.o("workbook", **{"original-version": "18.1", "source-build": "2025.2.2",
                       "source-platform": "win", "version": "18.1",
                       "xml:base": "https://localhost:8080"})
    x.o("document-format-change-manifest")
    for t in ["AccessibleZoneTabOrder", "DatagraphCoreV1",
              "ObjectModelEncapsulateLegacy", "ObjectModelTableType"]:
        x.e(t)
    x.c("document-format-change-manifest")

    write_datasource(x)

    x.o("worksheets")
    # (nama, dim, calc, mark)
    specs = [
        ("Median Price by Category", "Category", "AvgPrice", "Bar"),
        ("Avg Rating by Category", "Category", "AvgRating", "Bar"),
        ("Avg Unit Price by Category", "Category", "AvgUnit", "Bar"),
        ("Products by Price Tier", "Price Tier", "Products", "Bar"),
        ("Avg Discount by Tier", "Price Tier", "AvgDiscount", "Bar"),
        ("Top Brands", "Brand", "Products", "Bar"),
        ("Avg Value by Tier", "Price Tier", "AvgValue", "Bar"),
        ("KPI Products", None, "Products", "Text"),
        ("KPI Avg Price", None, "AvgPrice", "Text"),
        ("KPI Avg Rating", None, "AvgRating", "Text"),
    ]
    for nm, d, c, m in specs:
        write_worksheet(x, nm, d, c, m)
    x.c("worksheets")

    # dashboard
    x.o("dashboards")
    x.o("dashboard", name="Morrisons — Market Intelligence")
    x.e("style")
    x.e("size", maxheight="900", maxwidth="1400",
        minheight="900", minwidth="1400", **{"sizing-mode": "fixed"})
    x.o("zones")
    x.e("zone", h="100000", id="1", **{"type-v2": "layout-basic"},
        w="100000", x="0", y="0")
    x.c("zones")
    x.c("dashboard")
    x.c("dashboards")

    x.o("windows")
    x.o("window", **{"class": "dashboard",
                     "name": "Morrisons — Market Intelligence"})
    x.o("cards")
    x.c("cards")
    x.o("viewpoint")
    x.e("zoom")
    x.c("viewpoint")
    x.c("window")
    x.c("windows")

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
