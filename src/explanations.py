"""
explanations.py
===============
Narasi penjelasan untuk SETIAP chart & tabel di dashboard Morrisons.

STANDAR WAJIB (registry E56): setiap elemen visual wajib punya
  · KENAPA   — mengapa analisis ini dipilih
  · TUJUAN   — pertanyaan bisnis yang dijawab
  · DAMPAK   — implikasi / keputusan yang timbul
  plus CARA BACA bila grafik tidak intuitif.
"""

from __future__ import annotations

EXPLAIN = {
    "price_by_category": {
        "judul": "Median Harga per Kategori",
        "kenapa": "Harga rata-rata bisa menyesatkan karena produk mahal menarik "
                  "nilai ke atas. Median lebih tahan terhadap pencilan dan "
                  "mencerminkan 'produk tipikal' di rak.",
        "tujuan": "Memetakan struktur harga antar-kategori untuk memahami di mana "
                  "nilai belanja pelanggan terkonsentrasi.",
        "dampak": "Kategori dengan median tinggi (mis. alkohol) = margin & nilai "
                  "keranjang besar → prioritas merchandising. Kategori murah = "
                  "volume & frekuensi pembelian.",
        "baca": "Batang = median harga efektif (£); garis whisker = rentang P10–P90 "
                "(sebaran harga).",
    },
    "promo_by_category": {
        "judul": "Tingkat Promosi per Kategori",
        "kenapa": "Promosi berbiaya (margin tergerus). Tanpa peta intensitas, "
                  "retailer tak tahu di mana kompetisi harga paling mahal.",
        "tujuan": "Mengukur seberapa agresif tiap kategori mengandalkan potongan "
                  "harga untuk menarik pembeli.",
        "dampak": "Kategori promo >50% (alkohol, meat & fish) = margin rapuh; "
                  "perlu strategi harga alternatif. Kategori promo rendah = "
                  "ruang untuk kampanye diskon terarah.",
        "baca": "Batang = % SKU yang sedang promo; label tambahan = rata-rata "
                "kedalaman diskon.",
    },
    "brand_positioning": {
        "judul": "Positioning Harga Brand (price index)",
        "kenapa": "Membandingkan harga brand mentah itu menyesatkan (biskuit vs "
                  "sampanye). Indeks harga = harga brand ÷ median kategorinya → "
                  "perbandingan yang adil.",
        "tujuan": "Memetakan brand mana yang premium vs value secara relatif "
                  "terhadap kategori masing-masing.",
        "dampak": "Brand premium (indeks >1,15) = ruang margin; brand value "
                  "(<0,85) = senjata kompetisi harga. Peta ini memandu strategi "
                  "portfolio & private-label.",
        "baca": "Garis putus-putus = 1,0 (median kategori). Kanan = premium, "
                "kiri = value.",
    },
    "own_brand": {
        "judul": "Peluang Private-Label (premium vs value share)",
        "kenapa": "Di kategori di mana brand premium mendominasi tapi brand value "
                  "sedikit, ada 'ruang kosong' untuk produk retailer sendiri.",
        "tujuan": "Menemukan kategori dengan peluang private-label terbesar untuk "
                  "merebut segmen sensitif harga.",
        "dampak": "Gap besar (premium ≫ value) = peluang meluncurkan own-brand "
                  "murah dengan margin lebih baik & loyalitas toko.",
        "baca": "Batang merah = pangsa SKU premium; hijau = value. Gap lebar = "
                "peluang.",
    },
    "rating_vs_price": {
        "judul": "Rating vs Harga",
        "kenapa": "Menguji asumsi umum 'mahal = berkualitas'. Bila tak ada "
                  "korelasi, klaim premium berbasis harga tak berdasar.",
        "tujuan": "Mengetahui apakah pelanggan menilai produk mahal lebih tinggi.",
        "dampak": "Korelasi ~nol/negatif = strategi 'value' bisa menang; kampanye "
                  "berbasis harga-murah-tapi-berkualitas jadi kredibel. Penting "
                  "untuk positioning private-label.",
        "baca": "Tiap titik = 1 produk; warna = tier harga. Bila awan titik "
                "datar, tidak ada kaitan harga-rating.",
    },
    "portfolio": {
        "judul": "Komposisi Assortment",
        "kenapa": "Jumlah SKU per kategori menunjukkan alokasi ruang rak & "
                  "kedalaman pilihan yang ditawarkan.",
        "tujuan": "Memahami bauran produk: apakah assortment seimbang atau "
                  "berat di kategori tertentu.",
        "dampak": "Kategori dengan SKU dominan = fokus operasional & supplier "
                  "utama; kategori tipis = peluang ekspansi lini produk.",
        "baca": "Kiri = pangsa jumlah SKU; kanan = kepadatan brand (SKU per brand).",
    },
    "value_winners": {
        "judul": "Produk Value Terbaik",
        "kenapa": "Pelanggan ingin 'value' = rating tinggi + harga satuan murah, "
                  "bukan sekadar harga murah.",
        "tujuan": "Mengidentifikasi produk yang memberi kualitas terbaik per "
                  "pound — kandidat rekomendasi & endcap.",
        "dampak": "Daftar ini bisa jadi dasar kampanye 'best value', etalase "
                  "khusus, atau rekomendasi berbasis data — pendorong konversi.",
        "baca": "Skor = 60% rating + 40% murah (per 100g). Batang lebih panjang = "
                "value lebih baik.",
    },
    "content_completeness": {
        "judul": "Kelengkapan Konten Produk",
        "kenapa": "Deskripsi produk memengaruhi SEO situs & keputusan pembelian "
                  "online; data hilang = pengalaman buruk bagi pelanggan.",
        "tujuan": "Menemukan kategori dengan kelengkapan konten terendah.",
        "dampak": "Kategori dengan deskripsi bolong = prioritas perbaikan konten "
                  "→ peningkatan trafik organik & konversi.",
        "baca": "Batang = % produk dengan deskripsi; label = rata-rata panjang teks.",
    },
    "kpi": {
        "judul": "Metrik Ringkas (KPI Band)",
        "kenapa": "Pembaca perlu konteks cepat sebelum analisis detail.",
        "tujuan": "Menampilkan metrik inti (jumlah produk, median harga, "
                  "tingkat promo, diskon, jumlah brand).",
        "dampak": "Angka berubah mengikuti filter → dasar cepat untuk diskusi & "
                  "keputusan.",
        "baca": "Setiap kartu = satu metrik + konteksnya.",
    },
}


def text(key: str) -> str:
    e = EXPLAIN.get(key)
    if not e:
        return ""
    parts = [f"**{e['judul']}**",
             f"- **Kenapa:** {e['kenapa']}",
             f"- **Tujuan:** {e['tujuan']}",
             f"- **Dampak:** {e['dampak']}"]
    if e.get("baca"):
        parts.append(f"- **Cara baca:** {e['baca']}")
    return "\n".join(parts)


def render(key: str, expanded: bool = False, st=None):
    if st is None:
        import streamlit as st  # noqa
    e = EXPLAIN.get(key)
    if not e:
        return
    with st.expander(f"💡 {e['judul']} — Kenapa · Tujuan · Dampak", expanded=expanded):
        st.markdown(
            f"**🔎 Kenapa** — {e['kenapa']}\n\n"
            f"**🎯 Tujuan** — {e['tujuan']}\n\n"
            f"**📈 Dampak** — {e['dampak']}")
        if e.get("baca"):
            st.caption(f"👁️ Cara baca: {e['baca']}")


def audit() -> dict:
    return {k: all(v.get(f) for f in ("kenapa", "tujuan", "dampak"))
            for k, v in EXPLAIN.items()}


if __name__ == "__main__":
    ok = audit()
    print(f"Penjelasan: {len(ok)} | lengkap: {sum(ok.values())}")
    for k, v in ok.items():
        print(f"  {'OK ' if v else 'MISSING'} {k}")
