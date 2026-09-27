# 📐 Tableau Dashboard — Layout Blueprint
## Morrisons UK Grocery Market Intelligence

> **Tujuan dokumen ini:** spesifikasi teknis yang bisa langsung dieksekusi di
> Tableau Desktop/Public untuk membangun **1 dashboard utama** + 3 sub-dashboard
> dari data `data/processed/morrisons_clean.csv`.

---

## ⚡ Cara Tercepat: Pakai Bundel Siap-Pakai

Daripada menyiapkan data + calculated field manual, pakai bundel yang **sudah jadi**:

```
data/tableau/Tableau_Morrisons/
├── products.hyper      # 18.291 produk (extract native Tableau)
├── morrisons.tds       # datasource (buka langsung di Tableau)
└── CARA_PAKAI.md       # resep drag-and-drop 10 worksheet
```

Buka `morrisons.tds` di Tableau → semua kolom (`Category`, `Price Tier`,
`Effective Price`, `Value Score`, …) **sudah dihitung** → tinggal drag.

> Bundel ini dibuat oleh `src/build_tableau_hyper.py` dan **sudah diverifikasi
> terbuka bersih di Tableau Public Desktop 2026.2** (nol error di log).
>
> ⚠️ Mencoba menulis file `.twb` penuh secara programatik **gagal** (error skema
> `D2E8DA72`) — skema internal `.twb` terlalu ketat untuk disusun tanpa GUI.
> Pelajaran: kirim data dalam format native (`.hyper`) + datasource (`.tds`),
> bukan workbook penuh.

---

## 0. Persiapan Data (alternatif manual)

### 0.1 Koneksi
- **Sumber:** `data/processed/morrisons_clean.csv` (Text file)
- Di Tableau Hub → Connect → Text file → pilih CSV.

### 0.2 Cek Tipe Field
Setelah import, pastikan tipe field berikut benar (Tableau kadang salah tebak):

| Field | Tipe Tableau | Peran |
|-------|--------------|-------|
| `product_id` | String (Dimension) | ID |
| `name` | String (Dimension) | Nama produk |
| `brand` | String (Dimension) | Brand |
| `cat1` | String (Dimension) | **Kategori utama** |
| `cat2` | String (Dimension) | Sub-kategori |
| `price` | Number (Decimal) (Measure) | Harga tampil |
| `effective_price` | Number (Decimal) (Measure) | **Harga dibayar (pakai ini!)** |
| `list_price` | Number (Decimal) (Measure) | Harga normatif |
| `unit_price` | Number (Decimal) (Measure) | Harga satuan |
| `price_per_100g` | Number (Decimal) (Measure) | Harga per 100g |
| `rating` | Number (Decimal) (Measure) | Rating |
| `reviews` | Integer (Measure) | Jumlah review |
| `is_promo` | Boolean (Dimension) | Status promo |
| `discount_pct` | Number (Decimal) (Measure) | % diskon |
| `desc_len` | Integer (Measure) | Panjang deskripsi |

### 0.3 Calculated Fields (buat dulu sebelum sheet)

```
// 1. Jumlah produk (base measure)
[Product Count]          = COUNTD([product_id])

// 2. Promo rate (%)
[Promo Rate %]           = SUM(INT([is_promo])) / [Product Count]

// 3. Label harga
[Price Label]            = "£" + STR(ROUND([effective_price], 2))

// 4. Tier harga relatif kategori (sesuai analysis.py)
[Price Index]            =
  [effective_price]
  / {FIXED [cat1] : MEDIAN([effective_price])}

[Brand Tier]             =
  IF [Price Index] >= 1.15 THEN "Premium"
  ELSEIF [Price Index] <= 0.85 THEN "Value"
  ELSE "Mainstream" END

// 5. Value score (60% rating + 40% murah) — untuk sheet "Value Winners"
[Rating Rank]            = RANK_PERCENTILE(AVG([rating]))
[Price-per-100g Rank]    = RANK_PERCENTILE(AVG([price_per_100g]))
[Value Score]            = ([Rating Rank] * 0.6) + ((1 - [Price-per-100g Rank]) * 0.4)

// 6. KPI Promo Rate (untuk BAN)
[Promo Rate KPI]         = AVG([Promo Rate %])
```

### 0.4 Filter Global
- Tambahkan **Data Source Filter**: `is_promo` = ALL (biar bisa toggle)
- Buat **Parameter** `pTop N` (Integer, default 15) → dipakai di sheet leaderboard
- Buat **Parameter** `pMin Reviews` (Integer, default 10) → filter value winners

---

## 1. LAYOUT DASHBOARD UTAMA

Nama dashboard: **"Market Intelligence — Overview"**
Ukuran: **1366 × 900** (Desktop) atau 1200×800.

```
┌──────────────────────────────────────────────────────────────────────────┐
│  🏷️  HEADER  (h=70)                                                        │
│  Morrisons UK — Grocery Market Intelligence                                │
│  [KPI BAND — 5 angka besar]                                                │
├──────────┬──────────┬──────────┬──────────┬──────────┬─────────────────────┤
│ KPI BAND (h=110)                                                           │
│  18,100  │  £2.70   │  26.4%   │  −23.1%  │ £0.08    │  ← 5 BAN           │
│  Produk  │ Median   │  Promo   │ Med Dis  │ …        │                      │
│          │ Harga    │  Rate    │ count    │          │                      │
├──────────┴──────────┴──────────┴──────────┴──────────┴─────────────────────┤
│                                                                            │
│  ┌─────────────────────────────┐ ┌──────────────────────────────────────┐ │
│  │ 01. PRICE BY CATEGORY       │ │ 02. PROMO RATE BY CATEGORY           │ │
│  │ Bar chart horizontal        │ │ Bar chart horizontal (sorted)        │ │
│  │ h=280                       │ │ h=280                                │ │
│  └─────────────────────────────┘ └──────────────────────────────────────┘ │
│                                                                            │
│  ┌───────────────────────────────┐ ┌────────────────────────────────────┐ │
│  │ 03. BRAND POSITIONING         │ │ 04. OWN-BRAND OPPORTUNITY          │ │
│  │ Scatter: price_index vs rating│ │ Stacked/grouped bar premium vs val │ │
│  │ h=280                         │ │ h=280                              │ │
│  └───────────────────────────────┘ └────────────────────────────────────┘ │
│                                                                            │
│  ┌──────────────────────────────────────┐ ┌─────────────────────────────┐│
│  │ 05. RATING VS PRICE (hexbin/scatter)  │ │06. TOP VALUE FOR MONEY (table)│
│  │ h=260                                 │ │ h=260                        ││
│  └──────────────────────────────────────┘ └─────────────────────────────┘│
└──────────────────────────────────────────────────────────────────────────┘
```

**Grid:** 12 kolom, gutter 8px, padding dashboard 12px.
**Kontrol di header:** Filter `cat1` (dropdown multi-select) + toggle `is_promo` + parameter Top N.

---

## 2. SPESIFIKASI TIAP SHEET

### Sheet 1 — KPI Bands (5 angka)
Bukan sheet chart; gunakan **text objects / BAN worksheet**.

Buat worksheet `KPI_Products`:
- Marks = Text
- Text = `ATTR([Product Count])` (atau pakai Measure Names/Values trick)
- Format: font 36 bold, color `#1F5C3D`

Ulangi untuk 5 KPI:

| KPI | Nilai | Warna |
|-----|-------|-------|
| Total Produk | 18,100 | `#1F5C3D` |
| Median Harga | £2.70 | `#22303C` |
| Promo Rate | 26.4% | `#E4A11B` |
| Median Diskon | −23.1% | `#C0392B` |
| Brand Unik | 2,600 | `#2E6F95` |

> 💡 Cara cepat: satukan ke satu worksheet dengan 5 calculated `MIN(1)` di Rows/Columns + Measure Values. Alternatif paling simpel: 5 text boxes di dashboard.

---

### Sheet 2 — `Price by Category`
**Chart type:** Horizontal Bar + Error Bar (P10/P90).
- Rows: `cat1`
- Columns: `MEDIAN([effective_price])`
- Sort: descending by median
- Label: `[Price Label]`
- Untuk whisker P10–P90: tambahkan reference / dual danau — di Tableau pakai
  **Analytics pane → Reference Line** dari `PERCENTILE([effective_price], 0.10)`
  dan `0.90`.
- Color: `#1F5C3D`.
- Title: "Median Price by Category".

**Ukuran di dashboard:** w=6 grid, h≈280.

---

### Sheet 3 — `Promo Rate by Category`
- Rows: `cat1`
- Columns: `[Promo Rate %]`
- Format as %
- Sort descending
- Color: highlight max dengan `#E4A11B` (via calculated color), sisanya `#8B9AA6`.
- Label: promo rate + avg discount (`AVG([discount_pct])`).
- Title: "Promotion Intensity by Category".

---

### Sheet 4 — `Brand Positioning`
**Chart type:** Scatter.
- Columns: `MEDIAN([Price Index])`
- Rows: `MEDIAN([rating])`
- Detail: `brand`
- Size: `[Product Count]`
- Color: `[Brand Tier]` → Premium `#C0392B`, Value `#1F5C3D`, Mainstream `#8B9AA6`
- Reference line di x=1.0 (garis kategori median).
- Filter: `Product Count >= 10` (biar tidak noise).
- Tooltip: brand, median harga, jumlah SKU, rating.
- Title: "Brand Price Positioning vs Rating".

---

### Sheet 5 — `Own-Brand Opportunity`
**Chart type:** Grouped horizontal bar.
- Rows: `cat1`
- Columns: dua measure → `Premium Share %` & `Value Share %`
  (buat calculated: `SUM(IF [Brand Tier]="Premium" THEN 1 ELSE 0 END)/[Product Count]`)
- Bisa pakai **Measure Values** dengan dua measure.
- Sort by gap descending.
- Color: premium `#C0392B`, value `#1F5C3D`.
- Title: "Own-Brand Opportunity (premium vs value share)".

---

### Sheet 6 — `Rating vs Price`
**Chart type:** Scatter (density).
- Columns: `effective_price` (clip ≤ 30 via calculated `MIN([effective_price],30)`)
- Rows: `rating`
- Detail: `product_id`
- Opacity: 40%; Color: `#1F5C3D`
- Reference line vertikal median harga; horizontal median rating.
- Bila perlu density: gunakan dual + transparansi tinggi (Tableau tak punya hexbin
  native; scatter ber-transparansi cukup).
- Title: "Rating vs Price (ρ = 0.08)".

---

### Sheet 7 — `Top Value for Money`
**Chart type:** Table / Bar (top N).
- Filter: `reviews >= [pMin Reviews]`, `rating` not null
- Sort by `[Value Score]` descending, Top = `[pTop N]`
- Rows: `name`
- Text: Value Score, `price_per_100g`, rating.
- Color gradient pada value score (sequential kuning→hijau).
- Title: "Top Value-for-Money Products".

---

### Sheet 8 — `Brand Leaderboard`
- Rows: `brand`
- Columns: `[Product Count]`
- Sort descending, Top `[pTop N]` by Product Count
- Color: `#1F5C3D`
- Label: SKU + jumlah kategori + median rating.
- Title: "Brand Leaderboard — Shelf Presence".

---

### Sheet 9 — `Category Portfolio (donut)`
- Pie → ubah ke Donut (dual-axis trick).
- Angle: `[Product Count]`
- Label: `ATTR([cat1])` + % of total.
- Palette: pakai PALETTE dari make_charts.py.
- Title: "Assortment Share".

---

### Sheet 10 — `Content Completeness`
- Rows: `cat1`
- Columns: `AVG([desc_len])` atau `% with description`
- Chart: bar + reference line target (mis. 90%).
- Color: `#2E6F95`.
- Title: "Product Content Completeness".

---

## 3. INTERAKSI & FILTER DASHBOARD

| Aksi | Setup |
|------|-------|
| Klik kategori di sheet 2 → filter semua sheet | **Dashboard → Actions → Filter** (source: cat1) |
| Hover brand → highlight | **Highlight Action** |
| Filter kategori global | Parameter dropdown / filter card di kanan-atas |
| Toggle "hanya promo" | Parameter boolean → calculated filter |
| Reset | Tombol "Reset" via parameter action |

---

## 4. TEMA & FORMAT VISUAL

**Palet (samakan dengan chart PNG agar konsisten):**
```
Primary (Morrisons green) : #1F5C3D
Accent (yellow)           : #E4A11B
Dark (text)               : #22303C
Grey                      : #8B9AA6
Red (premium/alert)       : #C0392B
Blue                      : #2E6F95
Background                : #FFFFFF
Gridline                  : #EEEEEE
```

**Format angka:**
- Mata uang: `£#,##0.00`
- Persen: `0.0%`
- Hitungan: `#,##0`

**Font:** Tableau Book / Semibold. Judul 14–16, body 10–11.

**Judul dashboard:** kiri-atas, ada subjudul kecil "Real scraped data · n=18,100 products".

---

## 5. URUTAN PENGERJAAN (Checklist)

- [ ] Import CSV, perbaiki tipe field
- [ ] Buat semua Calculated Fields (§0.3)
- [ ] Buat 10 worksheet satu per satu (§2)
- [ ] Buat dashboard baru ukuran 1366×900
- [ ] Susun layout per grid (§1)
- [ ] Tambah KPI band
- [ ] Tambah filter & actions (§3)
- [ ] Terapkan palet & format (§4)
- [ ] Simpan ke Tableau Public → dapat URL
- [ ] Tempel URL ke README.md

---

## 6. FILE PENDUKUNG YANG TERSEDIA

Agar pembangunan lebih cepat, gunakan tabel insight yang sudah jadi di
`reports/tables/` sebagai **alternatif data source** untuk sheet tertentu
(lebih ringan & angka sudah final):

| Tableau Sheet | Bisa pakai file |
|---------------|-----------------|
| Price by Category | `reports/tables/price_by_category.csv` |
| Promo by Category | `reports/tables/promo_by_category.csv` |
| Brand Positioning | `reports/tables/brand_positioning.csv` |
| Own-Brand Opportunity | `reports/tables/own_brand_opportunity.csv` |
| Brand Leaderboard | `reports/tables/brand_leaderboard.csv` |
| Value for Money | `reports/tables/value_for_money.csv` |
| Content Completeness | `reports/tables/content_completeness.csv` |
| Rating by Quartile | `reports/tables/rating_by_price_quartile.csv` |

---

## 7. CATATAN EDITORIAL

- **Jangan** pakai kolom `price` untuk KPI — pakai **`effective_price`**
  (harga yang benar-benar dibayar). Lihat `REPORT.md` §2 soal jebakan ini.
- Sertakan catatan keterbatasan (rating hanya 33% produk) di dashboard sebagai
  text kecil — ini menunjukkan kejujuran analitis.
- Nama sheet di dashboard sebaiknya berbahasa Inggris; narasi/tooltip boleh dwibahasa.

---

*Blueprint ini melengkapi project `morrisons-market-intelligence` — dibuat oleh Sandi Ridwan.*
