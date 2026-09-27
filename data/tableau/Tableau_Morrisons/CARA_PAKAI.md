# 📊 Tableau — Cara Membangun Dashboard Morrisons (2–3 menit)

Bundel ini berisi data siap-pakai untuk Tableau Public Desktop.
Semua **calculated field sudah dihitung** — kamu tinggal **drag & drop**.

---

## 📁 Isi Bundel

| File | Isi |
|------|-----|
| `products.hyper` | **18.291 produk** (extract Tableau, format native) |
| `morrisons.tds` | Datasource — sudah menunjuk ke `products.hyper` |
| `CARA_PAKAI.md` | File ini |

**Kolom yang tersedia** (sudah rapi, tanpa perlu menghitung):

| Kolom | Tipe | Isi |
|-------|------|-----|
| `Category` | Dimension | 19 kategori |
| `Subcategory` | Dimension | sub-kategori |
| `Brand` | Dimension | 2.600+ brand |
| `Price Tier` | Dimension | **Premium / Mainstream / Value** (sudah dihitung) |
| `Product` | Dimension | nama produk |
| `Effective Price` | Measure | **harga dibayar** (promo jika ada) |
| `Price per 100g` | Measure | harga satuan (value analysis) |
| `Rating` | Measure | **-1 = belum ada rating** (disaring di view) |
| `Reviews` | Measure | jumlah review |
| `Discount Pct` | Measure | % diskon (0 = tidak promo) |
| `Is Promo` | Dimension | True/False |
| `Value Score` | Measure | skor value (0–1, -1 = tak berlaku) |

> ⚠️ **Rating = -1 artinya produk belum punya rating** (66% produk). Saat analisis
> rating, tambahkan filter `Rating >= 0`.

---

## 🚀 Buka Data (1 langkah)

**Cara A — lewat file .tds (paling cepat):**
1. Buka **Tableau Public Desktop**
2. `File` → `Open` → pilih **`morrisons.tds`**
3. Tableau terbuka di jendela Data Source → klik **`Sheet 1`** (kiri bawah) → mulai buat chart

**Cara B — lewat hyper langsung:**
1. `Connect` → `More...` → `Tableau Extract` → pilih **`products.hyper`**
2. Klik `Sheet 1`

---

## 🎨 Resep 10 Worksheet (drag saja)

Untuk tiap worksheet di bawah: **Rows** = taruh di baris, **Columns** = kolom, lalu pilih mark type.

### 1️⃣ Median Price by Category  *(bar horizontal)*
- `Category` → **Rows**
- `Effective Price` → **Columns** → ubah aggregasi ke **Median** (klik kanan measure → Measure → Median)
- Sort: descending (klik ikon sort di toolbar)
- Label: drag `Effective Price` lagi ke **Label**

### 2️⃣ Promotion Rate by Category  *(bar)*
- `Category` → **Rows**
- `Is Promo` → **Columns** → ubah ke **Average**
- Format sebagai % (klik kanan sumbu → Format → Numbers → Percentage)
- Sort descending

### 3️⃣ Products by Brand (Top 20)  *(bar)*
- `Brand` → **Rows**
- `Product` → **Columns** → **Count (Distinct)** atau `Number of Records`
- Filter: drag `Brand` ke Filters → **Top** → By field → Top 20

### 4️⃣ Brand Positioning  *(scatter)*
- `Price Tier` → **Color**
- `Effective Price` (avg) → **Columns**
- `Rating` (avg) → **Rows**
- `Brand` → **Detail**
- Filter: `Rating >= 0`
- Tambah garis referensi di x = 1.0 (Analytics pane → Reference Line)

### 5️⃣ Rating vs Price  *(scatter)*
- `Effective Price` → **Columns**
- `Rating` → **Rows**
- `Price Tier` → **Color**
- Filter: `Rating >= 0`

### 6️⃣ Discount Depth by Category  *(box plot)*
- `Category` → **Columns**
- `Discount Pct` → **Rows**
- Filter: `Is Promo = True`
- Analytics → Box Plot

### 7️⃣ Product Count by Price Tier  *(bar / donut)*
- `Price Tier` → **Color** + **Angle** (donut) atau **Columns** (bar)
- `Number of Records` → **Angle/Size**

### 8️⃣ Top Value-for-Money (table)  *(table)*
- `Product` → **Rows**
- `Value Score`, `Effective Price`, `Price per 100g`, `Rating` → **Text**
- Filter: `Value Score >= 0` → Sort desc

### 9️⃣ Avg Unit Price by Category  *(bar)*
- `Category` → **Rows**
- `Price per 100g` → **Columns** → **Average**

### 🔟 KPI Total Products  *(single value)*
- `Number of Records` → **Text** → format besar (font 36+)

---

## 🖥️ Rakit Dashboard

1. Klik ikon **New Dashboard** (bawah)
2. Set size: **1366 × 800**
3. Drag worksheet ke kanvas:
```
┌─────────────────────────────────────────────┐
│  KPI Total Products │ KPI Avg Price │ ...   │  ← baris atas (KPI)
├──────────────────────┬──────────────────────┤
│  Median Price        │  Promotion Rate      │
├──────────────────────┼──────────────────────┤
│  Brand Positioning   │  Products by Brand   │
├──────────────────────┴──────────────────────┤
│  Rating vs Price    │  Discount Depth       │
└─────────────────────────────────────────────┘
```
4. Tambah **Filter tindakan**: Dashboard → Actions → Add Action → Filter → Source: Category

---

## 🎨 Tema Warna (opsional, agar cocok dengan chart PNG)

Klik mark → **Color** → **Edit Colors** → masukkan hex:
```
Morrisons Green : #1F5C3D
Accent Yellow   : #E4A11B
Red (premium)   : #C0392B
Blue            : #2E6F95
Grey            : #8B9AA6
```

---

## 📤 Publish ke Tableau Public

`File` → `Save to Tableau Public` → login → otomatis dapat URL publik.
Tempel URL ke README utama portofolio.

---

## ℹ️ Catatan Teknis

- Data bersumber dari `morrisons_clean.csv` (18.291 baris, hasil parser).
- `Effective Price` & `Price Tier` & `Value Score` dihitung sama seperti
  `analysis.py` — sudah konsisten dengan laporan & dashboard Streamlit.
- Extract `.hyper` dibuat dengan **Tableau Hyper API** (bukan file kosong).

*Dibuat oleh Sandi Ridwan · project `morrisons-market-intelligence`.*
