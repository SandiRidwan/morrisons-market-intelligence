
# ---------------------------------------------------------------------------
# KONTEN INSIGHT — Morrisons Market Intelligence
# Sudut pandang: analis ritel/kategori yang mengelola harga, promosi, & assort.
# ---------------------------------------------------------------------------
from insight import register

register(
    "kpi",
    kesimpulan=(
        "KPI merangkum skala katalog: jumlah produk, kategori, rentang harga, "
        "dan pangsa promosi. Angka-angka ini menentukan seberapa besar ruang "
        "untuk optimalisasi harga & asortimen."),
    rekomendasi=[
        "Gunakan distribusi harga sebagai baseline sebelum mengubah strategi "
        "pricing kategori.",
        "Pantau rasio promosi — terlalu tinggi menggerus margin, terlalu rendah "
        "kehilangan daya tarik.",
        "Jadikan KPI ini tolok ukur bulanan untuk mendeteksi pergeseran katalog.",
    ],
    risiko=(
        "Mengelola harga tanpa baseline katalog berisiko keputusan yang tidak "
        "konsisten antar-kategori. Margin tergerus di satu sisi tanpa disadari."),
    tingkat="sedang",
)

register(
    "price_by_category",
    kesimpulan=(
        "Median harga berbeda tajam antar-kategori. Kategori bernilai tinggi "
        "(mis. daging) punya rentang harga lebar, sementara kategori pokok "
        "(mis. roti) lebih sempit. Struktur ini menentukan di mana tekanan harga "
        "paling sensitif."),
    rekomendasi=[
        "Terapkan strategi harga BEDA per kategori: kategori sensitif harga "
        "(pokok) → jaga kompetitif; kategori bernilai → ruang margin lebih besar.",
        "Fokuskan analisis kompetitor pada kategori dengan pembelian paling "
        "sering (bukan yang paling mahal).",
        "Waspadai kategori dengan harga median naik — bisa menandakan inflasi "
        "pemasok yang perlu dinegosiasikan.",
    ],
    risiko=(
        "Menaikkan harga di kategori sensitif (pokok) untuk mengejar margin "
        "berisiko kehilangan pelanggan inti. Salah kategori = penurunan volume "
        "yang tak terkompensasi."),
    tingkat="tinggi",
)

register(
    "portfolio",
    kesimpulan=(
        "Komposisi asortimen menunjukkan sebaran produk antar-kategori. "
        "Ketidakseimbangan (beberapa kategori terlalu ramping/tebal) menandakan "
        "peluang atau kelebihan yang bisa dioptimalkan."),
    rekomendasi=[
        "Tambah produk di kategori dengan permintaan tinggi tapi asortimen "
        "terbatas (celah peluang).",
        "Rampingkan kategori dengan banyak produk berkinerja rendah (SKU "
        "redundant) untuk efisiensi rak & modal.",
        "Seimbangkan asortimen agar pelanggan menemukan pilihan tanpa terlalu "
        "banyak keputusan (paradox of choice).",
    ],
    risiko=(
        "Asortimen terlalu lebar memperlambat perputaran stok & mengikat modal. "
        "Terlalu sempit membuat pelanggan beralih ke pesaing karena kurang pilihan."),
    tingkat="sedang",
)

register(
    "rating_vs_price",
    kesimpulan=(
        "Scatter rating vs harga mengungkap posisi produk: apakah harga tinggi "
        "selalu diikuti kepuasan tinggi? Titik dengan harga tinggi TAPI rating "
        "rendah adalah 'overpriced' — paling berisiko."),
    rekomendasi=[
        "Identifikasi produk 'overpriced' (harga tinggi, rating rendah) — "
        "kandidat untuk turun harga atau perbaikan kualitas.",
        "Tonjolkan produk 'value terbaik' (harga wajar, rating tinggi) dalam "
        "promosi — pendorong loyalitas.",
        "Gunakan rating sebagai sinyal kualitas untuk keputusan asortimen.",
    ],
    risiko=(
        "Produk overpriced mencoreng persepsi nilai toko secara keseluruhan. "
        "Pelanggan yang kecewa harga bisa beralih permanen ke pesaing."),
    tingkat="tinggi",
)

register(
    "promo_by_category",
    kesimpulan=(
        "Tingkat promosi berbeda antar-kategori. Kategori dengan promosi sangat "
        "tinggi bisa menandakan perang harga atau produk yang sulit terjual; "
        "promosi rendah menandakan margin stabil tapi mungkin kurang menarik."),
    rekomendasi=[
        "Evaluasi efektivitas promosi: apakah promosi TINGGI benar-benar menaikkan "
        "volume, atau hanya menggerus margin?",
        "Gunakan promosi terarah pada kategori yang elastis (responsif harga), "
        "hindari diskon di kategori yang pembeliannya sudah pasti.",
        "Hindari 'perang diskon' berkelanjutan — ia menurunkan ekspektasi harga "
        "pelanggan secara permanen.",
    ],
    risiko=(
        "Promosi terus-menerus melatih pelanggan menunggu diskon — pada akhirnya "
        "mereka tidak mau bayar harga normal. Margin turun permanen tanpa "
        "kenaikan volume yang menutupi."),
    tingkat="tinggi",
)

register(
    "brand_positioning",
    kesimpulan=(
        "Price index brand menunjukkan siapa bermain di segmen premium vs value. "
        "Peta ini mengungkap posisi kompetitif tiap merek dan celah di pasar "
        "yang belum tergarap."),
    rekomendasi=[
        "Hindari masuk ke segmen yang sudah padat (mis. value yang terlalu ramai) "
        "kecuali punya keunggulan struktural.",
        "Cari celah positioning: segmen harga dengan sedikit pemain tapi "
        "permintaan tinggi.",
        "Untuk private label, posisikan pada value (potensi margin) atau premium "
        "(potensi diferensiasi).",
    ],
    risiko=(
        "Positioning yang salah (mis. premium tanpa diferensiasi) membuat produk "
        "gagal bersaing dengan merek mapan. Investasi asortimen terbuang."),
    tingkat="sedang",
)

register(
    "own_brand",
    kesimpulan=(
        "Analisis private label mengungkap pangsa value vs premium. Private label "
        "umumnya punya margin lebih tinggi — tetapi harus meyakinkan pelanggan "
        "tentang kualitas agar diterima."),
    rekomendasi=[
        "Perluas private label di kategori dengan margin tinggi & loyalitas "
        "merek nasional rendah.",
        "Sediakan dua tingkatan private label: value (volume) & premium "
        "(margin) untuk menjangkau semua segmen.",
        "Investasi pada kualitas & kemasan private label — persepsi pelanggan "
        "adalah penentu utama.",
    ],
    risiko=(
        "Private label berkualitas rendah merusak reputasi seluruh toko, bukan "
        "hanya produknya. Pelanggan yang kecewa bisa meninggalkan semua merek "
        "toko untuk waktu lama."),
    tingkat="tinggi",
)

register(
    "value_winners",
    kesimpulan=(
        "Produk 'value terbaik' (kombinasi harga wajar & kualitas/rating baik) "
        "adalah magnet loyalitas. Daftar ini menunjukkan produk yang paling "
        "layak ditonjolkan sebagai daya tarik utama."),
    rekomendasi=[
        "Tonjolkan produk value winners dalam penempatan rak & materi promosi.",
        "Jadikan mereka 'loss leader' untuk menarik kunjungan — keuntungan datang "
        "dari keranjang keseluruhan.",
        "Jaga pasokan produk ini tanpa putus; kehabisan = kehilangan pelanggan.",
    ],
    risiko=(
        "Produk value winner yang kehabisan stok berulang membuat pelanggan "
        "percaya toko tidak andal dan beralih. Loyalitas terbangun lambat, "
        "hancur cepat."),
    tingkat="sedang",
)
