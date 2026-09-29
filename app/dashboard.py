"""
Morrisons UK — Grocery Market Intelligence Dashboard
=====================================================
Dashboard interaktif Streamlit + Plotly atas 11.208 produk hasil scraping (data terbaru).

Jalankan:
    streamlit run app/dashboard.py

Struktur:
- Sidebar: filter global (kategori, brand, tier, promo, harga)
- Tab: Overview | Pricing | Promotions | Brands | Value
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# --- path agar bisa impor modul src/ ---
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))
import explanations as X  # noqa: E402
import insights_content  # noqa: E402,F401
import insight as INS  # noqa: E402
import echarts_charts as EC  # noqa: E402  (treemap, boxplot, pictorialBar)

CLEAN_CSV = ROOT / "data" / "processed" / "morrisons_clean.csv"

# ---------------------------------------------------------------- palette
C = {
    "primary": "#1F5C3D", "accent": "#E4A11B", "dark": "#22303C",
    "grey": "#8B9AA6", "red": "#C0392B", "blue": "#2E6F95",
    "bg": "#0E1117", "card": "#1A1F2B",
}
CAT_COLORS = ["#1F5C3D", "#E4A11B", "#2E6F95", "#C0392B", "#6A4C93",
              "#2A9D8F", "#E76F51", "#264653", "#A4262C", "#457B9D",
              "#E9C46A", "#F4A261", "#9B5DE5", "#8B9AA6", "#F15BB5"]

st.set_page_config(
    page_title="Morrisons UK — Market Intelligence",
    page_icon="🛒",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ---------------------------------------------------------------- data
@st.cache_data(show_spinner="Memuat 18.000+ produk...")
def load_data() -> pd.DataFrame:
    df = pd.read_csv(CLEAN_CSV, low_memory=False)
    df["brand"] = df["brand"].astype(str).str.strip()
    df["cat1"] = df["cat1"].astype(str).str.strip()

    # --- kolom turunan (duplikat logika analysis.py agar app mandiri) ---
    # price index = harga ÷ median kategori-nya
    cat_med = df.groupby("cat1")["effective_price"].transform("median")
    df["price_index"] = (df["effective_price"] / cat_med).round(3)
    df["brand_tier"] = np.where(
        df["price_index"] >= 1.15, "Premium",
        np.where(df["price_index"] <= 0.85, "Value", "Mainstream"))

    # value_score (60% rating + 40% murah) untuk produk dengan >=10 review
    df["value_score"] = np.nan
    mask = (df["reviews"].fillna(0) >= 10) & df["rating"].notna() \
        & df["price_per_100g"].notna()
    sub = df[mask]
    if len(sub):
        pr = sub["price_per_100g"].rank(pct=True)
        rr = sub["rating"].rank(pct=True)
        df.loc[sub.index, "value_score"] = (rr * 0.6 + (1 - pr) * 0.4).round(3)
    return df


def kpi_card(col, label, value, delta=None, color=C["primary"]):
    col.markdown(
        f"""
        <div style="background:{C['card']};border-left:4px solid {color};
                    padding:14px 16px;border-radius:10px;height:110px;">
          <div style="color:#9AA7B4;font-size:0.78rem;text-transform:uppercase;
                      letter-spacing:.06em;">{label}</div>
          <div style="color:{color};font-size:1.9rem;font-weight:700;
                      margin-top:6px;line-height:1.1;">{value}</div>
          <div style="color:#6B7885;font-size:0.75rem;">{delta or ''}</div>
        </div>
        """, unsafe_allow_html=True)


def style_fig(fig, height=420):
    fig.update_layout(
        height=height,
        margin=dict(l=10, r=10, t=50, b=10),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#D5DBE1", family="Inter, system-ui, sans-serif"),
        title=dict(font=dict(size=16, color="#FFFFFF")),
        legend=dict(bgcolor="rgba(0,0,0,0)"),
    )
    fig.update_xaxes(gridcolor="#2A3038", zeroline=False)
    fig.update_yaxes(gridcolor="#2A3038", zeroline=False)
    return fig


# ---------------------------------------------------------------- load
df_all = load_data()

# ---------------------------------------------------------------- sidebar
st.sidebar.markdown("### 🎛️ Filters")
cats = sorted(df_all["cat1"].unique())
sel_cats = st.sidebar.multiselect("Category", cats, default=cats[:6])

all_brands = sorted(df_all["brand"].unique())
top_brands = df_all["brand"].value_counts().head(40).index.tolist()
sel_brands = st.sidebar.multiselect("Brand (top 40)", sorted(top_brands), default=[])

tiers = sorted(df_all["brand_tier"].dropna().unique())
sel_tiers = st.sidebar.multiselect("Price tier", tiers, default=tiers)

promo_only = st.sidebar.toggle("Promotions only", value=False)

pr_min, pr_max = float(df_all["effective_price"].min()), 25.0
price_range = st.sidebar.slider("Price range (£)", pr_min, pr_max, (pr_min, pr_max))

min_reviews = st.sidebar.slider("Min reviews (rating analysis)", 0, 100, 10, step=5)

st.sidebar.markdown("---")
st.sidebar.caption(
    "Data: scraped from groceries.morrisons.com · n=11,208 products\n\n"
    "⚠️ Rating tersedia untuk 99.7% produk.")

# ---------------------------------------------------------------- filter
df = df_all.copy()
if sel_cats:
    df = df[df["cat1"].isin(sel_cats)]
if sel_brands:
    df = df[df["brand"].isin(sel_brands)]
if sel_tiers:
    df = df[df["brand_tier"].isin(sel_tiers)]
if promo_only:
    df = df[df["is_promo"] == True]
df = df[(df["effective_price"] >= price_range[0]) &
        (df["effective_price"] <= price_range[1])]

# ---------------------------------------------------------------- header
st.markdown(
    f"""
    <div style="background:linear-gradient(100deg,{C['primary']},{C['blue']});
                padding:22px 26px;border-radius:14px;margin-bottom:18px;">
      <div style="font-size:1.75rem;font-weight:800;color:white;">
        🛒 Morrisons UK — Grocery Market Intelligence</div>
      <div style="color:#D7E4DC;font-size:0.9rem;margin-top:4px;">
        Interactive competitive analysis over real scraped retail data ·
        by <b>Sandi Ridwan</b></div>
    </div>
    """, unsafe_allow_html=True)

# ---------------------------------------------------------------- KPI band
k1, k2, k3, k4, k5 = st.columns(5)
med_price = df["effective_price"].median()
promo_rate = df["is_promo"].mean() * 100
med_disc = df["discount_pct"].median(skipna=True)
kpi_card(k1, "Products", f"{len(df):,}", f"of {len(df_all):,} total", C["primary"])
kpi_card(k2, "Median price", f"£{med_price:,.2f}", "effective price", C["dark"])
kpi_card(k3, "Promo rate", f"{promo_rate:.1f}%", "share on promotion", C["accent"])
kpi_card(k4, "Median discount", f"−{med_disc:.1f}%" if pd.notna(med_disc) else "—",
         "when on promo", C["red"])
kpi_card(k5, "Brands", f"{df['brand'].nunique():,}", "unique brands", C["blue"])

st.write("")

# ---------------------------------------------------------------- tabs
tab_ov, tab_price, tab_promo, tab_brand, tab_value = st.tabs(
    ["📊 Overview", "💷 Pricing", "🏷️ Promotions", "🏢 Brands", "⭐ Value"])

# ============================== OVERVIEW ==============================
with tab_ov:
    X.render("kpi", st=st)
    INS.box("kpi", st=st)
    X.render("price_by_category", st=st)
    X.render("portfolio", st=st)
    c1, c2 = st.columns([1.1, 1])
    with c1:
        t = (df.groupby("cat1")["effective_price"].median()
             .sort_values().reset_index())
        fig = px.bar(t, x="effective_price", y="cat1", orientation="h",
                     color="effective_price", color_continuous_scale="Greens",
                     labels={"effective_price": "Median price (£)", "cat1": ""})
        fig.update_traces(texttemplate="£%{x:.2f}", textposition="outside",
                          cliponaxis=False)
        style_fig(fig).update_layout(coloraxis_showscale=False)
        fig.update_layout(title="Median Price by Category")
        fig.update_xaxes(range=[0, t["effective_price"].max() * 1.2])
        st.plotly_chart(fig, use_container_width=True)
        INS.box("price_by_category", st=st)
    with c2:
        t = df["cat1"].value_counts().reset_index()
        t.columns = ["cat1", "count"]
        fig = px.pie(t, names="cat1", values="count", hole=0.55,
                     color_discrete_sequence=CAT_COLORS)
        fig.update_traces(textposition="inside", textinfo="percent",
                          textfont_size=10)
        style_fig(fig).update_layout(
            title="Assortment Share",
            legend=dict(orientation="v", font=dict(size=9), x=0.85))
        st.plotly_chart(fig, use_container_width=True)

    c3, c4 = st.columns(2)
    with c3:
        t = (df.groupby("brand_tier")["effective_price"]
             .agg(["count", "median"]).reset_index())
        fig = px.bar(t, x="brand_tier", y="count", color="brand_tier",
                     color_discrete_map={"Premium": C["red"],
                                         "Mainstream": C["grey"],
                                         "Value": C["primary"]},
                     text="count")
        fig.update_traces(textposition="outside")
        style_fig(fig).update_layout(title="SKU Count by Price Tier",
                                     showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
    with c4:
        t = (df[df["rating"].notna()]
             .groupby("cat1")["rating"].median().sort_values().reset_index())
        fig = px.bar(t, x="rating", y="cat1", orientation="h",
                     color="rating", color_continuous_scale="YlOrBr",
                     labels={"rating": "Median rating", "cat1": ""})
        fig.update_traces(texttemplate="%{x:.2f}", textposition="outside")
        style_fig(fig).update_layout(coloraxis_showscale=False,
                                     title="Median Rating by Category",
                                     xaxis_range=[0, 5.4])
        st.plotly_chart(fig, use_container_width=True)
    INS.box("portfolio", st=st)

    st.markdown("#### Hierarki kategori → brand (treemap ECharts)")
    st.caption("Treemap memetakan **dua tingkat sekaligus**: luas kotak luar = "
               "jumlah SKU per kategori, kotak di dalamnya = brand teratas di "
               "kategori itu. Cara cepat melihat kategori mana yang gemuk dan "
               "brand mana yang mendominasinya.")
    try:
        _roots = []
        for _cat, _g in df.groupby("cat1"):
            if len(_g) < 20:
                continue
            _tb = _g["brand"].value_counts().head(6)
            _roots.append({
                "name": str(_cat)[:20],
                "value": int(len(_g)),
                "children": [{"name": str(b)[:18], "value": int(n)}
                             for b, n in _tb.items()]})
        if _roots:
            _roots = sorted(_roots, key=lambda r: -r["value"])[:12]
            EC.treemap(_roots, title="SKU per kategori → brand teratas",
                       height=520)
    except Exception as _e:  # noqa: BLE001
        st.caption(f"treemap tak tersedia ({_e}).")
    INS.box("echarts_treemap", st=st)

# ============================== PRICING ==============================
with tab_price:
    X.render("rating_vs_price", st=st)
    c1, c2 = st.columns(2)
    with c1:
        fig = px.box(df[df["effective_price"] <= price_range[1]],
                     x="cat1", y="effective_price", color="cat1",
                     color_discrete_sequence=CAT_COLORS,
                     labels={"effective_price": "Effective price (£)", "cat1": ""})
        style_fig(fig, height=480).update_layout(
            title="Price Distribution by Category", showlegend=False)
        fig.update_xaxes(tickangle=-35, tickfont=dict(size=9))
        st.plotly_chart(fig, use_container_width=True)
    with c2:
        sub = df.dropna(subset=["rating"])
        fig = px.scatter(sub, x="effective_price", y="rating",
                         color="brand_tier",
                         color_discrete_map={"Premium": C["red"],
                                             "Mainstream": C["grey"],
                                             "Value": C["primary"]},
                         opacity=0.4, size_max=6,
                         labels={"effective_price": "Effective price (£)",
                                 "rating": "Rating"})
        fig.update_traces(marker=dict(size=5))
        # Spearman dihitung manual (rank -> Pearson) agar TIDAK butuh scipy
        # (scipy tidak tersedia di Streamlit Cloud secara default).
        _rr = sub[["effective_price", "rating"]].dropna()
        if len(_rr) > 2:
            _rho = (_rr["effective_price"].rank()
                    .corr(_rr["rating"].rank()))  # Spearman = Pearson of ranks
        else:
            _rho = float("nan")
        style_fig(fig, height=480).update_layout(
            title=f"Rating vs Price (Spearman ρ = {_rho:.3f})",
            xaxis_range=[0, price_range[1]])
        st.plotly_chart(fig, use_container_width=True)
    INS.box("rating_vs_price", st=st)

    # histogram harga
    fig = px.histogram(df[df["effective_price"] <= price_range[1]],
                       x="effective_price", nbins=60, color="brand_tier",
                       color_discrete_map={"Premium": C["red"],
                                           "Mainstream": C["grey"],
                                           "Value": C["primary"]},
                       barmode="stack",
                       labels={"effective_price": "Effective price (£)"})
    style_fig(fig, height=360).update_layout(title="Price Distribution (all filtered products)")
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("#### Sebaran harga per kategori (boxplot ECharts)")
    st.caption("Boxplot jauh lebih informatif dari bar rata-rata: garis tengah = "
               "**median**, kotak = **50% produk tengah**, titik = **produk "
               "pencilan** (sangat mahal/murah). Kategori dengan kotak panjang "
               "punya rentang harga sangat lebar.")
    try:
        _bc = df[df["effective_price"] <= price_range[1]]
        _bycat = (_bc.groupby("cat1")["effective_price"].apply(list)
                  .sort_values(key=lambda s: s.map(len), ascending=False).head(15))
        if len(_bycat):
            EC.boxplot(
                categories=[str(k)[:18] for k in _bycat.index],
                values=[list(v) for v in _bycat.values],
                title="Sebaran harga efektif per kategori (£)",
                yname="harga (£)", height=500)
    except Exception as _e:  # noqa: BLE001
        st.caption(f"boxplot tak tersedia ({_e}).")
    INS.box("echarts_boxplot", st=st)

# ============================== PROMOTIONS ==============================
with tab_promo:
    X.render("promo_by_category", st=st)
    c1, c2 = st.columns(2)
    with c1:
        t = (df.groupby("cat1")
             .agg(promo=("is_promo", "mean"), n=("is_promo", "size"))
             .reset_index())
        t["promo_pct"] = (t["promo"] * 100).round(1)
        t = t.sort_values("promo_pct")
        fig = px.bar(t, x="promo_pct", y="cat1", orientation="h",
                     color="promo_pct", color_continuous_scale="Oranges",
                     text="promo_pct",
                     labels={"promo_pct": "Promo rate (%)", "cat1": ""})
        fig.update_traces(texttemplate="%{text}%", textposition="outside")
        style_fig(fig).update_layout(coloraxis_showscale=False,
                                     title="Promotion Rate by Category")
        st.plotly_chart(fig, use_container_width=True)
    with c2:
        t = df[df["is_promo"] & df["discount_pct"].notna()]
        fig = px.box(t, x="cat1", y="discount_pct", color="cat1",
                     color_discrete_sequence=CAT_COLORS,
                     labels={"discount_pct": "Discount (%)", "cat1": ""})
        style_fig(fig, height=480).update_layout(
            title="Discount Depth when on Promotion", showlegend=False)
        fig.update_xaxes(tickangle=-35, tickfont=dict(size=9))
        st.plotly_chart(fig, use_container_width=True)

    c3, c4 = st.columns([1.2, 1])
    with c3:
        t = df["promo_type"].fillna("(none)").value_counts().head(8).reset_index()
        t.columns = ["type", "count"]
        fig = px.bar(t, x="count", y="type", orientation="h",
                     color="count", color_continuous_scale="Oranges", text="count")
        fig.update_traces(textposition="outside")
        style_fig(fig, height=340).update_layout(
            coloraxis_showscale=False, title="Promotion Types")
        st.plotly_chart(fig, use_container_width=True)
    with c4:
        t = df[df["is_promo"]].groupby("cat1")["discount_pct"].mean() \
            .round(1).sort_values(ascending=False).reset_index()
        st.markdown("##### Avg discount by category")
        st.dataframe(t.rename(columns={"cat1": "Category",
                                       "discount_pct": "Avg discount %"}),
                     use_container_width=True, hide_index=True, height=340)

    # scatter: harga vs diskon
    sub = df[df["is_promo"] & df["discount_pct"].notna()]
    fig = px.scatter(sub, x="effective_price", y="discount_pct",
                     color="cat1", color_discrete_sequence=CAT_COLORS,
                     opacity=0.5, hover_data=["brand", "name"],
                     labels={"effective_price": "Effective (promo) price (£)",
                             "discount_pct": "Discount (%)", "cat1": "Category"})
    style_fig(fig, height=400).update_layout(
        title="Promo Price vs Discount Depth", xaxis_range=[0, price_range[1]])
    st.plotly_chart(fig, use_container_width=True)
    INS.box("promo_by_category", st=st)

# ============================== BRANDS ==============================
with tab_brand:
    X.render("brand_positioning", st=st)
    X.render("own_brand", st=st)
    c1, c2 = st.columns([1, 1])
    with c1:
        t = df["brand"].value_counts().head(20).sort_values().reset_index()
        t.columns = ["brand", "count"]
        fig = px.bar(t, x="count", y="brand", orientation="h",
                     color="count", color_continuous_scale="Greens", text="count")
        fig.update_traces(textposition="outside")
        style_fig(fig, height=560).update_layout(
            coloraxis_showscale=False, title="Top 20 Brands by SKU Count")
        st.plotly_chart(fig, use_container_width=True)
        INS.box("own_brand", st=st)
    with c2:
        bp = (df.groupby("brand")
              .agg(products=("product_id", "size"),
                   price_index=("price_index", "median"),
                   rating=("rating", "median"))
              .reset_index())
        bp = bp[bp["products"] >= 5]
        fig = px.scatter(bp, x="price_index", y="rating",
                         size="products", color="price_index",
                         color_continuous_scale="RdYlGn_r",
                         hover_name="brand", size_max=30,
                         labels={"price_index": "Price index (÷ category median)",
                                 "rating": "Median rating"})
        fig.add_vline(x=1.0, line_dash="dash", line_color="#9AA7B4")
        style_fig(fig, height=560).update_layout(
            coloraxis_showscale=False,
            title="Brand Positioning (color: red=premium, green=value)")
        st.plotly_chart(fig, use_container_width=True)
        INS.box("brand_positioning", st=st)

    # bar: premium vs value share
    t = (df.groupby("cat1")["brand_tier"]
         .value_counts(normalize=True).mul(100).round(1)
         .unstack(fill_value=0).reset_index())
    fig = go.Figure()
    for tier, col in [("Premium", C["red"]), ("Value", C["primary"])]:
        if tier in t.columns:
            fig.add_bar(x=t["cat1"], y=t[tier], name=tier, marker_color=col)
    fig.update_layout(barmode="group")
    style_fig(fig, height=420).update_layout(
        title="Premium vs Value Share by Category",
        yaxis_title="% of SKUs", xaxis_title="")
    fig.update_xaxes(tickangle=-35, tickfont=dict(size=9))
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("#### Top brand — bar bertitik (pictorialBar ECharts)")
    st.caption("PictorialBar menampilkan jumlah SKU sebagai **blok bertitik** — "
               "lebih menarik secara visual untuk laporan klien, dengan pesan "
               "yang sama jelasnya: brand mana yang punya lini produk terlebar.")
    try:
        _tb = df["brand"].value_counts().head(14)
        EC.pictorial_bar(
            categories=[str(b)[:16] for b in _tb.index],
            values=[int(v) for v in _tb.values],
            symbol="rect", title="Top brand menurut jumlah SKU",
            yname="jumlah SKU", height=440)
    except Exception as _e:  # noqa: BLE001
        st.caption(f"pictorialBar tak tersedia ({_e}).")
    INS.box("echarts_pictorial", st=st)

# ============================== VALUE ==============================
with tab_value:
    X.render("value_winners", st=st)
    st.markdown("#### ⭐ Top value-for-money products")
    st.caption(f"Rating tinggi + harga per-100g rendah · min {min_reviews} reviews")
    sub = df[(df["reviews"] >= min_reviews) & df["rating"].notna()
             & df["price_per_100g"].notna()].copy()
    if len(sub):
        pr = sub["price_per_100g"].rank(pct=True)
        rr = sub["rating"].rank(pct=True)
        sub["value_score"] = (rr * 0.6 + (1 - pr) * 0.4)
        top = sub.sort_values("value_score", ascending=False).head(15)
        fig = px.bar(top.sort_values("value_score"), x="value_score", y="name",
                     orientation="h", color="value_score",
                     color_continuous_scale="YlGn", hover_data=["brand", "effective_price",
                                                                "price_per_100g", "rating"],
                     labels={"value_score": "Value score", "name": ""})
        style_fig(fig, height=520).update_layout(coloraxis_showscale=False,
                                                 title="Value Score Leaderboard")
        st.plotly_chart(fig, use_container_width=True)

        st.markdown("##### 📋 Detail tabel")
        show = top[["brand", "name", "cat1", "effective_price",
                    "price_per_100g", "rating", "reviews", "value_score"]]
        st.dataframe(show, use_container_width=True, hide_index=True)
    else:
        st.info("Tidak ada produk yang cocok dengan filter. Turunkan 'Min reviews'.")
    INS.box("value_winners", st=st)

# ---------------------------------------------------------------- footer
st.markdown(
    f"""
    <hr style="border-color:#2A3038;">
    <div style="color:{C['grey']};font-size:0.8rem;text-align:center;">
      📊 Morrisons UK Market Intelligence · data scraped from groceries.morrisons.com
      · built with Streamlit + Plotly · by <b>Sandi Ridwan</b><br>
      ⚠️ Rating available for 99.7% of products · prices are a single snapshot in time
    </div>
    """, unsafe_allow_html=True)
