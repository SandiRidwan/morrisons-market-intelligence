<div align="center">

<img src="https://readme-typing-svg.demolab.com?font=Orbitron&weight=900&size=44&duration=3000&pause=1000&color=00FF88&center=true&vCenter=true&width=760&height=70&lines=MORRISONS+MARKET+INTELLIGENCE" alt="Morrisons Market Intelligence" />

<img src="https://readme-typing-svg.demolab.com?font=Fira+Code&weight=700&size=16&duration=2500&pause=800&color=00FF88&center=true&vCenter=true&multiline=true&width=900&height=50&lines=18%2C100+Products+%E2%86%92+Parser+%E2%86%92+Insight+%E2%86%92+Interactive+Dashboard" alt="Tagline" />

<br/>

![Python](https://img.shields.io/badge/Python-3.10+-00FF88?style=for-the-badge&logo=python&logoColor=black)
![pandas](https://img.shields.io/badge/pandas-2.0-150458?style=for-the-badge&logo=pandas&logoColor=white)
[![Streamlit](https://img.shields.io/badge/Streamlit-Live_App-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)](https://morrisons-market-intelligence-6efv7fvigz9jlrz6fhlmdm.streamlit.app/)
[![Open Dashboard](https://img.shields.io/badge/▶_Live_Demo-Open_Dashboard-00FF88?style=for-the-badge)](https://morrisons-market-intelligence-6efv7fvigz9jlrz6fhlmdm.streamlit.app/)
![Plotly](https://img.shields.io/badge/Plotly-Interactive-3F4F75?style=for-the-badge&logo=plotly&logoColor=white)
![Tableau](https://img.shields.io/badge/Tableau-Blueprint-E97627?style=for-the-badge&logo=tableau&logoColor=white)
![Products](https://img.shields.io/badge/Products-11%2C208-00FF88?style=for-the-badge)
![Categories](https://img.shields.io/badge/Categories-13-00FF88?style=for-the-badge)
![License](https://img.shields.io/badge/License-MIT-0D1117?style=for-the-badge)

</div>

---

```
╔══════════════════════════════════════════════════════════════════════════╗
║                                                                          ║
║   ███╗   ███╗ ██████╗ ██████╗ ██████╗ ██╗███████╗ ██████╗ ███╗   ██╗     ║
║   ████╗ ████║██╔═══██╗██╔══██╗██╔══██╗██║██╔════╝██╔═══██╗████╗  ██║     ║
║   ██╔████╔██║██║   ██║██████╔╝██████╔╝██║███████╗██║   ██║██╔██╗ ██║     ║
║   ██║╚██╔╝██║██║   ██║██╔══██╗██╔══██╗██║╚════██║██║   ██║██║╚██╗██║     ║
║   ██║ ╚═╝ ██║╚██████╔╝██║  ██║██║  ██║██║███████║╚██████╔╝██║ ╚████║     ║
║   ╚═╝     ╚═╝ ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝╚══════╝ ╚═════╝ ╚═╝  ╚═══╝     ║
║                                                                          ║
║   GROCERY MARKET INTELLIGENCE · 11,208 PRODUCTS · STREAMLIT + TABLEAU    ║
╚══════════════════════════════════════════════════════════════════════════╝
```

---

## 🎬 Demo

<div align="center">

### ▶️ [**Buka Live Dashboard →**](https://morrisons-market-intelligence-6efv7fvigz9jlrz6fhlmdm.streamlit.app/)

[![Open in Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://morrisons-market-intelligence-6efv7fvigz9jlrz6fhlmdm.streamlit.app/)

<img src="reports/figures/dashboard_overview.png" width="880" alt="Interactive dashboard" />
<br/>
<sub><i>Interactive Streamlit dashboard — live filters, 5 tabs, 12+ charts · 11,208 real scraped products</i></sub>

</div>

**Run locally:**

```bash
streamlit run app/dashboard.py     # → http://localhost:8501
```

---

## 🧠 Overview

**Morrisons Market Intelligence** is an end-to-end data analyst project: it takes
the hard-to-get output of a retail scraping pipeline (11,208 products, 60 raw
columns of semi-structured data), cleans it, and turns it into **actionable
competitive insight** for pricing, marketing, and product teams — delivered as an
interactive dashboard, a business report, and a Tableau blueprint.

Continues the data-collection pipeline from
[`morrisons-product-scraper`](https://github.com/SandiRidwan/morrisons-product-scraper)
(reverse-engineered internal API + Playwright).

<div align="center">

| Metric | Value |
|-------:|:------|
| 🎯 Source | groceries.morrisons.com — **fresh scrape 2026** (new API) |
| 📦 Products analysed | **11,208** (from 18,291 raw rows) |
| 🗂️ Categories | 15 retail categories |
| 🏢 Brands | **1,955** unique brands |
| 💷 Price range | £0.15 – £300.00 (median **£2.70**) |
| 🏷️ On promotion | **21.9%** of SKUs (median discount −25.0%) |
| ⭐ Price↔quality | Spearman ρ = **−0.145** — cheaper rated higher |
| 🧩 Key trap caught | Column `Price` = *display* price (often "Was"); real promo price hidden in `others3` |
| 🖥️ Deliverables | Streamlit app · 10 charts · 10 insight tables · business `REPORT.md` · **Tableau bundle (`.hyper` + `.tds`, verified opening clean)** |
| 📁 Outputs | `reports/figures/` · `reports/tables/` · `data/tableau/` · `REPORT.md` |

</div>

---

## 🏗️ Architecture

```
┌──────────────────────────────────────────────────────────────────────┐
│                    morrisons_parser.py  (BRONZE → SILVER)             │
│   60 raw columns, info embedded in STRINGS → clean 24-column table    │
│   "£3.20" · "Rating: 4.6 (12 reviews)" · "Now £1.75, Was £2"          │
└──────────────────────────────┬───────────────────────────────────────┘
                               │
                               ▼
┌──────────────────────────────────────────────────────────────────────┐
│                        analysis.py  (GOLD)                            │
│   15+ pure, reusable insight functions                                │
│   price · promo · brand positioning · value · own-brand gap           │
└───────────────┬───────────────────────────────┬──────────────────────┘
                │                               │
                ▼                               ▼
┌───────────────────────────┐       ┌───────────────────────────────┐
│   make_charts.py          │       │   app/dashboard.py            │
│   10 static PNG charts    │       │   Streamlit + Plotly          │
│   (report / slides)       │       │   live filters · 5 tabs       │
└───────────────────────────┘       └───────────────────────────────┘
                │                               │
                └───────────────┬───────────────┘
                                ▼
                  ✅ Insight + recommendation · reproducible in seconds
```

---

## ⚡ Technical Challenges Solved

### Challenge 1 — The `Price` Column Trap (silent data corruption)

**Problem:** The scraped `Price` column often held the **display price** — which is frequently the *"Was"* price — while the real price a customer pays (the *"Now"* value) was buried inside a **text** field, `others3`. Trusting `Price` directly would have **systematically overstated** every price in the analysis, silently.

**Solution:** A dedicated parser recovers the true promo price and computes `effective_price` (promo if present, else list), then **every** metric uses `effective_price` — never the raw column.

```python
# ❌ Raw column: "£2.00" is the WAS price, not what you pay
row["Price"]            # "£2.00"
row["others3"]          # "Promotions: Now £1.75, Was £2"

# ✅ Parse the promo string → real price + discount
# "Now £1.75, Was £2"  →  promo_price=1.75, was=2.00, discount=12.5%
out["effective_price"] = out["promo_price"].fillna(out["price"])
```

---

### Challenge 2 — Semi-Structured Data (info hidden inside strings)

**Problem:** Almost nothing useful was in a clean column. Price, rating, unit
price, and promotions all lived **inside text strings** across 60 columns.

**Solution:** A separate, testable parser module (bronze → silver) with compiled
regex, per-field functions, and derived analytics computed at the end.

```python
"£3.20"                         -> price = 3.20
"Unit Price: £8.00 per kg"      -> unit_price=8.00, basis="kg"
"Rating: 4.6 (12 reviews)"      -> rating=4.6, reviews=12
"Promotions: Now £1.75, Was £2" -> promo_price=1.75, discount=12.5%
```

---

### Challenge 3 — Fair Cross-Category Brand Comparison

**Problem:** Comparing raw brand prices is misleading — comparing biscuits to
champagne tells you nothing about positioning.

**Solution:** A **price index** — brand price ÷ the median of its own category.
`>1.15` = Premium, `<0.85` = Value, else Mainstream.

```python
df["price_index"] = df["effective_price"] / df.groupby("cat1")["effective_price"].transform("median")
df["brand_tier"]  = np.where(df["price_index"] >= 1.15, "Premium",
                    np.where(df["price_index"] <= 0.85, "Value", "Mainstream"))
```

---

### Challenge 4 — A Runtime Column That Never Reached the File

**Problem:** `price_index` and `brand_tier` were built at runtime in `analysis.py`,
so they were **never written to `morrisons_clean.csv`** — the downstream Streamlit
app crashed with `KeyError: 'brand_tier'`.

**Solution:** The app computes its own derived columns on load (`load_data()`),
making it self-sufficient and robust to the CSV's schema.

```python
# In app/dashboard.py — self-contained, no missing-column crash
cat_med = df.groupby("cat1")["effective_price"].transform("median")
df["price_index"] = df["effective_price"] / cat_med
df["brand_tier"]  = np.where(df["price_index"] >= 1.15, "Premium", "Mainstream")
```

---

## 📊 Key Findings

<div align="center">

| # | Question | Finding |
|---|----------|---------|
| Q1 | Price structure by category? | Alcohol dearest & most volatile (median £7.25, spread 305%) |
| Q2 | How aggressive is promotion? | Alcohol 60% & Meat 55% of SKUs on promo (avg −26%) |
| Q3 | Who is premium vs value? | Nicorette 4.40× vs Original Source 0.16× (price index) |
| Q4 | Does price mean quality? | ρ = 0.08 — customers don't rate dearer items higher |
| Q5 | Where is private-label space? | Treats & Snacks (+9.8pp), Baby & Toddler (+9.2pp), Drinks (+8.2pp) |

</div>

| Price by category | Promotion intensity |
|:---:|:---:|
| ![price](reports/figures/01_price_by_category.png) | ![promo](reports/figures/02_promo_rate.png) |

| Brand positioning | Own-brand opportunity |
|:---:|:---:|
| ![brand](reports/figures/03_brand_positioning.png) | ![ownbrand](reports/figures/04_own_brand_gap.png) |

| Rating vs price | Top value products |
|:---:|:---:|
| ![rating](reports/figures/07_rating_by_quartile.png) | ![value](reports/figures/09_value_winners.png) |

---

## 📁 File Structure

```
morrisons-market-intelligence/
├── app/
│   ├── dashboard.py               # ⭐ Interactive Streamlit dashboard
│   └── README.md
├── src/
│   ├── morrisons_parser.py        # bronze → silver: parse raw strings
│   ├── analysis.py                # 15+ pure insight functions
│   ├── make_charts.py             # 10 static visualisations
│   ├── run_analysis.py            # end-to-end orchestrator (one command)
│   ├── build_tableau_extracts.py  # ready-to-import Tableau CSVs
│   ├── make_dashboard_mockup.py   # dashboard layout mockup
│   ├── build_notebook.py          # notebook generator
│   └── generate_sample_data.py    # synthetic demo data
├── notebooks/
│   └── morrisons_market_intelligence.ipynb
├── data/
│   ├── raw/                       # raw scraped CSV (not committed — 45 MB)
│   ├── processed/                 # clean CSV (committed — app runs on clone)
│   └── tableau/
│       ├── Tableau_Morrisons/     # ⭐ ready-to-open bundle
│       │   ├── products.hyper     #    18,291 products (native extract)
│       │   ├── morrisons.tds      #    datasource — open this in Tableau
│       │   └── CARA_PAKAI.md      #    drag-and-drop recipe
│       └── tableau_products.csv   # flat CSV for Tableau/Power BI
├── reports/
│   ├── figures/                   # 11 charts + dashboard screenshots
│   ├── tables/                    # 10 insight tables (CSV)
│   └── summary.json               # headline metrics
├── TABLEAU_DASHBOARD_BLUEPRINT.md # full Tableau build spec
├── REPORT.md                      # full business report
└── requirements.txt
```

---

## 🚀 Quick Start

### 1. Clone & Install

```bash
git clone https://github.com/SandiRidwan/morrisons-market-intelligence.git
cd morrisons-market-intelligence
pip install -r requirements.txt
```

### 2. Run the Dashboard

```bash
streamlit run app/dashboard.py     # → http://localhost:8501
```

### 3. Rebuild the Full Analysis (optional)

```bash
python src/morrisons_parser.py     # raw → clean
python src/run_analysis.py         # insight tables + summary.json
python src/make_charts.py          # 10 charts
python src/build_tableau_extracts.py
```

---

## 📊 Live Run Results

```
Pipeline run — Morrisons UK market intelligence

✅ Parse    morrisons_products.csv (18,291 rows, 60 cols)
              → 11,208 clean rows · 24 cols · price 100% valid
✅ Parse    rating 32.9% · promo 26.6% · unit price 100% recovered
✅ Analyse  price · promo · brand positioning · value · own-brand gap
✅ Charts   10 visualisations generated
✅ Report   REPORT.md + 10 insight tables + summary.json
✅ App      Streamlit dashboard — 5 tabs, live filters
──────────────────────────────────────────────────────────────
   Deliverables: report · charts · dashboard · Tableau blueprint
```

---

## 🛠️ Tech Stack

<div align="center">

| Layer | Technology |
|-------|------------|
| **Language** | Python 3.10+ |
| **Data** | pandas · numpy |
| **Parsing** | regex (compiled, semi-structured → structured) |
| **Visualisation** | matplotlib · Plotly |
| **Dashboard** | Streamlit (interactive web app) |
| **BI Blueprint** | Tableau (spec + ready-to-import extracts) |
| **Data Collection** | Playwright · mitmproxy · curl_cffi (from scraper repo) |

</div>

---

## 🏆 Why This Matters

<div align="center">

| Capability | Companies Hiring For It | Market Value |
|---|---|---|
| Retail price intelligence | CPG, grocery, e-commerce, pricing teams | $40–80/hr |
| Data cleaning & parsing | Any data-driven org | $35–70/hr |
| Interactive dashboard (Streamlit/Tableau) | Product, BI, growth analytics | $50–100/hr |
| **Full chain: scrape → clean → analyse → dashboard** | Rare combined skillset | **$75–150/hr** |

</div>

This project proves the **whole chain**, not just one link: getting hard-to-reach
web data *and* turning it into a decision a business can act on — with a dashboard
a stakeholder can actually click through.

---

## 📝 Lessons Learned

1. **A price column can lie.** The displayed price is often the *"Was"* — the real
   one hides in promo text. Always verify column semantics before analysing.
2. **Parse semi-structured data in a dedicated, testable module** (bronze → silver),
   never inline in a notebook.
3. **Runtime columns don't persist.** Anything computed in memory won't be in the
   CSV — compute it again in the consumer, or write it out.
4. **Fair comparisons need normalisation.** Raw cross-category prices mislead;
   an index against the category median is the honest baseline.
5. **Screenshots are the best dashboard QA.** Headless-click every tab — you catch
   clipped labels and empty charts instantly.
6. **Tableau Public API is read-only.** Programmatic dashboards = Streamlit/Plotly;
   Tableau stays a manual blueprint.

---

## 👤 Author

<div align="center">

<img src="https://readme-typing-svg.demolab.com?font=Orbitron&weight=700&size=20&duration=3000&pause=1000&color=00FF88&center=true&vCenter=true&width=400&lines=Sandi+Ridwan" />

**Data Automation Engineer · Web Scraping Specialist · AI Automation Builder**

📍 Palu, Central Sulawesi, Indonesia

[![Upwork](https://img.shields.io/badge/Upwork-Hire_Me-00FF88?style=for-the-badge&logo=upwork&logoColor=black)](https://www.upwork.com/freelancers/~011f6d0fbb4a372974)
[![LinkedIn](https://img.shields.io/badge/LinkedIn-Connect-0077B5?style=for-the-badge&logo=linkedin&logoColor=white)](https://linkedin.com/in/sandi-ridwan)
[![GitHub](https://img.shields.io/badge/GitHub-Follow-181717?style=for-the-badge&logo=github&logoColor=white)](https://github.com/SandiRidwan)
[![Tableau](https://img.shields.io/badge/Tableau_Public-Profile-E97627?style=for-the-badge&logo=tableau&logoColor=white)](https://public.tableau.com/app/profile/sandi.ridwan)

</div>

---

<div align="center">
<img src="https://readme-typing-svg.demolab.com?font=Fira+Code&size=12&duration=4000&pause=1000&color=00FF88&center=true&vCenter=true&width=760&lines=18%2C100+Products+%7C+Parsed+%7C+Analysed+%7C+Dashboarded+%7C+Telling+stories+from+raw+web+data" />
</div>

---

## 📄 License

MIT License — Educational and portfolio purposes only.
