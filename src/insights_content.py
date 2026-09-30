
# ---------------------------------------------------------------------------
# KONTEN INSIGHT — Morrisons Market Intelligence
# Sudut pandang: analis ritel/kategori yang mengelola harga, promosi, & assort.
# Format rekomendasi = KAYA (aksi + langkah + metrik + pemilik).
# ---------------------------------------------------------------------------
from insight import register

register(
    "kpi",
    kesimpulan=(
        "KPI merangkum skala katalog: jumlah produk, kategori, rentang harga, "
        "dan pangsa promosi. Angka-angka ini menentukan seberapa besar ruang "
        "untuk optimalisasi harga & asortimen."),
    rekomendasi=[
        {
            "aksi": "Jadikan KPI katalog sebagai baseline resmi sebelum mengubah strategi pricing kategori.",
            "langkah": [
                "Bekukan snapshot baseline: 11.208 produk, 13 kategori, 792 unique brand, dari scraping groceries.morrisons.com.",
                "Hitung median harga (effective_price) per 13 kategori dan simpan sebagai 'garis dasar' pembanding.",
                "Catat promo rate awal (~10.8%) dan median discount (~-24.2%) sebagai titik acuan margin.",
                "Sosialisasikan baseline ini ke tim kategori sebagai angka rujukan tunggal sebelum keputusan harga diambil.",
            ],
            "metrik": "Baseline ter-dokumentasi untuk 13/13 kategori; deviasi harga >5% vs baseline wajib dijustifikasi.",
            "pemilik": "Head of Category Analytics",
        },
        {
            "aksi": "Pantau rasio promosi bulanan agar tetap di koridor sehat (target ~10.8%).",
            "langkah": [
                "Hitung promo rate = jumlah is_promo TRUE ÷ 11.208 produk setiap bulan.",
                "Bandingkan dengan koridor: >13% alarm margin tergerus, <8% alarm daya tarik melemah.",
                "Tandai kategori dengan promo rate menyimpang >3pp dari rata-rata rantai untuk ditinjau.",
                "Laporkan penyimpangan ke tim promosi dengan rekomendasi penyesuaian diskon.",
            ],
            "metrik": "Promo rate bulanan dalam rentang 8%–13%; jumlah kategori menyimpang <3 per bulan.",
            "pemilik": "Promotion & Pricing Manager",
        },
        {
            "aksi": "Jadikan KPI ini tolok ukur bulanan untuk mendeteksi pergeseran katalog dini.",
            "langkah": [
                "Tetapkan review bulanan atas 4 KPI inti: jumlah produk, jumlah kategori, median harga, promo rate.",
                "Buat ambang peringatan: perubahan jumlah produk >5% atau median harga >3% memicu investigasi.",
                "Telusuri akar pergeseran (delisting SKU, kenaikan harga pemasok, atau banjir promo).",
                "Terbitkan ringkasan 1-halaman ke manajemen tiap bulan dengan status merah/kuning/hijau.",
            ],
            "metrik": "100% bulan terlapor; waktu deteksi pergeseran katalog <1 siklus bulan.",
            "pemilik": "Category Insights Lead",
        },
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
        {
            "aksi": "Terapkan strategi harga BEDA per kategori sesuai price_index terhadap median kategori.",
            "langkah": [
                "Hitung price_index = effective_price ÷ median kategori untuk seluruh 11.208 produk.",
                "Segmen kategori pokok (mis. roti, susu) → jaga price_index ≤0.95 agar tetap kompetitif.",
                "Segmen kategori bernilai (mis. daging, seafood) → longgarkan ke price_index 1.05–1.15 untuk ruang margin.",
                "Jalankan uji A/B harga pada 1–2 kategori sebelum rollout penuh ke 13 kategori.",
            ],
            "metrik": "Price index kategori pokok ≤0.95; margin bruto kategori bernilai naik ≥2pp.",
            "pemilik": "Category Pricing Manager",
        },
        {
            "aksi": "Fokuskan analisis kompetitor pada kategori dengan pembelian paling sering, bukan yang termahal.",
            "langkah": [
                "Peringkat 13 kategori berdasarkan frekuensi pembelian (bukan harga median).",
                "Pilih 4–5 kategori paling sering sebagai fokus pemantauan harga kompetitor mingguan.",
                "Gunakan reviews dan rating (tersedia 99.7%) sebagai proksi popularitas untuk memvalidasi pilihan.",
                "Skor prioritas gabungan = frekuensi tinggi × price_index rendah.",
            ],
            "metrik": "Cakupan pemantauan kompetitor 100% pada 5 kategori paling sering dibeli.",
            "pemilik": "Competitive Intelligence Analyst",
        },
        {
            "aksi": "Waspadai kategori dengan median harga naik — indikasi inflasi pemasok untuk dinegosiasikan.",
            "langkah": [
                "Lacak perubahan median harga per kategori tiap kuartal dari snapshot scraping.",
                "Tandai kategori dengan kenaikan median >3% sebagai 'watchlist inflasi'.",
                "Telusuri apakah kenaikan serentak (pemasok) atau terisolasi (1 brand).",
                "Bawa watchlist ke sesi negosiasi pemasok dengan data median sebagai bukti.",
            ],
            "metrik": "100% kategori dengan kenaikan median >3% masuk daftar negosiasi dalam 1 kuartal.",
            "pemilik": "Procurement & Supplier Relations",
        },
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
        {
            "aksi": "Tambah produk di kategori dengan permintaan tinggi tapi asortimen terbatas (celah peluang).",
            "langkah": [
                "Petakan sebaran 11.208 produk ke 13 kategori; tandai kategori ramping (<5% SKU).",
                "Silang dengan sinyal permintaan: rating tinggi (mendekati 99.7% ketersediaan data) + reviews banyak.",
                "Identifikasi 2–3 celah SKU dalam kategori ramping dengan permintaan terbukti.",
                "Ajukan onboarding 5–10 SKU per celah ke tim assortment.",
            ],
            "metrik": "Kenaikan jumlah SKU ≥10% di kategori target tanpa penurunan rating rata-rata kategori.",
            "pemilik": "Assortment & Sourcing Lead",
        },
        {
            "aksi": "Rampingkan kategori dengan banyak produk berkinerja rendah (SKU redundant) untuk efisiensi rak & modal.",
            "langkah": [
                "Hitung value_score (60% rating + 40% murah, min 10 reviews) per produk.",
                "Tandai SKU berkinerja rendah: rating bawah + value_score rendah + reviews <10.",
                "Susun kandidat delisting di kategori dengan SKU berlebih (kategori gemuk).",
                "Uji dampak dengan daftar 20 SKU kandidat sebelum delisting masif.",
            ],
            "metrik": "Perputaran stok naik ≥5% setelah trimming; delisting tidak menurunkan penjualan kategori >2%.",
            "pemilik": "Category Manager",
        },
        {
            "aksi": "Seimbangkan asortimen agar pelanggan menemukan pilihan tanpa paradox of choice.",
            "langkah": [
                "Ukur rasio SKU per kategori (indeks 1.0 = rata-rata 11.208 ÷ 13 kategori ≈ 862 SKU).",
                "Tandai kategori dengan SKU >2× rata-rata (terlalu tebal) dan <0.5× (terlalu ramping).",
                "Rebalance bertahap: tambah di ramping, kurangi di tebal, jaga jangkar brand utama.",
                "Monitor jumlah reviews per kategori sebagai sinyal keterlibatan pelanggan.",
            ],
            "metrik": "Rasio SKU antar-kategori dalam rentang 0.5×–2× rata-rata.",
            "pemilik": "Head of Merchandising",
        },
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
        {
            "aksi": "Identifikasi produk 'overpriced' (harga tinggi, rating rendah) untuk turun harga atau perbaikan kualitas.",
            "langkah": [
                "Kueri produk dengan price_index ≥1.15 (Premium) TAPI rating di kuartil terbawah.",
                "Filter hanya produk dengan reviews cukup (≥10) agar sinyal rating andal.",
                "Klasifikasi penyebab: harga keliru, kualitas kurang, atau deskripsi satuan salah.",
                "Tetapkan tindakan per kandidat: repricing, perbaikan kualitas, atau delisting.",
            ],
            "metrik": "Konversi ≥50% produk overpriced menjadi rating naik atau harga terkoreksi dalam 1 kuartal.",
            "pemilik": "Category Quality & Pricing Officer",
        },
        {
            "aksi": "Tonjolkan produk 'value terbaik' (harga wajar, rating tinggi) dalam promosi untuk loyalitas.",
            "langkah": [
                "Pilih produk dengan value_score tinggi (60% rating + 40% murah, min 10 reviews).",
                "Kelompokkan pemenang dari 792 brand untuk mendapat magnet lintas-kategori.",
                "Tempatkan di rak utama & materi promosi sebagai pendorong loyalitas.",
                "Pantau rating & reviews pasca-promosi untuk memastikan kepuasan terjaga.",
            ],
            "metrik": "Kenaikan reviews ≥10% pada produk value winner; rating tetap ≥kuartil atas.",
            "pemilik": "Marketing & Loyalty Manager",
        },
        {
            "aksi": "Gunakan rating sebagai sinyal kualitas untuk keputusan asortimen (rating tersedia 99.7%).",
            "langkah": [
                "Tandai produk tanpa rating (0.3% = sekitar 34 produk) untuk ditinjau datanya.",
                "Bobot keputusan asortimen dengan rating + jumlah reviews, bukan hanya harga.",
                "Hindari memasukkan SKU rating rendah meski harganya menarik.",
                "Integrasikan skor kualitas ke scorecard pemilihan pemasok.",
            ],
            "metrik": "100% keputusan asortimen baru menyertakan rating & reviews sebagai kriteria.",
            "pemilik": "Assortment Committee",
        },
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
        {
            "aksi": "Evaluasi efektivitas promosi: apakah promo TINGGI benar-benar menaikkan volume atau hanya menggerus margin?",
            "langkah": [
                "Hitung promo rate & median discount per kategori dari is_promo dan discount_pct.",
                "Bandingkan dengan baseline rantai: promo rate ~10.8%, median discount ~-24.2%.",
                "Pisahkan kategori yang promonya 'efektif' (volume naik) vs 'defensif' (hanya margin turun).",
                "Hentikan atau kurangi diskon pada kategori defensif.",
            ],
            "metrik": "Rasio promo efektif ≥70%; margin kategori tidak turun >2pp akibat diskon.",
            "pemilik": "Promotion Effectiveness Analyst",
        },
        {
            "aksi": "Gunakan promosi terarah pada kategori elastis, hindari diskon di kategori dengan pembelian pasti.",
            "langkah": [
                "Klasifikasi 13 kategori: elastis (responsif harga) vs inelastis (kebutuhan pokok).",
                "Alokasikan mayoritas budget promo ke kategori elastis.",
                "Untuk kategori inelastis, ganti diskon dengan ketersediaan & kesegaran.",
                "Ukur elastisitas dari respons volume terhadap discount_pct historis.",
            ],
            "metrik": "≥80% budget promo terkonsentrasi di kategori elastis terbukti.",
            "pemilik": "Trade Marketing Manager",
        },
        {
            "aksi": "Hindari 'perang diskon' berkelanjutan yang menurunkan ekspektasi harga pelanggan secara permanen.",
            "langkah": [
                "Lacak rata-rata discount_pct per kategori tiap bulan; waspadai tren menurun (semakin besar).",
                "Tetapkan plafon diskon per kategori (mis. jangan lampaui -35%).",
                "Tandai kategori dengan discount mendekati median -24.2% berulang sebagai risiko margin.",
                "Rotasi promosi agar tidak semua kategori terdiskon serentak.",
            ],
            "metrik": "Tidak ada kategori dengan discount_pct rata-rata lebih dalam dari -35% selama 2 kuartal.",
            "pemilik": "Head of Commercial Strategy",
        },
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
        {
            "aksi": "Hindari masuk ke segmen yang sudah padat (mis. value terlalu ramai) kecuali punya keunggulan struktural.",
            "langkah": [
                "Klasifikasi 792 brand ke brand_tier: Premium (price_index ≥1.15), Value (≤0.85), Mainstream.",
                "Hitung kepadatan tiap tier & setiap kategori (jumlah brand & SKU).",
                "Tandai tier yang over-crowded (SKU berlimpah, differensiasi tipis).",
                "Tolak penambahan SKU baru di tier padat tanpa keunggulan biaya/kualitas jelas.",
            ],
            "metrik": "0 brand baru masuk tier over-crowded tanpa justifikasi struktural tertulis.",
            "pemilik": "Brand Portfolio Manager",
        },
        {
            "aksi": "Cari celah positioning: segmen harga dengan sedikit pemain tapi permintaan tinggi.",
            "langkah": [
                "Buat matriks tier × kategori dan hitung jumlah brand aktif per sel.",
                "Tandai sel dengan sedikit brand (low competition) namun reviews/rating tinggi (permintaan).",
                "Validasi kelayakan pasokan sebelum masuk sel tersebut.",
                "Pilot 1–2 brand di celah terpilih sebelum ekspansi.",
            ],
            "metrik": "Identifikasi ≥3 sel celah; minimal 1 pilot brand diluncurkan per tahun.",
            "pemilik": "Category Development Manager",
        },
        {
            "aksi": "Posisikan private label pada value (margin) atau premium (diferensiasi) secara sengaja.",
            "langkah": [
                "Ukur posisi private label saat ini terhadap brand_tier (Premium/Value/Mainstream).",
                "Tentukan target: value untuk volume/margin, atau premium untuk diferensiasi.",
                "Sesuaikan price_index private label agar konsisten dengan tier target.",
                "Komunikasikan positioning ke pelanggan lewat kemasan & kanal promosi.",
            ],
            "metrik": "Price index private label konsisten dengan tier target dalam ±0.05.",
            "pemilik": "Own Brand Strategy Lead",
        },
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
        {
            "aksi": "Perluas private label di kategori dengan margin tinggi & loyalitas merek nasional rendah.",
            "langkah": [
                "Skor 13 kategori berdasarkan margin (relatif) × loyalitas brand nasional (rendah = peluang).",
                "Pilih 3 kategori teratas sebagai target ekspansi private label.",
                "Tentukan jumlah SKU baru per kategori sesuai celah assortment.",
                "Luncurkan bertahap dan pantau penerimaan lewat rating & reviews.",
            ],
            "metrik": "Kenaikan pangsa SKU private label ≥5pp di kategori target dalam 1 tahun.",
            "pemilik": "Own Brand Development Manager",
        },
        {
            "aksi": "Sediakan dua tingkatan private label: value (volume) & premium (margin) untuk menjangkau semua segmen.",
            "langkah": [
                "Posisikan lini value pada price_index ≤0.85 dan lini premium ≥1.15.",
                "Pastikan tidak ada kanibalisasi: bedakan positioning, kemasan, ukuran.",
                "Isi kedua tier di kategori prioritas dengan SKU pemenang berbasis value_score.",
                "Ukur bauran penjualan value vs premium tiap kuartal.",
            ],
            "metrik": "Kontribusi tier premium terhadap penjualan private label ≥25%.",
            "pemilik": "Own Brand Strategy Lead",
        },
        {
            "aksi": "Investasi pada kualitas & kemasan private label — persepsi pelanggan adalah penentu utama.",
            "langkah": [
                "Pantau rating private label vs merek nasional di kategori yang sama.",
                "Tandai SKU private label dengan rating di bawah median kategori untuk perbaikan.",
                "Uji peningkatan kemasan/kualitas pada 3 SKU lalu bandingkan rating & reviews.",
                "Terapkan standar mutu minimum sebelum SKU private label diluncurkan.",
            ],
            "metrik": "Rating rata-rata private label ≥ rating median kategori; gap ≤0.2 bintang.",
            "pemilik": "Product Quality & Branding Lead",
        },
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
        {
            "aksi": "Tonjolkan produk value winners dalam penempatan rak & materi promosi.",
            "langkah": [
                "Ambil produk dengan value_score tertinggi (60% rating + 40% murah, min 10 reviews).",
                "Pilih pemenang beragam dari 13 kategori agar daya tarik menyeluruh.",
                "Tempatkan pada rak mata (eye-level) & tandai dengan signage value.",
                "Sertakan dalam materi promosi lintas-kanal.",
            ],
            "metrik": "Kenaikan penjualan unit ≥8% pada produk yang ditonjolkan.",
            "pemilik": "Retail Marketing Manager",
        },
        {
            "aksi": "Jadikan mereka 'loss leader' untuk menarik kunjungan; keuntungan dari keranjang keseluruhan.",
            "langkah": [
                "Pilih 5–10 value winner dengan potensi trafik tertinggi.",
                "Terapkan harga agresif terbatas sebagai magnet kunjungan.",
                "Analisis keranjang: ukur penjualan produk pelengkap yang ikut naik.",
                "Evaluasi apakah margin keranjang menutupi margin yang dikorbankan.",
            ],
            "metrik": "Nilai keranjang rata-rata pembeli loss leader naik ≥10%.",
            "pemilik": "Head of Pricing & Promotions",
        },
        {
            "aksi": "Jaga pasokan produk ini tanpa putus; kehabisan = kehilangan pelanggan.",
            "langkah": [
                "Tetapkan level stok pengaman khusus untuk value winners teratas.",
                "Pasang peringatan otomatis saat stok menipis.",
                "Siapkan substitusi ber-vskor tinggi jika SKU utama kosong.",
                "Tinjau ketersediaan mingguan untuk daftar pemenang.",
            ],
            "metrik": "Ketersediaan (in-stock rate) value winners ≥98% setiap bulan.",
            "pemilik": "Supply Chain & Replenishment Manager",
        },
    ],
    risiko=(
        "Produk value winner yang kehabisan stok berulang membuat pelanggan "
        "percaya toko tidak andal dan beralih. Loyalitas terbangun lambat, "
        "hancur cepat."),
    tingkat="sedang",
)


# --------------------------------------------------------------------------
# Chart ECharts (v2) — insight & rekomendasi.
# --------------------------------------------------------------------------

register(
    "echarts_treemap",
    kesimpulan=(
        "Treemap memetakan dua tingkat sekaligus: luas kategori = jumlah SKU, "
        "kotak di dalamnya = brand teratas. Kategori gemuk dengan brand dominan "
        "tunggal menandakan konsentrasi pasokan (risiko bila brand itu bermasalah); "
        "kategori tersebar merata lebih tangguh terhadap gangguan satu pemasok."),
    rekomendasi=[
        {
            "aksi": "Tandai kategori dengan satu brand menyerap porsi besar SKU — tambah alternatif untuk kurangi risiko pasokan.",
            "langkah": [
                "Hitung pangsa SKU brand teratas per kategori dari 792 brand.",
                "Tandai kategori dengan brand dominan menyerap >40% SKU kategori.",
                "Cari & onboard 1–2 brand alternatif untuk kategori berisiko.",
                "Pantau konsentrasi tiap kuartal sebagai indikator risiko pasokan.",
            ],
            "metrik": "Pangsa SKU brand teratas turun di bawah 40% di kategori berisiko tinggi.",
            "pemilik": "Supply Risk & Sourcing Manager",
        },
        {
            "aksi": "Untuk kategori gemuk, negosiasikan lebih agresif (volume besar = daya tawar).",
            "langkah": [
                "Identifikasi kategori gemuk (SKU tinggi) sebagai prioritas negosiasi.",
                "Siapkan data volume SKU & jumlah brand sebagai bukti daya tawar.",
                "Susun target syarat dagang (harga, term, slotting) per kategori gemuk.",
                "Jadwalkan sesi negosiasi khusus untuk kategori terpilih.",
            ],
            "metrik": "Perbaikan syarat dagang ≥3% pada minimal 3 kategori gemuk.",
            "pemilik": "Procurement Lead",
        },
        {
            "aksi": "Gunakan treemap untuk mengomunikasikan struktur katalog ke manajemen secara instan.",
            "langkah": [
                "Jadikan treemap bagian tetap laporan katalog bulanan.",
                "Anotasi kategori gemuk & brand dominan langsung pada visual.",
                "Sertakan narasi 3 kalimat tentang konsentrasi & peluang.",
                "Distribusikan ke manajemen sebelum rapat kategori.",
            ],
            "metrik": "Treemap hadir di 100% laporan katalog bulanan.",
            "pemilik": "Category Insights Lead",
        },
    ],
    risiko=(
        "Konsentrasi brand yang tak terlihat menyembunyikan risiko: gangguan "
        "satu pemasok bisa mengosongkan seluruh rak kategori. Sebaliknya, rasio "
        "SKU bukan ukuran penjualan — jangan samakan jumlah SKU dengan omzet."),
    tingkat="sedang",
)

register(
    "echarts_boxplot",
    kesimpulan=(
        "Boxplot harga per kategori menampilkan MEDIAN, SEBARAN, dan PENCILAN "
        "harga. Kategori dengan kotak panjang & banyak pencilan atas = rentang "
        "harga sangat lebar (produk murah sampai premium dalam satu kategori), "
        "menandakan peluang segmentasi. Kategori dengan kotak sempit = pasar "
        "harga yang ketat/komoditas."),
    rekomendasi=[
        {
            "aksi": "Kategori berjarak lebar → kembangkan tier premium & value terpisah; jangan pakai satu harga tengah.",
            "langkah": [
                "Ukur lebar sebaran harga (IQR) per kategori dari 11.208 produk.",
                "Tandai kategori IQR lebar sebagai kandidat segmentasi tier.",
                "Rancang SKU premium (price_index ≥1.15) & value (≤0.85) di kategori tersebut.",
                "Luncurkan tier baru dan pantau penerimaan tiap segmen.",
            ],
            "metrik": "≥2 kategori lebar memiliki tier premium & value aktif dengan penjualan terukur.",
            "pemilik": "Category Strategy Manager",
        },
        {
            "aksi": "Selidiki pencilan harga atas: apakah produk premium wajar atau salah data (mis. deskripsi satuan).",
            "langkah": [
                "Deteksi produk dengan price_index jauh di atas 1.15 di tiap kategori.",
                "Verifikasi kesesuaian satuan/kemasan pada data scraping.",
                "Pisahkan pencilan sah (premium asli) dari galat data.",
                "Koreksi galat data dan tandai premium asli sebagai referensi tier.",
            ],
            "metrik": "100% pencilan atas terverifikasi; galat data terkoreksi <1 siklus pelaporan.",
            "pemilik": "Data Quality Analyst",
        },
        {
            "aksi": "Untuk kategori sempit, bersaing lewat ketersediaan & kesegaran, bukan harga.",
            "langkah": [
                "Identifikasi kategori IQR sempit (pasar komoditas/ketat).",
                "Alihkan fokus kompetitif dari harga ke ketersediaan & kesegaran.",
                "Tetapkan target in-stock rate tinggi untuk kategori tersebut.",
                "Hindari perang harga di kategori sempit yang selisihnya tipis.",
            ],
            "metrik": "In-stock rate kategori sempit ≥98%; tidak ada penurunan harga agresif >3%.",
            "pemilik": "Operations & Availability Manager",
        },
    ],
    risiko=(
        "Menetapkan satu harga mewakili kategori berjarak lebar berisiko "
        "kehilangan segmen premium (margin tinggi) atau mencemari citra value. "
        "Distribusi, bukan rata-rata, yang menentukan strategi tier."),
    tingkat="tinggi",
)

register(
    "echarts_pictorial",
    kesimpulan=(
        "Bar bertitik menampilkan jumlah SKU brand teratas sebagai blok visual — "
        "lebih cepat dicerna untuk laporan. Brand teratas mencerminkan kekuatan "
        "lini produk, tetapi sekali lagi: banyak SKU ≠ banyak penjualan. Ia "
        "menjawab 'siapa mendominasi RAK', bukan 'siapa mendominasi KERANJANG'."),
    rekomendasi=[
        {
            "aksi": "Pasangkan jumlah SKU dengan data penjualan bila tersedia sebelum menyimpulkan brand 'pemenang'.",
            "langkah": [
                "Ambil peringkat brand berdasarkan jumlah SKU dari 792 brand.",
                "Tambahkan kolom penjualan/unit terjual (bila tersedia) untuk konteks.",
                "Tandai brand dengan SKU tinggi namun penjualan rendah sebagai kandidat tinjauan.",
                "Ubah definisi 'pemenang' menjadi berbasis penjualan, bukan SKU.",
            ],
            "metrik": "100% brand-review menyertakan data penjualan; bukan SKU saja.",
            "pemilik": "Commercial Analytics Lead",
        },
        {
            "aksi": "Untuk brand dengan SKU banyak tapi rating rendah, tinjau ulang mutu/relevansi produk.",
            "langkah": [
                "Silang jumlah SKU per brand dengan rating rata-rata (99.7% ketersediaan data).",
                "Tandai brand SKU banyak + rating di bawah median kategori.",
                "Tinjau relevansi & mutu SKU brand tersebut.",
                "Kurangi SKU lemah atau dorong perbaikan kualitas.",
            ],
            "metrik": "Penurunan SKU lemah ≥10% pada brand bermasalah; rating naik atau stabil.",
            "pemilik": "Category Manager",
        },
        {
            "aksi": "Gunakan grafik ini sebagai pembuka diskusi brand-review, bukan bukti kinerja.",
            "langkah": [
                "Jadikan pictorial sebagai slide pembuka sesi brand-review.",
                "Sertakan disclaimer 'SKU ≠ penjualan' pada visual.",
                "Lanjutkan dengan data penjualan, rating, dan value_score sebagai substansi.",
                "Catat keputusan tindak lanjut per brand yang dibahas.",
            ],
            "metrik": "Sesi brand-review bulanan terlaksana dengan agenda & tindak lanjut tercatat.",
            "pemilik": "Head of Category Analytics",
        },
    ],
    risiko=(
        "Menilai kekuatan brand dari jumlah SKU saja menyesatkan — SKU berlebih "
        "justru bisa menandakan rak penuh produk berkinerja rendah. Keputusan "
        "asortimen tanpa data penjualan berisiko memperbesar masalah."),
    tingkat="sedang",
)
